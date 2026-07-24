import sqlite3, shutil

shutil.copy("jogo.db", "jogo_backup_chassi.db")
print("[OK] Backup: jogo_backup_chassi.db")

con = sqlite3.connect("jogo.db")
cur = con.cursor()

# Recria a tabela permitindo chassi_fornecedor_id NULO.
# SQLite nao deixa alterar coluna direto, entao: renomeia, cria nova, copia, apaga.
cur.executescript("""
PRAGMA foreign_keys=off;

ALTER TABLE carros_jogadores RENAME TO _carros_old;

CREATE TABLE carros_jogadores (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    orcamento FLOAT,
    motor_fornecedor_id INTEGER NOT NULL,
    combustivel_fornecedor_id INTEGER NOT NULL,
    pneu_fornecedor_id INTEGER NOT NULL,
    chassi_fornecedor_id INTEGER,
    cambio_fornecedor_id INTEGER NOT NULL,
    suspensao_fornecedor_id INTEGER NOT NULL,
    engenheiro_fornecedor_id INTEGER,
    combustivel_carregado FLOAT,
    cor_primaria VARCHAR(7),
    cor_secundaria VARCHAR(7),
    modelo_motor INTEGER,
    modelo_combustivel INTEGER,
    modelo_pneu INTEGER,
    modelo_cambio INTEGER,
    modelo_suspensao INTEGER
);

INSERT INTO carros_jogadores SELECT * FROM _carros_old;
DROP TABLE _carros_old;

PRAGMA foreign_keys=on;
""")

con.commit()
con.close()
print("[OK] Trava NOT NULL do chassi removida. Pode criar equipe com chassi nulo.")