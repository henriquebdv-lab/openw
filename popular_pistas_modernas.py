"""
Grava os valores sugeridos e aprovados para as 7 pistas modernas
que não possuíam dados canônicos na planilha Ayres.
"""

from pistas_reais_db import listar_pistas_reais, atualizar_pista_real

DADOS_PISTAS_MODERNAS = {
    "Circuit of the Americas": {
        "categoria_cambio_ideal": "E", "categoria_suspensao_ideal": "F",
        "tempo_pit_stop_segundos": 14.0,
        "influencia_motor": 11, "influencia_cambio": 12, "influencia_suspensao": 13,
        "influencia_pneu": 11, "influencia_combustivel": 10, "influencia_engenheiro": 10
    },
    "Autódromo Hermanos Rodríguez": {
        "categoria_cambio_ideal": "H", "categoria_suspensao_ideal": "C",
        "tempo_pit_stop_segundos": 16.0,
        "influencia_motor": 14, "influencia_cambio": 9, "influencia_suspensao": 8,
        "influencia_pneu": 9, "influencia_combustivel": 8, "influencia_engenheiro": 12
    },
    "Moscow Raceway": {
        "categoria_cambio_ideal": "C", "categoria_suspensao_ideal": "G",
        "tempo_pit_stop_segundos": 14.0,
        "influencia_motor": 7, "influencia_cambio": 12, "influencia_suspensao": 14,
        "influencia_pneu": 12, "influencia_combustivel": 8, "influencia_engenheiro": 10
    },
    "Norisring": {
        "categoria_cambio_ideal": "B", "categoria_suspensao_ideal": "A",
        "tempo_pit_stop_segundos": 12.0,
        "influencia_motor": 14, "influencia_cambio": 13, "influencia_suspensao": 7,
        "influencia_pneu": 10, "influencia_combustivel": 11, "influencia_engenheiro": 8
    },
    "Motorsport Arena Oschersleben": {
        "categoria_cambio_ideal": "C", "categoria_suspensao_ideal": "H",
        "tempo_pit_stop_segundos": 13.0,
        "influencia_motor": 8, "influencia_cambio": 11, "influencia_suspensao": 14,
        "influencia_pneu": 14, "influencia_combustivel": 9, "influencia_engenheiro": 9
    },
    "Sochi Autodrom": {
        "categoria_cambio_ideal": "F", "categoria_suspensao_ideal": "E",
        "tempo_pit_stop_segundos": 15.0,
        "influencia_motor": 11, "influencia_cambio": 10, "influencia_suspensao": 10,
        "influencia_pneu": 8, "influencia_combustivel": 12, "influencia_engenheiro": 11
    },
    "Yas Marina Circuit": {
        "categoria_cambio_ideal": "G", "categoria_suspensao_ideal": "D",
        "tempo_pit_stop_segundos": 14.0,
        "influencia_motor": 12, "influencia_cambio": 11, "influencia_suspensao": 11,
        "influencia_pneu": 10, "influencia_combustivel": 12, "influencia_engenheiro": 10
    }
}

def aplicar_pistas_modernas():
    pistas = listar_pistas_reais()
    if not pistas:
        print("Nenhuma pista encontrada no banco.")
        return

    atualizadas = 0
    nao_encontradas = list(DADOS_PISTAS_MODERNAS.keys())

    for pista in pistas:
        nome = pista["nome"]
        if nome in DADOS_PISTAS_MODERNAS:
            atualizar_pista_real(pista["id"], **DADOS_PISTAS_MODERNAS[nome])
            print(f"[OK] {nome} atualizada com os valores de balanceamento.")
            atualizadas += 1
            nao_encontradas.remove(nome)

    print(f"\nTotal atualizado: {atualizadas}/7")
    if nao_encontradas:
        print("Pistas NÃO ENCONTRADAS no banco:")
        for n in nao_encontradas:
            print(f" - {n}")

if __name__ == "__main__":
    aplicar_pistas_modernas()