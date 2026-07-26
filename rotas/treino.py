"""
Rotas de treino:
- /treino-livre            (treino interativo, 1 clique = 1 volta com sliders)
- /treino-livre/ranking    (ranking de melhores voltas)
- /treino-oficial          (define pneu/combustível/pit pra corrida)
"""
import random
from flask import render_template, request, redirect, url_for, session, flash

from constantes import TANQUE_MAXIMO_LITROS, VARIACAO_ALEATORIA_DESVIO_PADRAO
from models import db, Usuario, FornecedorPneu, FornecedorCombustivel, ResultadoTreinoLivre, SetupFimDeSemana, IdealPistaSlider, AjusteSalvo
from models_temporada import Temporada
from extensoes import login_requerido
from pistas_reais_db import (
    criar_banco as criar_banco_pistas_reais,
    listar_pistas_reais, obter_pista_real,
)
import modelos_componente
from rotas.corrida import _aplicar_dados_pista_no_carro
from equipamentos import Pneu, Combustivel


def gerar_frase_feedback(componente, erro):
    """Gera o feedback do piloto baseado na magnitude e direção do erro (-98 a +98)."""
    mag = abs(erro)
    if mag <= 2: return "O carro tá no trilho, perfeito! Não mexe em nada."

    if componente == "cambio":
        if erro < 0:
            if mag <= 10: return "Quase lá, bate no limite de giro um milésimo antes."
            if mag <= 25: return "Relação um tiquinho curta, sinto o motor esgoelar leve no fim da reta."
            if mag <= 50: return "Câmbio curto demais, tô perdendo muita velocidade final."
            if mag <= 75: return "Marchas absurdamente curtas. Chego no limite muito antes da placa de freio."
            return "Parece marcha de trator! Bate o limite na metade da reta, arruma isso."
        else:
            if mag <= 10: return "Quase perfeito, demora um cabelo pra encher a última marcha."
            if mag <= 25: return "Tá meio longo, nas saídas de baixa o carro fica meio xoxo."
            if mag <= 50: return "Câmbio longo demais, o giro despenca muito nas trocas."
            if mag <= 75: return "Muito longo. Chego no fim da reta e a última marcha ainda não encheu."
            return "Câmbio infinito! O carro nem tem força pra puxar essas marchas, tá péssimo."
            
    elif componente == "suspensao":
        if erro < 0:
            if mag <= 10: return "Muito perto. Deita um pelinho a mais nas de alta."
            if mag <= 25: return "Um pouco mole. O carro rola de lado e demora a apoiar."
            if mag <= 50: return "Suspensão mole demais, tá parecendo uma banheira na zebra."
            if mag <= 75: return "Mole demais! O chassi tá ralando no chão nas curvas fortes."
            return "Isso é uma mola ou um pudim? Impossível pilotar assim, amoleceu demais."
        else:
            if mag <= 10: return "Quase lá. O carro tá pouca coisa nervoso na entrada."
            if mag <= 25: return "Meio dura. O volante dá uns trancos secos na zebra."
            if mag <= 50: return "Dura demais. Pula muito e não traciona nas ondulações."
            if mag <= 75: return "Parece um kart duro! Escorrega seco nas saídas de curva."
            return "Tiraram a suspensão? Soldaram o eixo? Tá impossível de duro."
            
    elif "aero" in componente:
        if erro < 0:
            if mag <= 10: return "Falta pouquíssima asa, escorrega um fiozinho na alta."
            if mag <= 25: return "Falta pressão aerodinâmica. O carro tá arisco na entrada de curva."
            if mag <= 50: return "Pouquíssima asa. Não tenho aderência pra atacar as curvas médias."
            if mag <= 75: return "Zero downforce! Tenho que frear no meio da reta pra conseguir contornar."
            return "Vou decolar! O carro não gruda no chão de jeito nenhum."
        else:
            if mag <= 10: return "Tá com um tiquinho de arrasto a mais do que precisa."
            if mag <= 25: return "Muita asa. O carro entra bem, mas sinto que prende na reta."
            if mag <= 50: return "Asa em excesso. O carro prega no chão mas não anda de reta."
            if mag <= 75: return "Arrasto aerodinâmico bizarro. Perco um tempão empurrando vento."
            return "Colocaram um paraquedas no carro? Não sai do lugar nas retas!"
            
    return "Algo estranho com o acerto, não tô sentindo bem o carro."


def get_ideal_slider(pista_id, slider_name):
    """Busca ou gera de forma determinística o valor ideal 1-99 para o slider na pista."""
    ideal = IdealPistaSlider.query.filter_by(pista_real_id=pista_id, slider=slider_name).first()
    if not ideal:
        # Usa seed específica para garantir que a pista tenha sempre a mesma base
        # Como o Aerofólio é um slider único na tela, AeroD e AeroT terão o mesmo ideal por enquanto
        seed_key = f"aero_{pista_id}" if "aero" in slider_name else f"{slider_name}_{pista_id}"
        random.seed(seed_key)
        val = random.randint(1, 99)
        random.seed()  # Reseta o gerador
        
        ideal = IdealPistaSlider(pista_real_id=pista_id, slider=slider_name, valor_base=val)
        db.session.add(ideal)
        db.session.commit()
    
    # Fase 2: Aplicar AJUSTE_INFLUENCIA e AJUSTE_CONTRATO aqui (atualmente com peso 0)
    ajuste_influencia = 0 
    ajuste_contrato = 0
    final = ideal.valor_base + ajuste_influencia + ajuste_contrato
    return max(1, min(99, final))


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
        """TREINO LIVRE: Setup de Parque Fechado (Parte A) + Ajuste Fino e Feedback (Parte B)"""
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.equipe:
            return redirect(url_for("minha_equipe"))
        
        equipe = usuario.equipe
        temporada = Temporada.ativa_atual()
        proxima_corrida = temporada.proxima_corrida() if temporada else None

        if not proxima_corrida:
            flash("Nenhuma temporada ou corrida ativa. O treino não está disponível.", "warning")
            return redirect(url_for("home"))

        criar_banco_pistas_reais()
        pista = obter_pista_real(proxima_corrida.pista_real_id)

        # PARTE A: Validação do Parc Fermé
        setup_fds = SetupFimDeSemana.query.filter_by(equipe_id=equipe.id, corrida_id=proxima_corrida.id).first()
        if not setup_fds:
            flash("Você precisa montar o seu carro para o fim de semana antes de ir para a pista.", "warning")
            return redirect(url_for("montagem_fim_de_semana"))

        # Recuperar estado da sessão (PARTE B)
        session_key = f"stint_treino_{equipe.id}"
        stint = session.get(session_key)

        pneu_contratado = FornecedorPneu.query.get(equipe.pneu_fornecedor_id)
        combustivel_contratado = FornecedorCombustivel.query.get(equipe.combustivel_fornecedor_id)

        if request.method == "POST":
            acao = request.form.get("acao")

            if acao == "iniciar":
                combustivel_litros = float(request.form.get("combustivel_litros", 30))
                modelo_pneu = int(request.form.get("modelo_pneu", 50))
                
                session[session_key] = {
                    "ativo": True,
                    "combustivel_litros": combustivel_litros,
                    "combustivel_restante": combustivel_litros,
                    "modelo_pneu": modelo_pneu,
                    "desgaste": 0.0,
                    "voltas": [],
                    "encerrou_por": None
                }
                # Prepara sliders iniciais
                session[f"treino_sliders_{equipe.id}"] = {
                    "cambio": 50, "suspensao": 50, "aerofolio": 50
                }
                return redirect(url_for("treino_livre_view"))

            elif acao == "fazer_volta":
                if not stint or not stint.get("ativo"):
                    return redirect(url_for("treino_livre_view"))

                s_cambio = int(request.form.get("slider_cambio", 50))
                s_susp = int(request.form.get("slider_suspensao", 50))
                s_aero = int(request.form.get("slider_aerofolio", 50))

                session[f"treino_sliders_{equipe.id}"] = {
                    "cambio": s_cambio, "suspensao": s_susp, "aerofolio": s_aero
                }

                # Resgata Ideais da Pista
                ideais = {
                    "cambio": get_ideal_slider(pista["id"], "cambio"),
                    "suspensao": get_ideal_slider(pista["id"], "suspensao"),
                    "aero_dianteiro": get_ideal_slider(pista["id"], "aero_dianteiro"),
                    "aero_traseiro": get_ideal_slider(pista["id"], "aero_traseiro"),
                    "freio": 50 # DLC Futuro
                }

                # Calcula Erros (-98 a +98)
                erros = {
                    "cambio": s_cambio - ideais["cambio"],
                    "suspensao": s_susp - ideais["suspensao"],
                    "aero_dianteiro": s_aero - ideais["aero_dianteiro"],
                    "aero_traseiro": s_aero - ideais["aero_traseiro"],
                    "freio": 50 - ideais["freio"]
                }
                
                erro_absoluto_total = sum(abs(e) for e in erros.values())
                # 490 = 98 max error * 5 components. Calcula porcentagem de acerto.
                acerto_geral = max(0.0, 100.0 - (erro_absoluto_total / 490.0) * 100.0)

                # Prioriza a frase do pior slider
                pior_comp = max(erros, key=lambda k: abs(erros[k]))
                pior_erro = erros[pior_comp]
                feedback = gerar_frase_feedback(pior_comp, pior_erro)

                # Monta carro 100% da equipe e aplica peças do Parc Fermé
                carro = equipe.montar_carro()
                carro.pneu = Pneu(pneu_contratado.nome, pneu_contratado.custo_temporada, pneu_contratado.performance, pneu_contratado.desgaste)
                carro.combustivel = Combustivel(combustivel_contratado.nome, combustivel_contratado.custo_temporada, combustivel_contratado.eficiencia, combustivel_contratado.aumento_potencia_motor)
                carro.definir_modelos(
                    motor=setup_fds.modelo_motor, 
                    cambio=setup_fds.modelo_cambio, 
                    suspensao=setup_fds.modelo_suspensao, 
                    pneu=stint["modelo_pneu"]
                )
                _aplicar_dados_pista_no_carro(carro, pista)

                consumo = carro.consumo_por_volta()
                if consumo <= 0: consumo = 0.1

                # Executa Lógica de Fim de Volta
                if stint["combustivel_restante"] < consumo:
                    stint["ativo"] = False
                    stint["encerrou_por"] = "Pane Seca (Acabou o Combustível)"
                else:
                    # Penalidade no tempo baseada no erro total do setup
                    tempo_volta = carro.tempo_base() + random.gauss(0, VARIACAO_ALEATORIA_DESVIO_PADRAO) + (erro_absoluto_total * 0.02)
                    
                    stint["combustivel_restante"] -= consumo
                    stint["desgaste"] += carro.desgaste_por_volta()

                    if stint["desgaste"] >= 100.0:
                        stint["ativo"] = False
                        stint["encerrou_por"] = "Pneu Estourou"
                        feedback = "Estourou o pneu! Bati o carro e o treino acabou."

                    stint["voltas"].insert(0, {
                        "numero": len(stint["voltas"]) + 1,
                        "tempo": round(tempo_volta, 3),
                        "desgaste_pneu": round(stint["desgaste"], 1),
                        "combustivel_restante": round(stint["combustivel_restante"], 2),
                        "feedback": feedback,
                        "acerto": round(acerto_geral, 1)
                    })

                    # Registrar Recorde Geral se aplicável
                    melhor_stint = min(stint["voltas"], key=lambda v: v["tempo"])
                    if melhor_stint["tempo"] == round(tempo_volta, 3):
                        res_db = ResultadoTreinoLivre.query.filter_by(equipe_id=equipe.id).first()
                        if not res_db or not res_db.melhor_volta_tempo or tempo_volta < res_db.melhor_volta_tempo:
                            ResultadoTreinoLivre.registrar_se_melhor(equipe.id, {
                                "pneu_nome": pneu_contratado.nome,
                                "combustivel_nome": combustivel_contratado.nome,
                                "total_voltas": len(stint["voltas"]),
                                "melhor_volta_numero": len(stint["voltas"]),
                                "melhor_volta_tempo": tempo_volta,
                                "tempo_medio": tempo_volta, # Simplificado para o DB
                                "erro_setup": round(acerto_geral, 1)
                            })

                session[session_key] = stint
                return redirect(url_for("treino_livre_view"))

            elif acao == "salvar_ajuste":
                s_cambio = int(request.form.get("slider_cambio", 50))
                s_susp = int(request.form.get("slider_suspensao", 50))
                s_aero = int(request.form.get("slider_aerofolio", 50))

                ajuste = AjusteSalvo.query.filter_by(equipe_id=equipe.id, pista_real_id=pista["id"]).first()
                if not ajuste:
                    ajuste = AjusteSalvo(equipe_id=equipe.id, pista_real_id=pista["id"])
                    db.session.add(ajuste)

                ajuste.ajuste_cambio = s_cambio
                ajuste.ajuste_suspensao = s_susp
                ajuste.ajuste_aero_dianteiro = s_aero
                ajuste.ajuste_aero_traseiro = s_aero
                db.session.commit()

                # Save for Treino Oficial compatibility (Fase Posterior)
                session["treino_livre_salvo"] = {
                    "ajuste_cambio": s_cambio, "ajuste_suspensao": s_susp, "ajuste_freio": 50,
                    "ajuste_aerofolio_dianteiro": s_aero, "ajuste_aerofolio_traseiro": s_aero,
                }

                session.pop(session_key, None)
                flash("Ajuste refinado salvo com sucesso! O carro está pronto para o Treino Oficial.", "success")
                return redirect(url_for("treino_oficial_view"))

            elif acao == "descartar":
                session.pop(session_key, None)
                return redirect(url_for("treino_livre_view"))

        sliders_atuais = session.get(f"treino_sliders_{equipe.id}", {"cambio": 50, "suspensao": 50, "aerofolio": 50})
        meu_resultado = ResultadoTreinoLivre.query.filter_by(equipe_id=equipe.id).first()

        return render_template(
            "treino_livre.html",
            equipe=equipe, 
            pista=pista, 
            setup_fds=setup_fds,
            stint=stint, 
            sliders_atuais=sliders_atuais,
            modelos_disponiveis=modelos_componente.MODELOS,
            meu_resultado=meu_resultado,
            pneu_contratado=pneu_contratado,
            combustivel_contratado=combustivel_contratado
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