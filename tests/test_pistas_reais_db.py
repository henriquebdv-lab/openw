import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import pistas_reais_db
from corrida import calcular_tempo_pit_stop


class PistasReaisDBTests(unittest.TestCase):
    def test_calcular_tempo_pit_stop_combina_pista_e_treinamento(self):
        config = SimpleNamespace(pit_tempo_sem_treino=25.0, pit_tempo_treino_completo=9.0)

        self.assertAlmostEqual(calcular_tempo_pit_stop(20.0, config, 0.0), 20.0)
        self.assertAlmostEqual(calcular_tempo_pit_stop(20.0, config, 100.0), 7.2)

    def test_criar_banco_adiciona_campos_de_categoria_da_pista(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            caminho_temp = tmp.name

        try:
            with patch.object(pistas_reais_db, "CAMINHO_BANCO", caminho_temp):
                pistas_reais_db.criar_banco()
                conexao = pistas_reais_db.obter_conexao()
                colunas = [row[1] for row in conexao.execute("PRAGMA table_info(pistas_reais)")]
                conexao.close()

            self.assertIn("categoria_cambio_ideal", colunas)
            self.assertIn("categoria_suspensao_ideal", colunas)
        finally:
            if os.path.exists(caminho_temp):
                os.remove(caminho_temp)

    def test_inserir_pista_real_persiste_categorias(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            caminho_temp = tmp.name

        try:
            with patch.object(pistas_reais_db, "CAMINHO_BANCO", caminho_temp):
                pistas_reais_db.criar_banco()
                pistas_reais_db.inserir_pista_real(
                    nome="Monza",
                    pais="Itália",
                    extensao_km=5.8,
                    caminho_svg="M0 0",
                    largura_viewbox=100,
                    altura_viewbox=100,
                    tempo_pit_stop_segundos=22.0,
                    categoria_cambio_ideal="AB",
                    categoria_suspensao_ideal="CD",
                )
                pista = pistas_reais_db.obter_pista_real(1)

            self.assertEqual(pista["categoria_cambio_ideal"], "AB")
            self.assertEqual(pista["categoria_suspensao_ideal"], "CD")
        finally:
            if os.path.exists(caminho_temp):
                os.remove(caminho_temp)


if __name__ == "__main__":
    unittest.main()
