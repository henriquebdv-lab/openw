"""
Classificação (qualifying) - 1 volta rápida por equipe, sem desgaste.
"""


class Classificacao:
    def __init__(self, carros):
        self.carros = carros

    def gerar_grid_largada(self):
        resultados = [
            {
                "equipe": carro.equipe.nome,
                "carro": carro,
                "tempo_classificacao": round(carro.tempo_com_variacao(), 3),
            }
            for carro in self.carros
        ]

        resultados.sort(key=lambda r: r["tempo_classificacao"])

        for posicao, resultado in enumerate(resultados, start=1):
            resultado["posicao_grid"] = posicao

        return resultados