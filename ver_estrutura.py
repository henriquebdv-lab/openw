import sqlite3
import shutil
import os
import sys

DB = "jogo.db"
EMAIL = "henriquebdv@gmail.com"

# --- 1) Backup de seguranca -------------------------------------------------
backup = "jogo_backup_antes_reset.db"
shutil.copy(DB, backup)
print(f"[OK] Backup criado: {backup} ({os.path.getsize(backup)} bytes)")

con = sqlite3.connect(DB)
cur = con.cursor()

# --- 2) Acha seu usuario ----------------------------------------------------
row = cur.execute("SELECT id FROM usuarios WHERE email = ?", (EMAIL,)).fetchone()
if not row:
    print(f"[ERRO] Usuario {EMAIL} nao encontrado.")
    con.close()
    sys.exit(1)
usuario_id = row[0]
print(f"[OK] Usuario id = {usuario_id}")

# --- 3) Acha as equipes desse usuario --------------------------------------
equipes = [r[0] for r in cur.execute(
    "SELECT id FROM carros_jogadores WHERE usuario_id = ?", (usuario_id,))]
print(f"[OK] Equipes do usuario: {equipes}")

if not equipes:
    print("[i] Nenhuma equipe pra apagar. Nada a fazer.")
    con.close()
    sys.exit(0)

placeholders = ",".join("?" * len(equipes))

# --- 4) Apaga dependentes que tem coluna equipe_id --------------------------
tabelas_dependentes = [
    "desenvolvimentos",
    "resultados_treino_livre",
    "treinamentos_box",
    "resultados_classificacao",
    "resultados_corrida",
]
for tabela in tabelas_dependentes:
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({tabela})")]
    if "equipe_id" in cols:
        n = cur.execute(
            f"DELETE FROM {tabela} WHERE equipe_id IN ({placeholders})",
            equipes,
        ).rowcount
        print(f"[OK] {tabela}: {n} linha(s) apagada(s)")
    else:
        print(f"[i] {tabela}: sem coluna equipe_id, ignorado")

# --- 5) Apaga a(s) equipe(s) ------------------------------------------------
n = cur.execute(
    f"DELETE FROM carros_jogadores WHERE id IN ({placeholders})", equipes
).rowcount
print(f"[OK] carros_jogadores: {n} equipe(s) apagada(s)")

con.commit()
con.close()
print("\n[PRONTO] Sua equipe foi resetada. Seu login continua ativo.")
print("Entre no jogo e monte uma equipe nova pela tela normal.")