"""
Importa TODOS os CSVs de pista real de uma vez, direto da pasta "tracks/"
do repositório TUMFTM/racetrack-database (baixado como ZIP e extraído).

Como usar:
    python importar_todas_pistas.py "C:\\caminho\\para\\racetrack-database-master\\tracks"
"""

import os
import sys
import random

from converter_pista_real import ler_coordenadas_csv, converter_para_svg_path
from pistas_reais_db import criar_banco, inserir_pista_real

# Nome de exibição e país de cada pista (baseado no README do repositório)
INFO_PISTAS = {
    "Austin": ("Circuit of the Americas", "Estados Unidos"),
    "BrandsHatch": ("Brands Hatch", "Reino Unido"),
    "Budapest": ("Hungaroring", "Hungria"),
    "Catalunya": ("Circuit de Barcelona-Catalunya", "Espanha"),
    "Hockenheim": ("Hockenheimring", "Alemanha"),
    "IMS": ("Indianapolis Motor Speedway", "Estados Unidos"),
    "Melbourne": ("Albert Park Circuit", "Austrália"),
    "MexicoCity": ("Autódromo Hermanos Rodríguez", "México"),
    "Montreal": ("Circuit Gilles Villeneuve", "Canadá"),
    "Monza": ("Autodromo Nazionale Monza", "Itália"),
    "MoscowRaceway": ("Moscow Raceway", "Rússia"),
    "Norisring": ("Norisring", "Alemanha"),
    "Nuerburgring": ("Nürburgring", "Alemanha"),
    "Oschersleben": ("Motorsport Arena Oschersleben", "Alemanha"),
    "Sakhir": ("Bahrain International Circuit", "Bahrein"),
    "SaoPaulo": ("Autódromo José Carlos Pace (Interlagos)", "Brasil"),
    "Sepang": ("Sepang International Circuit", "Malásia"),
    "Shanghai": ("Shanghai International Circuit", "China"),
    "Silverstone": ("Silverstone Circuit", "Reino Unido"),
    "Sochi": ("Sochi Autodrom", "Rússia"),
    "Spa": ("Circuit de Spa-Francorchamps", "Bélgica"),
    "Spielberg": ("Red Bull Ring", "Áustria"),
    "Suzuka": ("Suzuka International Racing Course", "Japão"),
    "YasMarina": ("Yas Marina Circuit", "Emirados Árabes Unidos"),
    "Zandvoort": ("Circuit Zandvoort", "Holanda"),
}


def importar_pasta(caminho_pasta):
    criar_banco()

    arquivos_csv = [f for f in os.listdir(caminho_pasta) if f.lower().endswith(".csv")]
    print(f"Encontrados {len(arquivos_csv)} arquivos .csv em {caminho_pasta}")

    importadas = 0
    falhas = []

    for arquivo in arquivos_csv:
        nome_base = arquivo.replace(".csv", "")
        caminho_completo = os.path.join(caminho_pasta, arquivo)

        try:
            with open(caminho_completo, "r", encoding="utf-8") as f:
                conteudo = f.read()

            pontos = ler_coordenadas_csv(conteudo)
            caminho_svg, extensao_km = converter_para_svg_path(pontos)

            nome_exibicao, pais = INFO_PISTAS.get(nome_base, (nome_base, "Desconhecido"))

            tempo_pit_stop = round(random.uniform(18.0, 26.0), 1)
            inserir_pista_real(nome_exibicao, pais, extensao_km, caminho_svg, 460, 320, tempo_pit_stop)
            print(f"  OK: {nome_exibicao} ({pais}) - {extensao_km}km")
            importadas += 1

        except Exception as erro:
            falhas.append((arquivo, str(erro)))
            print(f"  FALHOU: {arquivo} - {erro}")

    print()
    print(f"Importadas: {importadas}/{len(arquivos_csv)}")
    if falhas:
        print("Falhas:", falhas)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python importar_todas_pistas.py <caminho_da_pasta_tracks>")
        sys.exit(1)

    importar_pasta(sys.argv[1])
