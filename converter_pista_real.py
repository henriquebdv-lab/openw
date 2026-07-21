"""
Converte o CSV de coordenadas reais (formato do TUMFTM racetrack-database:
x_m, y_m, w_tr_right_m, w_tr_left_m) num traçado SVG, escalado e centralizado
pra caber num viewBox do jogo.
"""

import csv
import io


def ler_coordenadas_csv(conteudo_csv):
    """
    conteudo_csv: string com o conteúdo bruto do arquivo .csv
    Retorna lista de tuplas (x, y) em metros.
    """
    linhas = conteudo_csv.strip().splitlines()

    # O arquivo pode ter um cabeçalho tipo "# x_m,y_m,w_tr_right_m,w_tr_left_m" - ignora comentários
    linhas_dados = [linha for linha in linhas if linha.strip() and not linha.strip().startswith("#")]

    pontos = []
    leitor = csv.reader(linhas_dados)
    for linha in leitor:
        if len(linha) < 2:
            continue
        try:
            x = float(linha[0])
            y = float(linha[1])
            pontos.append((x, y))
        except ValueError:
            continue  # pula linha de cabeçalho textual, se houver

    return pontos


def converter_para_svg_path(pontos, largura_viewbox=460, altura_viewbox=320, margem=25):
    """
    Recebe os pontos em metros (coordenadas reais) e devolve:
    - o atributo 'd' de um <path> SVG, escalado e centralizado
    - a extensão da pista em km (perímetro aproximado, somando as distâncias entre pontos)
    """
    if len(pontos) < 3:
        raise ValueError("Poucos pontos pra formar um traçado")

    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    largura_real = x_max - x_min
    altura_real = y_max - y_min

    area_disponivel_largura = largura_viewbox - 2 * margem
    area_disponivel_altura = altura_viewbox - 2 * margem

    escala = min(area_disponivel_largura / largura_real, area_disponivel_altura / altura_real)

    largura_final = largura_real * escala
    altura_final = altura_real * escala
    offset_x = margem + (area_disponivel_largura - largura_final) / 2
    offset_y = margem + (area_disponivel_altura - altura_final) / 2

    def transformar(ponto):
        x, y = ponto
        px = offset_x + (x - x_min) * escala
        # inverte Y porque coordenada de mapa cresce pra cima, SVG cresce pra baixo
        py = offset_y + (altura_real - (y - y_min)) * escala
        return px, py

    pontos_svg = [transformar(p) for p in pontos]

    comandos = [f"M {pontos_svg[0][0]:.2f} {pontos_svg[0][1]:.2f}"]
    for px, py in pontos_svg[1:]:
        comandos.append(f"L {px:.2f} {py:.2f}")
    comandos.append("Z")

    caminho_svg = " ".join(comandos)

    # extensão aproximada: soma das distâncias reais entre pontos consecutivos (em metros -> km)
    extensao_m = 0.0
    for i in range(len(pontos) - 1):
        x1, y1 = pontos[i]
        x2, y2 = pontos[i + 1]
        extensao_m += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    # fecha o loop
    x1, y1 = pontos[-1]
    x2, y2 = pontos[0]
    extensao_m += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    extensao_km = round(extensao_m / 1000, 3)

    return caminho_svg, extensao_km


def gerar_svg_completo(caminho_svg, largura_viewbox, altura_viewbox, nome_pista=""):
    return f'''<svg viewBox="0 0 {largura_viewbox} {altura_viewbox}" xmlns="http://www.w3.org/2000/svg">
    <rect width="{largura_viewbox}" height="{altura_viewbox}" fill="#eef7ee"/>
    <path d="{caminho_svg}" fill="none" stroke="#2b2b2b" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="{caminho_svg}" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-dasharray="5,5"/>
</svg>'''
