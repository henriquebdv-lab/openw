"""
Rotas públicas de temporada e pistas:
- /temporada     (classificação/ranking da temporada ativa)
- /pistas-reais  (lista de pistas reais)
"""
from flask import render_template

from models_temporada import Temporada
from pontuacao import ranking_temporada
from pistas_reais_db import (
    criar_banco as criar_banco_pistas_reais,
    listar_pistas_reais,
)


def registrar(app):

    @app.route("/pistas-reais")
    def pistas_reais_view():
        criar_banco_pistas_reais()
        pistas = listar_pistas_reais()
        return render_template("pistas_reais.html", pistas=pistas)

    @app.route("/temporada")
    def temporada_view():
        temporada = Temporada.ativa_atual()
        if not temporada:
            return render_template("temporada.html", temporada=None, ranking=[], pistas_por_id={})
        ranking = ranking_temporada(temporada)
        pistas_por_id = {p["id"]: p for p in listar_pistas_reais()}
        return render_template("temporada.html", temporada=temporada, ranking=ranking, pistas_por_id=pistas_por_id)
