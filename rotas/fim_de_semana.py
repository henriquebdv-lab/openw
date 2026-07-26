"""
Rota de Montagem do Fim de Semana (Etapa 1 do Parc FermÃ©).
"""
from flask import render_template, request, redirect, url_for, session, flash
from models import db, Usuario, SetupFimDeSemana
from models_temporada import Temporada
from extensoes import login_requerido
from pistas_reais_db import obter_pista_real, criar_banco as criar_banco_pistas_reais
import modelos_componente

def registrar(app):
    @app.route("/montar-fim-de-semana", methods=["GET", "POST"])
    @login_requerido
    def montagem_fim_de_semana():
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.equipe:
            return redirect(url_for("minha_equipe"))
        
        equipe = usuario.equipe
        temporada = Temporada.ativa_atual()
        proxima_corrida = temporada.proxima_corrida() if temporada else None
        
        if not proxima_corrida:
            return render_template("montagem_fim_de_semana.html", equipe=equipe, pista=None)

        criar_banco_pistas_reais()
        pista = obter_pista_real(proxima_corrida.pista_real_id)

        setup_existente = SetupFimDeSemana.query.filter_by(
            equipe_id=equipe.id, corrida_id=proxima_corrida.id
        ).first()

        if request.method == "POST":
            mod_cambio = request.form.get("modelo_cambio")
            mod_susp = request.form.get("modelo_suspensao")
            
            if modelos_componente.modelo_valido(mod_cambio) and modelos_componente.modelo_valido(mod_susp):
                if setup_existente:
                    setup_existente.modelo_cambio = int(mod_cambio)
                    setup_existente.modelo_suspensao = int(mod_susp)
                else:
                    novo_setup = SetupFimDeSemana(
                        equipe_id=equipe.id,
                        corrida_id=proxima_corrida.id,
                        modelo_cambio=int(mod_cambio),
                        modelo_suspensao=int(mod_susp)
                    )
                    db.session.add(novo_setup)
                
                db.session.commit()
                flash("Montagem do fim de semana salva com sucesso!", "success")
                return redirect(url_for("montagem_fim_de_semana"))
            else:
                flash("Modelos invÃ¡lidos selecionados.", "danger")

        return render_template(
            "montagem_fim_de_semana.html",
            equipe=equipe,
            pista=pista,
            modelos_disponiveis=modelos_componente.MODELOS,
            setup_existente=setup_existente
        )