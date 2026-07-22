"""
Progressão do desenvolvimento (chassi/aero) e do treinamento de boxes.

- Desenvolvimento é feito pelo Engenheiro contratado.
- Cada peça (chassi e aero) tem seu próprio percentual "em construção"
  que sobe até 100%.
- O que sobe durante a temporada só passa a valer NA PRÓXIMA temporada.
- Treinamento de boxes tem efeito imediato (a partir da próxima corrida).
"""

from datetime import datetime, timedelta


def calcular_custo_proximo_avanco(percentual_atual, custo_base, custo_fator):
    """Custo em R$ do próximo passo de desenvolvimento/treinamento."""
    incremento_atual = int(percentual_atual // 5)
    return custo_base * (custo_fator ** incremento_atual)


def calcular_tempo_proximo_avanco_horas(percentual_atual, tempo_base, tempo_fator):
    """Tempo em horas até o próximo passo ficar pronto."""
    incremento_atual = int(percentual_atual // 5)
    return tempo_base + (tempo_fator * incremento_atual / 20.0)


def verificar_conclusao(registro, incremento_percentual, alvo_atributo="percentual"):
    """Se o horário de conclusão passou, aplica o incremento no atributo alvo."""
    if not getattr(registro, "em_progresso", False):
        return False
    horario_conclusao = getattr(registro, "horario_conclusao", None)
    if not horario_conclusao:
        return False
    if datetime.utcnow() < horario_conclusao:
        return False
    # Aplica incremento
    valor_atual = float(getattr(registro, alvo_atributo, 0) or 0)
    novo_valor = min(100.0, valor_atual + incremento_percentual)
    setattr(registro, alvo_atributo, novo_valor)
    registro.em_progresso = False
    registro.inicio_em = None
    registro.horario_conclusao = None
    from models import db
    db.session.commit()
    return True


def avancar(registro, equipe, custo_base, custo_fator, tempo_base, tempo_fator,
            incremento_percentual, alvo_atributo="percentual"):
    """Inicia o próximo passo de desenvolvimento/treinamento.
    Retorna (sucesso, mensagem)."""
    from models import db

    valor_atual = float(getattr(registro, alvo_atributo, 0) or 0)

    if getattr(registro, "em_progresso", False):
        return False, "Já existe um trabalho em progresso."
    if valor_atual >= 100.0:
        return False, "Já está em 100%."

    custo = calcular_custo_proximo_avanco(valor_atual, custo_base, custo_fator)
    if float(equipe.orcamento or 0) < custo:
        return False, f"Saldo insuficiente. Custo: R$ {custo:,.2f}"

    tempo_horas = calcular_tempo_proximo_avanco_horas(valor_atual, tempo_base, tempo_fator)

    equipe.orcamento = float(equipe.orcamento or 0) - custo
    registro.em_progresso = True
    registro.inicio_em = datetime.utcnow()
    registro.horario_conclusao = datetime.utcnow() + timedelta(hours=tempo_horas)
    db.session.commit()

    return True, f"Iniciado! Conclui em {tempo_horas:.1f}h. Custo: R$ {custo:,.2f}"


# ---------------------------------------------------------
# FIM DE TEMPORADA — aplica chassi/aero em construção
# ---------------------------------------------------------
def aplicar_desenvolvimento_da_temporada(desenvolvimento, engenheiro_atual):
    """Chamado quando a temporada termina. Aplica no carro do jogador
    o chassi e aero que ele desenvolveu durante a temporada.

    Regra:
    - Se chassi_em_construcao == 100 E aero_em_construcao == 100 E
      tem engenheiro contratado → aplica ambos.
    - Se qualquer um falhar, jogador não participa da próxima temporada.

    Retorna dict com o status da aplicação.
    """
    from models import db

    tem_engenheiro = engenheiro_atual is not None
    chassi_ok = (desenvolvimento.chassi_percentual_em_construcao or 0) >= 100.0
    aero_ok = (desenvolvimento.aero_percentual_em_construcao or 0) >= 100.0

    if not (tem_engenheiro and chassi_ok and aero_ok):
        return {
            "aplicado": False,
            "motivo_falha": {
                "sem_engenheiro": not tem_engenheiro,
                "chassi_incompleto": not chassi_ok,
                "aero_incompleto": not aero_ok,
            },
        }

    # Aplica: o que estava em construção vira o aplicado
    desenvolvimento.chassi_percentual_aplicado = 100.0
    desenvolvimento.aero_percentual_aplicado = 100.0
    desenvolvimento.chassi_percentual_em_construcao = 0.0
    desenvolvimento.aero_percentual_em_construcao = 0.0
    desenvolvimento.nivel_engenheiro_projetista = engenheiro_atual.nivel or 1

    db.session.commit()

    return {
        "aplicado": True,
        "novo_nivel": desenvolvimento.nivel_engenheiro_projetista,
    }
