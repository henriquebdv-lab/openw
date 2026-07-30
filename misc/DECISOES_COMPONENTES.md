# DECISÕES DE COMPONENTES — Balanceamento, Progressão e Identidade

> Anotações do que descobrimos analisando a Planilha Ayres + n17ro, e as decisões
> de design tomadas em conversa. Base pros prompts de implementação.
> Última atualização: 30/07/2026

---

## 🎯 IDENTIDADE DO JOGO (a regra que filtra todas as outras)

> **"Aqui é ESTRATÉGIA, lá é MANAGER."** — Henrique

- **O jogador É o PILOTO.** Não é um manager que contrata pilotos.
- Foco total em **ESTRATÉGIA DE CORRIDA**: setup, pneu, combustível, stints,
  parc fermé, leitura de pista.
- ❌ **NÃO entra:** contrato de piloto, habilidades de piloto, treinamento de
  piloto, mercado de pilotos, gestão de staff/RH. Isso é manager (GPRO, F1 Manager).
- ✅ **Filtro pra ideias novas:** "isso serve à estratégia do piloto, ou é gestão
  de manager?" Se for manager, não entra.
- Isso DIFERENCIA o jogo: o mundo já tem managers; não tem um jogo de estratégia
  de piloto no estilo do Estratégia F1 antigo.

---

## 🧭 O QUE COMPÕE O TEMPO DE VOLTA HOJE (foto real do carro.py)

### ⬇️ Deixam MAIS RÁPIDO (subtraem tempo)
| Componente | De onde vem |
|---|---|
| Motor | `potencia_efetiva_motor() × influência_motor` |
| Pneu | `pneu.performance × influência_pneu` |
| Chassi | `chassi.performance` (engenheiro/desenvolvimento) |
| Aerodinâmica | `performance_aero` (engenheiro/desenvolvimento) |
| Câmbio | `cambio.performance × influência_câmbio` |
| Suspensão | `suspensao.performance × influência_suspensão` |
| Engenheiro | `eficiencia_exata × BONUS × influência` |

### ⬆️ Deixam MAIS LENTO (somam tempo)
| Fator | O que é |
|---|---|
| Erro de letra | câmbio/suspensão que não casam com a pista (× 0.3) |
| Pneu errado | pneu fora da condição da pista (× 1.0) |
| Delta do modelo | o 50-900 (baixo = rápido, alto = lento) |
| Ruído aleatório | `random.gauss` por volta |
| Desgaste do pneu | penalidade a partir de 70% de desgaste |

### 🔴 FURO CONFIRMADO
- **O COMBUSTÍVEL NÃO AFETA O TEMPO HOJE.** Só define quantas voltas dá.
  Carregar 150L ou 50L dá o MESMO tempo de volta. Está errado.

---

## ⛽ DECISÃO: PESO DO COMBUSTÍVEL (encerra pendência #5 do regras.md)

- O combustível passa a ter **PESO que influencia o tempo de volta**.
- Carro **cheio = mais lento**; conforme queima, fica **mais rápido**.
- Cria estratégia real: largar leve (rápido, para antes) vs pesado (lento no
  início, menos paradas).
- ⚠️ Implementar no `tempo_base()`/`tempo_com_variacao()`: acréscimo proporcional
  ao combustível a bordo naquela volta.
- ❓ Calibrar: quantos segundos por X litros (testar, não inventar).

---

## 🔢 FORNECEDORES: 30 + NÍVEL 1..30

- De 100 → **30 fornecedores por categoria**.
- Cada fornecedor tem **NÍVEL de 1 a 30** (como na planilha), VISÍVEL pro jogador.
- A palavra "tier" NÃO se usa mais pra fornecedor → agora é **nível**.
- Valor do contrato conforme o nível + a curva descoberta.
- **Preço SUAVE/linear** entre níveis (pouca variação entre vizinhos).
- Na tela: só **nome + nível + preço**. Nada de "fraco/forte/barato/caro".

---

## 🏎️ MOTOR — padrão descoberto (confirmado com 20 fornecedores da Ayres)

2 stats: **Potência (HP)** e **Consumo (Lt/km)**.

- **Potência** sobe com o modelo (xx-50 ~350 HP → xx-900 ~460 HP).
- Na Ayres os fornecedores vinham em "trios": a cada 3, a potência subia ~15 HP.
  Dentro do trio, potência ~igual.
- **Consumo** sobe com o modelo (xx-50 ~0.70 → xx-900 ~1.3 Lt/km).
- Cada fornecedor tem um PERFIL de consumo:
  - BEBERRÃO (~0.70 no xx-50)
  - ECONÔMICO / "achado" (~0.55 no xx-50 = ~21% menos), com a MESMA potência
- Diferença de consumo maior nos modelos baixos (27% no xx-50), menor nos altos (13%).

**Trade-off:** modelo alto = mais forte MAS bebe mais.

---

## 🛞 PNEU — padrão descoberto + ajuste crítico

Stats: **Durabilidade (km)**, **Condição**, **Fator temperatura**, **Performance**.

- **Durabilidade** sobe com o modelo: xx-50 ~112 km → xx-900 ~248 km.
  Variação por fornecedor (~108-118 no xx-50) = o "achado" dura mais.
- **Condição** pelo modelo: 50-500 seco · 600-700 molhada · 800-900 encharcada.
- **Fator temperatura**: 20°C neutro; cada grau ±0.01 (quente gasta mais rápido).
- 🔴 **PERFORMANCE (decisão do Henrique):** o pneu PRECISA de um número que
  influencie o TEMPO DE VOLTA. Senão não faz sentido pneus que duram igual e
  custam diferente.
  - **Trade-off:** macio (xx-50) rápido mas dura pouco · duro (xx-500) mais lento
    mas dura muito. O "achado" é o equilíbrio bom.

---

## 🐛 BUG NO CÓDIGO (modelos_componente.py)

- Hoje `fator_consumo` == `fator_desgaste` (o MESMO número). ERRADO.
- Consumo (motor) e desgaste (pneu) são coisas diferentes, com curvas diferentes.
- Também: todos os componentes usam UMA curva genérica. Precisa de curvas
  específicas por componente (motor, pneu), baseadas na Ayres.

---

## ⚡ SISTEMA DE TIER — UPGRADES TEMPORÁRIOS (ideia nova, inspirada no GPRO/WoW)

### O conceito
O jogador pode **comprar upgrades (tiers)** pra melhorar peças durante a temporada.
Aqui a palavra "tier" tem lugar certo (upgrade progressivo, como no WoW).

### Peças que a equipe FABRICA (podem receber tier)
1. Motor
2. Freio  *(estrutura pode ser criada agora; ativa quando o freio sair do DLC)*
3. Suspensão
4. Câmbio
5. Aerodinâmica
6. Chassi

### 🔒 REGRA DE LIMITE (o freio de balanceamento)
- Só **2 peças** podem ter tier ativo ao mesmo tempo.
- Somando no **máximo 5 upgrades** entre as duas.
- Ex.: 3 no motor + 2 no chassi = 5 ✅
- Se ativou motor e câmbio, NÃO pode ativar na suspensão ❌

### 💰 Economia
- **Caro**, custo **exponencial** nos tiers altos.
- ⏳ **TEMPORÁRIO**: não passa pra próxima temporada (zera na virada).
- Dreno recorrente de dinheiro — vantagem no curto prazo, sem bola de neve.

### 📈 O que melhora
- Multiplicador de eficiência sobre o que a peça já faz (ex.: até ~125%).
- Motor → mais potência ✅ · Suspensão/Câmbio → mais performance ✅ ·
  Chassi/Aero → mais performance ✅
- ⛽ Combustível NÃO entra no tier.

### 🎯 Por que é bom design
- Dá destino pro dinheiro (loop de progressão que faltava).
- Diferencia jogadores do mesmo nível por DECISÃO, não por sorte.
- Combina com a INFLUÊNCIA da pista (motor influência 15 → vale investir lá).
- Duas estratégias econômicas:
  - **Tier** = investe agora, colhe NESTA temporada (some depois)
  - **Engenheiro** = investe agora, colhe na PRÓXIMA temporada

---

## 🛑 FREIO — estrutura no banco

- Quando for mexer no banco, **criar a estrutura do freio** (tabela/campos),
  mesmo ficando DORMENTE.
- Motivo: evita ter que recriar o banco de novo quando o DLC do freio for ativado.
- O freio **não funciona** ainda (não afeta tempo, não entra no treino livre).

---

## 🎮 INSIGHTS DO GPRO (referência analisada)

- O ajuste do carro lá vai de **1 a 999** com apenas **8 voltas** pra acertar.
  → Muito mais difícil. O nosso (1-99, com voltas limitadas pelo combustível) é
  mais amigável — o Henrique chegou a 99,4% sem planilha. Nosso design é melhor
  nesse ponto.
- No GPRO **o consumo de combustível não fica claro** pro jogador — o mesmo
  problema que identificamos aqui. Queremos fazer MELHOR (dados visíveis).
- O GPRO é MANAGER (contrato/habilidades/treino de piloto). O nosso é ESTRATÉGIA
  (o jogador é o piloto). Ver seção IDENTIDADE.

---

## 📋 A FAZER (ordem de implementação)

### Prioridade 1 — Balanceamento base (prompt já pronto)
1. Reduzir fornecedores 100 → 30, com nível 1..30 visível.
2. Preço suave/linear por nível.
3. MOTOR: curva de potência + consumo (dados Ayres).
4. PNEU: durabilidade + performance + separar fator_consumo de fator_desgaste.
5. Manter achado/furada no seed (variação pequena de preço).
6. (se mexer no banco) criar a estrutura do FREIO, dormente.

### Prioridade 2 — Peso do combustível
7. Combustível a bordo passa a somar tempo. Calibrar com teste.

### Prioridade 3 — Sistema de Tier
8. Estrutura no banco (peças, nº de tiers, custo, validade = temporada).
9. Regra de limite (2 peças / 5 upgrades no total).
10. Tela pro jogador comprar/ver os tiers ativos.
11. Zerar os tiers na virada da temporada.

### ⏭️ Próximas peças a analisar (uma de cada vez)
- SUSPENSÃO (próxima) · depois: câmbio, combustível, engenheiro.

---

## 🎨 TELA DE ESTRATÉGIA (estilo F1 Manager 24) — anotado
- Adaptar a timeline de stints: cada stint com **cor própria** (pedido e ainda
  não feito), barras de desgaste/janela de parada.
- Frente separada (visual), não depende do balanceamento.
