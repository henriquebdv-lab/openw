"""
Classe Carro - junta equipe + equipamentos + Engenheiro (opcional).

Chassi e Aerodinâmica não são fornecedores contratados. São projetados
pelo Engenheiro que a equipe contratou, e a performance vem do nível
desse engenheiro + percentual de desenvolvimento aplicado.

REFACTOR xx-50/xx-900 (Etapa 3):
- Cada corrida, o jogador pode escolher qual MODELO (50 a 900) usar de
  cada componente. Isso é um MODIFICADOR calculado, não muda o banco.
- Como aplicamos cada modelo (pra NÃO contar efeito duas vezes):
    * Motor/Combustível: delta de velocidade + fator de consumo
    * Pneu: delta de velocidade + fator de desgaste + define a condição
      (seco/molhada/encharcada) usada no casamento com a pista
    * Câmbio/Suspensão: o modelo APENAS define a letra A-J usada no
      casamento com a categoria ideal da pista (o efeito no tempo já vem
      de _fator_categoria_pista, então NÃO somamos delta aqui)
- Se nenhum modelo for escolhido, o carro se comporta IGUAL a antes
  (100% retrocompatível).
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
import modelos_componente


class Carro:
    def __init__(self, equipe, motor, combustivel, pneu, chassi, cambio, suspensao,
                 engenheiro=None, combustivel_carregado=110.0, tempo_pit_stop=None):
        self.equipe = equipe
        self.motor = motor
        self.combustivel = combustivel
        self.pneu = pneu
        self.chassi = chassi          # chassi projetado pelo engenheiro (não é fornecedor)
        self.cambio = cambio
        self.suspensao = suspensao
        self.engenheiro = engenheiro
        self.combustivel_carregado = combustivel_carregado
        self.tempo_pit_stop = tempo_pit_stop if tempo_pit_stop is not None else PIT_STOP_SEGUNDOS
        # Performance da aerodinâmica (setado pelo CarroJogador.montar_carro)
        self.performance_aero = 0.0

        # REFACTOR: modelos escolhidos pra ESTA corrida (50 a 900).
        # Vazio = nenhum modelo escolhido = comportamento antigo.
        # Chaves possíveis: "motor", "combustivel", "pneu", "cambio", "suspensao"
        self.modelos_corrida = {}

    # -----------------------------------------------------
    # REFACTOR: helpers dos modelos xx-50/xx-900
    # -----------------------------------------------------
    def definir_modelos(self, motor=None, combustivel=None, pneu=None,
                        cambio=None, suspensao=None):
        """Define os modelos (50-900) escolhidos pra esta corrida.
        Passe só os que quiser; os demais ficam sem modificador.
        Ignora valores inválidos silenciosamente."""
        escolhidos = {
            "motor": motor, "combustivel": combustivel, "pneu": pneu,
            "cambio": cambio, "suspensao": suspensao,
        }
        for componente, numero in escolhidos.items():
            if numero is not None and modelos_componente.modelo_valido(numero):
                self.modelos_corrida[componente] = int(numero)

    def _mod(self, componente):
        """Retorna o dict de modificadores do modelo escolhido pro
        componente, ou None se não houver escolha."""
        numero = self.modelos_corrida.get(componente)
        if numero is None:
            return None
        return modelos_componente.modificadores(numero, componente)

    def _delta_velocidade_modelos(self):
        """Soma o delta de velocidade dos modelos que afetam o tempo
        DIRETAMENTE: motor, combustível e pneu.
        Câmbio/suspensão NÃO entram aqui (efeito vem do casamento de letra)."""
        delta = 0.0
        for componente in ("motor", "combustivel", "pneu"):
            mod = self._mod(componente)
            if mod:
                delta += mod["velocidade_delta_s"]
        return delta

    def _categoria_cambio_efetiva(self):
        """Letra do câmbio: se um modelo foi escolhido, ele manda;
        senão usa a categoria fixa do fornecedor."""
        mod = self._mod("cambio")
        if mod:
            return mod["letra"]
        return (self.cambio.categoria_pista or "A").upper()

    def _categoria_suspensao_efetiva(self):
        mod = self._mod("suspensao")
        if mod:
            return mod["letra"]
        return (self.suspensao.categoria_pista or "A").upper()

    def _condicao_pneu_efetiva(self):
        """Condição do pneu (seco/molhada/encharcada): modelo manda se
        escolhido; senão usa a categoria_chuva do fornecedor."""
        mod = self._mod("pneu")
        if mod:
            # normaliza "molhada" -> mesma família de "intermediario"/"chuva"
            return mod["condicao_pista"]
        return (self.pneu.categoria_chuva or "seco").lower()

    # -----------------------------------------------------
    def potencia_efetiva_motor(self):
        return self.motor.potencia * (1 + self.combustivel.aumento_potencia_motor)

    def _fator_influencia(self, nome):
        valor = getattr(self, f"influencia_pista_{nome}", INFLUENCIA_ESCALA)
        return (valor or INFLUENCIA_ESCALA) / INFLUENCIA_ESCALA

    def _fator_categoria_pista(self):
        categoria_cambio_carro = self._categoria_cambio_efetiva()
        categoria_suspensao_carro = self._categoria_suspensao_efetiva()

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
        categoria_pneu = self._condicao_pneu_efetiva()
        # "molhada" (nome usado pelos modelos) conta como "intermediario"
        if categoria_pneu == "molhada":
            categoria_pneu = "intermediario"
        elif categoria_pneu == "encharcada":
            categoria_pneu = "chuva"
        categoria_pista = (getattr(self, "categoria_chuva", "seco") or "seco").lower()
        mapa = {
            "seco":         {"seco": 0.0, "intermediario": 1.0, "chuva": 2.0},
            "intermediario": {"seco": 1.0, "intermediario": 0.0, "chuva": 1.0},
            "chuva":        {"seco": 2.0, "intermediario": 1.0, "chuva": 0.0},
        }
        return mapa.get(categoria_pneu, {}).get(categoria_pista, 0.0)

    def penalidade_desgaste_pneu(self, desgaste_atual):
        """Perda de tempo em segundos por causa do desgaste do pneu.
        Curva progressiva:
        - 0-70%: sem penalidade
        - 70-85%: leve (até 1.5s)
        - 85-95%: médio (até 5s)
        - 95-100%: pesado (até 12s)
        - >=100%: pneu estoura (15s + abandono)
        """
        if desgaste_atual is None or desgaste_atual < 70:
            return 0.0
        if desgaste_atual < 85:
            return (desgaste_atual - 70) * (1.5 / 15)
        if desgaste_atual < 95:
            return 1.5 + (desgaste_atual - 85) * (3.5 / 10)
        if desgaste_atual < 100:
            return 5.0 + (desgaste_atual - 95) * (7.0 / 5)
        return 15.0

    def tempo_base(self):
        tempo = TEMPO_VOLTA_BASE_SEGUNDOS

        tempo -= self.potencia_efetiva_motor() * self._fator_influencia("motor")
        tempo -= self.pneu.performance * self._fator_influencia("pneu")
        # Chassi: performance já vem calculada com base no nível + %aplicado
        tempo -= self.chassi.performance
        # Aerodinâmica: bônus separado calculado no CarroJogador.montar_carro
        tempo -= (self.performance_aero or 0.0)
        tempo -= self.cambio.performance * self._fator_influencia("cambio")
        tempo -= self.suspensao.performance * self._fator_influencia("suspensao")

        if self.engenheiro:
            tempo -= (self.engenheiro.eficiencia_exata
                      * BONUS_DESIGNER_ESCALA
                      * self._fator_influencia("engenheiro"))

        tempo += self._fator_categoria_pista() * 0.3
        tempo += self._fator_categoria_chuva() * 1.0

        # REFACTOR: delta de velocidade dos modelos (motor/combustível/pneu)
        tempo += self._delta_velocidade_modelos()

        return tempo

    def tempo_com_variacao(self, desgaste_atual=0.0):
        variacao = random.gauss(0, VARIACAO_ALEATORIA_DESVIO_PADRAO)
        penalidade_pneu = self.penalidade_desgaste_pneu(desgaste_atual)
        return self.tempo_base() + variacao + penalidade_pneu

    def consumo_por_volta(self):
        eficiencia_total = min(self.motor.eficiencia_combustivel + self.combustivel.eficiencia, 0.9)
        tamanho_volta_km = getattr(self, "tamanho_volta_km", None)
        if tamanho_volta_km and tamanho_volta_km > 0:
            consumo = CONSUMO_BASE_LITROS_POR_KM * (1 - eficiencia_total) * tamanho_volta_km
        else:
            consumo = CONSUMO_BASE_MOTOR * (1 - eficiencia_total)
        if self.engenheiro:
            consumo *= (1 - self.engenheiro.bonus_eficiencia)
        consumo *= self._fator_influencia("combustivel")

        # REFACTOR: fator de consumo dos modelos de motor e combustível
        for componente in ("motor", "combustivel"):
            mod = self._mod(componente)
            if mod:
                consumo *= mod["fator_consumo"]

        return consumo

    def desgaste_por_volta(self):
        desgaste = self.pneu.desgaste
        if self.engenheiro:
            desgaste *= (1 - self.engenheiro.bonus_eficiencia)
        temperatura = getattr(self, "temperatura_pista", TEMPERATURA_REFERENCIA)
        if temperatura is None:
            temperatura = TEMPERATURA_REFERENCIA
        fator_temp = 1.0 + (temperatura - TEMPERATURA_REFERENCIA) * DESGASTE_POR_GRAU_FRACAO
        desgaste *= max(0.1, fator_temp)

        # REFACTOR: fator de desgaste do modelo de pneu
        mod = self._mod("pneu")
        if mod:
            desgaste *= mod["fator_desgaste"]

        return desgaste

    def __repr__(self):
        return f"Carro({self.equipe.nome}: {self.motor.nome}/{self.pneu.nome})"
