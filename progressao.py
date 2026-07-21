"""
Lógica compartilhada dos sistemas de progresso 0-100% (Desenvolvimento
de chassi/aero e Treinamento de box) - os dois funcionam do mesmo jeito:
clica pra avançar, paga um custo, espera um tempo, percentual sobe.
"""

from datetime import datetime, timedelta

from models import db


def calcular_custo_proximo_avanco(percentual_atual, custo_base, custo_fator):
    return round(custo_base * (1 + (percentual_atual / 100) * custo_fator), 2)


def calcular_tempo_proximo_avanco_horas(percentual_atual, tempo_base_horas, tempo_fator_horas):
    return round(tempo_base_horas + (percentual_atual / 100) * tempo_fator_horas, 2)


def verificar_conclusao(registro, incremento_percentual):
    """Se o tempo de espera já passou, aplica o avanço automaticamente."""
    if registro.em_progresso and registro.horario_conclusao and datetime.utcnow() >= registro.horario_conclusao:
        registro.percentual = min(100.0, registro.percentual + incremento_percentual)
        registro.em_progresso = False
        registro.inicio_em = None
        registro.horario_conclusao = None
        db.session.commit()


def avancar(registro, equipe, custo_base, custo_fator, tempo_base_horas, tempo_fator_horas, incremento_percentual):
    """
    Tenta iniciar o próximo avanço. Retorna (sucesso: bool, mensagem: str).
    """
    verificar_conclusao(registro, incremento_percentual)

    if registro.em_progresso:
        return False, "Ainda em andamento - espera terminar pra avançar de novo."

    if registro.percentual >= 100:
        return False, "Já está em 100%, não tem mais o que avançar."

    custo = calcular_custo_proximo_avanco(registro.percentual, custo_base, custo_fator)

    if equipe.orcamento < custo:
        return False, f"Orçamento insuficiente - precisa de {custo:,.0f}, você tem {equipe.orcamento:,.0f}."

    tempo_horas = calcular_tempo_proximo_avanco_horas(registro.percentual, tempo_base_horas, tempo_fator_horas)

    equipe.orcamento -= custo
    registro.em_progresso = True
    registro.inicio_em = datetime.utcnow()
    registro.horario_conclusao = datetime.utcnow() + timedelta(hours=tempo_horas)
    db.session.commit()

    return True, f"Avançando +{incremento_percentual}%! Custou {custo:,.0f}, pronto em {tempo_horas:.1f}h."
