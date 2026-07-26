"""
Seed de TESTE do Open Wheel Strategy.

Monta um ambiente de teste completo de uma vez só, pra você não precisar
recriar cadastro/admin/temporada na mão toda vez que zerar o banco.

USO (depois de recriar o banco):
    python criar_banco.py
    python seed_teste.py

O que ele cria:
    - 2 usuários JÁ admin (senha padrao de teste), com nick "Razor"
    - Os fornecedores (popular_banco: 100 de cada categoria)
    - A "TEMPORADA 1" ativa, com as 10 primeiras corridas do calendario

E idempotente: se rodar de novo, nao duplica (verifica antes de criar).
"""
from app import app
from models import db, Usuario, FornecedorMotor
from models_temporada import Temporada, CorridaAgendada
from seed_fornecedores import popular_banco
from pistas_reais_db import criar_banco as criar_banco_pistas_reais, listar_pistas_reais


# ---- CONFIG DO SEED (mude aqui se quiser) ----
USUARIOS_ADMIN = [
    "henriquebdv@gmail.com",
    "henriquebettegaclaro@gmail.com",
]
SENHA_PADRAO = "123456"          # so pra teste!
NICK = "Razor"
NOME_TEMPORADA = "TEMPORADA 1"
QTD_CORRIDAS = 10


def criar_admins():
    criados = 0
    for email in USUARIOS_ADMIN:
        u = Usuario.query.filter_by(email=email).first()
        if u:
            # garante que continua admin/nick mesmo se ja existir
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
    print(f"[OK] Admins: {criados} criado(s), {len(USUARIOS_ADMIN) - criados} ja existia(m). Senha padrao: {SENHA_PADRAO}")


def criar_fornecedores():
    # so popula se ainda nao houver fornecedores (evita duplicar)
    if FornecedorMotor.query.count() > 0:
        print("[SKIP] Fornecedores ja existem (nao populei de novo).")
        return
    popular_banco()
    print("[OK] Fornecedores gerados (100 por categoria).")


def criar_temporada():
    existente = Temporada.query.filter_by(nome=NOME_TEMPORADA).first()
    if existente:
        print(f"[SKIP] Temporada '{NOME_TEMPORADA}' ja existe.")
        return

    # desativa outras temporadas e cria a nova como ativa
    Temporada.query.update({"ativa": False})
    temporada = Temporada(nome=NOME_TEMPORADA, ativa=True)
    db.session.add(temporada)
    db.session.flush()  # pega o id

    criar_banco_pistas_reais()
    pistas = listar_pistas_reais()[:QTD_CORRIDAS]
    for i, pista in enumerate(pistas, start=1):
        db.session.add(CorridaAgendada(
            temporada_id=temporada.id,
            pista_real_id=pista["id"],
            pista_nome=pista["nome"],
            ordem=i,
            executada=False,
        ))
    db.session.commit()
    print(f"[OK] '{NOME_TEMPORADA}' criada e ativa, com {len(pistas)} corridas.")


def main():
    with app.app_context():
        criar_admins()
        criar_fornecedores()
        criar_temporada()
        print("\n=== SEED DE TESTE CONCLUIDO ===")
        print(f"Logue com: {USUARIOS_ADMIN[0]} / senha: {SENHA_PADRAO}")


if __name__ == "__main__":
    main()
