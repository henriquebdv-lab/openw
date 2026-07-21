from app import app, db
from sqlalchemy import text
app.app_context().push()
conn = db.engine.connect()
print(conn.execute(text('SELECT name FROM sqlite_master WHERE type="table" AND name="fornecedores_pneu"')).fetchall())
print(conn.execute(text('PRAGMA table_info(fornecedores_pneu)')).fetchall())
print(conn.execute(text('PRAGMA table_info(fornecedores_cambio)')).fetchall())
print(conn.execute(text('PRAGMA table_info(fornecedores_suspensao)')).fetchall())
