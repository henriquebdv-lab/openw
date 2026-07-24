"""
Open Wheel Strategy — ponto de entrada do app.

Este arquivo agora é ENXUTO: só cria o app, liga as extensões, registra os
filtros de template, o context_processor, os comandos de CLI e as rotas
(que vivem em arquivos pequenos dentro de rotas/).

As rotas foram divididas em arquivos pequenos, mas os NOMES das rotas
continuam idênticos (login, minha_equipe, corrida_view, ...), então nenhum
template precisou ser alterado.
"""
import click
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, session

import config
from models import db, Usuario, garantir_colunas_fornecedores
from models_temporada import Temporada
from extensoes import migrate, init_oauth
from fornecedores_config import FORNECEDORES_CONFIG
from pistas_reais_db import criar_banco as criar_banco_pistas_reais
from rotas import registrar_rotas


# ---------------------------------------------------------
# Filtros de template
# ---------------------------------------------------------
def _registrar_filtros(app):
    @app.template_filter("tempo_min")
    def _filtro_tempo_min(segundos):
        if segundos is None or segundos == "":
            return "-"
        try:
            segundos = float(segundos)
        except (TypeError, ValueError):
            return "-"
        sinal = "-" if segundos < 0 else ""
        segundos = abs(segundos)
        minutos = int(segundos // 60)
        segs = segundos - (minutos * 60)
        return f"{sinal}{minutos}:{segs:06.3f}"

    @app.template_filter("tempo_dif")
    def _filtro_tempo_dif(segundos):
        if segundos is None:
            return "-"
        try:
            segundos = float(segundos)
        except (TypeError, ValueError):
            return "-"
        if segundos == 0:
            return "-"
        if abs(segundos) >= 60:
            minutos = int(abs(segundos) // 60)
            s = abs(segundos) - (minutos * 60)
            sinal = "-" if segundos < 0 else "+"
            return f"{sinal}{minutos}:{s:06.3f}"
        return f"+{segundos:.3f}s"

    @app.template_filter("dinheiro")
    def _filtro_dinheiro(valor):
        if valor is None:
            return "-"
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return "-"
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------
# Context processor (variáveis globais nos templates)
# ---------------------------------------------------------
def _registrar_contexto(app):
    @app.context_processor
    def injetar_globais():
        usuario_id = session.get("usuario_id")
        usuario = Usuario.query.get(usuario_id) if usuario_id else None
        return {
            "usuario_logado": usuario,
            "categorias_fornecedor": FORNECEDORES_CONFIG,
            "temporada_ativa": Temporada.ativa_atual(),
        }


# ---------------------------------------------------------
# Comandos de linha de comando (flask init-db, tornar-admin)
# ---------------------------------------------------------
def _registrar_cli(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Banco inicializado!")

    @app.cli.command("tornar-admin")
    @click.argument("email")
    def tornar_admin(email):
        usuario = Usuario.query.filter_by(email=email.strip().lower()).first()
        if not usuario:
            print(f"Nenhum usuário com {email}.")
            return
        usuario.eh_admin = True
        db.session.commit()
        print(f"{email} agora é admin!")


# ---------------------------------------------------------
# Fábrica do app
# ---------------------------------------------------------
def criar_app():
    app = Flask(__name__)
    app.config.from_object(config)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "dev-secret-key-troque-em-producao"

    db.init_app(app)
    migrate.init_app(app, db)
    init_oauth(app)

    with app.app_context():
        garantir_colunas_fornecedores()
        criar_banco_pistas_reais()

    _registrar_filtros(app)
    _registrar_contexto(app)
    _registrar_cli(app)
    registrar_rotas(app)
    return app


app = criar_app()


if __name__ == "__main__":
    app.run(debug=True)
