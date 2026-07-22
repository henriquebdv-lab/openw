"""
Todas as constantes de regras do jogo, num lugar só (DRY: se um número
precisa mudar, muda aqui e só aqui).
"""

TEMPO_VOLTA_BASE_SEGUNDOS = 90.0
PIT_STOP_SEGUNDOS = 22.0
LIMITE_DESGASTE_PNEU = 100.0
COMBUSTIVEL_MINIMO = 0.0
VARIACAO_ALEATORIA_DESVIO_PADRAO = 0.15  # segundos - "ruído" natural de cada volta

CONSUMO_BASE_MOTOR = 3.0
CONSUMO_BASE_LITROS_POR_KM = 0.65

BONUS_DESIGNER_ESCALA = 5.0

TANQUE_MAXIMO_LITROS = 150.0

IMPORTANCIA_FIXA_MOTOR = 5
IMPORTANCIA_FIXA_CAMBIO = 6
IMPORTANCIA_FIXA_SUSPENSAO = 7
IMPORTANCIA_FIXA_PNEU = 8
IMPORTANCIA_FIXA_COMBUSTIVEL = 9
IMPORTANCIA_FIXA_ENGENHEIRO = 10

INFLUENCIA_ESCALA = 10.0

TEMPERATURA_REFERENCIA = 20.0
DESGASTE_POR_GRAU_FRACAO = 0.01

NUMERO_TRECHOS_CORRIDA = 4

# ---------------------------------------------------------
# QUEBRA MECÂNICA
# ---------------------------------------------------------
CHANCE_QUEBRA_BASE = 0.10
CHANCE_QUEBRA_MINIMA = 0.02

# ---------------------------------------------------------
# CHASSI E AERODINÂMICA (novo)
# ---------------------------------------------------------
# Chassi e aero NÃO são contratos com fornecedor - são projetados
# pelo Engenheiro que a equipe contrata. O jogador novo recebe
# chassi + aero de graça, ambos projetados por engenheiro nível 1.
#
# O nível do engenheiro afeta a performance máxima do chassi/aero.
# Escala linear entre nível 1 (fraco) e nível 10 (topo).
#
# Efeito no tempo de volta:
#   chassi_performance = CHASSI_PERFORMANCE_NIVEL_1 + (nivel - 1) * (CHASSI_PERFORMANCE_NIVEL_10 - CHASSI_PERFORMANCE_NIVEL_1) / 9
# Multiplicado pelo percentual_aplicado (0 a 100%).

# Chassi
CHASSI_PERFORMANCE_NIVEL_1 = 0.2     # segundos a menos por volta (fraco)
CHASSI_PERFORMANCE_NIVEL_10 = 2.0    # segundos a menos por volta (topo)

# Aerodinâmica
AERO_PERFORMANCE_NIVEL_1 = 0.1       # segundos a menos por volta (fraco)
AERO_PERFORMANCE_NIVEL_10 = 1.0      # segundos a menos por volta (topo)


def performance_chassi_do_nivel(nivel_engenheiro):
    """Retorna a performance máxima do chassi projetado por um
    engenheiro do nível informado (escala linear entre 1 e 10)."""
    n = max(1, min(10, int(nivel_engenheiro or 1)))
    return CHASSI_PERFORMANCE_NIVEL_1 + (n - 1) * (
        (CHASSI_PERFORMANCE_NIVEL_10 - CHASSI_PERFORMANCE_NIVEL_1) / 9.0
    )


def performance_aero_do_nivel(nivel_engenheiro):
    """Idem para aerodinâmica."""
    n = max(1, min(10, int(nivel_engenheiro or 1)))
    return AERO_PERFORMANCE_NIVEL_1 + (n - 1) * (
        (AERO_PERFORMANCE_NIVEL_10 - AERO_PERFORMANCE_NIVEL_1) / 9.0
    )
