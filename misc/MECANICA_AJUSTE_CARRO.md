# MECÂNICA DE AJUSTE DO CARRO (Treino Livre) — Engenharia Reversa

> **O que é:** a "alma" do ajuste fino do carro, extraída das planilhas do jogo
> original (n17ro e Malhado). Documento canônico pra qualquer IA (ou pra nós)
> entender COMO o treino livre funciona, sem precisar das planilhas originais.
>
> **Fontes (engenharia reversa):**
> - estrategiaf1_2005_byn17ro.xls → frases de feedback por faixa de erro (-98 a +98)
> - EF1_Malhado_V0.10.TL-Beta.xls → sistema de ajuste fino + variância + % de acerto

---

## 1. O CONCEITO CENTRAL
No Treino Livre, o carro tem ajustes (sliders). Cada ajuste tem um VALOR IDEAL
SECRETO para aquela pista (o jogador não vê). O jogador começa com valores
quaisquer, faz 1 volta, e o piloto dá um feedback indicando se está perto/longe
do ideal e pra que lado mexer. Ajusta e repete até chegar perto (ou acabar
pneu/combustível). Quanto mais perto do ideal, mais rápida a volta.

---

## 2. OS AJUSTES (SLIDERS)
Canônico (Malhado) = 5 ajustes, cada um de 1 a 99:
1. Câmbio  2. Suspensão  3. Aerofólio Dianteiro  4. Aerofólio Traseiro  5. Freio (DLC)

🎨 NOSSA VERSÃO:
- 3 sliders VISÍVEIS (Câmbio, Suspensão, Aerofólio), estrutura pronta pra 5.
- Ajustes 1-99 (ajuste fino). NÃO confundir com modelos 50-900 (peças, parc fermé).

---

## 3. O VALOR IDEAL SECRETO POR SLIDER (fórmula)
- Cada slider tem um valor ideal (1-99) que o jogador tenta acertar. Escondido.
- NÃO existe nas planilhas Ayres. Nós CALCULAMOS.

### 🎨 DECISÃO: o ideal vem de 3 fontes combinadas
```
valor_ideal(slider, jogador, pista) =
    BASE(pista, slider)               # sorteio ALEATÓRIO FIXO por pista+slider
                                      # (salvo no banco; a "cara" daquela pista)
  + AJUSTE_INFLUENCIA(pista, slider)  # desloca conforme influência M/C/S/P/G/E
                                      # da pista (Ayres 5-15; 10 = neutro)
  + AJUSTE_CONTRATO(peça do jogador)  # desloca conforme a peça contratada
  -> clamp final entre 1 e 99
```
- Determinístico (mesma pista+peça = mesmo ideal). Personalizado por jogador.

### ⚙️ FASEAMENTO
- FASE 1 (feito): só a BASE aleatória fixa por pista (salva em IdealPistaSlider).
  AJUSTE_INFLUENCIA e AJUSTE_CONTRATO existem com PESO 0.
- FASE 2 (futuro): ligar os pesos e calibrar, garantindo que fica acertável (1-99).

---

## 4. O ERRO E O FEEDBACK (planilha n17ro)
Feedback baseado no ERRO = (valor escolhido − valor ideal), de -98 a +98:
- Negativo = ABAIXO do ideal (AUMENTAR). Positivo = ACIMA (DIMINUIR). 0 = acerto.

### 4.1 Faixas (do pior ao melhor) — referência de TOM
| Erro (abs) | Sentido | Exemplo de tom |
|---|---|---|
| ~75-98 | muito longe | "pior ajuste que já vi" |
| ~50-74 | longe | "muito longe do ideal" |
| ~30-50 | médio | "razoável, mas não dá pra correr bem" |
| ~13-28 | quase lá | "no caminho certo, melhora um pouco" |
| ~4-12 | perto | "quase bom, chegando perto" |
| ~1-3 | encostou | "bem próximo do ideal" |
| 0 | acertou | perfeito |

### 4.2 A DIREÇÃO (crucial)
As frases dão a direção: erro negativo → "aumenta"; positivo → "diminui".
A mesma distância tem frase diferente conforme o LADO.

### 4.3 ⚠️ Propriedade intelectual
Frases do n17ro são REFERÊNCIA de tom/faixa. Escrever as NOSSAS (não copiar).

---

## 5. O % DE ACERTO GERAL (planilha Malhado)
- Além das frases, mostrar uma % geral de acerto do setup (ex: "Setup: 87%").
- 100% quando todos os sliders batem o ideal; cai conforme o erro médio sobe.
- Fórmula usada: acerto = max(0, 100 − (soma_erros_abs / (98*nº_sliders)) * 100).

---

## 6. VARIÂNCIA / AJUSTE PASSO-A-PASSO (Malhado)
O jogador mexe pra cima/baixo; ao achar a frase "quase lá", reduz o passo e afina
(busca binária manual). Não precisa expor "variância" — basta feedback + % subirem
coerentemente conforme se aproxima.

---

## 7. FLUXO DO TREINO LIVRE
1. Pré-requisito: carro montado no Parc Fermé (motor/câmbio/susp travados). Se
   não montou, redireciona pra Montagem do Fim de Semana.
2. Carro simulado a 100% (sem desgaste histórico — regra 4.1.1).
3. Jogador ajusta sliders (1-99) + escolhe pneu/combustível DO TREINO.
4. "Fazer 1 volta": calcula erro de cada slider vs ideal → frase (pior slider) +
   % geral + tempo da volta (com penalidade de desgaste do pneu) + combustível.
5. Repete até: combustível zerar OU pneu estourar OU clicar "Salvar ajuste".
6. Salvar: ajuste vira o setup da corrida (AjusteSalvo) e libera o Treino Oficial.

---

## 8. RELAÇÃO COM AS OUTRAS CAMADAS (não confundir)
| Camada | O que é | Onde | Valores |
|---|---|---|---|
| PEÇAS (modelos) | Motor/câmbio/susp/pneu/comb | Parc Fermé + Estratégia | 50-900 |
| AJUSTE FINO | Sliders do setup | Treino Livre | 1-99 (ideal secreto) |
| INFLUÊNCIA | Peso do componente na pista | Dado da pista (Ayres) | 5-15 (10 neutro) |

---

## 9. DADOS TÉCNICOS DE APOIO (das planilhas)
- Desgaste por temperatura: 20°C neutro; ±0,01 por grau.
- Consumo por modelo de motor: modelo maior consome mais.
- Durabilidade de pneu por modelo: MI-50 ~111km ... MI-900 ~243km (maior dura mais).
- Tanque máximo: 150 litros. Volta de qualy consome 1 volta de combustível.
- Rampa de desgaste no tempo (carro.py, em DESGASTE 0→100; na tela mostrar VIDA 100→0):
  0-70% desgaste: sem penalidade; 70-85 leve; 85-95 médio; 95-100 pesado; 100 estoura.

---

## 10. RESUMO (elevator pitch)
No Treino Livre, cada pista tem valores ideais secretos (1-99) para os ajustes do
carro. O jogador tenta adivinhá-los: faz uma volta, o piloto dá uma frase indicando
quão longe está e pra que lado mexer, e um medidor mostra a % geral de acerto.
Ajusta e repete até chegar perto (ou acabar pneu/combustível), então salva. Quanto
mais perto do ideal, mais rápida a volta. É camada SEPARADA das peças (50-900) e
das influências da pista (5-15).
