"""
Rotas de desenvolvimento e treinamento:
- /minha-equipe/desenvolvimento  (chassi + aero em construção pra próxima temporada)
- /minha-equipe/treinamento      (treinamento de boxes)
"""
from datetime import datetime

from flask import render_template, request, redirect, url_for, session

from models import Usuario, Configuracao, Desenvolvimento, TreinamentoBox
from extensoes import login_requerido
from progressao import (
    calcular_custo_proximo_avanco, calcular_tempo_proximo_avanco_horas,
    verificar_conclusao, avancar,
)


def registrar(app):

    @app.route("/minha-equipe/desenvolvimento", methods=["GET", "POST"])
    @login_requerido
    def desenvolvimento_view():
        """Nova versão: desenvolve chassi + aero separadamente (em construção
        pra próxima temporada)."""
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.equipe:
            return redirect(url_for("minha_equipe"))
        equipe = usuario.equipe
        registro = Desenvolvimento.obter_ou_criar(equipe.id)
        config = Configuracao.obter()
        # Verifica se algum trabalho em progresso concluiu
        if registro.em_progresso and registro.horario_conclusao and datetime.utcnow() >= registro.horario_conclusao:
            alvo = getattr(registro, "alvo_em_progresso", None) or "chassi_percentual_em_construcao"
            atual = float(getattr(registro, alvo, 0) or 0)
            novo = min(100.0, atual + config.dev_incremento_percentual)
            setattr(registro, alvo, novo)
            registro.em_progresso = False
            registro.inicio_em = None
            registro.horario_conclusao = None
            from models import db
            db.session.commit()
        mensagem = None
        if request.method == "POST":
            peca = request.form.get("peca", "chassi")  # chassi ou aero
            if peca not in ("chassi", "aero"):
                peca = "chassi"
            alvo_atributo = f"{peca}_percentual_em_construcao"
            _, mensagem = avancar(
                registro, equipe,
                config.dev_custo_base, config.dev_custo_fator,
                config.dev_tempo_base_horas, config.dev_tempo_fator_horas,
                config.dev_incremento_percentual,
                alvo_atributo=alvo_atributo,
            )
            session[f"desenvolvimento_alvo_{equipe.id}"] = alvo_atributo
        proximo_custo_chassi = calcular_custo_proximo_avanco(
            registro.chassi_percentual_em_construcao or 0, config.dev_custo_base, config.dev_custo_fator
        )
        proximo_custo_aero = calcular_custo_proximo_avanco(
            registro.aero_percentual_em_construcao or 0, config.dev_custo_base, config.dev_custo_fator
        )
        proximo_tempo_chassi = calcular_tempo_proximo_avanco_horas(
            registro.chassi_percentual_em_construcao or 0, config.dev_tempo_base_horas, config.dev_tempo_fator_horas
        )
        proximo_tempo_aero = calcular_tempo_proximo_avanco_horas(
            registro.aero_percentual_em_construcao or 0, config.dev_tempo_base_horas, config.dev_tempo_fator_horas
        )
        return render_template("desenvolvimento.html",
            equipe=equipe, registro=registro,
            proximo_custo_chassi=proximo_custo_chassi,
            proximo_custo_aero=proximo_custo_aero,
            proximo_tempo_chassi=proximo_tempo_chassi,
            proximo_tempo_aero=proximo_tempo_aero,
            mensagem=mensagem)

    @app.route("/minha-equipe/treinamento", methods=["GET", "POST"])
    @login_requerido
    def treinamento_view():
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.equipe:
            return redirect(url_for("minha_equipe"))
        equipe = usuario.equipe
        registro = TreinamentoBox.obter_ou_criar(equipe.id)
        config = Configuracao.obter()
        verificar_conclusao(registro, config.treino_incremento_percentual)
        mensagem = None
        if request.method == "POST":
            _, mensagem = avancar(registro, equipe, config.treino_custo_base, config.treino_custo_fator,
                                  config.treino_tempo_base_horas, config.treino_tempo_fator_horas, config.treino_incremento_percentual)
        proximo_custo = calcular_custo_proximo_avanco(registro.percentual, config.treino_custo_base, config.treino_custo_fator)
        proximo_tempo = calcular_tempo_proximo_avanco_horas(registro.percentual, config.treino_tempo_base_horas, config.treino_tempo_fator_horas)
        tempo_pit_atual = config.pit_tempo_sem_treino - ((config.pit_tempo_sem_treino - config.pit_tempo_treino_completo) * (registro.percentual / 100))
        return render_template("treinamento.html", equipe=equipe, registro=registro,
                               proximo_custo=proximo_custo, proximo_tempo=proximo_tempo, mensagem=mensagem,
                               tempo_pit_atual=round(tempo_pit_atual, 1))
