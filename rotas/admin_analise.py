"""
Rota administrativa para análise gráfica e tabular de componentes.
Expõe as métricas reais (Potência, Consumo, Durabilidade, etc.) ao longo
da curva de modelos 50 a 900.
"""

from flask import render_template, request, jsonify
from models import (
    FornecedorMotor, FornecedorCombustivel, FornecedorPneu, 
    FornecedorCambio, FornecedorSuspensao, FornecedorFreio, 
    FornecedorEngenheiro, FornecedorChassi
)
import modelos_componente

def registrar(app):
    @app.route('/admin/analise')
    def admin_analise():
        # Coleta todos os fornecedores para popular os dropdowns da interface
        categorias = {
            "motor": [{"id": f.id, "nome": f.nome, "nivel": f.nivel} for f in FornecedorMotor.query.order_by(FornecedorMotor.nivel, FornecedorMotor.custo_temporada).all()],
            "pneu": [{"id": f.id, "nome": f.nome, "nivel": f.nivel} for f in FornecedorPneu.query.order_by(FornecedorPneu.nivel, FornecedorPneu.custo_temporada).all()],
            "combustivel": [{"id": f.id, "nome": f.nome, "nivel": f.nivel} for f in FornecedorCombustivel.query.order_by(FornecedorCombustivel.nivel, FornecedorCombustivel.custo_temporada).all()],
            "cambio": [{"id": f.id, "nome": f.nome, "nivel": f.nivel} for f in FornecedorCambio.query.order_by(FornecedorCambio.nivel, FornecedorCambio.custo_temporada).all()],
            "suspensao": [{"id": f.id, "nome": f.nome, "nivel": f.nivel} for f in FornecedorSuspensao.query.order_by(FornecedorSuspensao.nivel, FornecedorSuspensao.custo_temporada).all()],
            "freio": [{"id": f.id, "nome": f.nome, "nivel": f.nivel} for f in FornecedorFreio.query.order_by(FornecedorFreio.nivel, FornecedorFreio.custo_temporada).all()],
            "engenheiro": [{"id": f.id, "nome": f.nome, "nivel": f.nivel} for f in FornecedorEngenheiro.query.order_by(FornecedorEngenheiro.nivel, FornecedorEngenheiro.custo_temporada).all()]
        }
        return render_template('admin_analise.html', categorias=categorias)

    @app.route('/admin/analise/api/dados')
    def admin_analise_dados():
        categoria = request.args.get('categoria', 'motor')
        id1 = request.args.get('id1', type=int)
        id2 = request.args.get('id2', type=int)

        MAPA_MODELS = {
            "motor": FornecedorMotor,
            "pneu": FornecedorPneu,
            "combustivel": FornecedorCombustivel,
            "cambio": FornecedorCambio,
            "suspensao": FornecedorSuspensao,
            "freio": FornecedorFreio,
            "engenheiro": FornecedorEngenheiro
        }

        Model = MAPA_MODELS.get(categoria)
        if not Model:
            return jsonify({"erro": "Categoria inválida"})

        todos = Model.query.all()
        if not todos:
            return jsonify({"erro": "Nenhum fornecedor encontrado nesta categoria"})

        f1 = Model.query.get(id1) if id1 else None
        f2 = Model.query.get(id2) if id2 else None

        estatisticas = gerar_estatisticas_globais(categoria, todos)

        return jsonify({
            "modelos": modelos_componente.MODELOS,
            "estatisticas": estatisticas,
            "fornecedor1": formatar_fornecedor(f1, categoria) if f1 else None,
            "fornecedor2": formatar_fornecedor(f2, categoria) if f2 else None,
        })


def formatar_fornecedor(fornecedor, categoria):
    return {
        "nome": fornecedor.nome,
        "nivel": fornecedor.nivel,
        "curvas": gerar_curvas(fornecedor, categoria)
    }


def gerar_curvas(fornecedor, categoria):
    modelos = modelos_componente.MODELOS
    curvas = {}

    if categoria == "motor":
        potencias = []
        consumos = []
        for m in modelos:
            mod = modelos_componente.modificadores(m, "motor")
            # Potência = base + ganho do modelo
            pot = fornecedor.potencia + mod.get('potencia_delta', 0)
            # Consumo = (1 - eficiencia) * fator_consumo
            cons = (1 - fornecedor.eficiencia_combustivel) * mod.get('fator_consumo', 1.0)
            potencias.append(round(pot, 3))
            consumos.append(round(cons, 3))
        curvas["Potência"] = potencias
        curvas["Consumo"] = consumos

    elif categoria == "pneu":
        performances = []
        desgastes = []
        durabilidades = []
        for m in modelos:
            mod = modelos_componente.modificadores(m, "pneu")
            # Performance real: subtrair delta (pois delta negativo no jogo é = MAIS RÁPIDO).
            # Assim o gráfico sobe para melhor performance.
            perf = fornecedor.performance - mod.get('velocidade_delta_s', 0)
            desg = fornecedor.desgaste * mod.get('fator_desgaste', 1.0)
            durab = (100.0 / desg) if desg > 0 else 0
            
            performances.append(round(perf, 3))
            desgastes.append(round(desg, 3))
            durabilidades.append(round(durab, 2))
        curvas["Durabilidade"] = durabilidades
        curvas["Performance"] = performances
        curvas["Desgaste"] = desgastes

    elif categoria == "combustivel":
        eficiencias = []
        potencias = []
        for m in modelos:
            eficiencias.append(round(fornecedor.eficiencia, 3))
            potencias.append(round(fornecedor.aumento_potencia_motor, 3))
        curvas["Eficiência Base"] = eficiencias
        curvas["Bônus de Potência"] = potencias

    elif categoria == "engenheiro":
        eficiencias = []
        for m in modelos:
            eficiencias.append(round(fornecedor.eficiencia_exata, 4))
        curvas["Eficiência Exata Base"] = eficiencias

    else:
        # Câmbio, Suspensão, Freio - Curva de performance constante
        performances = []
        for m in modelos:
            performances.append(round(fornecedor.performance, 3))
        curvas["Performance Base"] = performances

    return curvas


def gerar_estatisticas_globais(categoria, todos):
    if not todos:
        return {}

    if categoria == "motor":
        maior_pot = max(todos, key=lambda x: x.potencia)
        menor_pot = min(todos, key=lambda x: x.potencia)
        mais_eco = max(todos, key=lambda x: x.eficiencia_combustivel)
        mais_beb = min(todos, key=lambda x: x.eficiencia_combustivel)
        melhor_rel = max(todos, key=lambda x: x.potencia / max(0.001, (1 - x.eficiencia_combustivel)))

        return {
            "Maior Potência Base": f"{maior_pot.nome} ({maior_pot.potencia} HP) - Nível {maior_pot.nivel}",
            "Menor Potência Base": f"{menor_pot.nome} ({menor_pot.potencia} HP) - Nível {menor_pot.nivel}",
            "Fornecedor Mais Econômico (Base)": f"{mais_eco.nome} (Efic. {mais_eco.eficiencia_combustivel}) - Nível {mais_eco.nivel}",
            "Fornecedor Mais Beberrão (Base)": f"{mais_beb.nome} (Efic. {mais_beb.eficiencia_combustivel}) - Nível {mais_beb.nivel}",
            "Melhor Relação Pot/Cons (Base)": f"{melhor_rel.nome} - Nível {melhor_rel.nivel}"
        }

    elif categoria == "pneu":
        maior_perf = max(todos, key=lambda x: x.performance)
        menor_perf = min(todos, key=lambda x: x.performance)
        maior_desg = max(todos, key=lambda x: x.desgaste)
        menor_desg = min(todos, key=lambda x: x.desgaste)

        return {
            "Maior Performance Base": f"{maior_perf.nome} ({maior_perf.performance}) - Nível {maior_perf.nivel}",
            "Menor Performance Base": f"{menor_perf.nome} ({menor_perf.performance}) - Nível {menor_perf.nivel}",
            "Maior Desgaste Base": f"{maior_desg.nome} ({maior_desg.desgaste}) - Nível {maior_desg.nivel}",
            "Menor Desgaste Base (Dura Mais)": f"{menor_desg.nome} ({menor_desg.desgaste}) - Nível {menor_desg.nivel}"
        }

    elif categoria == "combustivel":
        maior_ef = max(todos, key=lambda x: x.eficiencia)
        maior_pot = max(todos, key=lambda x: x.aumento_potencia_motor)
        return {
            "Mais Econômico": f"{maior_ef.nome} ({maior_ef.eficiencia}) - Nível {maior_ef.nivel}",
            "Maior Bônus de Potência": f"{maior_pot.nome} ({maior_pot.aumento_potencia_motor}) - Nível {maior_pot.nivel}"
        }

    else:
        # Categorias Genéricas (Câmbio, Suspensão, etc)
        maior_perf = max(todos, key=lambda x: getattr(x, 'performance', 0))
        menor_perf = min(todos, key=lambda x: getattr(x, 'performance', 0))
        return {
            "Maior Performance Base": f"{maior_perf.nome} ({getattr(maior_perf, 'performance', 0)}) - Nível {maior_perf.nivel}",
            "Menor Performance Base": f"{menor_perf.nome} ({getattr(menor_perf, 'performance', 0)}) - Nível {menor_perf.nivel}"
        }