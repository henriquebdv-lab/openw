"""
Banco de dados SEPARADO só pra pistas reais (dado de referência estático,
baseado no OpenStreetMap via TUMFTM racetrack-database, licença LGPL-3.0).

Fica num arquivo .db diferente do jogo.db principal, sem se misturar com
os dados dinâmicos do jogo (usuários, equipes, resultados).
"""

import sqlite3
import os

CAMINHO_BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pistas_reais.db")
FONTE_PADRAO = "OpenStreetMap, via TUMFTM racetrack-database (licença LGPL-3.0)"


def obter_conexao():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    conexao = obter_conexao()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS pistas_reais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            pais TEXT NOT NULL,
            extensao_km REAL NOT NULL,
            caminho_svg TEXT NOT NULL,
            largura_viewbox INTEGER NOT NULL,
            altura_viewbox INTEGER NOT NULL,
            tempo_pit_stop_segundos REAL NOT NULL DEFAULT 20.0,
            categoria_cambio_ideal TEXT DEFAULT 'A',
            categoria_suspensao_ideal TEXT DEFAULT 'A',
            influencia_motor INTEGER DEFAULT 10,
            influencia_cambio INTEGER DEFAULT 10,
            influencia_suspensao INTEGER DEFAULT 10,
            influencia_pneu INTEGER DEFAULT 10,
            influencia_combustivel INTEGER DEFAULT 10,
            influencia_engenheiro INTEGER DEFAULT 10,
            temperatura_ambiente REAL DEFAULT 20.0,
            temperatura_trecho_1 REAL DEFAULT 20.0,
            temperatura_trecho_2 REAL DEFAULT 20.0,
            temperatura_trecho_3 REAL DEFAULT 20.0,
            temperatura_trecho_4 REAL DEFAULT 20.0,
            fonte TEXT DEFAULT '""" + FONTE_PADRAO + """'
        )
    """)

    # Compat: em bancos antigos, adiciona colunas novas via ALTER TABLE.
    # Cada ALTER ignora o erro se a coluna já existir.
    for coluna, definicao in [
        ("tempo_pit_stop_segundos", "REAL NOT NULL DEFAULT 20.0"),
        ("categoria_cambio_ideal", "TEXT DEFAULT 'A'"),
        ("categoria_suspensao_ideal", "TEXT DEFAULT 'A'"),
        ("influencia_motor", "INTEGER DEFAULT 10"),
        ("influencia_cambio", "INTEGER DEFAULT 10"),
        ("influencia_suspensao", "INTEGER DEFAULT 10"),
        ("influencia_pneu", "INTEGER DEFAULT 10"),
        ("influencia_combustivel", "INTEGER DEFAULT 10"),
        ("influencia_engenheiro", "INTEGER DEFAULT 10"),
        ("temperatura_ambiente", "REAL DEFAULT 20.0"),
        ("temperatura_trecho_1", "REAL DEFAULT 20.0"),
        ("temperatura_trecho_2", "REAL DEFAULT 20.0"),
        ("temperatura_trecho_3", "REAL DEFAULT 20.0"),
        ("temperatura_trecho_4", "REAL DEFAULT 20.0"),
    ]:
        try:
            conexao.execute(f"ALTER TABLE pistas_reais ADD COLUMN {coluna} {definicao}")
        except sqlite3.OperationalError:
            pass

    # Migração de dado: se as colunas de categoria estão com 2 letras
    # tipo "AB" (formato antigo), separa em 1 letra cada:
    #   - categoria_cambio_ideal recebe a 1ª letra (câmbio)
    #   - categoria_suspensao_ideal recebe a 2ª letra (suspensão)
    try:
        conexao.execute("""
            UPDATE pistas_reais
            SET categoria_suspensao_ideal = substr(categoria_cambio_ideal, 2, 1),
                categoria_cambio_ideal = substr(categoria_cambio_ideal, 1, 1)
            WHERE length(categoria_cambio_ideal) = 2
        """)
    except sqlite3.OperationalError:
        pass

    # Migração: se as 4 temperaturas de trecho estão no default (20) e
    # temperatura_ambiente foi customizada, copia pra todos os 4 trechos
    # (assim quem já editou a temp_ambiente antes não perde o valor).
    try:
        conexao.execute("""
            UPDATE pistas_reais
            SET temperatura_trecho_1 = temperatura_ambiente,
                temperatura_trecho_2 = temperatura_ambiente,
                temperatura_trecho_3 = temperatura_ambiente,
                temperatura_trecho_4 = temperatura_ambiente
            WHERE temperatura_trecho_1 = 20.0
              AND temperatura_trecho_2 = 20.0
              AND temperatura_trecho_3 = 20.0
              AND temperatura_trecho_4 = 20.0
              AND temperatura_ambiente != 20.0
        """)
    except sqlite3.OperationalError:
        pass

    conexao.commit()
    conexao.close()


def inserir_pista_real(nome, pais, extensao_km, caminho_svg, largura_viewbox, altura_viewbox,
                       tempo_pit_stop_segundos=20.0,
                       categoria_cambio_ideal="A", categoria_suspensao_ideal="B",
                       influencia_motor=10, influencia_cambio=10, influencia_suspensao=10,
                       influencia_pneu=10, influencia_combustivel=10, influencia_engenheiro=10,
                       temperatura_ambiente=20.0,
                       temperatura_trecho_1=None, temperatura_trecho_2=None,
                       temperatura_trecho_3=None, temperatura_trecho_4=None):
    # Se não passou temperatura por trecho, usa a temperatura_ambiente pros 4
    t1 = temperatura_trecho_1 if temperatura_trecho_1 is not None else temperatura_ambiente
    t2 = temperatura_trecho_2 if temperatura_trecho_2 is not None else temperatura_ambiente
    t3 = temperatura_trecho_3 if temperatura_trecho_3 is not None else temperatura_ambiente
    t4 = temperatura_trecho_4 if temperatura_trecho_4 is not None else temperatura_ambiente

    conexao = obter_conexao()
    conexao.execute(
        """INSERT INTO pistas_reais (
            nome, pais, extensao_km, caminho_svg, largura_viewbox, altura_viewbox,
            tempo_pit_stop_segundos, categoria_cambio_ideal, categoria_suspensao_ideal,
            influencia_motor, influencia_cambio, influencia_suspensao,
            influencia_pneu, influencia_combustivel, influencia_engenheiro,
            temperatura_ambiente,
            temperatura_trecho_1, temperatura_trecho_2, temperatura_trecho_3, temperatura_trecho_4
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (nome, pais, extensao_km, caminho_svg, largura_viewbox, altura_viewbox,
         tempo_pit_stop_segundos, categoria_cambio_ideal, categoria_suspensao_ideal,
         influencia_motor, influencia_cambio, influencia_suspensao,
         influencia_pneu, influencia_combustivel, influencia_engenheiro,
         temperatura_ambiente, t1, t2, t3, t4),
    )
    conexao.commit()
    conexao.close()


def atualizar_pista_real(pista_id, **campos):
    """Atualiza campos específicos de uma pista (usado pela tela admin)."""
    campos_permitidos = {
        "tempo_pit_stop_segundos", "categoria_cambio_ideal", "categoria_suspensao_ideal",
        "influencia_motor", "influencia_cambio", "influencia_suspensao",
        "influencia_pneu", "influencia_combustivel", "influencia_engenheiro",
        "temperatura_ambiente",
        "temperatura_trecho_1", "temperatura_trecho_2",
        "temperatura_trecho_3", "temperatura_trecho_4",
    }
    campos_validos = {k: v for k, v in campos.items() if k in campos_permitidos}
    if not campos_validos:
        return

    conexao = obter_conexao()
    partes_set = ", ".join(f"{k} = ?" for k in campos_validos.keys())
    valores = list(campos_validos.values()) + [pista_id]
    conexao.execute(f"UPDATE pistas_reais SET {partes_set} WHERE id = ?", valores)
    conexao.commit()
    conexao.close()


def calcular_numero_voltas(extensao_km, distancia_minima_km=290, distancia_maxima_km=320, maximo_voltas=79):
    """
    Calcula quantas voltas fazem a distância total da corrida ficar entre
    290km e 320km, respeitando o máximo de 79 voltas. Pistas muito curtas
    podem não conseguir chegar em 290km sem passar de 79 voltas - nesse
    caso, usa o máximo de voltas mesmo ficando abaixo da faixa ideal.
    """
    distancia_alvo = (distancia_minima_km + distancia_maxima_km) / 2
    voltas = max(1, min(round(distancia_alvo / extensao_km), maximo_voltas))
    distancia_total = voltas * extensao_km
    tentativas = 0
    while not (distancia_minima_km <= distancia_total <= distancia_maxima_km) and tentativas < 30:
        if distancia_total < distancia_minima_km and voltas < maximo_voltas:
            voltas += 1
        elif distancia_total > distancia_maxima_km and voltas > 1:
            voltas -= 1
        else:
            break
        distancia_total = voltas * extensao_km
        tentativas += 1
    return voltas, round(distancia_total, 2)


def listar_pistas_reais():
    conexao = obter_conexao()
    linhas = conexao.execute("SELECT * FROM pistas_reais ORDER BY nome").fetchall()
    conexao.close()
    return [dict(linha) for linha in linhas]


def obter_pista_real(pista_id):
    conexao = obter_conexao()
    linha = conexao.execute("SELECT * FROM pistas_reais WHERE id = ?", (pista_id,)).fetchone()
    conexao.close()
    return dict(linha) if linha else None
