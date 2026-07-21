"""
Gera 100 fornecedores por categoria, organizados em 10 tiers de 10.

Regras do balanceamento (baseado no manual "Guia do Iniciante"):
- Jogador começa com R$ 55.000 (configurável em admin_configuracoes)
- Precisa pagar 5 contratos anuais (motor, combustível, pneu, câmbio,
  suspensão) e ainda sobrar dinheiro pra montagem da 1ª corrida
- Faixas do Tier 1 pensadas pra 5 contratos tier 1 caberem em R$ 27.000
  aproximadamente, sobrando ~28k pra montagem

Estrutura de cada tier (10 fornecedores):
- 10 categorias (A-J pra câmbio/suspensão, ou 10 opções pra motor etc)
- Dentro do tier, ~2 "furadas" (parecem baratas mas performance ruim),
  ~2 "achados" (bom custo-benefício), e ~6 "normais". Performance é
  ESCONDIDA do jogador - só admin vê.

Nomes:
- Numeração cresce com qualidade: #1 é o pior/mais barato de todos,
  #100 é o melhor/mais caro. Ordem no select bate com ordem de qualidade.
"""

import random

from models import (
    db, FornecedorMotor, FornecedorCombustivel, FornecedorPneu,
    FornecedorChassi, FornecedorCambio, FornecedorSuspensao,
    FornecedorEngenheiro,
)

QUANTIDADE_PADRAO = 100
FORNECEDORES_POR_TIER = 10
NUMERO_TIERS = 10

# Prefixos/sufixos pra nomes fictícios
PREFIXOS_MOTOR = ["Turbo", "Power", "Apex", "Vortex", "Blaze"]
SUFIXOS_MOTOR = ["Dynamics", "Racing", "Motors", "Systems", "Engineering"]

PREFIXOS_COMBUSTIVEL = ["Race", "Eco", "Max", "Pure", "Ultra"]
SUFIXOS_COMBUSTIVEL = ["Fuel", "Gas", "Energy", "Petro", "Blend"]

PREFIXOS_PNEU = ["Grip", "Track", "Speed", "Vector", "Ace"]
SUFIXOS_PNEU = ["Tire", "Tread", "Rubber", "Traction"]

PREFIXOS_CHASSI = ["Aero", "Carbon", "Light", "Rigid", "Nano"]
SUFIXOS_CHASSI = ["Chassis", "Frame", "Structures", "Build"]

PREFIXOS_CAMBIO = ["Shift", "Quick", "Rapid", "Smooth", "Sync"]
SUFIXOS_CAMBIO = ["Trans", "Box", "Drive", "Gears"]

PREFIXOS_SUSPENSAO = ["Stable", "Firm", "Adaptive", "Balance", "Active"]
SUFIXOS_SUSPENSAO = ["Susp", "Ride", "Dampers", "Control"]

NOMES_PESSOA = ["Ricardo", "Marcos", "Felipe", "André", "Bruno", "Carlos",
                "Diego", "Eduardo", "Gabriel", "Henrique", "Igor", "Lucas",
                "Mateus", "Rafael", "Thiago", "Vitor"]
SOBRENOMES_PESSOA = ["Silva", "Santos", "Oliveira", "Souza", "Costa", "Pereira",
                     "Ferreira", "Almeida", "Ribeiro", "Martins", "Carvalho",
                     "Rocha", "Dias", "Mendes", "Freitas"]


def gerar_nome_item(prefixos, sufixos, indice_global):
    """Nome com número global (1-100), que também é a ordem de qualidade."""
    return f"{random.choice(prefixos)}{random.choice(sufixos)} #{indice_global}"


def gerar_nome_pessoa(indice_global):
    return f"{random.choice(NOMES_PESSOA)} {random.choice(SOBRENOMES_PESSOA)} #{indice_global}"


# ---------------------------------------------------------
# Faixas de custo por tier (R$ - custo_temporada anual)
# ---------------------------------------------------------
# Cada tupla é (min_tier1, max_tier10). O custo cresce exponencialmente
# entre tiers pra dar sensação de que o topo é "muito melhor" que o meio.

FAIXAS_CUSTO_TEMPORADA = {
    "motor":       (8_000,   200_000),
    "combustivel": (4_000,   100_000),
    "pneu":        (5_000,   130_000),
    "chassi":      (3_000,    80_000),
    "cambio":      (5_000,   130_000),
    "suspensao":   (5_000,   130_000),
    "engenheiro": (15_000,   400_000),
}


def custo_temporada_do_tier(categoria, tier):
    """Cresce exponencialmente do tier 1 ao 10 pra dar sensação de progressão."""
    minimo, maximo = FAIXAS_CUSTO_TEMPORADA[categoria]
    fator = (tier - 1) / (NUMERO_TIERS - 1)   # 0.0 no tier 1, 1.0 no tier 10
    # Curva exponencial: cresce devagar no início e acelera no topo
    valor = minimo * ((maximo / minimo) ** fator)
    return round(valor / 1000) * 1000   # arredonda pra múltiplo de 1000


def custo_montagem_do_temporada(custo_temporada):
    """Montagem por corrida ~= 10% do contrato anual."""
    return round(custo_temporada * random.uniform(0.08, 0.12) / 100) * 100


# ---------------------------------------------------------
# Classificação de itens dentro do tier
# ---------------------------------------------------------
# Cada tier tem 10 fornecedores. Distribuímos assim:
#   - 2 "furada": custo próximo do topo do tier, performance BAIXA (pega ruim)
#   - 2 "achado": custo próximo do fundo do tier, performance ALTA (jogador feliz)
#   - 6 "normal": custo e performance médios pro tier

CLASSIFICACOES_POR_TIER = (
    ["furada"] * 2 + ["achado"] * 2 + ["normal"] * 6
)


def _aplicar_classificacao(classificacao, custo_base, performance_base):
    """Ajusta custo e performance de acordo com classificação.
    Retorna (custo_ajustado, performance_ajustada, multiplicador_perf)."""
    if classificacao == "furada":
        # Custa quase o mesmo, mas rende 60-75%
        multiplicador = random.uniform(0.60, 0.75)
        custo = custo_base * random.uniform(0.95, 1.05)
    elif classificacao == "achado":
        # Custa menos, mas rende 110-125%
        multiplicador = random.uniform(1.10, 1.25)
        custo = custo_base * random.uniform(0.85, 0.95)
    else:
        multiplicador = random.uniform(0.95, 1.05)
        custo = custo_base * random.uniform(0.98, 1.02)
    return custo, performance_base * multiplicador, multiplicador


# ---------------------------------------------------------
# Geração propriamente dita (uma função por categoria)
# ---------------------------------------------------------

def _gerar_categoria_tier(tier, custo_temporada_base, categorias_letra=None, indices_globais=None):
    """Retorna uma lista de dicts com dados brutos pra 10 fornecedores do tier."""
    classificacoes = CLASSIFICACOES_POR_TIER.copy()
    random.shuffle(classificacoes)
    resultado = []
    for i in range(FORNECEDORES_POR_TIER):
        cls = classificacoes[i]
        custo, _, mult_perf = _aplicar_classificacao(cls, custo_temporada_base, 1.0)
        item = {
            "classificacao": cls,
            "custo_temporada": max(1000, round(custo / 100) * 100),
            "mult_perf": mult_perf,
            "letra": categorias_letra[i] if categorias_letra else None,
            "indice_global": indices_globais[i] if indices_globais else None,
        }
        item["custo_montagem"] = custo_montagem_do_temporada(item["custo_temporada"])
        resultado.append(item)
    return resultado


def gerar_motores(quantidade=QUANTIDADE_PADRAO):
    """10 tiers de 10 motores. Potência escala com tier."""
    motores = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier("motor", tier)
        potencia_base = 0.3 * tier              # tier 1 = 0.3, tier 10 = 3.0
        eficiencia_base = 0.05 * tier           # tier 1 = 0.05, tier 10 = 0.50
        indice_inicial = (tier - 1) * FORNECEDORES_POR_TIER + 1
        for slot in range(FORNECEDORES_POR_TIER):
            indice_global = indice_inicial + slot
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            motores.append(FornecedorMotor(
                nome=gerar_nome_item(PREFIXOS_MOTOR, SUFIXOS_MOTOR, indice_global),
                custo_temporada=max(1000, round(custo / 100) * 100),
                custo_montagem=custo_montagem_do_temporada(max(1000, round(custo / 100) * 100)),
                potencia=round(potencia_base * mult, 2),
                eficiencia_combustivel=round(eficiencia_base * mult, 3),
                ativo=True,
            ))
    # Ordena pra que o BD receba em ordem crescente de qualidade/custo
    motores.sort(key=lambda m: m.custo_temporada)
    return motores[:quantidade]


def gerar_combustiveis(quantidade=QUANTIDADE_PADRAO):
    combustiveis = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier("combustivel", tier)
        ef_base = 0.03 * tier
        aumento_base = 0.025 * tier
        indice_inicial = (tier - 1) * FORNECEDORES_POR_TIER + 1
        for slot in range(FORNECEDORES_POR_TIER):
            indice_global = indice_inicial + slot
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            combustiveis.append(FornecedorCombustivel(
                nome=gerar_nome_item(PREFIXOS_COMBUSTIVEL, SUFIXOS_COMBUSTIVEL, indice_global),
                custo_temporada=max(1000, round(custo / 100) * 100),
                custo_montagem=custo_montagem_do_temporada(max(1000, round(custo / 100) * 100)),
                eficiencia=round(ef_base * mult, 3),
                aumento_potencia_motor=round(aumento_base * mult, 3),
                ativo=True,
            ))
    combustiveis.sort(key=lambda c: c.custo_temporada)
    return combustiveis[:quantidade]


def gerar_pneus(quantidade=QUANTIDADE_PADRAO):
    """Pneus com 3 categorias de chuva. Cada tier tem ~4 seco / 3 interm / 3 chuva."""
    CATEGORIAS_CHUVA_DISTRIB = (
        ["seco"] * 4 + ["intermediario"] * 3 + ["chuva"] * 3
    )
    pneus = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier("pneu", tier)
        performance_base = 0.25 * tier
        desgaste_base = 3.0 - (0.22 * tier)   # tier 1 = mais desgaste, tier 10 = menos
        indice_inicial = (tier - 1) * FORNECEDORES_POR_TIER + 1
        categorias_chuva = CATEGORIAS_CHUVA_DISTRIB.copy()
        random.shuffle(categorias_chuva)
        for slot in range(FORNECEDORES_POR_TIER):
            indice_global = indice_inicial + slot
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            pneus.append(FornecedorPneu(
                nome=gerar_nome_item(PREFIXOS_PNEU, SUFIXOS_PNEU, indice_global),
                custo_temporada=max(1000, round(custo / 100) * 100),
                custo_montagem=custo_montagem_do_temporada(max(1000, round(custo / 100) * 100)),
                performance=round(performance_base * mult, 2),
                desgaste=round(max(0.8, desgaste_base / max(0.5, mult)), 2),
                ativo=True,
                categoria_chuva=categorias_chuva[slot],
            ))
    pneus.sort(key=lambda p: p.custo_temporada)
    return pneus[:quantidade]


def gerar_chassis(quantidade=QUANTIDADE_PADRAO):
    chassis = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier("chassi", tier)
        performance_base = 0.2 * tier
        indice_inicial = (tier - 1) * FORNECEDORES_POR_TIER + 1
        for slot in range(FORNECEDORES_POR_TIER):
            indice_global = indice_inicial + slot
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            chassis.append(FornecedorChassi(
                nome=gerar_nome_item(PREFIXOS_CHASSI, SUFIXOS_CHASSI, indice_global),
                custo_temporada=max(1000, round(custo / 100) * 100),
                custo_montagem=custo_montagem_do_temporada(max(1000, round(custo / 100) * 100)),
                performance=round(performance_base * mult, 2),
                ativo=True,
            ))
    chassis.sort(key=lambda c: c.custo_temporada)
    return chassis[:quantidade]


def _gerar_categoria_pista(quantidade, categoria_key, prefixos, sufixos, Model, performance_scale):
    """Câmbio e suspensão: cada tier tem 1 fornecedor de cada letra A-J."""
    LETRAS = list("ABCDEFGHIJ")   # 10 letras, uma por slot
    itens = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier(categoria_key, tier)
        performance_base = performance_scale * tier
        indice_inicial = (tier - 1) * FORNECEDORES_POR_TIER + 1
        letras_embaralhadas = LETRAS.copy()
        random.shuffle(letras_embaralhadas)
        for slot in range(FORNECEDORES_POR_TIER):
            indice_global = indice_inicial + slot
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            itens.append(Model(
                nome=gerar_nome_item(prefixos, sufixos, indice_global),
                custo_temporada=max(1000, round(custo / 100) * 100),
                custo_montagem=custo_montagem_do_temporada(max(1000, round(custo / 100) * 100)),
                performance=round(performance_base * mult, 2),
                ativo=True,
                categoria_pista=letras_embaralhadas[slot],
            ))
    itens.sort(key=lambda x: x.custo_temporada)
    return itens[:quantidade]


def gerar_cambios(quantidade=QUANTIDADE_PADRAO):
    return _gerar_categoria_pista(quantidade, "cambio", PREFIXOS_CAMBIO, SUFIXOS_CAMBIO,
                                   FornecedorCambio, performance_scale=0.15)


def gerar_suspensoes(quantidade=QUANTIDADE_PADRAO):
    return _gerar_categoria_pista(quantidade, "suspensao", PREFIXOS_SUSPENSAO, SUFIXOS_SUSPENSAO,
                                   FornecedorSuspensao, performance_scale=0.15)


def gerar_engenheiros(quantidade=QUANTIDADE_PADRAO):
    """Engenheiros: nível visível 1-10 = tier. Eficiência exata escala com tier."""
    engenheiros = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier("engenheiro", tier)
        eficiencia_base = 0.04 * tier   # tier 1 = 0.04, tier 10 = 0.40
        indice_inicial = (tier - 1) * FORNECEDORES_POR_TIER + 1
        for slot in range(FORNECEDORES_POR_TIER):
            indice_global = indice_inicial + slot
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            engenheiros.append(FornecedorEngenheiro(
                nome=gerar_nome_pessoa(indice_global),
                custo_temporada=max(1000, round(custo / 100) * 100),
                custo_montagem=custo_montagem_do_temporada(max(1000, round(custo / 100) * 100)),
                nivel=tier,   # nível visível ao jogador = tier
                eficiencia_exata=round(eficiencia_base * mult, 4),
                ativo=True,
            ))
    engenheiros.sort(key=lambda e: e.custo_temporada)
    return engenheiros[:quantidade]


# ---------------------------------------------------------
# Popular banco (mantém a lógica de "nunca apaga fornecedor em uso")
# ---------------------------------------------------------

MAPA_FK_EQUIPE = [
    (FornecedorMotor,        "motor_fornecedor_id"),
    (FornecedorCombustivel,  "combustivel_fornecedor_id"),
    (FornecedorPneu,         "pneu_fornecedor_id"),
    (FornecedorChassi,       "chassi_fornecedor_id"),
    (FornecedorCambio,       "cambio_fornecedor_id"),
    (FornecedorSuspensao,    "suspensao_fornecedor_id"),
    (FornecedorEngenheiro,   "engenheiro_fornecedor_id"),
]


def popular_banco(quantidade=QUANTIDADE_PADRAO, limpar_antes=True):
    """
    Gera fornecedores fictícios respeitando a regra "nunca apagar dado real":
    - Fornecedores NÃO usados por nenhum jogador são deletados.
    - Fornecedores em uso são desativados (ativo=False), então não aparecem
      pra novos jogadores, mas os jogadores atuais continuam funcionando.
    - Depois insere `quantidade` fornecedores novos e ativos.
    """
    from models import CarroJogador

    if limpar_antes:
        for Model, nome_coluna_fk in MAPA_FK_EQUIPE:
            coluna_fk = getattr(CarroJogador, nome_coluna_fk)
            ids_em_uso = {
                linha[0]
                for linha in db.session.query(coluna_fk).filter(coluna_fk.isnot(None)).all()
            }
            if ids_em_uso:
                Model.query.filter(~Model.id.in_(ids_em_uso)).delete(synchronize_session=False)
                Model.query.filter(Model.id.in_(ids_em_uso)).update(
                    {"ativo": False}, synchronize_session=False
                )
            else:
                Model.query.delete(synchronize_session=False)
        db.session.commit()

    db.session.bulk_save_objects(gerar_motores(quantidade))
    db.session.bulk_save_objects(gerar_combustiveis(quantidade))
    db.session.bulk_save_objects(gerar_pneus(quantidade))
    db.session.bulk_save_objects(gerar_chassis(quantidade))
    db.session.bulk_save_objects(gerar_cambios(quantidade))
    db.session.bulk_save_objects(gerar_suspensoes(quantidade))
    db.session.bulk_save_objects(gerar_engenheiros(quantidade))
    db.session.commit()
