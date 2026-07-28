"""
Rotas de corrida:
- /estrategia-corrida   (define estratégia + salva modelos 50-900 e N stints)
- /classificacao        (visualização do grid)
- /corrida              (visualização do resultado)
"""
import os
import json
from datetime import datetime

from flask import render_template, request, redirect, url_for, session, flash

from config import BASE_DIR
from models import db, Usuario, CarroJogador, Configuracao, TreinamentoBox, ResultadoClassificacao, ResultadoCorrida, FornecedorPneu, FornecedorCombustivel, EstrategiaStint, SetupFimDeSemana
from models_temporada import Temporada
from extensoes import login_requerido
from pontuacao import pontos_por_posicao, premio_por_posicao
from corrida import Corrida, calcular_tempo_pit_stop
from pistas_reais_db import (
    criar_banco as criar_banco_pistas_reais,
    listar_pistas_reais, obter_pista_real, calcular_numero_voltas,
)
import modelos_componente


def _aplicar_dados_pista_no_carro(carro, pista):
    cat_cambio = (pista.get("categoria_cambio_ideal") or "A").upper()
    cat_suspensao = (pista.get("categoria_suspensao_ideal") or "A").upper()
    carro.categoria_cambio_ideal_pista = cat_cambio[0] if cat_cambio else "A"
    carro.categoria_suspensao_ideal_pista = cat_suspensao[0] if cat_suspensao else "A"
    carro.categoria_chuva = "seco"
    carro.temperatura_pista = pista.get("temperatura_trecho_1") or pista.get("temperatura_ambiente") or 20.0
    carro.tamanho_volta_km = pista.get("extensao_km") or 0.0
    carro.influencia_pista_motor = pista.get("influencia_motor") or 10
    carro.influencia_pista_cambio = pista.get("influencia_cambio") or 10
    carro.influencia_pista_suspensao = pista.get("influencia_suspensao") or 10
    carro.influencia_pista_pneu = pista.get("influencia_pneu") or 10
    carro.influencia_pista_combustivel = pista.get("influencia_combustivel") or 10
    carro.influencia_pista_engenheiro = pista.get("influencia_engenheiro") or 10


def _executar_corrida_e_persistir(pista, corrida_agendada=None, equipes_elegiveis=None):
    numero_voltas, distancia_total = calcular_numero_voltas(pista["extensao_km"])
    config = Configuracao.obter()
    
    todas_equipes = equipes_elegiveis if equipes_elegiveis is not None else CarroJogador.query.all()
    
    # TRAVA DE SEGURANÇA: Se não há equipes elegíveis, aborta imediatamente para não corromper o JSON.
    if not todas_equipes:
        return None
    
    carros = []
    for equipe_db in todas_equipes:
        carro = equipe_db.montar_carro()
        if corrida_agendada:
            setup = SetupFimDeSemana.query.filter_by(equipe_id=equipe_db.id, corrida_id=corrida_agendada.id).first()
            if setup:
                carro.definir_modelos(
                    motor=setup.modelo_motor,
                    cambio=setup.modelo_cambio,
                    suspensao=setup.modelo_suspensao
                )
        carros.append(carro)
        
    percentuais_treino_box = []
    
    for carro, equipe_db in zip(carros, todas_equipes):
        treinamento = TreinamentoBox.obter_ou_criar(equipe_db.id)
        carro.tempo_pit_stop = calcular_tempo_pit_stop(pista["tempo_pit_stop_segundos"], config, treinamento.percentual)
        _aplicar_dados_pista_no_carro(carro, pista)
        
        carro.stints = [
            {'ordem': s.ordem, 'modelo_pneu': s.modelo_pneu, 'voltas': s.voltas, 'combustivel_litros': s.combustivel_litros}
            for s in equipe_db.stints
        ]
        
        percentuais_treino_box.append(float(treinamento.percentual or 0.0))
        
    temp_fallback = pista.get("temperatura_ambiente") or 20.0
    temperaturas_trechos = [
        pista.get("temperatura_trecho_1") or temp_fallback,
        pista.get("temperatura_trecho_2") or temp_fallback,
        pista.get("temperatura_trecho_3") or temp_fallback,
        pista.get("temperatura_trecho_4") or temp_fallback,
    ]
    resultado = Corrida(
        carros,
        total_voltas=numero_voltas,
        temperaturas_trechos=temperaturas_trechos,
        consumo_qualifying=True,
        percentuais_treino_box=percentuais_treino_box,
        config=config
    ).simular()
    
    resultado["pista"] = pista
    resultado["distancia_total"] = distancia_total
    resultado["temperaturas_trechos"] = temperaturas_trechos
    equipes_por_nome = {e.nome: e for e in todas_equipes}
    resultados_para_temporada = []
    
    for posicao_info in resultado["classificacao_final"]:
        equipe_db = equipes_por_nome[posicao_info["equipe"]]
        db.session.add(ResultadoCorrida(
            equipe_id=equipe_db.id,
            tempo_total_segundos=posicao_info["tempo_total_segundos"],
            pit_stops=posicao_info["pit_stops"],
            posicao_final=posicao_info["posicao"],
        ))
        custo_montagem = float(equipe_db.custo_total_montagem() or 0)
        equipe_db.orcamento = float(equipe_db.orcamento or 0) - custo_montagem
        
        premio = premio_por_posicao(
            posicao_info["posicao"],
            posicao_info.get("abandonou", False),
            premio_base=getattr(config, 'premio_corrida_pos_1', 12000.0)
        )
        
        equipe_db.orcamento = float(equipe_db.orcamento or 0) + premio
        if corrida_agendada is not None:
            pontos = pontos_por_posicao(
                posicao_info["posicao"],
                posicao_info.get("abandonou", False),
            )
            resultados_para_temporada.append({
                "equipe_id": equipe_db.id,
                "equipe_nome": equipe_db.nome,
                "posicao": posicao_info["posicao"],
                "pontos": pontos,
                "premio": premio,
                "abandonou": posicao_info.get("abandonou", False),
                "motivo_abandono": posicao_info.get("motivo_abandono"),
                "tempo_total": posicao_info["tempo_total_segundos"],
                "custo_montagem": custo_montagem,
            })
            
    if corrida_agendada is not None:
        corrida_agendada.salvar_resultados(resultados_para_temporada)
        corrida_agendada.executada = True
        corrida_agendada.data_execucao = datetime.utcnow()
        
        # BUGFIX: Limpa o grid da classificação para não dar o bug de "corridas avançam sozinhas" na próxima etapa.
        ResultadoClassificacao.query.delete()
        
    db.session.commit()
    
    caminho_replay = os.path.join(BASE_DIR, 'ultimo_replay.json')
    try:
        with open(caminho_replay, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar replay: {e}")
        
    return resultado


def registrar(app):

    @app.route("/estrategia-corrida", methods=["GET", "POST"])
    @login_requerido
    def estrategia_corrida_view():
        usuario = Usuario.query.get(session["usuario_id"])
        if not usuario.equipe:
            return redirect(url_for("minha_equipe"))
            
        equipe = usuario.equipe
        pneu_contratado = FornecedorPneu.query.get(equipe.pneu_fornecedor_id)
        combustivel_contratado = FornecedorCombustivel.query.get(equipe.combustivel_fornecedor_id)
        
        temporada = Temporada.ativa_atual()
        proxima_corrida = temporada.proxima_corrida() if temporada else None
        pista = None
        voltas_pista = 0
        if proxima_corrida:
            criar_banco_pistas_reais()
            pista = obter_pista_real(proxima_corrida.pista_real_id)
            if pista:
                voltas_pista, _ = calcular_numero_voltas(pista["extensao_km"])

        if request.method == "POST":
            modelos_pneu_stints = request.form.getlist("modelo_pneu[]")
            voltas_stints = request.form.getlist("voltas[]")
            litros_stints = request.form.getlist("combustivel_litros[]")
            
            EstrategiaStint.query.filter_by(equipe_id=equipe.id).delete()
            
            for i in range(len(modelos_pneu_stints)):
                try:
                    novo_stint = EstrategiaStint(
                        equipe_id=equipe.id,
                        ordem=i + 1,
                        modelo_pneu=int(modelos_pneu_stints[i]),
                        voltas=int(voltas_stints[i]),
                        combustivel_litros=float(litros_stints[i])
                    )
                    db.session.add(novo_stint)
                except ValueError:
                    continue 
                
            db.session.commit()
            flash("Estratégia de corrida salva com sucesso!", "success")
            return redirect(url_for("estrategia_corrida_view"))

        stints = EstrategiaStint.query.filter_by(equipe_id=equipe.id).order_by(EstrategiaStint.ordem).all()
        if not stints:
            stints = [{"ordem": 1, "modelo_pneu": 100, "voltas": 20, "combustivel_litros": 60.0}]

        return render_template(
            "estrategia_corrida.html",
            equipe=equipe,
            pneu_contratado=pneu_contratado,
            combustivel_contratado=combustivel_contratado,
            modelos_disponiveis=modelos_componente.MODELOS,
            stints=stints,
            pista=pista,
            voltas_pista=voltas_pista
        )

    @app.route("/classificacao", methods=["GET"])
    @login_requerido
    def classificacao_view():
        resultados_db = ResultadoClassificacao.query.order_by(ResultadoClassificacao.posicao_grid).all()
        resultado = None
        if resultados_db:
            resultado = [{"posicao_grid": r.posicao_grid, "equipe": r.equipe.nome if r.equipe else f"Equipe #{r.equipe_id}", "tempo_classificacao": r.tempo_classificacao} for r in resultados_db]
        return render_template("classificacao.html", resultado=resultado)

    @app.route("/corrida", methods=["GET"])
    @login_requerido
    def corrida_view():
        resultado = None
        caminho_replay = os.path.join(BASE_DIR, 'ultimo_replay.json')
        if os.path.exists(caminho_replay):
            try:
                with open(caminho_replay, 'r', encoding='utf-8') as f:
                    resultado = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar replay: {e}")
                
        criar_banco_pistas_reais()
        temporada = Temporada.ativa_atual()
        proxima_corrida_temporada = temporada.proxima_corrida() if temporada else None

        cores_equipes = {}
        todas_equipes = CarroJogador.query.all()
        for eq in todas_equipes:
            cores_equipes[eq.nome] = eq.cor_primaria or "#cc0000"

        return render_template(
            "corrida.html", 
            resultado=resultado, 
            temporada=temporada, 
            proxima_corrida_temporada=proxima_corrida_temporada,
            cores_equipes=cores_equipes
        )