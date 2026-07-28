"""
Seed de TESTE do Open Wheel Strategy.

Monta um ambiente de teste completo de uma vez so:
    python criar_banco.py
    python seed_teste.py

Cria:
    - 1 usuario admin (senha 123456), nick "Razor"
    - Fornecedores (popular_banco)
    - "TEMPORADA 1" ativa com 10 corridas
    - Equipe completa pro admin (fornecedores mais baratos + eng nv1)
    - N JOGADORES FAKE (bots) montados COMO UM JOGADOR:
      * Orcamento inicial de 55.000
      * Escolhem os fornecedores MAIS BARATOS de cada categoria (motor,
        combustivel, pneu, cambio, suspensao) + engenheiro nivel 1
      * Os contratos (custo_temporada) sao DEBITADOS do orcamento (igual jogador)
      * Ja preparados pra quali+corrida (parc ferme, ajuste fino, quali, stints)

Assim os bots NAO "roubam": todos correm com pecas baratas equivalentes, e os
tempos na 1a temporada ficam parelhos (sem bot com peca cara de graca).

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
]
SENHA_PADRAO = "123456"
NICK = "Razor"
NOME_TEMPORADA = "TEMPORADA 1"
QTD_CORRIDAS = 10
NOMES_EQUIPE = ["Racing Titans"]
QTD_BOTS = 19          # jogadores fake prontos pra correr (grid cheio: 19 bots + voce = 20)
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
    """Retorna o fornecedor ATIVO mais barato (menor custo_temporada)."""
    return Model.query.filter_by(ativo=True).order_by(Model.custo_temporada).first()


def _montar_equipe_como_jogador(usuario, nome_equipe):
    """Monta uma equipe IGUAL a um jogador iniciante:
    - pega os 5 fornecedores MAIS BARATOS + engenheiro nivel 1
    - DEBITA os contratos (custo_temporada) do orcamento de 55.000
    Retorna a equipe criada (ou None se faltar fornecedor)."""
    config = Configuracao.obter()

    motor = _mais_barato(FornecedorMotor)
    comb = _mais_barato(FornecedorCombustivel)
    pneu = _mais_barato(FornecedorPneu)
    cambio = _mais_barato(FornecedorCambio)
    susp = _mais_barato(FornecedorSuspensao)
    eng = (FornecedorEngenheiro.query.filter_by(nivel=1, ativo=True)
           .order_by(FornecedorEngenheiro.custo_temporada).first())

    if not all([motor, comb, pneu, cambio, susp]):
        return None

    # Debita os contratos dos 5 fornecedores (igual ao jogador real).
    # Engenheiro nivel 1 e "gratis" (incluso), entao NAO entra no debito.
    orcamento = float(config.orcamento_inicial)
    total_contratos = float(
        (motor.custo_temporada or 0) + (comb.custo_temporada or 0) +
        (pneu.custo_temporada or 0) + (cambio.custo_temporada or 0) +
        (susp.custo_temporada or 0)
    )
    orcamento_final = orcamento - total_contratos

    equipe = CarroJogador(
        usuario_id=usuario.id,
        nome=nome_equipe,
        orcamento=orcamento_final,   # <-- ja debitado
        motor_fornecedor_id=motor.id,
        combustivel_fornecedor_id=comb.id,
        pneu_fornecedor_id=pneu.id,
        chassi_fornecedor_id=None,
        cambio_fornecedor_id=cambio.id,
        suspensao_fornecedor_id=susp.id,
        engenheiro_fornecedor_id=eng.id if eng else None,
        combustivel_carregado=110.0,
    )
    db.session.add(equipe)
    db.session.flush()
    db.session.add(Desenvolvimento(
        equipe_id=equipe.id, chassi_percentual_aplicado=100.0,
        aero_percentual_aplicado=100.0, nivel_engenheiro_projetista=1))
    return equipe


def criar_equipes_admins():
    """Equipe completa (mais baratos + debito) pra cada admin sem equipe."""
    criadas = 0
    admins = Usuario.query.filter(Usuario.email.in_(USUARIOS_ADMIN)).order_by(Usuario.id).all()
    for indice, usuario in enumerate(admins):
        if usuario.equipe:
            continue
        nome = NOMES_EQUIPE[indice] if indice < len(NOMES_EQUIPE) else f"Equipe {indice+1}"
        equipe = _montar_equipe_como_jogador(usuario, nome)
        if equipe is None:
            print("[AVISO] Faltam fornecedores. Rode a geracao antes.")
            return
        criadas += 1
    db.session.commit()
    print(f"[OK] Equipes dos admins: {criadas} criada(s) (piloto {NICK}, pecas mais baratas, orcamento debitado).")


def criar_bots(proxima_corrida):
    """Gera QTD_BOTS jogadores fake montados COMO JOGADOR (mais baratos + debito)
    e JA PRONTOS pra quali+corrida da proxima corrida (parc ferme/ajuste/quali/stints)."""
    if not proxima_corrida:
        print("[AVISO] Sem proxima corrida — bots nao gerados.")
        return
    if Usuario.query.filter(Usuario.email.like("bot%@fake.com")).count() > 0:
        print("[SKIP] Bots ja existem.")
        return

    pista_id = proxima_corrida.pista_real_id
    criados = 0

    for i in range(1, QTD_BOTS + 1):
        u = Usuario(email=f"bot{i}@fake.com", eh_admin=False, nick=f"Bot {i}")
        u.definir_senha("bot")
        db.session.add(u)
        db.session.flush()

        # MONTA A EQUIPE IGUAL A UM JOGADOR (mais baratos + debito do orcamento)
        car = _montar_equipe_como_jogador(u, f"Bot Team {i}")
        if car is None:
            print("[AVISO] Faltam fornecedores pra montar bots.")
            return
        db.session.flush()

        # Parc Ferme (travado) — modelos 50-900 random (isso e "setup", nao custo)
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
    print(f"[OK] {criados} bots montados COMO JOGADOR (pecas mais baratas + orcamento debitado) e prontos pra correr.")


def criar_temporada():
    existente = Temporada.query.filter_by(nome=NOME_TEMPORADA).first()
    if existente:
        print(f"[SKIP] Temporada '{NOME_TEMPORADA}' ja existe.")
        return existente
    Temporada.query.update({"ativa": False})
    temporada = Temporada(nome=NOME_TEMPORADA, ativa=True)
    db.session.add(temporada)
    db.session.flush()
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
        print("Todos (voce + bots) com pecas mais baratas = tempos parelhos na 1a temporada.")
        print("Va no /admin -> Dia de Corrida -> rodar classificacao e corrida.")


if __name__ == "__main__":
    main()
