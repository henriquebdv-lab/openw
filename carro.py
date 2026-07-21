"""
Classe Carro - junta equipe + equipamentos (motor, combustível, pneu,
chassi, câmbio, suspensão) + opcionalmente um engenheiro (pessoa
contratada à parte, pode não existir ainda).

O Engenheiro acumula 2 efeitos: reduz consumo/desgaste (baseado no
Nível) e desenvolve chassi/aerodinâmica (eficiência exata, que já vem
escalada pelo percentual de Desenvolvimento da equipe).

Efeitos vindos do como.txt aplicados aqui:
- Cada pista tem uma "influência" por componente (M/C/S/P/G/E).
  Multiplica o efeito do componente no tempo_base.
- Categoria de câmbio/suspensão do carro deve bater com a categoria
  ideal da pista (1ª letra = câmbio, 2ª letra = suspensão).
- Temperatura da pista afeta desgaste do pneu (20°C = neutro).
- Consumo em litros/km depende do tamanho da volta e das eficiências
  (motor + combustível). Referência: 0.500 L/km.
"""

import random

from constantes import (
    TEMPO_VOLTA_BASE_SEGUNDOS,
    VARIACAO_ALEATORIA_DESVIO_PADRAO,
    CONSUMO_BASE_MOTOR,
    CONSUMO_BASE_LITROS_POR_KM,
    BONUS_DESIGNER_ESCALA,
    PIT_STOP_SEGUNDOS,
    INFLUENCIA_ESCALA,
    TEMPERATURA_REFERENCIA,
    DESGASTE_POR_GRAU_FRACAO,
)


class Carro:
    def __init__(self, equipe, motor, combustivel, pneu, chassi, cambio, suspensao,
                 engenheiro=None, combustivel_carregado=110.0, tempo_pit_stop=None):
        self.equipe = equipe
        self.motor = motor
        self.combustivel = combustivel
        self.pneu = pneu
        self.chassi = chassi
        self.cambio = cambio
        self.suspensao = suspensao
        self.engenheiro = engenheiro
        self.combustivel_carregado = combustivel_carregado
        # Se não informado, usa o valor padrão fixo (compatibilidade/testes)
        self.tempo_pit_stop = tempo_pit_stop if tempo_pit_stop is not None else PIT_STOP_SEGUNDOS

        # Atributos setados dinamicamente pelo app antes da corrida.
        # Se não forem setados, os defaults dão comportamento neutro
        # (funciona igual ao antigo, sem crash):
        #   - categoria_cambio_ideal_pista, categoria_suspensao_ideal_pista (1 letra cada)
        #   - categoria_chuva (string)
        #   - temperatura_pista (°C, muda entre trechos durante a corrida)
        #   - influencia_pista_motor, _cambio, _suspensao, _pneu, _combustivel, _engenheiro
        #   - tamanho_volta_km

    def potencia_efetiva_motor(self):
        """Potência do motor já somada ao bônus que o combustível dá."""
        return self.motor.potencia * (1 + self.combustivel.aumento_potencia_motor)

    def _fator_influencia(self, nome):
        """Retorna o multiplicador da pista pra esse componente.
        10 = neutro (comportamento igual ao antigo). > 10 = mais importante
        nessa pista, < 10 = menos importante.
        """
        valor = getattr(self, f"influencia_pista_{nome}", INFLUENCIA_ESCALA)
        return (valor or INFLUENCIA_ESCALA) / INFLUENCIA_ESCALA

    def _fator_categoria_pista(self):
        """Penalidade por câmbio/suspensão fora da categoria ideal da pista.
        Retorna o total de "letras erradas" (0 = perfeito, 18 = pior caso).

        Baseado no como.txt: câmbio ideal = 1ª letra da pista,
        suspensão ideal = 2ª letra da pista.
        """
        categoria_cambio_carro = (self.cambio.categoria_pista or "A").upper()
        categoria_suspensao_carro = (self.suspensao.categoria_pista or "A").upper()

        categoria_cambio_ideal = getattr(self, "categoria_cambio_ideal_pista", None)
        categoria_suspensao_ideal = getattr(self, "categoria_suspensao_ideal_pista", None)

        if not categoria_cambio_ideal or not categoria_suspensao_ideal:
            return 0.0

        try:
            diff_cambio = abs(
                ord(categoria_cambio_carro[0]) - ord(categoria_cambio_ideal.upper()[0])
            )
            diff_suspensao = abs(
                ord(categoria_suspensao_carro[0]) - ord(categoria_suspensao_ideal.upper()[0])
            )
        except (IndexError, TypeError):
            return 0.0

        return diff_cambio + diff_suspensao

    def _fator_categoria_chuva(self):
        """Penalidade por pneu inadequado pro clima da pista.
        Retorna 0 (correto), 1 (1 nível de erro) ou 2 (2 níveis).
        """
        categoria_pneu = (self.pneu.categoria_chuva or "seco").lower()
        categoria_pista = (getattr(self, "categoria_chuva", "seco") or "seco").lower()
        mapa = {
            "seco":         {"seco": 0.0, "intermediario": 1.0, "chuva": 2.0},
            "intermediario": {"seco": 1.0, "intermediario": 0.0, "chuva": 1.0},
            "chuva":        {"seco": 2.0, "intermediario": 1.0, "chuva": 0.0},
        }
        return mapa.get(categoria_pneu, {}).get(categoria_pista, 0.0)

    def tempo_base(self):
        tempo = TEMPO_VOLTA_BASE_SEGUNDOS

        # Cada componente diminui o tempo, multiplicado pela influência
        # da pista (10 = neutro, 20 = 2x mais importante, 5 = metade).
        tempo -= self.potencia_efetiva_motor() * self._fator_influencia("motor")
        tempo -= self.pneu.performance * self._fator_influencia("pneu")
        tempo -= self.chassi.performance  # chassi não tem influência de pista
        tempo -= self.cambio.performance * self._fator_influencia("cambio")
        tempo -= self.suspensao.performance * self._fator_influencia("suspensao")

        if self.engenheiro:
            tempo -= (self.engenheiro.eficiencia_exata
                      * BONUS_DESIGNER_ESCALA
                      * self._fator_influencia("engenheiro"))

        # Penalidades (adicionam tempo):
        # Categoria de câmbio/suspensão errada: 0.3s por letra de diferença
        tempo += self._fator_categoria_pista() * 0.3
        # Pneu inadequado pro clima: 1s por nível de erro
        tempo += self._fator_categoria_chuva() * 1.0

        return tempo

    def tempo_com_variacao(self):
        variacao = random.gauss(0, VARIACAO_ALEATORIA_DESVIO_PADRAO)
        return self.tempo_base() + variacao

    def consumo_por_volta(self):
        """Consumo em litros por volta.

        Regra do como.txt: consumo é medido em litros/km, e depende do
        tamanho da volta da pista. Referência: 0.500 L/km.

        Fórmula: base_L_por_km × (1 - eficiencias) × tamanho_volta_km
                 × fator_engenheiro × fator_influencia_combustivel_pista

        Se tamanho_volta_km não foi setado (backward compat, testes),
        cai no comportamento antigo de litros/volta fixo.
        """
        eficiencia_total = min(self.motor.eficiencia_combustivel + self.combustivel.eficiencia, 0.9)

        tamanho_volta_km = getattr(self, "tamanho_volta_km", None)
        if tamanho_volta_km and tamanho_volta_km > 0:
            # Modo novo (baseado no como.txt): consumo em L/km × distância
            consumo = CONSUMO_BASE_LITROS_POR_KM * (1 - eficiencia_total) * tamanho_volta_km
        else:
            # Modo antigo (compat): consumo fixo por volta
            consumo = CONSUMO_BASE_MOTOR * (1 - eficiencia_total)

        if self.engenheiro:
            consumo *= (1 - self.engenheiro.bonus_eficiencia)
        # Influência do combustível na pista afeta consumo efetivo
        consumo *= self._fator_influencia("combustivel")
        return consumo

    def desgaste_por_volta(self):
        """Desgaste do pneu por volta, ajustado pela temperatura da pista.
        Referência: 20°C = neutro. Cada grau acima aumenta desgaste, cada
        grau abaixo reduz (baseado no como.txt).

        A temperatura pode mudar entre trechos da corrida - quem seta
        `carro.temperatura_pista` é a classe Corrida, antes de cada volta.
        """
        desgaste = self.pneu.desgaste
        if self.engenheiro:
            desgaste *= (1 - self.engenheiro.bonus_eficiencia)

        # Fator de temperatura
        temperatura = getattr(self, "temperatura_pista", TEMPERATURA_REFERENCIA)
        if temperatura is None:
            temperatura = TEMPERATURA_REFERENCIA
        fator_temp = 1.0 + (temperatura - TEMPERATURA_REFERENCIA) * DESGASTE_POR_GRAU_FRACAO
        desgaste *= max(0.1, fator_temp)  # nunca menos que 10% do desgaste base

        return desgaste

    def __repr__(self):
        return f"Carro({self.equipe.nome}: {self.motor.nome}/{self.pneu.nome})"
