"""
Classes de domínio dos equipamentos/pessoas que compõem o carro.

Cada uma dessas classes é "montada" a partir de um Fornecedor salvo no
banco (ver models.py) - aqui só existe a lógica de cálculo, os dados
concretos (nome, custo, status) vêm do banco e são gerenciados pelo
painel admin.
"""


class Motor:
    """2 status, ambos visíveis pro jogador: potência e eficiência de combustível."""

    def __init__(self, nome, custo, potencia, eficiencia_combustivel):
        self.nome = nome
        self.custo = custo
        self.potencia = potencia                        # segundos que reduz do tempo de volta
        self.eficiencia_combustivel = eficiencia_combustivel  # 0.0 a ~0.5 (quanto reduz o consumo)


class Combustivel:
    """Eficiência e % de aumento de potência do motor - visíveis só pro admin."""

    def __init__(self, nome, custo, eficiencia, aumento_potencia_motor):
        self.nome = nome
        self.custo = custo
        self.eficiencia = eficiencia                      # reduz consumo por volta
        self.aumento_potencia_motor = aumento_potencia_motor  # % que soma na potência do motor


class Pneu:
    def __init__(self, nome, custo, performance, desgaste, categoria_chuva="seco"):
        self.nome = nome
        self.custo = custo
        self.performance = performance
        self.desgaste = desgaste  # % de desgaste por volta
        self.categoria_chuva = categoria_chuva


class Chassi:
    def __init__(self, nome, custo, performance):
        self.nome = nome
        self.custo = custo
        self.performance = performance


class Cambio:
    def __init__(self, nome, custo, performance, categoria_pista="A"):
        self.nome = nome
        self.custo = custo
        self.performance = performance
        self.categoria_pista = categoria_pista


class Suspensao:
    def __init__(self, nome, custo, performance, categoria_pista="A"):
        self.nome = nome
        self.custo = custo
        self.performance = performance
        self.categoria_pista = categoria_pista


class Engenheiro:
    """
    Papel único que junta o que antes eram 2 coisas separadas:
    - Reduz consumo/desgaste (baseado no Nível, visível ao jogador)
    - Desenvolve chassi/aerodinâmica (eficiência exata, escondida do
      jogador - só o admin vê/edita; o efeito real depende também do
      percentual de Desenvolvimento da equipe)
    """
    BONUS_POR_NIVEL = {1: 0.0, 2: 0.03, 3: 0.06, 4: 0.10, 5: 0.15}

    def __init__(self, nome, custo, nivel, eficiencia_exata=0.0):
        self.nome = nome
        self.custo = custo
        self.nivel = nivel                    # visível pro jogador
        self.eficiencia_exata = eficiencia_exata  # escondido do jogador

    @property
    def bonus_eficiencia(self):
        return self.BONUS_POR_NIVEL.get(self.nivel, 0.0)
