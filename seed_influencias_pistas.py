"""
Grava os valores CANÔNICOS de influência nas pistas reais.

IMPORTANTE:
- As pistas já foram importadas (importar_todas_pistas.py) no banco
  separado pistas_reais.db. Este script NÃO cria nem apaga pistas.
- Ele apenas ATUALIZA as influências (M/C/S/P/G/E) das pistas pras
  quais temos valores canônicos da planilha de referência.
- Toda pista que não estiver no dicionário abaixo continua com 10
  (neutro) em tudo, que é o padrão do banco. Você ajusta o resto
  depois na tela admin.
- Range válido: 7 a 15 (10 = neutro). Não existe influência de Freio.
- As pistas são identificadas pelo NOME DE EXIBIÇÃO salvo no banco
  (ex: "Red Bull Ring", não "Spielberg").

Como rodar:
    python seed_influencias_pistas.py
"""

from pistas_reais_db import listar_pistas_reais, atualizar_pista_real


# ---------------------------------------------------------
# Influências canônicas conhecidas da planilha de referência.
# Chave = NOME DE EXIBIÇÃO exatamente como está salvo no banco.
# Só coloque aqui pistas que você tem valor de verdade; o resto
# fica neutro (10) automaticamente.
# ---------------------------------------------------------
INFLUENCIAS_CANONICAS = {
    # Spielberg = Red Bull Ring = A1-Ring: M9 C8 S7 P11 G12 E14
    "Red Bull Ring": {
        "influencia_motor": 9,
        "influencia_cambio": 8,
        "influencia_suspensao": 7,
        "influencia_pneu": 11,
        "influencia_combustivel": 12,
        "influencia_engenheiro": 14,
    },
}


def aplicar_influencias():
    pistas = listar_pistas_reais()
    if not pistas:
        print("Nenhuma pista encontrada no banco. Rode importar_todas_pistas.py antes.")
        return

    atualizadas = 0
    nao_encontradas = list(INFLUENCIAS_CANONICAS.keys())

    for pista in pistas:
        nome = pista["nome"]
        if nome in INFLUENCIAS_CANONICAS:
            atualizar_pista_real(pista["id"], **INFLUENCIAS_CANONICAS[nome])
            print(f"  OK: {nome} -> {INFLUENCIAS_CANONICAS[nome]}")
            atualizadas += 1
            if nome in nao_encontradas:
                nao_encontradas.remove(nome)

    print()
    print(f"Pistas atualizadas com valores canônicos: {atualizadas}")
    print(f"Demais pistas continuam neutras (influência 10 em tudo).")

    if nao_encontradas:
        print()
        print("AVISO: estes nomes canônicos NÃO foram encontrados no banco")
        print("(confira se o nome de exibição bate exatamente):")
        for nome in nao_encontradas:
            print(f"  - {nome}")


if __name__ == "__main__":
    aplicar_influencias()
