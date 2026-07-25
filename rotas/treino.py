"""
Rotas de treino:
- /treino-livre            (treino livre real, stint volta a volta)
- /treino-livre/ranking    (ranking de melhores voltas)
- /treino-oficial          (define pneu/combustível/pit pra corrida)
"""
from flask import render_template, request, redirect, url_for, session

from constantes import TANQUE_MAXIMO_LITROS
from models import Usuario, FornecedorPneu, FornecedorCombustivel, ResultadoTreinoLivre
from extensoes import login_requerido
from treino_livre_sim import simular_treino_livre_real
from pistas_reais_db import (
    criar_banco as criar_banco_pistas_reais,
    listar_pistas_reais, obter_pista_real,
)
import modelos_componente


def simular_treino_livre(ajustes):
    total = sum(ajustes.values())
    erro = abs(total - 250)
    tempo_volta = 90.0 + (erro / 10.0)
    if erro < 20:
        resumo = "Setup muito bom para esse treino."
        dicas = "Ajustes próximos do ideal; mantenha a consistência."
    elif erro < 60:
        resumo = "Setup razoável, ainda há margem para melhorar."
        dicas = "Aumente o câmbio e a suspensão em pequenas etapas."
    else:
        resumo = "Setup ainda longe do ideal."
        dicas = "Reduza o excesso de ajuste e busque equilíbrio entre freio e aerodinâmica."
    return {"tempo_volta": round(tempo_volta, 3), "resumo": resumo, "dicas": dicas}


def simular_treino_oficial(ajustes, pneu, combustivel, volta_primeiro_pit, outro_pit):
    total = sum(ajustes.values())
    equilibrio = max(0, 250 - abs(total - 250))
    tempo_volta = 82.0 + (abs(total - 250) / 20.0) - (pneu.performance / 120.0) - (combustivel.eficiencia / 30.0) + (equilibrio / 100.0)
    if volta_primeiro_pit <= 8:
        estrategia = "Estratégia agressiva: primeiro pit cedo."
    elif volta_primeiro_pit <= 18:
        estrategia = "Estratégia equilibrada: primeiro pit no meio da corrida."
    else:
        estrategia = "Estratégia conservadora: primeiro pit mais tarde."
    if outro_pit:
        estrategia += " Um segundo pit também foi previsto."
    else:
        estrategia += " A corrida deve terminar com um único pit stop."
    return {"tempo_volta": round(tempo_volta, 3), "estrategia": estrategia,
            "pneu": pneu.nome, "combustivel": combustivel.nome}


def registrar(app):

    @app.route("/treino-livre", methods=["GET", "POST"])
    @login_requerido
    def treino_livre_view():
        """TREINO LIVRE REAL (stint de teste, volta a volta)."""
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.equipe:
            return redirect(url_for("minha_equipe"))
        equipe = usuario.equipe
        criar_banco_pistas_reais()
        pistas = listar_pistas_reais()
        
        pneu_contratado = FornecedorPneu.query.get(equipe.pneu_fornecedor_id)
        combustivel_contratado = FornecedorCombustivel.query.get(equipe.combustivel_fornecedor_id)
        
        resultado = None
        mensagem = None
        novo_recorde = False
        escolhas = {
            "pista_id": (pistas[0]["id"] if pistas else None),
            "combustivel_litros": 30.0,
            "modelo_cambio": equipe.modelo_cambio or 500,
            "modelo_suspensao": equipe.modelo_suspensao or 500,
            "modelo_pneu": equipe.modelo_pneu or "",
        }
        if request.method == "POST":
            def _int(nome, padrao=None):
                valor = request.form.get(nome)
                try:
                    return int(valor)
                except (TypeError, ValueError):
                    return padrao
            escolhas["pista_id"] = _int("pista_id", escolhas["pista_id"])
            try:
                litros = float(request.form.get("combustivel_litros", 30.0))
            except (TypeError, ValueError):
                litros = 30.0
            litros = min(TANQUE_MAXIMO_LITROS, max(1.0, litros))
            escolhas["combustivel_litros"] = litros
            modelo_cambio = _int("modelo_cambio", None)
            modelo_suspensao = _int("modelo_suspensao", None)
            modelo_pneu_raw = request.form.get("modelo_pneu")
            modelo_pneu = (
                int(modelo_pneu_raw)
                if (modelo_pneu_raw and modelos_componente.modelo_valido(modelo_pneu_raw))
                else None
            )
            escolhas["modelo_cambio"] = modelo_cambio or ""
            escolhas["modelo_suspensao"] = modelo_suspensao or ""
            escolhas["modelo_pneu"] = modelo_pneu or ""
            
            pista = obter_pista_real(escolhas["pista_id"]) if escolhas["pista_id"] else None
            if not pneu_contratado or not combustivel_contratado:
                mensagem = "Você tem um contrato quebrado de pneu ou combustível."
            else:
                resultado = simular_treino_livre_real(
                    equipe, pneu_contratado, combustivel_contratado, litros,
                    pista=pista,
                    modelo_cambio=modelo_cambio,
                    modelo_suspensao=modelo_suspensao,
                    modelo_pneu=modelo_pneu,
                )
                from models import db
                _, novo_recorde = ResultadoTreinoLivre.registrar_se_melhor(equipe.id, resultado)
                session.setdefault("treino_livre_salvo", {
                    "ajuste_cambio": 50, "ajuste_suspensao": 50, "ajuste_freio": 50,
                    "ajuste_aerofolio_dianteiro": 50, "ajuste_aerofolio_traseiro": 50,
                })
                if novo_recorde:
                    mensagem = "Treino concluído — novo recorde salvo no ranking!"
                else:
                    mensagem = "Treino concluído. Não superou seu melhor tempo; o recorde anterior foi mantido."
        meu_resultado = ResultadoTreinoLivre.query.filter_by(equipe_id=equipe.id).first()
        return render_template(
            "treino_livre.html",
            equipe=equipe, pistas=pistas, 
            pneu_contratado=pneu_contratado, combustivel_contratado=combustivel_contratado,
            modelos_disponiveis=modelos_componente.MODELOS,
            escolhas=escolhas, resultado=resultado, mensagem=mensagem,
            novo_recorde=novo_recorde, meu_resultado=meu_resultado,
        )

    @app.route("/treino-livre/ranking")
    @login_requerido
    def treino_livre_ranking_view():
        usuario = Usuario.query.get(session["usuario_id"])
        resultados = (
            ResultadoTreinoLivre.query
            .filter(ResultadoTreinoLivre.melhor_volta_tempo.isnot(None))
            .order_by(ResultadoTreinoLivre.melhor_volta_tempo.asc())
            .all()
        )
        minha_equipe_id = usuario.equipe.id if usuario.equipe else None
        return render_template(
            "treino_livre_ranking.html",
            resultados=resultados, minha_equipe_id=minha_equipe_id,
        )

    @app.route("/treino-oficial", methods=["GET", "POST"])
    @login_requerido
    def treino_oficial_view():
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.equipe:
            return redirect(url_for("minha_equipe"))
        ajustes = session.get("treino_livre_salvo") or {"ajuste_cambio": 50, "ajuste_suspensao": 50, "ajuste_freio": 50,
                                                         "ajuste_aerofolio_dianteiro": 50, "ajuste_aerofolio_traseiro": 50}
        
        pneu_contratado = FornecedorPneu.query.get(usuario.equipe.pneu_fornecedor_id)
        combustivel_contratado = FornecedorCombustivel.query.get(usuario.equipe.combustivel_fornecedor_id)
        
        resultado = None
        mensagem = None
        if not session.get("treino_livre_salvo"):
            mensagem = "Complete primeiro o treino livre."
            
        if request.method == "POST":
            if not session.get("treino_livre_salvo"):
                return render_template("treino_oficial.html", ajustes=ajustes, pneu_contratado=pneu_contratado, combustivel_contratado=combustivel_contratado, resultado=None, mensagem=mensagem, equipe=usuario.equipe)
            
            volta_primeiro_pit = int(request.form.get("volta_primeiro_pit", 10))
            outro_pit = request.form.get("outro_pit") == "on"
            resultado = simular_treino_oficial(ajustes, pneu_contratado, combustivel_contratado, volta_primeiro_pit, outro_pit)
            
            from models import db
            usuario.equipe.estrategia_volta_pit = volta_primeiro_pit
            usuario.equipe.estrategia_dois_pits = outro_pit
            db.session.commit()

            session["treino_oficial_salvo"] = {
                "volta_primeiro_pit": volta_primeiro_pit, "outro_pit": outro_pit,
            }
            mensagem = "Treino oficial concluído e salvo."
            
        return render_template("treino_oficial.html", ajustes=ajustes, pneu_contratado=pneu_contratado, combustivel_contratado=combustivel_contratado, resultado=resultado, mensagem=mensagem, equipe=usuario.equipe)