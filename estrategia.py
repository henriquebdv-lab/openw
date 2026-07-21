def montar_estrategia_corrida(ajustes, pneu, combustivel, volta_primeiro_pit, outro_pit):
    """Cria uma estratégia simples para a corrida a partir do setup e dos itens escolhidos."""
    total = sum(ajustes.values())
    equilibrio = max(0, 250 - abs(total - 250))
    risco = "conservadora"

    if volta_primeiro_pit <= 8:
        risco = "agressiva"
    elif volta_primeiro_pit <= 18:
        risco = "equilibrada"

    resumo = (
        f"Estratégia {risco}: primeiro pit stop na volta {volta_primeiro_pit}. "
        f"Pneu {pneu.nome} e combustível {combustivel.nome} foram selecionados."
    )
    if outro_pit:
        resumo += " Será feito um segundo pit stop durante a corrida."
    else:
        resumo += " A corrida seguirá com um único pit stop."

    return {
        "resumo": resumo,
        "volta_primeiro_pit": volta_primeiro_pit,
        "outro_pit": outro_pit,
        "equilibrio_setup": equilibrio,
    }


def sugerir_estrategia_estrategista(ajustes):
    """Sugere uma estratégia simplificada como se um estrategista tivesse feito o cálculo."""
    total = sum(ajustes.values())
    erro = abs(total - 250)

    if erro < 20:
        volta = 12
        resumo = "Estratégia do estrategista: pit stop na volta 12 com ritmo constante e segundo stop opcional."
    elif erro < 60:
        volta = 15
        resumo = "Estratégia do estrategista: pit stop na volta 15 para preservar pneus e combustível."
    else:
        volta = 18
        resumo = "Estratégia do estrategista: pit stop tardio na volta 18, com foco em gestão de desgaste."

    return {
        "volta_primeiro_pit": volta,
        "resumo": resumo,
    }
