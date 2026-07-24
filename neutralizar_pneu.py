import sqlite3

con = sqlite3.connect("jogo.db")
cur = con.cursor()
n = cur.execute("UPDATE fornecedores_pneu SET categoria_chuva = 'seco'").rowcount
con.commit()
con.close()
print(f"[OK] {n} pneus neutralizados para 'seco'.")