# -*- coding: utf-8 -*-
"""
popular_categorias_pistas.py
=====================================================================
Popula categorias ideais (cambio/suspensao), tempo de boxes e
influencias das pistas do Open Wheel Strategy com os dados canonicos
da Planilha Ayres (ver dados_pistas_ayres.py).

CORRIGE O BUG: hoje todas as pistas aparecem "cambio A / susp. B"
porque as categorias ideais nunca foram populadas (ficaram no default).

Schema conhecido do banco (tabela 'pistas_reais'):
  id, nome, pais, extensao_km, caminho_svg, largura_viewbox,
  altura_viewbox, fonte, tempo_pit_stop_segundos,
  categoria_cambio_ideal, categoria_suspensao_ideal,
  influencia_motor, influencia_cambio, influencia_suspensao,
  influencia_pneu, influencia_combustivel, influencia_engenheiro,
  temperatura_ambiente, temperatura_trecho_1..4

COMO USAR (Windows, na pasta do projeto, com o .venv ativo):
  1) python popular_categorias_pistas.py            <- SIMULACAO (nao grava)
  2) confira o relatorio
  3) python popular_categorias_pistas.py --apply     <- grava de verdade

OPCOES:
  --apply         grava no banco
  --db CAMINHO    caminho do banco (default: procura pistas_reais.db)
  --clamp         clampa influencias no range 7-15 (regra do "dia 7")
                  SEM --clamp usa os valores REAIS da Ayres (5-15) <- recomendado
  --espelhadas    tambem popula versoes espelhadas (troca cambio<->susp
                  e influencia C<->S) - ver regra 8.1.1
=====================================================================
"""

import argparse
import os
import re
import sqlite3
import sys
import unicodedata

try:
    from dados_pistas_ayres import PISTAS_AYRES, ALIASES
except ImportError:
    print("ERRO: coloque o arquivo dados_pistas_ayres.py na mesma pasta.")
    sys.exit(1)


# --- Nomes de coluna do banco (schema conhecido) --------------------------
TABELA = "pistas_reais"
COL_NOME = "nome"
COL_CAMBIO = "categoria_cambio_ideal"
COL_SUSP = "categoria_suspensao_ideal"
COL_BOXES = "tempo_pit_stop_segundos"
COL_INFL = {
    "M": "influencia_motor",
    "C": "influencia_cambio",
    "S": "influencia_suspensao",
    "P": "influencia_pneu",
    "G": "influencia_combustivel",
    "E": "influencia_engenheiro",
}

# Marcas que identificam uma pista espelhada pelo nome
MARCAS_ESPELHO = ["espelh", "reverso", "invert", "mirror", "reverse"]


# --- Normalizacao de nomes pra matching -----------------------------------
_RUIDO = [
    "circuit", "circuito", "autodromo", "autodrome", "international",
    "speedway", "motorsport", "arena", "grand prix", "gp", "raceway",
    "internacional",
]


def normalizar(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    for r in _RUIDO:
        s = re.sub(r"\b" + re.escape(r) + r"\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


_ALIAS_NORM = {normalizar(k): v for k, v in ALIASES.items()}
_AYRES_NORM = {normalizar(k): k for k in PISTAS_AYRES.keys()}


def achar_ayres(nome_banco: str):
    n = normalizar(nome_banco)
    if not n:
        return None
    if n in _ALIAS_NORM:
        return _ALIAS_NORM[n]
    if n in _AYRES_NORM:
        return _AYRES_NORM[n]
    for norm_key, chave in _AYRES_NORM.items():
        if norm_key and (norm_key in n or n in norm_key):
            return chave
    for norm_alias, chave in _ALIAS_NORM.items():
        if norm_alias and (norm_alias in n or n in norm_alias):
            return chave
    return None


def clamp715(v: int) -> int:
    return max(7, min(15, v))


def achar_banco(caminho_cli):
    if caminho_cli and os.path.exists(caminho_cli):
        return caminho_cli
    candidatos = [
        "pistas_reais.db",
        os.path.join("instance", "pistas_reais.db"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    for raiz, _, arqs in os.walk("."):
        for a in arqs:
            if a.endswith(".db") and "pista" in a.lower():
                return os.path.join(raiz, a)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="grava no banco")
    ap.add_argument("--db", default=None, help="caminho do banco")
    ap.add_argument("--clamp", action="store_true", help="clampa influencias 7-15")
    ap.add_argument("--espelhadas", action="store_true", help="popula espelhadas")
    args = ap.parse_args()

    db = achar_banco(args.db)
    if not db:
        print("ERRO: nao achei o banco. Use --db CAMINHO.")
        sys.exit(1)
    print(f"[i] Banco: {db}")
    print(f"[i] Tabela: {TABELA}")
    print(f"[i] Modo influencias: {'CLAMP 7-15' if args.clamp else 'REAL Ayres 5-15'}")
    print(f"[i] Espelhadas: {'SIM' if args.espelhadas else 'nao'}")
    print()

    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute(f"SELECT id, {COL_NOME} FROM {TABELA}")
    linhas = cur.fetchall()

    casadas, sem_match, updates = [], [], []

    for pid, nome in linhas:
        base_nome = nome or ""
        eh_espelhada = any(m in normalizar(base_nome) for m in MARCAS_ESPELHO)

        chave = achar_ayres(base_nome)
        if eh_espelhada and not chave:
            # tenta achar removendo a marca de espelho do nome
            limpo = normalizar(base_nome)
            for m in MARCAS_ESPELHO:
                limpo = limpo.replace(m, " ")
            chave = achar_ayres(limpo)

        if not chave:
            sem_match.append(nome)
            continue
        if eh_espelhada and not args.espelhadas:
            continue

        d = PISTAS_AYRES[chave]
        cambio, susp = d["cambio"], d["suspensao"]
        infl = dict(d["infl"])

        if eh_espelhada:
            cambio, susp = susp, cambio                    # troca letra (8.1.1)
            infl["C"], infl["S"] = infl["S"], infl["C"]    # troca influencia C<->S

        if args.clamp:
            infl = {k: clamp715(v) for k, v in infl.items()}

        sets = [f"{COL_CAMBIO}=?", f"{COL_SUSP}=?", f"{COL_BOXES}=?"]
        vals = [cambio, susp, d["boxes_seg"]]
        for letra, col in COL_INFL.items():
            sets.append(f"{col}=?")
            vals.append(infl[letra])
        vals.append(pid)

        updates.append((f"UPDATE {TABELA} SET {', '.join(sets)} WHERE id=?", vals))
        casadas.append((nome, chave, cambio, susp, d["boxes_seg"], infl,
                        "ESPELHADA" if eh_espelhada else ""))

    # --- Relatorio ---
    print("=" * 78)
    print(f"CASADAS COM DADO CANONICO ({len(casadas)}):")
    print("=" * 78)
    for nome, chave, cambio, susp, boxes, infl, tag in casadas:
        infl_str = " ".join(f"{k}{v}" for k, v in infl.items())
        print(f"  {(nome or '')[:34]:34} -> {chave[:20]:20} "
              f"Cam {cambio} Sus {susp} Box {boxes:>2}s | {infl_str} {tag}")

    print()
    print("=" * 78)
    print(f"SEM CORRESPONDENCIA ({len(sem_match)}) - precisam de logica manual:")
    print("=" * 78)
    for nome in sem_match:
        print(f"  - {nome}")

    print()
    if args.apply:
        for sql, vals in updates:
            cur.execute(sql, vals)
        con.commit()
        print(f"[OK] {len(updates)} pistas atualizadas e GRAVADAS no banco.")
    else:
        print(f"[SIMULACAO] {len(updates)} pistas SERIAM atualizadas.")
        print("           Rode de novo com --apply pra gravar de verdade.")
    con.close()


if __name__ == "__main__":
    main()
