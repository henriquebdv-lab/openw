"""
Gera 30 fornecedores por categoria, organizados em Níveis de 1 a 30.

Regras do balanceamento:
- Jogador começa com R$ 55.000 (configurável em admin_configuracoes)
- 30 Fornecedores. O Nível (1 a 30) reflete poder e é VISÍVEL.
- Preço cresce suave e linearmente por nível.
- O nome expõe apenas a Marca e o Preço. A indicação de #1 a #100 foi removida.
- O "achado" e a "furada" continuam existindo (variação pequena em preço/performance
  dentro do mesmo tier/nível para criar o componente de sorte/leitura).
"""

import random

from models import (
    db, FornecedorMotor, FornecedorCombustivel, FornecedorPneu,
    FornecedorChassi, FornecedorCambio, FornecedorSuspensao,
    FornecedorFreio, FornecedorEngenheiro,
)

NUMERO_NIVEIS = 30

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

PREFIXOS_FREIO = ["Stop", "Brake", "Carbon", "Grip", "Halt"]
SUFIXOS_FREIO = ["Pads", "Systems", "Caliper", "Force"]

NOMES_PESSOA = ["Ricardo", "Marcos", "Felipe", "André", "Bruno", "Carlos",
                "Diego", "Eduardo", "Gabriel", "Henrique", "Igor", "Lucas",
                "Mateus", "Rafael", "Thiago", "Vitor"]
SOBRENOMES_PESSOA = ["Silva", "Santos", "Oliveira", "Souza", "Costa", "Pereira",
                     "Ferreira", "Almeida", "Ribeiro", "Martins", "Carvalho",
                     "Rocha", "Dias", "Mendes", "Freitas"]


def gerar_nome_item(prefixos, sufixos):
    return f"{random.choice(prefixos)}{random.choice(sufixos)}"


def gerar_nome_pessoa():
    return f"{random.choice(NOMES_PESSOA)} {random.choice(SOBRENOMES_PESSOA)}"


# ---------------------------------------------------------
# Faixas de custo por nível (R$ - custo_temporada anual)
# Crescimento linear do Nível 1 ao 30
# ---------------------------------------------------------
FAIXAS_CUSTO_TEMPORADA = {
    "motor":       (8_000,   200_000),
    "combustivel": (4_000,   100_000),
    "pneu":        (5_000,   130_000),
    "chassi":      (3_000,    80_000),
    "cambio":      (5_000,   130_000),
    "suspensao":   (5_000,   130_000),
    "freio":       (4_000,   100_000),
    "engenheiro": (15_000,   400_000),
}


def custo_temporada_do_nivel(categoria, nivel):
    """Cresce de maneira estritamente linear do nível 1 ao 30."""
    minimo, maximo = FAIXAS_CUSTO_TEMPORADA[categoria]
    fator = (nivel - 1) / (NUMERO_NIVEIS - 1)
    valor = minimo + (maximo - minimo) * fator
    return round(valor / 1000) * 1000


def custo_montagem_do_temporada(custo_temporada):
    return round(custo_temporada * random.uniform(0.08, 0.12) / 100) * 100


def _sortear_classificacao():
    """60% normal, 20% achado, 20% furada"""
    return random.choices(["normal", "achado", "furada"], weights=[6, 2, 2])[0]


def _aplicar_classificacao(classificacao, custo_base, performance_base):
    if classificacao == "furada":
        multiplicador = random.uniform(0.70, 0.85)
        custo = custo_base * random.uniform(0.95, 1.05)
    elif classificacao == "achado":
        multiplicador = random.uniform(1.10, 1.25)
        custo = custo_base * random.uniform(0.85, 0.95)
    else:
        multiplicador = random.uniform(0.95, 1.05)
        custo = custo_base * random.uniform(0.98, 1.02)
    return custo, performance_base * multiplicador, multiplicador


def gerar_motores(quantidade=NUMERO_NIVEIS):
    motores = []
    for nivel in range(1, NUMERO_NIVEIS + 1):
        custo_base = custo_temporada_do_nivel("motor", nivel)
        potencia_base = 0.1 * nivel
        eficiencia_base = 0.015 * nivel
        
        cls = _sortear_classificacao()
        custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
        custo_final = max(1000, round(custo / 100) * 100)
        
        motores.append(FornecedorMotor(
            nome=gerar_nome_item(PREFIXOS_MOTOR, SUFIXOS_MOTOR),
            nivel=nivel,
            custo_temporada=custo_final,
            custo_montagem=custo_montagem_do_temporada(custo_final),
            potencia=round(potencia_base * mult, 2),
            eficiencia_combustivel=round(eficiencia_base * mult, 3),
            ativo=True,
        ))
    return motores


def gerar_combustiveis(quantidade=NUMERO_NIVEIS):
    combustiveis = []
    for nivel in range(1, NUMERO_NIVEIS + 1):
        custo_base = custo_temporada_do_nivel("combustivel", nivel)
        ef_base = 0.01 * nivel
        aumento_base = 0.008 * nivel
        
        cls = _sortear_classificacao()
        custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
        custo_final = max(1000, round(custo / 100) * 100)
        
        combustiveis.append(FornecedorCombustivel(
            nome=gerar_nome_item(PREFIXOS_COMBUSTIVEL, SUFIXOS_COMBUSTIVEL),
            nivel=nivel,
            custo_temporada=custo_final,
            custo_montagem=custo_montagem_do_temporada(custo_final),
            eficiencia=round(ef_base * mult, 3),
            aumento_potencia_motor=round(aumento_base * mult, 3),
            ativo=True,
        ))
    return combustiveis


def gerar_pneus(quantidade=NUMERO_NIVEIS):
    pneus = []
    for nivel in range(1, NUMERO_NIVEIS + 1):
        custo_base = custo_temporada_do_nivel("pneu", nivel)
        performance_base = 0.08 * nivel
        desgaste_base = 3.0 - (0.07 * nivel)
        
        cls = _sortear_classificacao()
        custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
        custo_final = max(1000, round(custo / 100) * 100)
        
        pneus.append(FornecedorPneu(
            nome=gerar_nome_item(PREFIXOS_PNEU, SUFIXOS_PNEU),
            nivel=nivel,
            custo_temporada=custo_final,
            custo_montagem=custo_montagem_do_temporada(custo_final),
            performance=round(performance_base * mult, 2),
            desgaste=round(max(0.8, desgaste_base / max(0.5, mult)), 2),
            ativo=True,
            categoria_chuva="seco",
        ))
    return pneus


def gerar_chassis(quantidade=NUMERO_NIVEIS):
    chassis = []
    for nivel in range(1, NUMERO_NIVEIS + 1):
        custo_base = custo_temporada_do_nivel("chassi", nivel)
        performance_base = 0.06 * nivel
        
        cls = _sortear_classificacao()
        custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
        custo_final = max(1000, round(custo / 100) * 100)
        
        chassis.append(FornecedorChassi(
            nome=gerar_nome_item(PREFIXOS_CHASSI, SUFIXOS_CHASSI),
            nivel=nivel,
            custo_temporada=custo_final,
            custo_montagem=custo_montagem_do_temporada(custo_final),
            performance=round(performance_base * mult, 2),
            ativo=True,
        ))
    return chassis


def _gerar_categoria_pista(quantidade, categoria_key, prefixos, sufixos, Model, performance_scale):
    LETRAS = list("ABCDEFGHIJ")
    itens = []
    for nivel in range(1, NUMERO_NIVEIS + 1):
        custo_base = custo_temporada_do_nivel(categoria_key, nivel)
        performance_base = performance_scale * nivel
        
        cls = _sortear_classificacao()
        custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
        custo_final = max(1000, round(custo / 100) * 100)
        
        itens.append(Model(
            nome=gerar_nome_item(prefixos, sufixos),
            nivel=nivel,
            custo_temporada=custo_final,
            custo_montagem=custo_montagem_do_temporada(custo_final),
            performance=round(performance_base * mult, 2),
            ativo=True,
            categoria_pista=random.choice(LETRAS),
        ))
    return itens


def gerar_cambios(quantidade=NUMERO_NIVEIS):
    return _gerar_categoria_pista(quantidade, "cambio", PREFIXOS_CAMBIO, SUFIXOS_CAMBIO,
                                  FornecedorCambio, performance_scale=0.05)


def gerar_suspensoes(quantidade=NUMERO_NIVEIS):
    return _gerar_categoria_pista(quantidade, "suspensao", PREFIXOS_SUSPENSAO, SUFIXOS_SUSPENSAO,
                                  FornecedorSuspensao, performance_scale=0.05)


def gerar_freios(quantidade=NUMERO_NIVEIS):
    freios = []
    for nivel in range(1, NUMERO_NIVEIS + 1):
        custo_base = custo_temporada_do_nivel("freio", nivel)
        performance_base = 0.05 * nivel
        
        cls = _sortear_classificacao()
        custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
        custo_final = max(1000, round(custo / 100) * 100)
        
        freios.append(FornecedorFreio(
            nome=gerar_nome_item(PREFIXOS_FREIO, SUFIXOS_FREIO),
            nivel=nivel,
            custo_temporada=custo_final,
            custo_montagem=custo_montagem_do_temporada(custo_final),
            performance=round(performance_base * mult, 2),
            ativo=True,
        ))
    return freios


def gerar_engenheiros(quantidade=NUMERO_NIVEIS):
    engenheiros = []
    for nivel in range(1, NUMERO_NIVEIS + 1):
        custo_base = custo_temporada_do_nivel("engenheiro", nivel)
        eficiencia_base = 0.013 * nivel
        
        cls = _sortear_classificacao()
        custo, _, mult = _aplicar_classificacao(cls, custo_base, 1.0)
        custo_final = max(1000, round(custo / 100) * 100)
        
        engenheiros.append(FornecedorEngenheiro(
            nome=gerar_nome_pessoa(),
            nivel=nivel,
            custo_temporada=custo_final,
            custo_montagem=custo_montagem_do_temporada(custo_final),
            eficiencia_exata=round(eficiencia_base * mult, 4),
            ativo=True,
        ))
    return engenheiros


# ---------------------------------------------------------
# Popular banco
# ---------------------------------------------------------
MAPA_FK_EQUIPE = [
    (FornecedorMotor,        "motor_fornecedor_id"),
    (FornecedorCombustivel,  "combustivel_fornecedor_id"),
    (FornecedorPneu,         "pneu_fornecedor_id"),
    (FornecedorChassi,       "chassi_fornecedor_id"),
    (FornecedorCambio,       "cambio_fornecedor_id"),
    (FornecedorSuspensao,    "suspensao_fornecedor_id"),
    (FornecedorFreio,        "freio_fornecedor_id"),
    (FornecedorEngenheiro,   "engenheiro_fornecedor_id"),
]

GERADORES = {
    FornecedorMotor:        gerar_motores,
    FornecedorCombustivel:  gerar_combustiveis,
    FornecedorPneu:         gerar_pneus,
    FornecedorChassi:       gerar_chassis,
    FornecedorCambio:       gerar_cambios,
    FornecedorSuspensao:    gerar_suspensoes,
    FornecedorFreio:        gerar_freios,
    FornecedorEngenheiro:   gerar_engenheiros,
}

def _ids_em_uso(Model, campo_fk):
    from models import CarroJogador
    ids = set()
    for equipe in CarroJogador.query.all():
        valor = getattr(equipe, campo_fk, None)
        if valor:
            ids.add(valor)
    return ids

def popular_banco(quantidade=NUMERO_NIVEIS, limpar_antes=True):
    for Model, campo_fk in MAPA_FK_EQUIPE:
        if limpar_antes:
            ids_protegidos = _ids_em_uso(Model, campo_fk)
            for antigo in Model.query.all():
                if antigo.id in ids_protegidos:
                    antigo.ativo = False
                else:
                    db.session.delete(antigo)
            db.session.flush()

        gerador = GERADORES[Model]
        for novo in gerador(quantidade):
            db.session.add(novo)

    db.session.commit()

if __name__ == "__main__":
    from app import app
    with app.app_context():
        popular_banco()
        print("Fornecedores populados com sucesso: 30 níveis por categoria.")