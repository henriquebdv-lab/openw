"""
Modelos xx-50 a xx-900 de cada componente contratado.

CONCEITO (decisão de arquitetura):
- O jogador contrata 1 fornecedor por temporada (motor, pneu, combustível,
  câmbio, suspensão) — isso continua igual, no banco.
- A CADA CORRIDA, o jogador escolhe qual MODELO do fornecedor usar: um número
  de 50 a 900. Isso NÃO cria linhas no banco: o modelo é um MODIFICADOR
  calculado em cima das stats base do fornecedor.
- Regra geral:
    * modelo BAIXO (50)  -> mais RÁPIDO, mas dura/rende MENOS (desgasta/consome mais)
    * modelo ALTO (900)  -> mais LENTO, mas dura/rende MAIS (desgasta/consome menos)

Os 10 modelos (não são igualmente espaçados; segue o padrão do jogo):
    50, 100, 200, 300, 400, 500, 600, 700, 800, 900

Categorias:
- Câmbio/Suspensão: cada modelo corresponde a uma letra A-J.
    A=50, B=100, C=200, D=300, E=400, F=500, G=600, H=700, I=800, J=900
    (a pista pede uma letra ideal; escolher o modelo certo = acerto perfeito)
- Pneu: cada modelo tem uma condição de pista:
    50-500 = seco, 600-700 = molhada, 800-900 = encharcada

Este módulo é PURO (sem banco, sem Flask), fácil de testar e de plugar
depois no carro.py / corrida.py.
"""

# Os 10 modelos, na ordem oficial
MODELOS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]

# Letra da categoria de pista (câmbio/suspensão) por modelo
LETRAS = "ABCDEFGHIJ"

# Faixas de intensidade do modificador. Ajuste fino aqui se quiser
# deixar a diferença entre modelos mais suave ou mais agressiva.
# velocidade: segundos por volta somados ao tempo (negativo = mais rápido)
VELOCIDADE_MODELO_50 = -0.40    # modelo mais baixo: ganha tempo
VELOCIDADE_MODELO_900 = +0.60   # modelo mais alto: perde tempo
# desgaste/consumo: multiplicador (>1 gasta mais, <1 gasta menos)
FATOR_MODELO_50 = 1.45          # modelo baixo desgasta/consome bem mais
FATOR_MODELO_900 = 0.65         # modelo alto economiza


def indice_modelo(numero):
    """Retorna 0..9 pra um número de modelo. Erro se inválido."""
    return MODELOS.index(int(numero))


def fracao_modelo(numero):
    """Normaliza o modelo pra 0.0 (modelo 50) .. 1.0 (modelo 900)."""
    return indice_modelo(numero) / (len(MODELOS) - 1)


def _lerp(a, b, t):
    """Interpolação linear simples entre a e b, com t de 0 a 1."""
    return a + (b - a) * t


def letra_do_modelo(numero):
    """Câmbio/suspensão: A=50 ... J=900."""
    return LETRAS[indice_modelo(numero)]


def modelo_da_letra(letra):
    """Inverso de letra_do_modelo: 'A' -> 50, 'J' -> 900."""
    return MODELOS[LETRAS.index(letra.upper())]


def condicao_pista_do_modelo(numero):
    """Pneu: seco / molhada / encharcada, conforme o modelo."""
    n = int(numero)
    if n <= 500:
        return "seco"
    elif n <= 700:
        return "molhada"
    return "encharcada"


def modificadores(numero, componente="generico"):
    """
    Retorna os modificadores do modelo escolhido.

    Retorno (dict):
      - velocidade_delta_s: segundos somados ao tempo de volta
                            (negativo = mais rápido)
      - fator_desgaste:      multiplicador de desgaste do pneu/componente
      - fator_consumo:       multiplicador de consumo de combustível
      - letra:               letra A-J (só útil pra câmbio/suspensão)
      - condicao_pista:      seco/molhada/encharcada (só útil pra pneu)

    `componente` pode ajustar a intensidade no futuro; por ora todos usam
    a mesma curva base, o que já dá um jogo equilibrado.
    """
    numero = int(numero)
    frac = fracao_modelo(numero)

    velocidade_delta_s = round(_lerp(VELOCIDADE_MODELO_50, VELOCIDADE_MODELO_900, frac), 3)
    fator = round(_lerp(FATOR_MODELO_50, FATOR_MODELO_900, frac), 3)

    return {
        "modelo": numero,
        "velocidade_delta_s": velocidade_delta_s,
        "fator_desgaste": fator,
        "fator_consumo": fator,
        "letra": letra_do_modelo(numero),
        "condicao_pista": condicao_pista_do_modelo(numero),
    }


def modelo_valido(numero):
    """True se o número é um dos 10 modelos oficiais."""
    try:
        return int(numero) in MODELOS
    except (ValueError, TypeError):
        return False


if __name__ == "__main__":
    print("Modelo | Vel(s) | Fator desg/cons | Letra | Condição pneu")
    print("-" * 60)
    for m in MODELOS:
        mod = modificadores(m)
        print(f"  {m:4d} | {mod['velocidade_delta_s']:+6.3f} | "
              f"{mod['fator_desgaste']:>6.3f}          | "
              f"  {mod['letra']}   | {mod['condicao_pista']}")
