"""
Todas as constantes de regras do jogo, num lugar só (DRY: se um número
precisa mudar, muda aqui e só aqui).
"""

TEMPO_VOLTA_BASE_SEGUNDOS = 90.0
PIT_STOP_SEGUNDOS = 22.0
LIMITE_DESGASTE_PNEU = 100.0
COMBUSTIVEL_MINIMO = 0.0
VARIACAO_ALEATORIA_DESVIO_PADRAO = 0.15  # segundos - "ruído" natural de cada volta

# Consumo base em litros por VOLTA (compat: usado só se o carro não tem
# tamanho_volta_km setado; senão usa CONSUMO_BASE_LITROS_POR_KM abaixo).
CONSUMO_BASE_MOTOR = 3.0

# Consumo base em litros por KM - referência do como.txt: 0.500 L/km.
# Multiplicado pelo tamanho da volta e reduzido pelas eficiências
# (motor + combustível).
CONSUMO_BASE_LITROS_POR_KM = 0.65

BONUS_DESIGNER_ESCALA = 5.0     # multiplica a eficiência exata do engenheiro no desenvolvimento (em segundos)

# ---------------------------------------------------------
# Regras vindas do "como.txt" (Manual Estratégia F1)
# ---------------------------------------------------------

# Tanque máximo em litros (regra do manual: "capacidade máxima é 150L")
TANQUE_MAXIMO_LITROS = 150.0

# Importâncias fixas de cada componente no desempenho do carro. Valores
# do jogo, escondidos do jogador. Cada pista tem uma "influência"
# (multiplicador) por corrida - o efeito final é importancia * influencia_pista.
IMPORTANCIA_FIXA_MOTOR = 5
IMPORTANCIA_FIXA_CAMBIO = 6
IMPORTANCIA_FIXA_SUSPENSAO = 7
IMPORTANCIA_FIXA_PNEU = 8
IMPORTANCIA_FIXA_COMBUSTIVEL = 9
IMPORTANCIA_FIXA_ENGENHEIRO = 10

# Divisor pra escalar o efeito da influência. Se a influência da pista é
# igual a esse valor, o fator vale 1.0 (neutro). Se é 20, fator = 2.0
# (componente conta o dobro). Se é 5, fator = 0.5.
INFLUENCIA_ESCALA = 10.0

# Temperatura de referência (°C). A cada grau acima/abaixo, o desgaste
# do pneu aumenta/diminui (baseado no como.txt: 20°C = neutro).
TEMPERATURA_REFERENCIA = 20.0
DESGASTE_POR_GRAU_FRACAO = 0.01  # 1% a mais/menos de desgaste por grau

# Corrida é dividida em 4 trechos (como.txt: "a corrida é dividida em 4
# trechos e a temperatura pode mudar de um trecho para outro").
NUMERO_TRECHOS_CORRIDA = 4
