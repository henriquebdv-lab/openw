from app import app
from models import db

# Cria o contexto da aplicação para o banco de dados saber onde operar
with app.app_context():
    db.create_all()
    print("✅ Banco de dados recriado com sucesso!")