"""
Modelos xx-50 a xx-900 de cada componente contratado.

Regra geral matemática separada por componente:
- PNEU: Modelo BAIXO (50) -> RÁPIDO, mas desgasta pneu rápido.
        Modelo ALTO (900) -> LENTO, mas pneu duro duradouro.
- MOTOR: Modelo BAIXO (50) -> MENOS POTÊNCIA, mas economiza combustível (carro leve).
         Modelo ALTO (900) -> MAIS POTÊNCIA, mas bebe muito (carro pesado).
"""

MODELOS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
LETRAS = "ABCDEFGHIJ"

# --- PNEU e GENÉRICO ---
VELOCIDADE_PNEU_50 = -0.40
VELOCIDADE_PNEU_900 = +0.60
FATOR_DESGASTE_PNEU_50 = 1.50
FATOR_DESGASTE_PNEU_900 = 0.60

FATOR_CONSUMO_GENERICO_50 = 1.30
FATOR_CONSUMO_GENERICO_900 = 0.70

# --- MOTOR (Curva de Potência e Consumo progressivos) ---
POTENCIA_MOTOR_50 = 0.00
POTENCIA_MOTOR_900 = 0.80
FATOR_CONSUMO_MOTOR_50 = 0.75
FATOR_CONSUMO_MOTOR_900 = 1.45


def indice_modelo(numero):
    return MODELOS.index(int(numero))


def fracao_modelo(numero):
    return indice_modelo(numero) / (len(MODELOS) - 1)


def _lerp(a, b, t):
    return a + (b - a) * t


def letra_do_modelo(numero):
    return LETRAS[indice_modelo(numero)]


def condicao_pista_do_modelo(numero):
    n = int(numero)
    if n <= 500:
        return "seco"
    elif n <= 700:
        return "molhada"
    return "encharcada"


def modificadores(numero, componente="generico"):
    """
    Retorna os modificadores do modelo escolhido.
    A potência extra do motor é injetada na chave 'potencia_delta'.
    """
    numero = int(numero)
    frac = fracao_modelo(numero)

    velocidade_delta_s = 0.0
    potencia_delta = 0.0
    fator_desgaste = 1.0
    fator_consumo = 1.0

    if componente == "motor":
        potencia_delta = round(_lerp(POTENCIA_MOTOR_50, POTENCIA_MOTOR_900, frac), 3)
        fator_consumo = round(_lerp(FATOR_CONSUMO_MOTOR_50, FATOR_CONSUMO_MOTOR_900, frac), 3)
    elif componente == "pneu":
        velocidade_delta_s = round(_lerp(VELOCIDADE_PNEU_50, VELOCIDADE_PNEU_900, frac), 3)
        fator_desgaste = round(_lerp(FATOR_DESGASTE_PNEU_50, FATOR_DESGASTE_PNEU_900, frac), 3)
    else:
        velocidade_delta_s = round(_lerp(VELOCIDADE_PNEU_50, VELOCIDADE_PNEU_900, frac), 3)
        fator_consumo = round(_lerp(FATOR_CONSUMO_GENERICO_50, FATOR_CONSUMO_GENERICO_900, frac), 3)

    return {
        "modelo": numero,
        "velocidade_delta_s": velocidade_delta_s,
        "potencia_delta": potencia_delta,
        "fator_desgaste": fator_desgaste,
        "fator_consumo": fator_consumo,
        "letra": letra_do_modelo(numero),
        "condicao_pista": condicao_pista_do_modelo(numero),
    }


def modelo_valido(numero):
    try:
        return int(numero) in MODELOS
    except (ValueError, TypeError):
        return False