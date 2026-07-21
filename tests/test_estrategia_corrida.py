import unittest

from estrategia import montar_estrategia_corrida, sugerir_estrategia_estrategista


class TestEstrategiaCorrida(unittest.TestCase):
    def test_montar_estrategia_corrida_gera_resumo(self):
        ajustes = {
            "ajuste_cambio": 50,
            "ajuste_suspensao": 50,
            "ajuste_freio": 50,
            "ajuste_aerofolio_dianteiro": 50,
            "ajuste_aerofolio_traseiro": 50,
        }
        pneu = type("Pneu", (), {"nome": "P1", "performance": 90})()
        combustivel = type("Combustivel", (), {"nome": "C1", "eficiencia": 80})()

        estrategia = montar_estrategia_corrida(ajustes, pneu, combustivel, 12, True)

        self.assertIn("pit stop", estrategia["resumo"].lower())
        self.assertEqual(estrategia["volta_primeiro_pit"], 12)
        self.assertTrue(estrategia["outro_pit"])

    def test_sugerir_estrategia_estrategista_recomenda_valores(self):
        ajustes = {
            "ajuste_cambio": 55,
            "ajuste_suspensao": 50,
            "ajuste_freio": 45,
            "ajuste_aerofolio_dianteiro": 50,
            "ajuste_aerofolio_traseiro": 50,
        }
        recomendacao = sugerir_estrategia_estrategista(ajustes)

        self.assertGreaterEqual(recomendacao["volta_primeiro_pit"], 1)
        self.assertIn("Estratégia", recomendacao["resumo"])
