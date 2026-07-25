"""
Rotas de corrida:
- /estrategia-corrida   (define estratégia + salva modelos 50-900)
- /classificacao        (visualização do grid)
- /corrida              (visualização do resultado)
"""
import os
import json
from datetime import datetime

from flask import render_template, request, redirect, url_for, session, flash

from config import BASE_DIR
from models import db, Usuario, CarroJogador, Configuracao, TreinamentoBox, ResultadoClassificacao, ResultadoCorrida, FornecedorPneu, FornecedorCombustivel
from models_temporada import Temporada
from extensoes import login_requerido
from pontuacao import pontos_por_posicao, premio_por_posicao
from classificacao import Classificacao
from corrida import Corrida, calcular_tempo_pit_stop
from estrategia import montar_estrategia_corrida, sugerir_estrategia_estrategista
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


def _executar_corrida_e_persistir(pista, corrida_agendada=None):
    numero_voltas, distancia_total = calcular_numero_voltas(pista["extensao_km"])
    config = Configuracao.obter()
    todas_equipes = CarroJogador.query.all()
    carros = [equipe_db.montar_carro() for equipe_db in todas_equipes]
    percentuais_treino_box = []
    
    for carro, equipe_db in zip(carros, todas_equipes):
        treinamento = TreinamentoBox.obter_ou_criar(equipe_db.id)
        carro.tempo_pit_stop = calcular_tempo_pit_stop(pista["tempo_pit_stop_segundos"], config, treinamento.percentual)
        _aplicar_dados_pista_no_carro(carro, pista)
        
        carro.estrategia_volta_pit = equipe_db.estrategia_volta_pit
        carro.estrategia_dois_pits = equipe_db.estrategia_dois_pits
        
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
    db.session.commit()
    
    # NOVO: Salva o replay num arquivo local para que a tela de Corrida do jogador
    # possa ler depois sem precisarmos alterar o schema do banco.
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
        ajustes = session.get("treino_livre_salvo") or {"ajuste_cambio": 50, "ajuste_suspensao": 50, "ajuste_freio": 50,
                                                         "ajuste_aerofolio_dianteiro": 50, "ajuste_aerofolio_traseiro": 50}
        treino_oficial = session.get("treino_oficial_salvo") or {}
        
        pneu_contratado = FornecedorPneu.query.get(usuario.equipe.pneu_fornecedor_id)
        combustivel_contratado = FornecedorCombustivel.query.get(usuario.equipe.combustivel_fornecedor_id)
        
        resultado = None
        mensagem = None
        sugestao = None
        
        if request.method == "POST":
            volta_primeiro_pit = int(request.form.get("volta_primeiro_pit", 10))
            outro_pit = request.form.get("outro_pit") == "on"
            resultado = montar_estrategia_corrida(ajustes, pneu_contratado, combustivel_contratado, volta_primeiro_pit, outro_pit)
            sugestao = sugerir_estrategia_estrategista(ajustes)
            
            usuario.equipe.estrategia_volta_pit = volta_primeiro_pit
            usuario.equipe.estrategia_dois_pits = outro_pit
            
            campos_modelo = {
                "modelo_motor": request.form.get("modelo_motor"),
                "modelo_combustivel": request.form.get("modelo_combustivel"),
                "modelo_pneu": request.form.get("modelo_pneu"),
                "modelo_cambio": request.form.get("modelo_cambio"),
                "modelo_suspensao": request.form.get("modelo_suspensao"),
            }
            for campo, valor in campos_modelo.items():
                if valor is None:
                    continue
                if valor == "":
                    setattr(usuario.equipe, campo, None)
                elif modelos_componente.modelo_valido(valor):
                    setattr(usuario.equipe, campo, int(valor))
            db.session.commit()
            mensagem = "Estratégia salva no banco de dados com sucesso."
            
        return render_template("estrategia_corrida.html", ajustes=ajustes, treino_oficial=treino_oficial,
                               pneu_contratado=pneu_contratado, combustivel_contratado=combustivel_contratado, resultado=resultado, sugestao=sugestao,
                               mensagem=mensagem, equipe=usuario.equipe,
                               modelos_disponiveis=modelos_componente.MODELOS)

    @app.route("/classificacao", methods=["GET"])
    @login_requerido
    def classificacao_view():
        # APENAS LEITURA: Busca do banco os resultados gerados pelo admin
        resultados_db = ResultadoClassificacao.query.order_by(ResultadoClassificacao.posicao_grid).all()
        resultado = None
        
        if resultados_db:
            resultado = []
            for r in resultados_db:
                resultado.append({
                    "posicao_grid": r.posicao_grid,
                    "equipe": r.equipe.nome if r.equipe else f"Equipe #{r.equipe_id}",
                    "tempo_classificacao": r.tempo_classificacao
                })
                
        return render_template("classificacao.html", resultado=resultado)

    @app.route("/corrida", methods=["GET"])
    @login_requerido
    def corrida_view():
        # APENAS LEITURA: Lê o arquivo gerado pela execução do admin
        resultado = None
        caminho_replay = os.path.join(BASE_DIR, 'ultimo_replay.json')
        
        if os.path.exists(caminho_replay):
            try:
                with open(caminho_replay, 'r', encoding='utf-8') as f:
                    resultado = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar replay: {e}")
                
        # Mantém as variáveis de interface para a tela não quebrar
        criar_banco_pistas_reais()
        temporada = Temporada.ativa_atual()
        proxima_corrida_temporada = temporada.proxima_corrida() if temporada else None
        
        return render_template("corrida.html", 
                               resultado=resultado,
                               temporada=temporada,
                               proxima_corrida_temporada=proxima_corrida_temporada)