"""
Classes de domínio dos equipamentos do carro.

- Motor, Combustível, Pneu, Câmbio, Suspensão: vêm de fornecedores contratados
- Chassi: projetado pelo Engenheiro contratado (nome+performance conceituais)
- Engenheiro: pessoa contratada, tem nível e eficiência
"""


class Motor:
    def __init__(self, nome, custo, potencia, eficiencia_combustivel):
        self.nome = nome
        self.custo = custo
        self.potencia = potencia
        self.eficiencia_combustivel = eficiencia_combustivel


class Combustivel:
    def __init__(self, nome, custo, eficiencia, aumento_potencia_motor):
        self.nome = nome
        self.custo = custo
        self.eficiencia = eficiencia
        self.aumento_potencia_motor = aumento_potencia_motor


class Pneu:
    def __init__(self, nome, custo, performance, desgaste, categoria_chuva="seco"):
        self.nome = nome
        self.custo = custo
        self.performance = performance
        self.desgaste = desgaste
        self.categoria_chuva = categoria_chuva


class Chassi:
    """Chassi NÃO é fornecedor. É projetado pelo Engenheiro.
    Custo é sempre 0 (não tem contrato)."""
    def __init__(self, nome, custo, performance):
        self.nome = nome
        self.custo = custo or 0.0
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
    def __init__(self, nome, custo, nivel, eficiencia_exata):
        self.nome = nome
        self.custo = custo
        self.nivel = nivel
        self.eficiencia_exata = eficiencia_exata
        # Bônus de eficiência derivado do nível (usado em consumo/desgaste)
        # Nível 1 = 0.0, Nível 10 = 0.09 (9% de redução)
        self.bonus_eficiencia = max(0, (int(nivel or 1) - 1) * 0.01)
