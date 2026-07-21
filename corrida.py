"""
Classe Corrida - simula vários carros ao mesmo tempo, volta a volta,
e calcula as posições de cada um a cada volta (o que gera as
"ultrapassagens" naturalmente, comparando tempo acumulado).

Regra do pneu: se o desgaste passar do limite, o pneu ESTOURA e o carro
abandona a corrida (não é mais um pit stop automático suave - é
definitivo). Combustível zerado continua sendo um pit stop normal.

Regras do como.txt aplicadas aqui:
- A corrida é dividida em 4 trechos, cada um com sua temperatura.
- Antes da corrida, cada carro fez 1 volta de qualifying que consumiu
  combustível do tanque (opcional, via consumo_qualifying=True).
"""

from constantes import LIMITE_DESGASTE_PNEU, COMBUSTIVEL_MINIMO, NUMERO_TRECHOS_CORRIDA


def calcular_tempo_pit_stop(tempo_pista_base, config, percentual_treinamento):
    """Combina o tempo de pit stop da pista real com o efeito do treinamento."""
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


class EstadoCarroNaCorrida:
    """Guarda o estado (combustível, desgaste) de um carro durante a corrida."""
    def __init__(self, carro, consumo_qualifying=False):
        self.carro = carro
        self.combustivel = carro.combustivel_carregado
        self.desgaste_pneu = 0.0
        self.tempo_acumulado = 0.0
        self.pit_stops = 0
        self.abandonou = False
        self.volta_abandono = None
        self.historico_voltas = []  # uma entrada por volta

        # Regra do como.txt: se houve volta de qualifying antes da corrida,
        # ela também gastou combustível (voltas totais = 1 qualifying + N corrida).
        # O consumo é calculado com o tamanho da volta da pista atual, então
        # o carro já precisa ter recebido tamanho_volta_km antes.
        if consumo_qualifying:
            consumo_qualifying_litros = self.carro.consumo_por_volta()
            self.combustivel = max(0.0, self.combustivel - consumo_qualifying_litros)
            self.combustivel_gasto_qualifying = round(consumo_qualifying_litros, 3)
        else:
            self.combustivel_gasto_qualifying = 0.0

    def rodar_volta(self, numero_volta):
        if self.abandonou:
            return  # carro já abandonou, não roda mais voltas
        tempo_volta = self.carro.tempo_com_variacao()
        self.combustivel -= self.carro.consumo_por_volta()
        self.desgaste_pneu += self.carro.desgaste_por_volta()
        if self.desgaste_pneu >= LIMITE_DESGASTE_PNEU:
            # Pneu estourou - abandono definitivo, não é pit stop
            self.abandonou = True
            self.volta_abandono = numero_volta
            self.tempo_acumulado += tempo_volta
            self.historico_voltas.append({
                "volta": numero_volta,
                "tempo_volta": round(tempo_volta, 3),
                "tempo_acumulado": round(self.tempo_acumulado, 3),
                "pit_stop": False,
                "abandonou": True,
            })
            return
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
            "pit_stop": pit_stop_nesta_volta,
            "abandonou": False,
        })


def _calcular_trecho_da_volta(numero_volta, total_voltas, numero_trechos=NUMERO_TRECHOS_CORRIDA):
    """Retorna o índice do trecho (0 a numero_trechos-1) pra uma volta.
    Divide as voltas em partes iguais: primeiras 25% = trecho 0, etc.
    """
    if total_voltas <= 0:
        return 0
    trecho = int((numero_volta - 1) * numero_trechos / total_voltas)
    return max(0, min(numero_trechos - 1, trecho))


class Corrida:
    def __init__(self, carros, total_voltas=60, temperaturas_trechos=None, consumo_qualifying=True):
        """carros: lista de instâncias de Carro (um por piloto competindo).
        temperaturas_trechos: lista opcional de 4 temperaturas (uma por trecho).
                              Se não passar, usa carro.temperatura_pista fixa.
        consumo_qualifying: se True, cada carro perde 1 volta de combustível
                            no início (representando a volta de qualifying).
        """
        self.total_voltas = total_voltas
        self.temperaturas_trechos = temperaturas_trechos
        # Antes de criar os estados, garanta que a temperatura inicial (trecho 0)
        # está setada em cada carro, pra que o consumo de qualifying use o
        # cenário correto de temperatura.
        if temperaturas_trechos:
            for carro in carros:
                carro.temperatura_pista = temperaturas_trechos[0]
        self.estados = [EstadoCarroNaCorrida(carro, consumo_qualifying=consumo_qualifying) for carro in carros]

    def simular(self):
        """
        Roda a corrida inteira e devolve:
        - classificacao_final: lista ordenada do 1º ao último colocado
          (quem abandonou fica depois de quem terminou, ordenado por
          quantas voltas conseguiu completar)
        - posicoes_por_volta: lista (uma por volta) com a ordem naquele momento
        """
        posicoes_por_volta = []
        for volta in range(1, self.total_voltas + 1):
            # Antes de rodar a volta, ajusta a temperatura de cada carro
            # pra do trecho atual (regra do como.txt: 4 trechos).
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
        """Quem não abandonou vem primeiro (por tempo); quem abandonou vem
        depois, ordenado por quem foi mais longe."""
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
                "volta_abandono": e.volta_abandono,
                "combustivel_qualifying": e.combustivel_gasto_qualifying,
                "historico_voltas": e.historico_voltas,
            }
            for posicao, e in enumerate(ordenados, start=1)
        ]
