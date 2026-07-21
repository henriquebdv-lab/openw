from flask import Flask

from models import db


def test_ativa_atual_sem_tabela_retorna_none():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from models_temporada import Temporada

        assert Temporada.ativa_atual() is None
