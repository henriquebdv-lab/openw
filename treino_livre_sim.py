"""
Treino Livre Real (stint de teste).

O jogador escolhe:
  - a pista (pra saber as categorias ideais de câmbio/suspensão -> feedback)
  - o pneu que quer testar
  - o combustível que quer testar
  - quanto combustível carregar (define quantas voltas dá pra rodar)
  - opcional: o setup de teste (modelos 50-900 de câmbio, suspensão e pneu)

A simulação roda VOLTA A VOLTA:
  - cada volta gera um tempo (com a mesma matemática do carro.py da corrida)
  - o combustível vai baixando; quando não dá pra mais uma volta, encerra
  - o pneu vai desgastando; se estourar (>=100%), encerra na hora
  - o piloto dá um FEEDBACK a cada volta (feedback_piloto.py)

Tudo é calculado em cima do carro real da equipe (equipe.montar_carro()),
então NADA aqui altera o banco: pneu/combustível/setup escolhidos valem
só pra este treino (sandbox).

Tempos ficam SEMPRE em segundos (float). Na tela use o filtro `tempo_min`
pra mostrar como 1:27.180.

Uso típico (na rota):
    from treino_livre_sim import simular_treino_livre_real
    resultado = simular_treino_livre_real(
        equipe_db, pneu_db, combustivel_db, combustivel_litros=30,
        pista=pista_dict, modelo_cambio=500, modelo_suspensao=400,
    )
"""

import modelos_componente
from equipamentos import Pneu, Combustivel
from feedback_piloto import frase_por_categoria


LETRAS = modelos_componente.LETRAS  # "ABCDEFGHIJ"

# Trava de segurança: mesmo com consumo minúsculo, não roda pra sempre.
CAP_VOLTAS = 300


def _idx(letra):
    """Índice 0..9 de uma letra de categoria (A..J). Robusto a lixo."""
    letra = (letra or "A").upper()[:1]
    return LETRAS.index(letra) if letra in LETRAS else 0


def _aplicar_pista(carro, pista):
    """Coloca no carro os dados da pista usados pelo cálculo de tempo/consumo
    e pelo casamento de categorias (câmbio/suspensão). Espelha o
    _aplicar_dados_pista_no_carro do app.py pra manter o mesmo comportamento.
    Se pista for None, deixa o carro num estado neutro (seco, sem penalidade)."""
    if not pista:
        carro.categoria_chuva = "seco"
        return

    cat_cambio = (pista.get("categoria_cambio_ideal") or "A").upper()
    cat_suspensao = (pista.get("categoria_suspensao_ideal") or "A").upper()
    carro.categoria_cambio_ideal_pista = cat_cambio[0] if cat_cambio else "A"
    carro.categoria_suspensao_ideal_pista = cat_suspensao[0] if cat_suspensao else "A"
    carro.categoria_chuva = "seco"
    carro.temperatura_pista = (
        pista.get("temperatura_trecho_1") or pista.get("temperatura_ambiente") or 20.0
    )
    carro.tamanho_volta_km = pista.get("extensao_km") or 0.0
    carro.influencia_pista_motor = pista.get("influencia_motor") or 10
    carro.influencia_pista_cambio = pista.get("influencia_cambio") or 10
    carro.influencia_pista_suspensao = pista.get("influencia_suspensao") or 10
    carro.influencia_pista_pneu = pista.get("influencia_pneu") or 10
    carro.influencia_pista_combustivel = pista.get("influencia_combustivel") or 10
    carro.influencia_pista_engenheiro = pista.get("influencia_engenheiro") or 10


def simular_treino_livre_real(equipe_db, pneu_db, combustivel_db, combustivel_litros,
                              pista=None, modelo_cambio=None, modelo_suspensao=None,
                              modelo_pneu=None, aleatorio=True):
    """
    Roda o treino livre volta a volta e devolve um dicionário com o resumo
    e o histórico de voltas.

    Parâmetros:
      equipe_db          : instância de CarroJogador (a equipe do jogador)
      pneu_db            : FornecedorPneu escolhido pra testar
      combustivel_db     : FornecedorCombustivel escolhido pra testar
      combustivel_litros : quanto combustível carregar (define o nº de voltas)
      pista              : dict da pista (opcional, mas recomendado p/ feedback)
      modelo_cambio      : 50..900 do câmbio a testar (opcional)
      modelo_suspensao   : 50..900 da suspensão a testar (opcional)
      modelo_pneu        : 50..900 do pneu a testar (opcional)
      aleatorio          : varia as frases de feedback (False = determinístico)

    Retorno (dict) com as chaves usadas pelo template e pelo ranking:
      pneu_nome, combustivel_nome, combustivel_litros, consumo_por_volta,
      total_voltas, melhor_volta_numero, melhor_volta_tempo, tempo_medio,
      erro_setup, encerrou_por ("combustivel" | "pneu"), pista_nome,
      letra_cambio, letra_suspensao, ideal_cambio, ideal_suspensao,
      voltas -> lista de {numero, tempo, desgaste_pneu, combustivel_restante, feedback}
    """
    carro = equipe_db.montar_carro()

    # --- Pneu e combustível escolhidos SÓ pra este treino (não toca no banco) ---
    carro.pneu = Pneu(
        pneu_db.nome, pneu_db.custo_temporada, pneu_db.performance, pneu_db.desgaste,
        categoria_chuva=getattr(pneu_db, "categoria_chuva", "seco") or "seco",
    )
    carro.combustivel = Combustivel(
        combustivel_db.nome, combustivel_db.custo_temporada,
        combustivel_db.eficiencia, combustivel_db.aumento_potencia_motor,
    )

    combustivel_litros = max(1.0, float(combustivel_litros or 0.0))
    carro.combustivel_carregado = combustivel_litros

    # --- Setup de teste (modelos 50-900). definir_modelos ignora inválidos/None ---
    carro.definir_modelos(cambio=modelo_cambio, suspensao=modelo_suspensao, pneu=modelo_pneu)

    # --- Dados da pista (categorias ideais, temperatura, tamanho da volta) ---
    _aplicar_pista(carro, pista)

    # Consumo depende do tamanho da volta -> por isso calculamos DEPOIS da pista.
    consumo = carro.consumo_por_volta()
    if consumo <= 0:
        consumo = 0.1  # trava anti-divisão-por-zero

    # Letras efetivas do setup escolhido x letras ideais da pista.
    letra_cambio = carro._categoria_cambio_efetiva()
    letra_suspensao = carro._categoria_suspensao_efetiva()
    if pista:
        ideal_cambio = (pista.get("categoria_cambio_ideal") or letra_cambio).upper()[:1]
        ideal_suspensao = (pista.get("categoria_suspensao_ideal") or letra_suspensao).upper()[:1]
    else:
        ideal_cambio = letra_cambio
        ideal_suspensao = letra_suspensao

    # Erro de setup = distância (em "passos" de letra) do ideal. 0 = perfeito.
    erro_setup = float(
        abs(_idx(letra_cambio) - _idx(ideal_cambio))
        + abs(_idx(letra_suspensao) - _idx(ideal_suspensao))
    )

    voltas = []
    tempos = []
    desgaste = 0.0
    combustivel_restante = combustivel_litros
    melhor_tempo = None
    melhor_numero = None
    encerrou_por = "combustivel"

    numero = 0
    while numero < CAP_VOLTAS:
        # Acabou o combustível pra mais uma volta -> fim do stint.
        if combustivel_restante < consumo:
            encerrou_por = "combustivel"
            break
        numero += 1

        tempo = carro.tempo_com_variacao(desgaste)
        combustivel_restante -= consumo
        desgaste += carro.desgaste_por_volta()
        estourou = desgaste >= 100.0

        # Feedback do piloto nesta volta.
        if estourou:
            feedback = "Estourou o pneu! Não dá pra continuar, treino encerrado."
        elif desgaste > 85.0:
            feedback = "Pneu no talo, tô escorregando muito — já era pra ter ido pro box."
        elif numero % 2 == 1:
            feedback = frase_por_categoria(ideal_cambio, letra_cambio, "cambio", aleatorio)
        else:
            feedback = frase_por_categoria(ideal_suspensao, letra_suspensao, "suspensao", aleatorio)

        tempos.append(tempo)
        if melhor_tempo is None or tempo < melhor_tempo:
            melhor_tempo = tempo
            melhor_numero = numero

        voltas.append({
            "numero": numero,
            "tempo": round(tempo, 3),
            "desgaste_pneu": round(min(desgaste, 100.0), 1),
            "combustivel_restante": round(max(combustivel_restante, 0.0), 2),
            "feedback": feedback,
        })

        if estourou:
            encerrou_por = "pneu"
            break

    total_voltas = len(voltas)
    tempo_medio = round(sum(tempos) / total_voltas, 3) if total_voltas else 0.0

    return {
        "pneu_nome": pneu_db.nome,
        "combustivel_nome": combustivel_db.nome,
        "combustivel_litros": round(combustivel_litros, 2),
        "consumo_por_volta": round(consumo, 3),
        "total_voltas": total_voltas,
        "melhor_volta_numero": melhor_numero or 0,
        "melhor_volta_tempo": round(melhor_tempo, 3) if melhor_tempo is not None else 0.0,
        "tempo_medio": tempo_medio,
        "erro_setup": erro_setup,
        "encerrou_por": encerrou_por,
        "pista_nome": (pista.get("nome") if pista else None),
        "letra_cambio": letra_cambio,
        "letra_suspensao": letra_suspensao,
        "ideal_cambio": ideal_cambio,
        "ideal_suspensao": ideal_suspensao,
        "voltas": voltas,
    }
