import unittest

from carro import Carro
from equipe import Equipe
from equipamentos import Motor, Combustivel, Pneu, Chassi, Cambio, Suspensao


class CategoriasCarroTests(unittest.TestCase):
    def test_categoria_pista_afeta_tempo_base(self):
        equipe = Equipe("Teste", 1000000)
        motor = Motor("M", 0, 1.0, 0.0)
        combustivel = Combustivel("C", 0, 0.0, 0.0)
        chassi = Chassi("Ch", 0, 0.0)

        pneu = Pneu("P", 0, 0.0, 1.0, categoria_chuva="seco")
        cambio = Cambio("G", 0, 0.0, categoria_pista="A")
        suspensao = Suspensao("S", 0, 0.0, categoria_pista="A")

        carro_bom = Carro(equipe, motor, combustivel, pneu, chassi, cambio, suspensao)
        carro_bom.categoria_pista = "A"
        carro_bom.categoria_chuva = "seco"

        carro_ruim = Carro(equipe, motor, combustivel, pneu, chassi, cambio, suspensao)
        carro_ruim.categoria_pista = "J"
        carro_ruim.categoria_chuva = "chuva"

        self.assertGreater(carro_bom.tempo_base(), carro_ruim.tempo_base())


if __name__ == "__main__":
    unittest.main()
