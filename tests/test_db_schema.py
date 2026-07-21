import os
import tempfile
import unittest

import sqlalchemy
from flask import Flask

from models import db, garantir_colunas_fornecedores


class DbSchemaTests(unittest.TestCase):
    def test_garantir_colunas_fornecedores_adiciona_colunas_ausentes(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            caminho_temp = tmp.name

        try:
            app = Flask(__name__)
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{caminho_temp}"
            app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
            db.init_app(app)

            with app.app_context():
                db.drop_all()
                db.create_all()
                garantir_colunas_fornecedores()

                inspector = sqlalchemy.inspect(db.engine)
                colunas_pneu = {coluna["name"] for coluna in inspector.get_columns("fornecedores_pneu")}
                colunas_cambio = {coluna["name"] for coluna in inspector.get_columns("fornecedores_cambio")}
                colunas_suspensao = {coluna["name"] for coluna in inspector.get_columns("fornecedores_suspensao")}

            with app.app_context():
                db.session.remove()
                db.engine.dispose()

            self.assertIn("categoria_chuva", colunas_pneu)
            self.assertIn("categoria_pista", colunas_cambio)
            self.assertIn("categoria_pista", colunas_suspensao)
        finally:
            if os.path.exists(caminho_temp):
                os.remove(caminho_temp)


if __name__ == "__main__":
    unittest.main()
