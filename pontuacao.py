"""
Sistema de pontos e premiação por corrida.

Regras (do manual de referência do jogo):

PONTOS INDIVIDUAIS (piloto): todos os 20 primeiros pontuam.
1º = 40   2º = 35   3º = 32   4º = 29   5º = 26
6º = 24   7º = 22   8º = 20   9º = 18   10º = 16
11º = 14  12º = 12  13º = 10  14º = 8   15º = 6
16º = 5   17º = 4   18º = 3   19º = 2   20º = 1

Quem abandona não recebe pontos nem prêmio.
"""

from collections import defaultdict


# ---------------------------------------------------------
# TABELA DE PONTOS
# ---------------------------------------------------------
PONTOS_POR_POSICAO = {
    1:  40,   2:  35,   3:  32,   4:  29,   5:  26,
    6:  24,   7:  22,   8:  20,   9:  18,  10:  16,
    11: 14,  12:  12,  13:  10,  14:   8,  15:   6,
    16:  5,  17:   4,  18:   3,  19:   2,  20:   1,
}


# ---------------------------------------------------------
# TABELA DE PRÊMIO ORIGINAL DE REFERÊNCIA
# ---------------------------------------------------------
PREMIO_POR_POSICAO = {
    1:  12000,   2:  11000,   3:  10500,   4:  10000,   5:   9500,
    6:   9200,   7:   8900,   8:   8600,   9:   8300,  10:   8000,
    11:  7700,  12:   7400,  13:   7100,  14:   6800,  15:   6500,
    16:  6200,  17:   6000,  18:   5800,  19:   5650,  20:   5500,
}


def pontos_por_posicao(posicao, abandonou=False):
    """Pontos individuais do piloto na corrida.
    Retorna 0 se abandonou ou se ficou fora do top 20."""
    if abandonou:
        return 0
    return PONTOS_POR_POSICAO.get(posicao, 0)


def premio_por_posicao(posicao, abandonou=False, premio_base=12000.0):
    """Prêmio em R$ do piloto na corrida.
    Retorna 0 se abandonou ou se ficou fora do top 20.
    A escala dos demais se baseia na proporção do 1º lugar."""
    if abandonou:
        return 0
    premio_original = PREMIO_POR_POSICAO.get(posicao, 0)
    if premio_original == 0:
        return 0
        
    proporcao = premio_original / 12000.0
    return round(premio_base * proporcao)


def ranking_temporada(temporada):
    """Percorre todas as corridas executadas da temporada e soma pontos
    por equipe. Retorna lista ordenada por (pontos DESC, vitórias DESC).

    Cada entrada: {equipe_id, equipe_nome, pontos_total, vitorias,
                   corridas, premio_total}
    """
    acumulado = defaultdict(lambda: {
        "pontos_total": 0,
        "vitorias": 0,
        "corridas": 0,
        "premio_total": 0,
        "equipe_nome": "",
    })
    for corrida_agendada in temporada.corridas_agendadas:
        if not corrida_agendada.executada:
            continue
        for r in corrida_agendada.resultados():
            eid = r.get("equipe_id")
            if eid is None:
                continue
            acumulado[eid]["equipe_nome"] = r.get("equipe_nome", "")
            acumulado[eid]["pontos_total"] += r.get("pontos", 0)
            acumulado[eid]["premio_total"] += r.get("premio", 0)
            acumulado[eid]["corridas"] += 1
            if r.get("posicao") == 1 and not r.get("abandonou"):
                acumulado[eid]["vitorias"] += 1

    lista = [{"equipe_id": eid, **dados} for eid, dados in acumulado.items()]
    lista.sort(key=lambda x: (-x["pontos_total"], -x["vitorias"]))
    return lista