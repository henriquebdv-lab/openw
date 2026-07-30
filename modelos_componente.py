"""
Modelos xx-50 a xx-900 de cada componente contratado.

O jogador contrata 1 fornecedor por temporada com base no Nível.
A CADA CORRIDA, o jogador escolhe qual MODELO do fornecedor usar: 50 a 900.

Regra geral matemática:
- PNEU: Modelo BAIXO (50) -> mais RÁPIDO, mas desgasta pneu rápido.
        Modelo ALTO (900) -> mais LENTO, mas pneu duro duradouro.
- MOTOR: Modelo BAIXO (50) -> mais LENTO, mas economiza combustível.
         Modelo ALTO (900) -> mais RÁPIDO (potente), mas bebe muito.
"""

MODELOS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
LETRAS = "ABCDEFGHIJ"

# --- PNEU e GENÉRICO (50 é rápido/desgasta, 900 é lento/conserva) ---
VELOCIDADE_PNEU_50 = -0.40
VELOCIDADE_PNEU_900 = +0.60
FATOR_DESGASTE_PNEU_50 = 1.50
FATOR_DESGASTE_PNEU_900 = 0.60

FATOR_CONSUMO_GENERICO_50 = 1.30
FATOR_CONSUMO_GENERICO_900 = 0.70

# --- MOTOR (Invertido: 50 é fraco/econômico, 900 é forte/beberrão) ---
VELOCIDADE_MOTOR_50 = +0.00
VELOCIDADE_MOTOR_900 = -0.80
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


def modelo_da_letra(letra):
    return MODELOS[LETRAS.index(letra.upper())]


def condicao_pista_do_modelo(numero):
    n = int(numero)
    if n <= 500:
        return "seco"
    elif n <= 700:
        return "molhada"
    return "encharcada"


def modificadores(numero, componente="generico"):
    """
    Retorna os modificadores do modelo escolhido, isolando as curvas corretas 
    para Motor e Pneu.
    """
    numero = int(numero)
    frac = fracao_modelo(numero)

    if componente == "motor":
        velocidade_delta_s = round(_lerp(VELOCIDADE_MOTOR_50, VELOCIDADE_MOTOR_900, frac), 3)
        fator_consumo = round(_lerp(FATOR_CONSUMO_MOTOR_50, FATOR_CONSUMO_MOTOR_900, frac), 3)
        fator_desgaste = 1.0
    elif componente == "pneu":
        velocidade_delta_s = round(_lerp(VELOCIDADE_PNEU_50, VELOCIDADE_PNEU_900, frac), 3)
        fator_desgaste = round(_lerp(FATOR_DESGASTE_PNEU_50, FATOR_DESGASTE_PNEU_900, frac), 3)
        fator_consumo = 1.0
    else:
        # Combustível e genéricos mantêm a curva original
        velocidade_delta_s = round(_lerp(VELOCIDADE_PNEU_50, VELOCIDADE_PNEU_900, frac), 3)
        fator_consumo = round(_lerp(FATOR_CONSUMO_GENERICO_50, FATOR_CONSUMO_GENERICO_900, frac), 3)
        fator_desgaste = 1.0

    return {
        "modelo": numero,
        "velocidade_delta_s": velocidade_delta_s,
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


if __name__ == "__main__":
    print("Modelo | Pneu Vel(s) | Pneu Desg | Motor Vel(s) | Motor Cons | Letra | Condição")
    print("-" * 80)
    for m in MODELOS:
        mod_pneu = modificadores(m, "pneu")
        mod_motor = modificadores(m, "motor")
        print(f"  {m:4d} | {mod_pneu['velocidade_delta_s']:+10.3f} | "
              f"{mod_pneu['fator_desgaste']:>9.3f} | "
              f"{mod_motor['velocidade_delta_s']:+12.3f} | "
              f"{mod_motor['fator_consumo']:>10.3f} | "
              f"  {mod_pneu['letra']}   | {mod_pneu['condicao_pista']}")