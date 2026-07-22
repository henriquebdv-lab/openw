"""
Classe Corrida - simula vários carros ao mesmo tempo, volta a volta,
e calcula as posições de cada um a cada volta.

Regras de abandono:
1. Pneu passou de 100% de desgaste -> pneu estoura -> abandono.
2. Quebra mecânica aleatória (sorteada no início da corrida).
   A chance é reduzida pelo Treinamento de Boxes.

Combustível zerado é pit stop automático (não abandono).
"""

import random

from constantes import (
    LIMITE_DESGASTE_PNEU,
    COMBUSTIVEL_MINIMO,
    NUMERO_TRECHOS_CORRIDA,
    CHANCE_QUEBRA_BASE,
    CHANCE_QUEBRA_MINIMA,
)


def calcular_tempo_pit_stop(tempo_pista_base, config, percentual_treinamento):
    tempo_pista_base = float(tempo_pista_base or 0.0)
    if config.pit_tempo_sem_treino <= 0:
        return round(tempo_pista_base, 3)
    reducao_maxima_fracao = 0.0
    if config.pit_tempo_sem_treino > 0:
        reducao_maxima_fracao = (
            (config.pit_tempo_sem_treino - config.pit_tempo_treino_completo) / config.pit_tempo_sem_treino
        )
    tempo_efetivo = tempo_pista_base * (1 - reducao_maxima_fracao * (percentual_treinamento / 100.0))
    return round(tempo_efetivo, 3)


def calcular_chance_quebra(percentual_treinamento_box):
    """Chance de o carro quebrar durante a corrida.
    - Treinamento 0%    -> 10% de chance
    - Treinamento 100%  -> 2% de chance
    - Escala linear no meio.
    """
    p = max(0.0, min(100.0, percentual_treinamento_box or 0.0)) / 100.0
    return CHANCE_QUEBRA_BASE - (CHANCE_QUEBRA_BASE - CHANCE_QUEBRA_MINIMA) * p


class EstadoCarroNaCorrida:
    """Guarda o estado (combustível, desgaste) de um carro durante a corrida."""
    def __init__(self, carro, consumo_qualifying=False, chance_quebra=0.0, total_voltas=1):
        self.carro = carro
        self.combustivel = carro.combustivel_carregado
        self.desgaste_pneu = 0.0
        self.tempo_acumulado = 0.0
        self.pit_stops = 0
        self.abandonou = False
        self.volta_abandono = None
        self.motivo_abandono = None   # "pneu" ou "quebra"
        self.historico_voltas = []

        # Consumo da volta de qualifying
        if consumo_qualifying:
            consumo_qualifying_litros = self.carro.consumo_por_volta()
            self.combustivel = max(0.0, self.combustivel - consumo_qualifying_litros)
            self.combustivel_gasto_qualifying = round(consumo_qualifying_litros, 3)
        else:
            self.combustivel_gasto_qualifying = 0.0

        # Sorteio de quebra mecânica no INÍCIO da corrida.
        # Se vai quebrar, sorteia também em qual volta (aleatória entre 2 e total-1
        # pra não quebrar logo na largada nem na última volta).
        self.vai_quebrar = random.random() < chance_quebra
        if self.vai_quebrar and total_voltas > 2:
            self.volta_quebra = random.randint(2, total_voltas - 1)
        else:
            self.volta_quebra = None
            self.vai_quebrar = False

    def rodar_volta(self, numero_volta):
        if self.abandonou:
            return

        tempo_volta = self.carro.tempo_com_variacao(self.desgaste_pneu)

        self.combustivel -= self.carro.consumo_por_volta()
        self.desgaste_pneu += self.carro.desgaste_por_volta()

        # --- 1) Verifica quebra mecânica ---
        if self.vai_quebrar and numero_volta == self.volta_quebra:
            self.abandonou = True
            self.motivo_abandono = "quebra"
            self.volta_abandono = numero_volta
            self.tempo_acumulado += tempo_volta
            self.historico_voltas.append({
                "volta": numero_volta,
                "tempo_volta": round(tempo_volta, 3),
                "tempo_acumulado": round(self.tempo_acumulado, 3),
                "desgaste_pneu": round(self.desgaste_pneu, 1),
                "pit_stop": False,
                "abandonou": True,
                "motivo": "quebra",
            })
            return

        # --- 2) Verifica pneu estourado ---
        if self.desgaste_pneu >= LIMITE_DESGASTE_PNEU:
            self.abandonou = True
            self.motivo_abandono = "pneu"
            self.volta_abandono = numero_volta
            self.tempo_acumulado += tempo_volta
            self.historico_voltas.append({
                "volta": numero_volta,
                "tempo_volta": round(tempo_volta, 3),
                "tempo_acumulado": round(self.tempo_acumulado, 3),
                "desgaste_pneu": round(self.desgaste_pneu, 1),
                "pit_stop": False,
                "abandonou": True,
                "motivo": "pneu",
            })
            return

        # --- 3) Pit stop automático se acabou o combustível ---
        pit_stop_nesta_volta = False
        if self.combustivel <= COMBUSTIVEL_MINIMO:
            tempo_volta += self.carro.tempo_pit_stop
            self.combustivel = self.carro.combustivel_carregado
            self.pit_stops += 1
            pit_stop_nesta_volta = True

        self.tempo_acumulado += tempo_volta
        self.historico_voltas.append({
            "volta": numero_volta,
            "tempo_volta": round(tempo_volta, 3),
            "tempo_acumulado": round(self.tempo_acumulado, 3),
            "desgaste_pneu": round(self.desgaste_pneu, 1),
            "pit_stop": pit_stop_nesta_volta,
            "abandonou": False,
        })


def _calcular_trecho_da_volta(numero_volta, total_voltas, numero_trechos=NUMERO_TRECHOS_CORRIDA):
    if total_voltas <= 0:
        return 0
    trecho = int((numero_volta - 1) * numero_trechos / total_voltas)
    return max(0, min(numero_trechos - 1, trecho))


class Corrida:
    def __init__(self, carros, total_voltas=60, temperaturas_trechos=None,
                 consumo_qualifying=True, percentuais_treino_box=None):
        """
        carros: lista de instâncias de Carro (um por piloto competindo).
        temperaturas_trechos: lista opcional de 4 temperaturas por trecho.
        consumo_qualifying: se True, cada carro perde 1 volta de combustível.
        percentuais_treino_box: lista opcional (paralela a `carros`) com o
            percentual de treinamento de box de cada equipe (0 a 100).
            Se não informado, usa 0 (chance de quebra máxima).
        """
        self.total_voltas = total_voltas
        self.temperaturas_trechos = temperaturas_trechos
        if temperaturas_trechos:
            for carro in carros:
                carro.temperatura_pista = temperaturas_trechos[0]

        percentuais = percentuais_treino_box or [0.0] * len(carros)
        self.estados = []
        for carro, pct_treino in zip(carros, percentuais):
            chance_quebra = calcular_chance_quebra(pct_treino)
            self.estados.append(EstadoCarroNaCorrida(
                carro,
                consumo_qualifying=consumo_qualifying,
                chance_quebra=chance_quebra,
                total_voltas=total_voltas,
            ))

    def simular(self):
        posicoes_por_volta = []
        for volta in range(1, self.total_voltas + 1):
            if self.temperaturas_trechos:
                trecho = _calcular_trecho_da_volta(volta, self.total_voltas)
                temperatura_trecho = self.temperaturas_trechos[trecho]
                for estado in self.estados:
                    estado.carro.temperatura_pista = temperatura_trecho

            for estado in self.estados:
                estado.rodar_volta(volta)
            posicoes_por_volta.append(self._ordem_atual())

        return {
            "classificacao_final": self._classificacao_final(),
            "posicoes_por_volta": posicoes_por_volta,
        }

    def _chave_ordenacao(self, estado):
        if estado.abandonou:
            return (1, -estado.volta_abandono)
        return (0, estado.tempo_acumulado)

    def _ordem_atual(self):
        ordenados = sorted(self.estados, key=self._chave_ordenacao)
        finalizados = [e for e in ordenados if not e.abandonou]
        tempo_lider = finalizados[0].tempo_acumulado if finalizados else 0.0
        resultado = []
        for i, e in enumerate(ordenados):
            if e.abandonou:
                diferenca_lider = None
                diferenca_frente = None
            else:
                diferenca_lider = e.tempo_acumulado - tempo_lider
                if i == 0:
                    diferenca_frente = 0.0
                else:
                    carro_da_frente = ordenados[i - 1]
                    diferenca_frente = (
                        e.tempo_acumulado - carro_da_frente.tempo_acumulado
                        if not carro_da_frente.abandonou else None
                    )
            resultado.append({
                "equipe": e.carro.equipe.nome,
                "posicao": i + 1,
                "tempo_acumulado": e.tempo_acumulado,
                "diferenca_lider": diferenca_lider,
                "diferenca_frente": diferenca_frente,
                "abandonou": e.abandonou,
                "desgaste_pneu": round(e.desgaste_pneu, 1),
            })
        return resultado

    def _classificacao_final(self):
        ordenados = sorted(self.estados, key=self._chave_ordenacao)
        return [
            {
                "posicao": posicao,
                "equipe": e.carro.equipe.nome,
                "tempo_total_segundos": round(e.tempo_acumulado, 2),
                "pit_stops": e.pit_stops,
                "abandonou": e.abandonou,
                "motivo_abandono": e.motivo_abandono,
                "volta_abandono": e.volta_abandono,
                "combustivel_qualifying": e.combustivel_gasto_qualifying,
                "desgaste_pneu_final": round(e.desgaste_pneu, 1),
                "historico_voltas": e.historico_voltas,
            }
            for posicao, e in enumerate(ordenados, start=1)
        ]
