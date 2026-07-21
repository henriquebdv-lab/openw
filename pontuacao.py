"""
Sistema de pontos por corrida (padrão F1: 25/18/15/12/10/8/6/4/2/1
pros 10 primeiros; do 11º em diante, 0 pontos). Quem abandona também
recebe 0.

Também calcula o ranking geral da temporada (soma dos pontos de todas
as corridas executadas até agora).
"""

from collections import defaultdict

PONTOS_POR_POSICAO = {
    1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
    6: 8, 7: 6, 8: 4, 9: 2, 10: 1,
}


def pontos_por_posicao(posicao, abandonou=False):
    if abandonou:
        return 0
    return PONTOS_POR_POSICAO.get(posicao, 0)


def ranking_temporada(temporada):
    """Percorre todas as corridas executadas da temporada e soma pontos
    por equipe. Retorna lista ordenada por (pontos DESC, vitórias DESC).

    Cada entrada: {equipe_id, equipe_nome, pontos_total, vitorias, corridas}
    """
    acumulado = defaultdict(
        lambda: {"pontos_total": 0, "vitorias": 0, "corridas": 0, "equipe_nome": ""}
    )
    for corrida_agendada in temporada.corridas_agendadas:
        if not corrida_agendada.executada:
            continue
        for r in corrida_agendada.resultados():
            eid = r.get("equipe_id")
            if eid is None:
                continue
            acumulado[eid]["equipe_nome"] = r.get("equipe_nome", "")
            acumulado[eid]["pontos_total"] += r.get("pontos", 0)
            acumulado[eid]["corridas"] += 1
            if r.get("posicao") == 1 and not r.get("abandonou"):
                acumulado[eid]["vitorias"] += 1

    lista = [{"equipe_id": eid, **dados} for eid, dados in acumulado.items()]
    lista.sort(key=lambda x: (-x["pontos_total"], -x["vitorias"]))
    return lista
