"""
Frases de feedback do piloto sobre o acerto (setup) do carro.

Como funciona:
- Cada componente ajustável (câmbio, suspensão, etc.) tem um valor "ideal"
  pra pista atual. A "distância do ideal" é quanto o acerto escolhido está
  longe disso, num range de -98 a +98.
  - distância NEGATIVA  -> acerto ABAIXO do ideal (curto/mole/baixo demais)
  - distância POSITIVA  -> acerto ACIMA do ideal  (longo/duro/alto demais)
  - distância ~zero     -> no ponto
- Cada faixa de distância tem várias frases equivalentes; o sistema sorteia
  uma pra não ficar repetitivo.
- Todas as frases são ORIGINAIS (não copiadas de nenhum outro jogo).

Uso:
    from feedback_piloto import frase_feedback
    txt = frase_feedback(distancia=-45, componente="cambio")
    # -> ex: "A relação tá curta, no fim da reta o carro morre de velocidade."

Componentes suportados (só muda o vocabulário, a lógica é a mesma):
    "cambio", "suspensao", "generico"
"""

import random


# Direção do erro por componente:
# (palavra pra ABAIXO do ideal, palavra pra ACIMA do ideal)
VOCABULARIO = {
    "cambio":     ("curta",  "longa"),   # relação curta x longa
    "suspensao":  ("mole",   "dura"),    # suspensão mole x dura
    "generico":   ("baixo",  "alto"),
}


# Faixas por MAGNITUDE (valor absoluto da distância).
# Cada faixa tem: (limite_superior, lista_de_frases)
# {dir} é substituído pela palavra da direção (curta/longa, mole/dura...).
# As frases valem tanto pra lado negativo quanto positivo — o {dir} resolve.

FAIXAS_MAGNITUDE = [
    # PERFEITO (0 a 3): setup no ponto
    (3, [
        "Tá perfeito, o carro faz exatamente o que eu peço.",
        "Acerto no ponto. Assim dá pra brigar por tempo.",
        "Não mexe em nada, esse é o acerto certo pra aqui.",
        "Carro redondo, entra e sai de curva sem reclamar.",
    ]),
    # MUITO PERTO (4 a 12): quase lá
    (12, [
        "Quase no ponto, mas ainda sinto o acerto um tico {dir} demais.",
        "Faltou um cabelo. Tá levemente {dir} pro meu gosto.",
        "Bom acerto, só ajustaria um pouquinho — ainda tá {dir}.",
        "Dá pra correr assim, mas mexendo um dedinho fica melhor.",
    ]),
    # LEVE (13 a 28)
    (28, [
        "Tá {dir} demais, dá pra sentir em algumas curvas.",
        "Precisa corrigir: o acerto ficou {dir} e me custa tempo.",
        "Perco um pouco de ritmo, o carro tá {dir} pra essa pista.",
        "Não tá horrível, mas {dir} desse jeito me atrapalha.",
    ]),
    # MÉDIO (29 a 50)
    (50, [
        "Bem {dir} demais, o carro fica difícil de colocar na curva.",
        "Tô sofrendo aqui, o acerto {dir} me tira muito tempo.",
        "Precisa mexer com firmeza: {dir} desse jeito não dá ritmo.",
        "O carro reclama em quase toda curva, tá {dir} demais.",
    ]),
    # GRANDE (51 a 74)
    (74, [
        "Muito {dir}! Assim eu não consigo confiar no carro.",
        "Tá longe do ponto, {dir} demais — todo giro é uma luta.",
        "Desse jeito não dá, o acerto {dir} me faz perder tempão.",
        "O carro tá um perigo, {dir} demais pra andar rápido.",
    ]),
    # EXTREMO (75 a 98)
    (98, [
        "Tá completamente {dir}! Impossível andar assim.",
        "Isso tá absurdo de {dir}, mal consigo manter na pista.",
        "Erramos feio: {dir} pra caramba, o carro é indirigível.",
        "Joga tudo fora e recomeça, esse acerto {dir} não presta.",
    ]),
]


def _direcao(distancia, componente):
    """Retorna a palavra certa (abaixo/acima do ideal) pro componente."""
    palavra_abaixo, palavra_acima = VOCABULARIO.get(componente, VOCABULARIO["generico"])
    return palavra_abaixo if distancia < 0 else palavra_acima


def frase_feedback(distancia, componente="generico", aleatorio=True):
    """
    Retorna uma frase de feedback pro acerto informado.

    distancia: número de -98 a +98 (0 = ideal). Valores fora do range são
               limitados automaticamente.
    componente: "cambio", "suspensao" ou "generico".
    aleatorio: se True, sorteia uma das frases da faixa; se False, pega
               sempre a primeira (útil pra testes determinísticos).
    """
    # Limita ao range válido
    distancia = max(-98, min(98, int(round(distancia))))
    magnitude = abs(distancia)

    for limite, frases in FAIXAS_MAGNITUDE:
        if magnitude <= limite:
            frase = random.choice(frases) if aleatorio else frases[0]
            # A faixa "perfeito" não usa {dir}; as outras usam.
            if "{dir}" in frase:
                frase = frase.format(dir=_direcao(distancia, componente))
            return frase

    # Fallback teórico (não deve acontecer por causa do limite de 98)
    return "Não consigo nem descrever esse acerto."


def frase_por_categoria(categoria_ideal, categoria_escolhida, componente="generico", aleatorio=True):
    """
    Atalho pra quando você trabalha com as categorias A-J (modelos 50-900).
    Converte a diferença entre a categoria ideal e a escolhida numa distância
    e retorna a frase.

    Ex: ideal="E" (400), escolhida="C" (200) -> distância -200 (limitada a -98).
    Cada letra vale 100 de "passo" (A=0, B=100, ... J=900 na prática, mas aqui
    usamos o índice A=0..J=9 e multiplicamos por ~22 pra caber no range -98..98).
    """
    letras = "ABCDEFGHIJ"
    try:
        i_ideal = letras.index(categoria_ideal.upper())
        i_escolhida = letras.index(categoria_escolhida.upper())
    except (ValueError, AttributeError):
        return frase_feedback(0, componente, aleatorio)

    # Diferença em "passos" de letra, escalada pro range -98..98.
    # 9 passos de diferença (A vs J) -> ~98. Então cada passo ~= 11.
    passos = i_escolhida - i_ideal
    distancia = passos * 11
    return frase_feedback(distancia, componente, aleatorio)


if __name__ == "__main__":
    # Demonstração rápida: mostra uma frase por faixa, pros dois componentes.
    print("=== CÂMBIO ===")
    for d in [-90, -60, -35, -20, -8, 0, 8, 20, 35, 60, 90]:
        print(f"  dist {d:+4d}: {frase_feedback(d, 'cambio', aleatorio=False)}")

    print("\n=== SUSPENSÃO ===")
    for d in [-90, -60, -35, -20, -8, 0, 8, 20, 35, 60, 90]:
        print(f"  dist {d:+4d}: {frase_feedback(d, 'suspensao', aleatorio=False)}")

    print("\n=== POR CATEGORIA (ideal=E) ===")
    for cat in "ABCDEFGHIJ":
        print(f"  escolhida {cat}: {frase_por_categoria('E', cat, 'cambio', aleatorio=False)}")
