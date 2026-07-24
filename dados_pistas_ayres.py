# -*- coding: utf-8 -*-
"""
dados_pistas_ayres.py
=====================================================================
Dados canonicos das pistas extraidos da Planilha Ayres (v5.12).
Fonte oficial do projeto Open Wheel Strategy (ver regras.md, secao 8).

Cada entrada tem:
  - cambio    : letra ideal de cambio (A-J)
  - suspensao : letra ideal de suspensao (A-J)
  - boxes_seg : tempo de entrada/saida de boxes (segundos)
  - infl      : dict de influencias {M, C, S, P, G, E}
                (F/freio omitido de proposito - freio e DLC futuro, regra 2.3)
  - tam_km    : extensao da pista em km (referencia da planilha)
  - voltas    : numero de voltas de referencia da planilha

IMPORTANTE - INFLUENCIAS:
  Os valores aqui sao os REAIS da planilha (range 5-15).
  Isso DIVERGE da regra 8.2/8.4 que definia range 7-15.
  O script de populacao permite escolher: usar 5-15 real OU clampar em 7-15.
=====================================================================
"""

# Chave = nome canonico Ayres (usado tambem pra matching)
PISTAS_AYRES = {
    "A1-Ring, Austria":              {"cambio": "A", "suspensao": "B", "boxes_seg": 14, "infl": {"M": 9,  "C": 8,  "S": 7,  "P": 11, "G": 12, "E": 14}, "tam_km": 307.100, "voltas": 71},
    "Sakhir, Bahrein":               {"cambio": "I", "suspensao": "F", "boxes_seg": 12, "infl": {"M": 12, "C": 14, "S": 11, "P": 9,  "G": 7,  "E": 10}, "tam_km": 304.484, "voltas": 57},
    "Aida, Japao":                   {"cambio": "B", "suspensao": "F", "boxes_seg": 11, "infl": {"M": 11, "C": 13, "S": 9,  "P": 12, "G": 7,  "E": 8},  "tam_km": 277.700, "voltas": 75},
    "Barcelona, Espanha":            {"cambio": "D", "suspensao": "H", "boxes_seg": 14, "infl": {"M": 9,  "C": 10, "S": 12, "P": 9,  "G": 10, "E": 11}, "tam_km": 307.300, "voltas": 65},
    "Bathurst, Australia":           {"cambio": "G", "suspensao": "A", "boxes_seg": 11, "infl": {"M": 9,  "C": 8,  "S": 13, "P": 14, "G": 10, "E": 7},  "tam_km": 310.600, "voltas": 50},
    "Brands Hatch, Gran Bretanha":   {"cambio": "F", "suspensao": "H", "boxes_seg": 17, "infl": {"M": 6,  "C": 9,  "S": 12, "P": 13, "G": 11, "E": 10}, "tam_km": 315.500, "voltas": 75},
    "Brno, Republica Tcheca":        {"cambio": "C", "suspensao": "F", "boxes_seg": 14, "infl": {"M": 7,  "C": 11, "S": 9,  "P": 7,  "G": 13, "E": 14}, "tam_km": 307.100, "voltas": 57},
    "Buenos Aires, Argentina":       {"cambio": "J", "suspensao": "I", "boxes_seg": 13, "infl": {"M": 13, "C": 9,  "S": 11, "P": 7,  "G": 11, "E": 9},  "tam_km": 306.600, "voltas": 72},
    "Detroit, Estados Unidos":       {"cambio": "A", "suspensao": "B", "boxes_seg": 10, "infl": {"M": 8,  "C": 6,  "S": 9,  "P": 15, "G": 12, "E": 10}, "tam_km": 253.400, "voltas": 63},
    "Dijon, Franca":                 {"cambio": "E", "suspensao": "H", "boxes_seg": 17, "infl": {"M": 11, "C": 9,  "S": 8,  "P": 14, "G": 6,  "E": 12}, "tam_km": 307.000, "voltas": 79},
    "Donington, Gran Bretanha":      {"cambio": "A", "suspensao": "D", "boxes_seg": 12, "infl": {"M": 7,  "C": 9,  "S": 13, "P": 8,  "G": 14, "E": 10}, "tam_km": 305.700, "voltas": 76},
    "Estoril, Portugal":             {"cambio": "H", "suspensao": "I", "boxes_seg": 15, "infl": {"M": 11, "C": 8,  "S": 12, "P": 8,  "G": 13, "E": 9},  "tam_km": 305.200, "voltas": 70},
    "Hockenheim, Alemanha":          {"cambio": "B", "suspensao": "F", "boxes_seg": 11, "infl": {"M": 13, "C": 8,  "S": 10, "P": 13, "G": 8,  "E": 9},  "tam_km": 307.100, "voltas": 45},
    "Hungaroring, Hungria":          {"cambio": "I", "suspensao": "I", "boxes_seg": 11, "infl": {"M": 12, "C": 14, "S": 6,  "P": 13, "G": 8,  "E": 8},  "tam_km": 305.500, "voltas": 77},
    "Indianapolis, Estados Unidos":  {"cambio": "D", "suspensao": "C", "boxes_seg": 17, "infl": {"M": 8,  "C": 8,  "S": 8,  "P": 15, "G": 12, "E": 10}, "tam_km": 306.600, "voltas": 73},
    "Interlagos, Brasil":            {"cambio": "B", "suspensao": "E", "boxes_seg": 12, "infl": {"M": 11, "C": 13, "S": 11, "P": 11, "G": 6,  "E": 8},  "tam_km": 305.900, "voltas": 71},
    "Jacarepagua, Brasil":           {"cambio": "E", "suspensao": "B", "boxes_seg": 11, "infl": {"M": 11, "C": 10, "S": 7,  "P": 10, "G": 9,  "E": 11}, "tam_km": 306.900, "voltas": 61},
    "Jerez, Espanha":                {"cambio": "J", "suspensao": "A", "boxes_seg": 12, "infl": {"M": 9,  "C": 11, "S": 15, "P": 11, "G": 8,  "E": 7},  "tam_km": 306.400, "voltas": 69},
    "Kyalami, Africa do Sul":        {"cambio": "G", "suspensao": "F", "boxes_seg": 10, "infl": {"M": 14, "C": 8,  "S": 8,  "P": 10, "G": 13, "E": 8},  "tam_km": 306.800, "voltas": 72},
    "Long Beach, Estados Unidos":    {"cambio": "F", "suspensao": "A", "boxes_seg": 14, "infl": {"M": 7,  "C": 11, "S": 11, "P": 14, "G": 9,  "E": 9},  "tam_km": 258.700, "voltas": 79},
    "Magny Cours, Franca":           {"cambio": "C", "suspensao": "B", "boxes_seg": 12, "infl": {"M": 12, "C": 6,  "S": 12, "P": 8,  "G": 13, "E": 9},  "tam_km": 305.800, "voltas": 72},
    "Melbourne, Australia":          {"cambio": "A", "suspensao": "H", "boxes_seg": 11, "infl": {"M": 10, "C": 7,  "S": 7,  "P": 14, "G": 12, "E": 11}, "tam_km": 307.600, "voltas": 58},
    "Monte Carlo, Monaco":           {"cambio": "E", "suspensao": "G", "boxes_seg": 12, "infl": {"M": 6,  "C": 9,  "S": 8,  "P": 13, "G": 15, "E": 10}, "tam_km": 262.800, "voltas": 78},
    "Montreal, Canada":              {"cambio": "B", "suspensao": "D", "boxes_seg": 11, "infl": {"M": 12, "C": 10, "S": 7,  "P": 8,  "G": 12, "E": 12}, "tam_km": 305.000, "voltas": 69},
    "Monza, Italia":                 {"cambio": "A", "suspensao": "B", "boxes_seg": 17, "infl": {"M": 14, "C": 14, "S": 8,  "P": 11, "G": 6,  "E": 8},  "tam_km": 306.700, "voltas": 53},
    "Nogaro, Franca":                {"cambio": "A", "suspensao": "E", "boxes_seg": 13, "infl": {"M": 13, "C": 11, "S": 14, "P": 9,  "G": 7,  "E": 7},  "tam_km": 287.100, "voltas": 79},
    "Nurburgring, Europa":           {"cambio": "F", "suspensao": "F", "boxes_seg": 11, "infl": {"M": 12, "C": 14, "S": 6,  "P": 6,  "G": 9,  "E": 14}, "tam_km": 305.200, "voltas": 67},
    "Oesterreichring, Austria":      {"cambio": "G", "suspensao": "C", "boxes_seg": 14, "infl": {"M": 7,  "C": 7,  "S": 14, "P": 12, "G": 12, "E": 10}, "tam_km": 308.900, "voltas": 52},
    "Paul Ricard, Franca":           {"cambio": "C", "suspensao": "G", "boxes_seg": 13, "infl": {"M": 11, "C": 12, "S": 6,  "P": 12, "G": 9,  "E": 11}, "tam_km": 305.000, "voltas": 79},
    "Phoenix, Estados Unidos":       {"cambio": "B", "suspensao": "B", "boxes_seg": 13, "infl": {"M": 14, "C": 12, "S": 6,  "P": 6,  "G": 13, "E": 11}, "tam_km": 293.900, "voltas": 79},
    "Ruapuna, Nova Zelandia":        {"cambio": "C", "suspensao": "E", "boxes_seg": 17, "infl": {"M": 6,  "C": 14, "S": 13, "P": 7,  "G": 8,  "E": 12}, "tam_km": 280.400, "voltas": 78},
    "San Marino, Imola":             {"cambio": "H", "suspensao": "D", "boxes_seg": 8,  "infl": {"M": 11, "C": 9,  "S": 10, "P": 8,  "G": 11, "E": 11}, "tam_km": 305.600, "voltas": 62},
    "Sepang, Malasia":               {"cambio": "H", "suspensao": "A", "boxes_seg": 16, "infl": {"M": 9,  "C": 6,  "S": 15, "P": 10, "G": 11, "E": 10}, "tam_km": 310.400, "voltas": 55},
    "Silverstone, Gran Bretanha":    {"cambio": "F", "suspensao": "C", "boxes_seg": 15, "infl": {"M": 10, "C": 10, "S": 9,  "P": 9,  "G": 7,  "E": 15}, "tam_km": 308.300, "voltas": 60},
    "Spa, Belgica":                  {"cambio": "E", "suspensao": "G", "boxes_seg": 9,  "infl": {"M": 6,  "C": 7,  "S": 13, "P": 14, "G": 11, "E": 9},  "tam_km": 306.600, "voltas": 44},
    "Suzuka, Japao":                 {"cambio": "J", "suspensao": "A", "boxes_seg": 10, "infl": {"M": 11, "C": 14, "S": 10, "P": 8,  "G": 11, "E": 7},  "tam_km": 301.600, "voltas": 53},
    "Tacna, Peru":                   {"cambio": "I", "suspensao": "I", "boxes_seg": 18, "infl": {"M": 10, "C": 13, "S": 10, "P": 8,  "G": 13, "E": 7},  "tam_km": 264.500, "voltas": 79},
    "Fuji Speedway, Japao":          {"cambio": "G", "suspensao": "H", "boxes_seg": 13, "infl": {"M": 13, "C": 12, "S": 5,  "P": 10, "G": 7,  "E": 8},  "tam_km": 314.847, "voltas": 69},
    "Interlagos 89, Brasil":         {"cambio": "E", "suspensao": "E", "boxes_seg": 12, "infl": {"M": 13, "C": 15, "S": 9,  "P": 11, "G": 7,  "E": 5},  "tam_km": 500.672, "voltas": 64},
    "Shangai, China":                {"cambio": "H", "suspensao": "B", "boxes_seg": 9,  "infl": {"M": 15, "C": 7,  "S": 11, "P": 8,  "G": 6,  "E": 5},  "tam_km": 305.256, "voltas": 56},
    "Indianapolis Oval, Estados Unidos": {"cambio": "I", "suspensao": "A", "boxes_seg": 9, "infl": {"M": 11, "C": 12, "S": 13, "P": 8,  "G": 9,  "E": 8},  "tam_km": 800.000, "voltas": 200},
    "Istanbul, Turquia":             {"cambio": "H", "suspensao": "C", "boxes_seg": 13, "infl": {"M": 13, "C": 11, "S": 7,  "P": 10, "G": 9,  "E": 8},  "tam_km": 304.095, "voltas": 57},
    "Tallinn, Estonia":              {"cambio": "G", "suspensao": "G", "boxes_seg": 12, "infl": {"M": 9,  "C": 9,  "S": 7,  "P": 10, "G": 13, "E": 13}, "tam_km": 309.600, "voltas": 52},
    "Virtasalmi, Finlandia":         {"cambio": "H", "suspensao": "C", "boxes_seg": 11, "infl": {"M": 7,  "C": 11, "S": 7,  "P": 14, "G": 10, "E": 12}, "tam_km": 276.500, "voltas": 79},
    "Zandvoort, Holanda":            {"cambio": "F", "suspensao": "E", "boxes_seg": 15, "infl": {"M": 9,  "C": 12, "S": 12, "P": 6,  "G": 8,  "E": 14}, "tam_km": 301.800, "voltas": 71},
    "Zeltweg, Austria":              {"cambio": "B", "suspensao": "B", "boxes_seg": 19, "infl": {"M": 10, "C": 11, "S": 13, "P": 9,  "G": 9,  "E": 8},  "tam_km": 252.800, "voltas": 79},
    "Adelaide, Australia":           {"cambio": "C", "suspensao": "D", "boxes_seg": 13, "infl": {"M": 7,  "C": 8,  "S": 14, "P": 11, "G": 9,  "E": 11}, "tam_km": 298.600, "voltas": 79},
    "Porto 58, Portugal":            {"cambio": "I", "suspensao": "H", "boxes_seg": 8,  "infl": {"M": 15, "C": 13, "S": 8,  "P": 10, "G": 9,  "E": 11}, "tam_km": 407.385, "voltas": 55},
}


# ---------------------------------------------------------------------------
# ALIASES: liga o nome que esta no SEU banco (pistas TUMFTM) -> chave Ayres.
# So inclui as que tem correspondencia. As nao listadas ficam SEM dado
# canonico e entram na "logica a definir" (ver regras.md secao 8.3).
# ---------------------------------------------------------------------------
ALIASES = {
    "albert park circuit":            "Melbourne, Australia",
    "autodromo nazionale monza":      "Monza, Italia",
    "autodromo jose carlos pace":     "Interlagos, Brasil",
    "interlagos":                     "Interlagos, Brasil",
    "bahrain international circuit":   "Sakhir, Bahrein",
    "brands hatch":                   "Brands Hatch, Gran Bretanha",
    "circuit gilles villeneuve":      "Montreal, Canada",
    "circuit zandvoort":              "Zandvoort, Holanda",
    "circuit de barcelona-catalunya": "Barcelona, Espanha",
    "circuit de spa-francorchamps":   "Spa, Belgica",
    "hockenheimring":                 "Hockenheim, Alemanha",
    "hungaroring":                    "Hungaroring, Hungria",
    "indianapolis motor speedway":    "Indianapolis, Estados Unidos",
    "nurburgring":                    "Nurburgring, Europa",
    "red bull ring":                  "A1-Ring, Austria",
    "sepang international circuit":    "Sepang, Malasia",
    "suzuka circuit":                 "Suzuka, Japao",
    "suzuka":                         "Suzuka, Japao",
    "silverstone circuit":            "Silverstone, Gran Bretanha",
    "silverstone":                    "Silverstone, Gran Bretanha",
    "autodromo enzo e dino ferrari":  "San Marino, Imola",
    "imola":                          "San Marino, Imola",
    "circuit de monaco":              "Monte Carlo, Monaco",
    "circuit gilles-villeneuve":      "Montreal, Canada",
    "fuji speedway":                  "Fuji Speedway, Japao",
    "shanghai international circuit":  "Shangai, China",
    "istanbul park":                  "Istanbul, Turquia",
}
