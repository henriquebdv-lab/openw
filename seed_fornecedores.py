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

Numeração dos nomes (IMPORTANTE):
- O número no nome (#1 a #100) reflete APENAS o CUSTO, do mais barato
  (#1) ao mais caro (#100).
- Ele NÃO indica qualidade. As "furadas" e "achados" continuam
  embaralhadas de propósito, então um #10 barato pode render mais que
  um #60 caro. É essa a graça de escolher no escuro.
- A numeração é aplicada DEPOIS de ordenar cada categoria por custo.
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


def gerar_nome_item(prefixos, sufixos):
    """Nome base do item, SEM número. O número é colocado depois,
    quando a lista já estiver ordenada por custo."""
    return f"{random.choice(prefixos)}{random.choice(sufixos)}"


def gerar_nome_pessoa():
    """Nome base da pessoa (engenheiro), SEM número."""
    return f"{random.choice(NOMES_PESSOA)} {random.choice(SOBRENOMES_PESSOA)}"


def _renumerar_por_custo(lista):
    """Recebe uma lista de fornecedores JÁ ORDENADA por custo_temporada
    e escreve o número no nome: #1 no mais barato, #N no mais caro.

    O número reflete só o custo, não a qualidade. As furadas/achados
    continuam embaralhadas de propósito."""
    for posicao, item in enumerate(lista, start=1):
        item.nome = f"{item.nome} #{posicao}"
    return lista


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
# - 2 "furada": custo próximo do topo do tier, performance BAIXA (pega ruim)
# - 2 "achado": custo próximo do fundo do tier, performance ALTA (jogador feliz)
# - 6 "normal": custo e performance médios pro tier

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

def gerar_motores(quantidade=QUANTIDADE_PADRAO):
    """10 tiers de 10 motores. Potência escala com tier."""
    motores = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier("motor", tier)
        potencia_base = 0.3 * tier              # tier 1 = 0.3, tier 10 = 3.0
        eficiencia_base = 0.05 * tier           # tier 1 = 0.05, tier 10 = 0.50
        for slot in range(FORNECEDORES_POR_TIER):
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            custo_final = max(1000, round(custo / 100) * 100)
            motores.append(FornecedorMotor(
                nome=gerar_nome_item(PREFIXOS_MOTOR, SUFIXOS_MOTOR),
                custo_temporada=custo_final,
                custo_montagem=custo_montagem_do_temporada(custo_final),
                potencia=round(potencia_base * mult, 2),
                eficiencia_combustivel=round(eficiencia_base * mult, 3),
                ativo=True,
            ))
    # Ordena por custo e numera #1 (mais barato) -> #100 (mais caro)
    motores.sort(key=lambda m: m.custo_temporada)
    motores = motores[:quantidade]
    return _renumerar_por_custo(motores)


def gerar_combustiveis(quantidade=QUANTIDADE_PADRAO):
    combustiveis = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier("combustivel", tier)
        ef_base = 0.03 * tier
        aumento_base = 0.025 * tier
        for slot in range(FORNECEDORES_POR_TIER):
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            custo_final = max(1000, round(custo / 100) * 100)
            combustiveis.append(FornecedorCombustivel(
                nome=gerar_nome_item(PREFIXOS_COMBUSTIVEL, SUFIXOS_COMBUSTIVEL),
                custo_temporada=custo_final,
                custo_montagem=custo_montagem_do_temporada(custo_final),
                eficiencia=round(ef_base * mult, 3),
                aumento_potencia_motor=round(aumento_base * mult, 3),
                ativo=True,
            ))
    combustiveis.sort(key=lambda c: c.custo_temporada)
    combustiveis = combustiveis[:quantidade]
    return _renumerar_por_custo(combustiveis)


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
        categorias_chuva = CATEGORIAS_CHUVA_DISTRIB.copy()
        random.shuffle(categorias_chuva)
        for slot in range(FORNECEDORES_POR_TIER):
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            custo_final = max(1000, round(custo / 100) * 100)
            pneus.append(FornecedorPneu(
                nome=gerar_nome_item(PREFIXOS_PNEU, SUFIXOS_PNEU),
                custo_temporada=custo_final,
                custo_montagem=custo_montagem_do_temporada(custo_final),
                performance=round(performance_base * mult, 2),
                desgaste=round(max(0.8, desgaste_base / max(0.5, mult)), 2),
                ativo=True,
                categoria_chuva=categorias_chuva[slot],
            ))
    pneus.sort(key=lambda p: p.custo_temporada)
    pneus = pneus[:quantidade]
    return _renumerar_por_custo(pneus)


def gerar_chassis(quantidade=QUANTIDADE_PADRAO):
    chassis = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier("chassi", tier)
        performance_base = 0.2 * tier
        for slot in range(FORNECEDORES_POR_TIER):
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            custo_final = max(1000, round(custo / 100) * 100)
            chassis.append(FornecedorChassi(
                nome=gerar_nome_item(PREFIXOS_CHASSI, SUFIXOS_CHASSI),
                custo_temporada=custo_final,
                custo_montagem=custo_montagem_do_temporada(custo_final),
                performance=round(performance_base * mult, 2),
                ativo=True,
            ))
    chassis.sort(key=lambda c: c.custo_temporada)
    chassis = chassis[:quantidade]
    return _renumerar_por_custo(chassis)


def _gerar_categoria_pista(quantidade, categoria_key, prefixos, sufixos, Model, performance_scale):
    """Câmbio e suspensão: cada tier tem 1 fornecedor de cada letra A-J."""
    LETRAS = list("ABCDEFGHIJ")   # 10 letras, uma por slot
    itens = []
    for tier in range(1, NUMERO_TIERS + 1):
        custo_base = custo_temporada_do_tier(categoria_key, tier)
        performance_base = performance_scale * tier
        letras_embaralhadas = LETRAS.copy()
        random.shuffle(letras_embaralhadas)
        for slot in range(FORNECEDORES_POR_TIER):
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            custo_final = max(1000, round(custo / 100) * 100)
            itens.append(Model(
                nome=gerar_nome_item(prefixos, sufixos),
                custo_temporada=custo_final,
                custo_montagem=custo_montagem_do_temporada(custo_final),
                performance=round(performance_base * mult, 2),
                ativo=True,
                categoria_pista=letras_embaralhadas[slot],
            ))
    itens.sort(key=lambda x: x.custo_temporada)
    itens = itens[:quantidade]
    return _renumerar_por_custo(itens)


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
        for slot in range(FORNECEDORES_POR_TIER):
            classificacoes = CLASSIFICACOES_POR_TIER.copy()
            random.shuffle(classificacoes)
            cls = classificacoes[slot]
            custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
            custo_final = max(1000, round(custo / 100) * 100)
            engenheiros.append(FornecedorEngenheiro(
                nome=gerar_nome_pessoa(),
                custo_temporada=custo_final,
                custo_montagem=custo_montagem_do_temporada(custo_final),
                nivel=tier,   # nível visível ao jogador = tier
                eficiencia_exata=round(eficiencia_base * mult, 4),
                ativo=True,
            ))
    engenheiros.sort(key=lambda e: e.custo_temporada)
    engenheiros = engenheiros[:quantidade]
    return _renumerar_por_custo(engenheiros)


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

# Liga cada Model à sua função geradora
GERADORES = {
    FornecedorMotor:        gerar_motores,
    FornecedorCombustivel:  gerar_combustiveis,
    FornecedorPneu:         gerar_pneus,
    FornecedorChassi:       gerar_chassis,
    FornecedorCambio:       gerar_cambios,
    FornecedorSuspensao:    gerar_suspensoes,
    FornecedorEngenheiro:   gerar_engenheiros,
}


def _ids_em_uso(Model, campo_fk):
    """Retorna o conjunto de IDs de fornecedores deste Model que estão
    sendo usados por alguma equipe (pra nunca apagá-los)."""
    from models import CarroJogador
    ids = set()
    for equipe in CarroJogador.query.all():
        valor = getattr(equipe, campo_fk, None)
        if valor:
            ids.add(valor)
    return ids


def popular_banco(quantidade=QUANTIDADE_PADRAO, limpar_antes=True):
    """
    Gera fornecedores fictícios respeitando a regra "nunca apagar dado real":
    - Fornecedores NÃO usados por nenhum jogador são deletados.
    - Fornecedores em uso são desativados (ativo=False), então não aparecem
      pra novos jogadores, mas os jogadores atuais continuam funcionando.
    - Depois insere quantidade fornecedores novos e ativos.
    """
    for Model, campo_fk in MAPA_FK_EQUIPE:
        if limpar_antes:
            ids_protegidos = _ids_em_uso(Model, campo_fk)
            for antigo in Model.query.all():
                if antigo.id in ids_protegidos:
                    # Em uso: apenas desativa, não deleta
                    antigo.ativo = False
                else:
                    # Não usado: pode deletar
                    db.session.delete(antigo)
            db.session.flush()

        # Gera e insere os novos fornecedores ativos
        gerador = GERADORES[Model]
        for novo in gerador(quantidade):
            db.session.add(novo)

    db.session.commit()


if __name__ == "__main__":
    # Permite rodar direto: python seed_fornecedores.py (dentro do contexto do app)
    from app import app
    with app.app_context():
        popular_banco()
        print("Fornecedores populados com sucesso: 100 por categoria, "
              "numerados #1 (mais barato) a #100 (mais caro).")
