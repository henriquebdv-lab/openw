import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------
# BANCO DE DADOS - SQLite (arquivo único, zero configuração)
# ---------------------------------------------------------
# Não precisa instalar servidor nenhum. O arquivo "jogo.db" é criado
# automaticamente na primeira vez que você rodar "flask init-db".
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'jogo.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "troque-essa-chave-depois"

# ---------------------------------------------------------
# LOGIN COM GOOGLE
# ---------------------------------------------------------
# Pegue essas credenciais em https://console.cloud.google.com/apis/credentials
# (veja o passo a passo que te expliquei no chat)
# Exemplo de boa prática:

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

# ---------------------------------------------------------
# ANTIGO: SQL Server (deixado aqui comentado, caso queira voltar depois)
# ---------------------------------------------------------
# import urllib.parse
# DB_SERVER = "localhost"
# DB_NAME = "OpenWheelStrategy"
# DB_USER = "sa"
# DB_PASSWORD = "sua_senha_aqui"
# DB_DRIVER = "ODBC Driver 17 for SQL Server"
# params = urllib.parse.quote_plus(
#     f"DRIVER={{{DB_DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_NAME};"
#     f"UID={DB_USER};PWD={DB_PASSWORD};"
# )
# SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
