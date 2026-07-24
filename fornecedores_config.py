"""
Configuração central dos fornecedores (usada nas telas de equipe e admin).

Ficava dentro do app.py; movi pra cá pra que qualquer rota (equipe, admin,
context_processor) importe do mesmo lugar, sem duplicar.

NOTE: FornecedorChassi continua mapeado no admin (LEGADO) mas não aparece
mais no formulário de criar equipe. Fica visível pra admin ver o histórico.
"""
from models import (
    FornecedorMotor, FornecedorCombustivel, FornecedorPneu,
    FornecedorCambio, FornecedorSuspensao, FornecedorEngenheiro,
)

CATEGORIAS_PISTA = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
CATEGORIAS_CHUVA = ["seco", "intermediario", "chuva"]

FORNECEDORES_CONFIG = {
    "motor": {"model": FornecedorMotor, "titulo": "Motor", "campo_equipe": "motor_fornecedor_id",
              "campos": [{"nome": "potencia", "label": "Potência", "tipo": "float"},
                         {"nome": "eficiencia_combustivel", "label": "Eficiência de Combustível", "tipo": "float"}]},
    "combustivel": {"model": FornecedorCombustivel, "titulo": "Combustível", "campo_equipe": "combustivel_fornecedor_id",
                    "campos": [{"nome": "eficiencia", "label": "Eficiência", "tipo": "float"},
                               {"nome": "aumento_potencia_motor", "label": "% Aumento Potência Motor", "tipo": "float"}]},
    "pneu": {"model": FornecedorPneu, "titulo": "Pneu", "campo_equipe": "pneu_fornecedor_id",
             "campos": [{"nome": "performance", "label": "Performance", "tipo": "float"},
                        {"nome": "desgaste", "label": "Desgaste", "tipo": "float"},
                        {"nome": "categoria_chuva", "label": "Faixa de chuva", "tipo": "string"}]},
    "cambio": {"model": FornecedorCambio, "titulo": "Câmbio", "campo_equipe": "cambio_fornecedor_id",
               "campos": [{"nome": "performance", "label": "Performance", "tipo": "float"},
                          {"nome": "categoria_pista", "label": "Categoria (A-J)", "tipo": "string"}]},
    "suspensao": {"model": FornecedorSuspensao, "titulo": "Suspensão", "campo_equipe": "suspensao_fornecedor_id",
                  "campos": [{"nome": "performance", "label": "Performance", "tipo": "float"},
                             {"nome": "categoria_pista", "label": "Categoria (A-J)", "tipo": "string"}]},
    "engenheiro": {"model": FornecedorEngenheiro, "titulo": "Engenheiro", "campo_equipe": "engenheiro_fornecedor_id",
                   "campos": [{"nome": "nivel", "label": "Nível", "tipo": "int"},
                              {"nome": "eficiencia_exata", "label": "Eficiência exata", "tipo": "float"}]},
}
