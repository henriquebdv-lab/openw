"""
Seed de TESTE do Open Wheel Strategy.

Monta um ambiente de teste completo de uma vez so:
    python criar_banco.py
    python seed_teste.py

Cria:
    - 2 usuarios admin (senha 123456), nick "Razor"
    - Fornecedores (popular_banco)
    - "TEMPORADA 1" ativa com 10 corridas
    - Equipe completa pra cada admin (fornecedores mais baratos + eng nv1)
    - 40 JOGADORES FAKE (bots) JA PRONTOS pra quali+corrida (grid cheio):
      fornecedores random, parc ferme random, ajuste fino random, dados de
      classificacao random e stints random. Assim da pra rodar a corrida no
      admin e ver o replay com grid cheio.

Idempotente: nao duplica se rodar de novo.
"""
import random

from app import app
from models import (
    db, Usuario, Configuracao, Desenvolvimento, CarroJogador,
    FornecedorMotor, FornecedorCombustivel, FornecedorPneu,
    FornecedorCambio, FornecedorSuspensao, FornecedorEngenheiro,
    SetupFimDeSemana, AjusteSalvo, DadosClassificacao, EstrategiaStint,
)
from models_temporada import Temporada, CorridaAgendada
from seed_fornecedores import popular_banco
from pistas_reais_db import criar_banco as criar_banco_pistas_reais, listar_pistas_reais
import modelos_componente


# ---- CONFIG (mude aqui se quiser) ----
USUARIOS_ADMIN = [
    "henriquebdv@gmail.com",
    "henriquebettegaclaro@gmail.com",
]
SENHA_PADRAO = "123456"
NICK = "Razor"
NOME_TEMPORADA = "TEMPORADA 1"
QTD_CORRIDAS = 10
NOMES_EQUIPE = ["Racing Titans", "Velocity GP"]
QTD_BOTS = 40          # jogadores fake prontos pra correr (grid cheio)
MODELOS = modelos_componente.MODELOS  # [50,100,...,900]


# ---------------------------------------------------------
def criar_admins():
    criados = 0
    for email in USUARIOS_ADMIN:
        u = Usuario.query.filter_by(email=email).first()
        if u:
            u.eh_admin = True
            if hasattr(u, "nick") and not u.nick:
                u.nick = NICK
            continue
        u = Usuario(email=email, eh_admin=True)
        u.definir_senha(SENHA_PADRAO)
        if hasattr(u, "nick"):
            u.nick = NICK
        db.session.add(u)
        criados += 1
    db.session.commit()
    print(f"[OK] Admins: {criados} criado(s). Senha padrao: {SENHA_PADRAO}")


def criar_fornecedores():
    if FornecedorMotor.query.count() > 0:
        print("[SKIP] Fornecedores ja existem.")
        return
    popular_banco()
    print("[OK] Fornecedores gerados.")


def _mais_barato(Model):
    return Model.query.filter_by(ativo=True).order_by(Model.custo_temporada).first()


def _id_aleatorio(Model):
    ids = [r.id for r in Model.query.filter_by(ativo=True).all()]
    return random.choice(ids) if ids else None


def criar_equipes_admins():
    """Equipe completa (fornecedores mais baratos) pra cada admin sem equipe."""
    config = Configuracao.obter()
    criadas = 0
    admins = Usuario.query.filter(Usuario.email.in_(USUARIOS_ADMIN)).order_by(Usuario.id).all()
    for indice, usuario in enumerate(admins):
        if usuario.equipe:
            continue
        motor = _mais_barato(FornecedorMotor)
        comb = _mais_barato(FornecedorCombustivel)
        pneu = _mais_barato(FornecedorPneu)
        cambio = _mais_barato(FornecedorCambio)
        susp = _mais_barato(FornecedorSuspensao)
        eng = (FornecedorEngenheiro.query.filter_by(nivel=1, ativo=True)
               .order_by(FornecedorEngenheiro.custo_temporada).first())
        if not all([motor, comb, pneu, cambio, susp]):
            print("[AVISO] Faltam fornecedores. Rode a geracao antes.")
            return
        nome = NOMES_EQUIPE[indice] if indice < len(NOMES_EQUIPE) else f"Equipe {indice+1}"
        equipe = CarroJogador(
            usuario_id=usuario.id, nome=nome, orcamento=float(config.orcamento_inicial),
            motor_fornecedor_id=motor.id, combustivel_fornecedor_id=comb.id,
            pneu_fornecedor_id=pneu.id, chassi_fornecedor_id=None,
            cambio_fornecedor_id=cambio.id, suspensao_fornecedor_id=susp.id,
            engenheiro_fornecedor_id=eng.id if eng else None, combustivel_carregado=110.0,
        )
        db.session.add(equipe); db.session.flush()
        db.session.add(Desenvolvimento(
            equipe_id=equipe.id, chassi_percentual_aplicado=100.0,
            aero_percentual_aplicado=100.0, nivel_engenheiro_projetista=1))
        criadas += 1
    db.session.commit()
    print(f"[OK] Equipes dos admins: {criadas} criada(s) (piloto {NICK}).")


def criar_bots(proxima_corrida):
    """Gera QTD_BOTS jogadores fake JA PRONTOS pra quali+corrida da proxima corrida.
    Fornecedores, parc ferme, ajuste fino, dados de quali e stints todos random."""
    if not proxima_corrida:
        print("[AVISO] Sem proxima corrida — bots nao gerados.")
        return
    if Usuario.query.filter(Usuario.email.like("bot%@fake.com")).count() > 0:
        print("[SKIP] Bots ja existem.")
        return

    config = Configuracao.obter()
    pista_id = proxima_corrida.pista_real_id
    eng1 = FornecedorEngenheiro.query.filter_by(nivel=1, ativo=True).first()
    criados = 0

    for i in range(1, QTD_BOTS + 1):
        u = Usuario(email=f"bot{i}@fake.com", eh_admin=False, nick=f"Bot {i}")
        u.definir_senha("bot")
        db.session.add(u); db.session.flush()

        car = CarroJogador(
            usuario_id=u.id, nome=f"Bot Team {i}", orcamento=float(config.orcamento_inicial),
            motor_fornecedor_id=_id_aleatorio(FornecedorMotor),
            combustivel_fornecedor_id=_id_aleatorio(FornecedorCombustivel),
            pneu_fornecedor_id=_id_aleatorio(FornecedorPneu),
            chassi_fornecedor_id=None,
            cambio_fornecedor_id=_id_aleatorio(FornecedorCambio),
            suspensao_fornecedor_id=_id_aleatorio(FornecedorSuspensao),
            engenheiro_fornecedor_id=eng1.id if eng1 else None,
            combustivel_carregado=110.0,
        )
        db.session.add(car); db.session.flush()
        db.session.add(Desenvolvimento(
            equipe_id=car.id, chassi_percentual_aplicado=100.0,
            aero_percentual_aplicado=100.0, nivel_engenheiro_projetista=1))

        # Parc Ferme (travado)
        db.session.add(SetupFimDeSemana(
            equipe_id=car.id, corrida_id=proxima_corrida.id,
            modelo_motor=random.choice(MODELOS), modelo_cambio=random.choice(MODELOS),
            modelo_suspensao=random.choice(MODELOS), travado=True))

        # Ajuste fino (treino livre) random
        db.session.add(AjusteSalvo(
            equipe_id=car.id, pista_real_id=pista_id,
            ajuste_cambio=random.randint(1, 99), ajuste_suspensao=random.randint(1, 99),
            ajuste_aero_dianteiro=random.randint(1, 99), ajuste_aero_traseiro=random.randint(1, 99),
            ajuste_freio=50))

        # Dados de classificacao (quali) random
        db.session.add(DadosClassificacao(
            equipe_id=car.id, corrida_id=proxima_corrida.id,
            modelo_pneu=random.choice(MODELOS), combustivel_litros=float(random.randint(5, 12))))

        # Estrategia: 1 a 3 stints random
        for ordem in range(1, random.randint(1, 3) + 1):
            db.session.add(EstrategiaStint(
                equipe_id=car.id, ordem=ordem, modelo_pneu=random.choice(MODELOS),
                voltas=random.randint(15, 30), combustivel_litros=float(random.randint(40, 110))))
        criados += 1

    db.session.commit()
    print(f"[OK] {criados} jogadores FAKE prontos pra quali+corrida (grid cheio).")


def criar_temporada():
    existente = Temporada.query.filter_by(nome=NOME_TEMPORADA).first()
    if existente:
        print(f"[SKIP] Temporada '{NOME_TEMPORADA}' ja existe.")
        return existente
    Temporada.query.update({"ativa": False})
    temporada = Temporada(nome=NOME_TEMPORADA, ativa=True)
    db.session.add(temporada); db.session.flush()
    criar_banco_pistas_reais()
    pistas = listar_pistas_reais()[:QTD_CORRIDAS]
    for i, pista in enumerate(pistas, start=1):
        db.session.add(CorridaAgendada(
            temporada_id=temporada.id, pista_real_id=pista["id"],
            pista_nome=pista["nome"], ordem=i, executada=False))
    db.session.commit()
    print(f"[OK] '{NOME_TEMPORADA}' criada e ativa, com {len(pistas)} corridas.")
    return temporada


def main():
    with app.app_context():
        criar_admins()
        criar_fornecedores()
        criar_equipes_admins()
        temporada = criar_temporada()
        prox = temporada.proxima_corrida() if temporada else None
        criar_bots(prox)
        print("\n=== SEED DE TESTE CONCLUIDO ===")
        print(f"Logue com: {USUARIOS_ADMIN[0]} / senha: {SENHA_PADRAO}")
        print(f"Proxima corrida: {prox.pista_nome if prox else '—'} | {QTD_BOTS} bots prontos.")
        print("Va no /admin -> Dia de Corrida -> rodar classificacao e corrida.")


if __name__ == "__main__":
    main()
