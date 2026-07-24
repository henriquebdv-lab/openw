import sqlite3

con = sqlite3.connect("jogo.db")
cur = con.cursor()

print("=== TABELAS ===")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(row[0])

con.close()