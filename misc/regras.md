# Open Wheel Strategy — Regras Canônicas

> **Como usar este arquivo:** cole ele na primeira mensagem de qualquer chat novo
> com a IA para que ela recupere todo o contexto do jogo. Também cole o
> `openwheel_tudo.txt` (código atual) e os templates que forem relevantes.
>
> **Convenção:**
> - 📜 CANÔNICO = está no manual (`como.txt`) ou nas planilhas de referência.
> - 🎨 NOSSA VERSÃO = decidido em conversa, virou regra oficial da nossa versão.
> - ❓ PENDENTE = ainda precisa ser decidido.
>
> **Sempre que uma regra CANÔNICA for contrariada, a IA deve PARAR e avisar.**

---

## 0. FONTES DA VERDADE

- `como.txt` — manual do Estrategia F1 (Preparar Carro, Treino Livre, Estratégia, Guia do Iniciante, Tabelas de Dados, Dicas)
- `estrategiaf1_2005_byn17ro.xls` — tabelas de temperatura/desgaste, consumo de motores, frases de feedback do piloto por range -98 a +98
- `EF1_Malhado_V0.10.TL-Beta.xls` — sistema de variância pra ajuste fino do treino livre
- `Planilha Ayres (v5.12).xls` — lista completa das 48 pistas (nome, tamanho, voltas, categoria ideal câmbio/suspensão, entrada/saída boxes, influências M/C/S/P/G/E/F). **Tabela extraída na íntegra na seção 8.7.**
- `Sem título 1.docx` — histórico de decisões do projeto (dia 7)

## 0.1 ⚠️ RESTRIÇÃO DE PROPRIEDADE INTELECTUAL

**A nossa versão NÃO pode usar:**

- Nome "Estratégia F1" ou similares (usar sempre "Open Wheel Strategy")
- Nomes de fornecedores canônicos: ZIPADNOR, POKGAST, VOECONO, ZURK, MIDILU, CEXUQE, WOVADA, COTASU, JOVOLT, xx-50 até xx-900 como nome de produto
- Nomes de pilotos, engenheiros e frases de feedback específicas herdados de outros jogos
- Nome dos autores das planilhas (Ayres, N17RO, Malhado)
- Referências a "F1" ou "Fórmula 1" (usar "monoposto", "openwheel")

**A nossa versão PODE usar:**

- Sistemas de pontos e valores (padrões públicos)
- Fórmulas matemáticas
- Estruturas de dados (níveis, categorias A-J, etc.)
- Nomes de pistas reais (fatos históricos, ex: Red Bull Ring, Interlagos)
- Dados técnicos objetivos de pistas reais

---

## 1. ORÇAMENTO E ECONOMIA

### 1.1 📜 Orçamento inicial

- Valor padrão: **R$ 55.000**
- Configurável pelo admin em `admin_configuracoes`
- **NUNCA** definido pelo jogador
- Fonte: `como.txt` ("Você tem em caixa R$55.000,00")

### 1.2 📜 Contratos anuais

- Motor, combustível, pneu, câmbio, suspensão **e engenheiro** são **contratos anuais obrigatórios**
- 🎨 **Nossa versão:** engenheiro **NÃO é opcional** — conta nova já vem com **Engenheiro nível 1** contratado automaticamente
- **Não podem ser rescindidos durante a temporada** (contratos anuais)
- Fonte: `como.txt` + decisão hoje
- ⚠️ **Ajuste de código pendente:** hoje o `equipes.html` mostra engenheiro como "OPCIONAL" com opção "Sem engenheiro". Precisa mudar pra obrigatório.

### 1.3 📜 Custo por corrida

- **custo_montagem** = custo por corrida das peças escolhidas (motor+câmbio+suspensão+pneu+combustível), debitado antes de cada corrida
- **custo_temporada** = custo do contrato anual, debitado uma vez ao assinar
- Fonte: `como.txt` (Fluxo Comprar / Contratos)

### 1.4 📜 Premiação por corrida (individual)

| Pos | Pts | Prêmio      | Pos | Pts | Prêmio    |
|-----|-----|-------------|-----|-----|-----------|
| 1º  | 40  | R$ 12.000   | 11º | 14  | R$ 7.700  |
| 2º  | 35  | R$ 11.000   | 12º | 12  | R$ 7.400  |
| 3º  | 32  | R$ 10.500   | 13º | 10  | R$ 7.100  |
| 4º  | 29  | R$ 10.000   | 14º | 8   | R$ 6.800  |
| 5º  | 26  | R$ 9.500    | 15º | 6   | R$ 6.500  |
| 6º  | 24  | R$ 9.200    | 16º | 5   | R$ 6.200  |
| 7º  | 22  | R$ 8.900    | 17º | 4   | R$ 6.000  |
| 8º  | 20  | R$ 8.600    | 18º | 3   | R$ 5.800  |
| 9º  | 18  | R$ 8.300    | 19º | 2   | R$ 5.650  |
| 10º | 16  | R$ 8.000    | 20º | 1   | R$ 5.500  |

- Quem abandona: 0 pontos e 0 prêmio
- ⚠️ **A REVER (marcado por Henrique):** talvez seja muito punitivo. Opções pra decidir:
  - **A)** Mantém 0/0 (fiel ao manual)
  - **B)** 0 pontos mas prêmio mínimo (ex: R$ 3.000 fixo pra cobrir custos da corrida)
  - **C)** Prêmio proporcional a quantas voltas completou antes de abandonar
  - **D)** Pontos zerados mas prêmio da última posição real
- Fonte: `como.txt` + `pontuacao.py`

### 1.5 📜 Premiação final por temporada (individual)

| Pos | Prêmio      | Pos | Prêmio     |
|-----|-------------|-----|------------|
| 1º  | R$ 100.000  | 11º | R$ 35.000  |
| 2º  | R$ 85.000   | 12º | R$ 33.000  |
| 3º  | R$ 75.000   | 13º | R$ 31.000  |
| 4º  | R$ 70.000   | 14º | R$ 29.000  |
| 5º  | R$ 65.000   | 15º | R$ 27.000  |
| 6º  | R$ 60.000   | 16º | R$ 25.000  |
| 7º  | R$ 55.000   | 17º | R$ 23.000  |
| 8º  | R$ 50.000   | 18º | R$ 22.000  |
| 9º  | R$ 45.000   | 19º | R$ 21.000  |
| 10º | R$ 40.000   | 20º | R$ 20.000  |

- Fonte: `como.txt` — **❓ não implementado ainda**
- Nota: a planilha Ayres também traz premiação por EQUIPE (1º = R$ 40.000 ... 20º = R$ 250) e por posição de largada, pra fase futura de duplas/equipes.

---

## 2. FORNECEDORES

### 2.1 🎨 Estrutura (nossa versão)

- **100 fornecedores por categoria** (motor, combustível, pneu, câmbio, suspensão, engenheiro)
- **10 tiers × 10 fornecedores por tier**
- Dentro de cada tier: 2 "furadas", 2 "achados", 6 "normais" — embaralhados, jogador não sabe qual é qual
- Numeração `#1` (mais barato) até `#100` (mais caro) — reflete só o custo, NÃO a qualidade
- Nomes gerados aleatoriamente (nada de ZIPADNOR/POKGAST)
- Fonte: `Sem título 1.docx` + `seed_fornecedores.py`

### 2.2 📜 Chassi e Aerodinâmica

- **NÃO são fornecedores contratados**
- São projetados pelo Engenheiro contratado
- Jogador novo recebe chassi + aero nível 1, 100% aplicado, **grátis**
- 🎨 Jogador novo também já vem com **Engenheiro nível 1 contratado** (ver regra 1.2)
- Fonte: `como.txt` + decisão do dia 7 + ajuste hoje

### 2.3 📜 Freio

- Existe no jogo original com 5º slot de ajuste no treino livre
- 🎨 **Nossa decisão:** freio fica como **DLC futuro**, NÃO entra no MVP
- MVP com 6 componentes: Motor, Câmbio, Suspensão, Pneu, Combustível, Engenheiro
- Pistas NÃO usam a coluna F por enquanto (mas o dado existe na Ayres, ver 8.7)
- Fonte: `Sem título 1.docx` (dia 7)

---

## 3. TREINO LIVRE

### 3.1 📜 Manual original

- 5 ajustes: **Câmbio, Suspensão, Freio, Aerofólio Dianteiro, Aerofólio Traseiro**, cada um 1-99
- Cada ajuste tem um valor ideal por pista (o jogador não sabe qual)
- Piloto faz 1 volta → sistema mostra tempo + frase de feedback → jogador ajusta → nova volta
- Repete até acabar combustível OU pneu OU jogador salvar
- **Botão "Salvar ajuste"** — o ajuste salvo é o que vai pra corrida
- Fonte: `como.txt` (Treino Livre)

### 3.2 ❓ Adaptação pra nossa versão (PENDENTE)

- Freio é DLC (2.3), então sobram 4 ajustes (câmbio, susp, aeroD, aeroT)? Ou 3? Ou mantém 5 com freio desabilitado?
- **Decisão: aguardando**

### 3.3 📜 Feedback do piloto

- Frases originais (nossas), por faixa de erro (-98 a +98)
- Faixas: perfeito (0-3), quase (4-12), leve (13-28), médio (29-50), grande (51-74), extremo (75-98)
- Vocabulário difere por componente
- Fonte: `feedback_piloto.py` + planilha n17ro (a planilha tem 99 frases numeradas de exemplo — usar só como inspiração, escrever as nossas)

### 3.4 📜 Voltas do treino livre

- Limite: combustível carregado E desgaste do pneu
- Se combustível zerar OU pneu chegar a 100%, treino acaba
- Pneu e combustível do treino livre são diferentes dos da corrida
- Fonte: `como.txt`

### 3.5 🎨 Fluxo interativo (DECIDIDO)

- **Opção A:** Cada clique = 1 volta.
- Ajusta sliders → "Fazer 1 volta" → vê tempo + feedback + desgaste/combustível → ajusta → repete.
- Encerra quando: combustível zera OU pneu estoura OU jogador clica "Salvar ajuste".
- Fonte: decisão hoje

### 3.6 ❓ Salvar o ajuste (PENDENTE)

- Tabela nova (`AjusteSalvo`)? 1 por equipe por pista? ou por equipe atual?
- Ajuste salvo vira setup padrão da próxima corrida
- **Decisão: aguardando**

---

## 4. TREINO OFICIAL E ESTRATÉGIA

### 4.1 📜 Treino Oficial

- Só pode ser feito **depois** de salvar o ajuste do treino livre
- Motor, câmbio e suspensão já estão montados
- Jogador define o **pneu** e **combustível** pra corrida + **volta do 1º pit stop**
- É uma volta única (qualifying)
- Fonte: `como.txt`

### 4.1.1 🎨 Treino Livre assume carro em 100% (NOSSA VERSÃO)

- Durante o Treino Livre, simula o carro como se **todos os componentes estivessem em 100%** (novos, sem desgaste)
- Foco em descobrir o **setup ideal** sem interferência de desgaste histórico
- Ao fechar, jogador salva a **estratégia** (ajustes + escolhas)
- Depois de salvar, **libera botão** que abre o Treino Oficial com **sugestão do melhor combustível** (baseado no consumo medido no treino livre)
- Fonte: decisão hoje

### 4.1.2 ❓ Horário programado do Treino Oficial (PENDENTE)

- Ideia: Treino Oficial de todos roda num **horário programado** (ex: 19h do dia da corrida)
- Manual: exibição ao vivo às 19h; site bloqueia preparação entre 19h-21:30h no dia da corrida
- **Perguntas em aberto:** como fica no modo solo? precisa scheduler (APScheduler)? roda automático se offline? bloqueia preparação?
- **Decisão: aguardando**

### 4.1.3 🎨 Interface de estratégia de pit stops (DECIDIDO)

- Interface com combos progressivos:
  1. Define **combustível de largada** (litros)
  2. **1º pit:** combo com **todas as voltas** da corrida
  3. **2º pit:** combo com apenas as **voltas restantes** (após o 1º)
  4. Repete pro 3º, 4º, 5º pit (original tinha corridas com 3-4 pits)
  5. **"Parar no fim"** sempre disponível
- Cada pit: escolhe modelo de pneu (50-900) + combustível a adicionar (litros, pode ser 0)
- Fonte: decisão hoje + `como.txt`

### 4.2 📜 Estratégia de Corrida

- Última etapa antes da corrida
- Define pneu e combustível de cada pit
- "Parar no Fim" pra não fazer mais paradas
- Convenção: pit na volta 15 = entra no fim da 14, sai no início da 15
- Fonte: `como.txt`

### 4.3 🔮 Estrategista contratado (DLC FUTURO)

- Original: opcional, R$ 200, dá sugestão de estratégia (não muito boa)
- 🎨 **Nossa decisão:** vira **DLC/upgrade futuro**, NÃO implementar nas primeiras versões
- Status: código parcial em `estrategia.py` pode ficar dormente
- Fonte: `como.txt` + decisão hoje

---

## 5. CORRIDA

### 5.1 📜 Volta a volta

- Cada volta: tempo = setup + fornecedores + influências da pista + desgaste do pneu + variação aleatória
- 🎨 **Trechos de temperatura de TAMANHO VARIÁVEL** (não 25% fixo). Exemplo real: trecho molhado curto de 7-8 voltas no meio da corrida
- Isso gera estratégia rica (ex: Henrique venceu parando no meio de trecho molhado curto pra trocar seco→seco enquanto adversários fizeram 2 pits seco→molhado→seco)
- 🎨 1ª versão pode usar 25% fixo, mas **o modelo de dados deve suportar trechos variáveis desde o início**
- Consumo e desgaste debitados por volta

### 5.2 📜 Pit stop

- Base: tempo específico da pista (`tempo_pit_stop_segundos`) — ver valores canônicos em 8.7
- Reduzido pelo **Treinamento de Boxes** (0-100%)
- Fonte: `como.txt` + `corrida.py`

### 5.3 📜 Abandono

- **Pneu estoura** (desgaste ≥ 100%) = abandono imediato
- 🎨 **Combustível zera na pista** = **abandono imediato** (punitivo, culpa do planejamento). NÃO é pit automático.
- **Quebra mecânica** = sorteio no início: sem treino 10%, treino 100% = 2%, escala linear
- Fonte: `como.txt` + `Sem título 1.docx` + decisão hoje

### 5.4 📜 Combustível

- Tanque máximo: **150 litros**
- 🎨 Se acabar na pista: **abandono** (ver 5.3)
- Consumo também na volta de qualifying (1 volta descontada)
- ⚠️ **Ajuste de código pendente:** `corrida.py` provavelmente ainda faz pit automático, precisa virar abandono

---

## 6. DESGASTE DO PNEU

### 6.1 📜 Fórmula base

- Desgaste/volta = `desgaste_base × fator_temperatura × fator_engenheiro × fator_modelo`
- Temperatura: referência 20°C = 0; cada grau ±1% (`DESGASTE_POR_GRAU_FRACAO = 0.01`)
- Fonte: `constantes.py` + `como.txt`

### 6.2 📜 Tabela de referência (n17ro)

| Temp °C | Desgaste extra m/km |
|---------|---------------------|
| -2°C    | -220 m/km           |
| 0°C     | -200 m/km           |
| 10°C    | -100 m/km           |
| 20°C    | 0 (neutro)          |
| 30°C    | +100 m/km           |
| 40°C    | +200 m/km           |
| 45°C    | +250 m/km           |

- 🎨 Nossa versão usa fórmula proporcional simplificada

### 6.3 📜 Penalidade por desgaste

- 0-70%: nenhuma · 70-85%: leve (~1.5s) · 85-95%: médio (~5s) · 95-100%: pesado (~12s) · ≥100%: estoura (15s + abandono)
- Fonte: `carro.py`

---

## 7. CATEGORIAS A-J E MODELOS xx-50/xx-900

### 7.1 📜 Mapeamento

| Modelo | Letra | Uso |
|--------|-------|-----|
| xx-50  | A | Câmbio/Suspensão (mais leve) |
| xx-100 | B | |
| xx-200 | C | |
| xx-300 | D | |
| xx-400 | E | |
| xx-500 | F | |
| xx-600 | G | Molhada (pneu) |
| xx-700 | H | |
| xx-800 | I | Encharcada (pneu) |
| xx-900 | J | (mais pesado) |

- Câmbio/Suspensão: cada pista pede uma letra ideal (ver 8.7)
- Pneu: 50-500 = seco, 600-700 = molhada, 800-900 = encharcada
- Fonte: `como.txt`

### 7.2 🎨 Como aplicamos na nossa versão

- 1 fornecedor por temporada por categoria; a cada corrida escolhe o modelo (50-900) de cada componente
- Modelo baixo (50): mais rápido, rende/dura menos · Modelo alto (900): mais lento, rende/dura mais
- Câmbio/susp: modelo define a letra A-J que casa com a pista · Pneu: modelo define condição (seco/molhada/encharcada)
- Fonte: `Sem título 1.docx` + `modelos_componente.py` + `carro.py`

### 7.3 🎨 Durabilidade dos pneus (KM por modelo) — DECIDIDO

- Cada modelo de pneu (50-900) tem durabilidade em km. Referência n17ro (fornecedor Midilu):
  - MI-50: 111 · MI-100: 134 · MI-200: 153 · MI-300: 166 · MI-400: 186 · MI-500: 202 · MI-600: 211 · MI-700: 237 · MI-800: 230 · MI-900: 243 (km)
- 🎨 **Nossa versão:** tabela de km **padrão por modelo**, com variação **muito pequena ou zero** entre fornecedores (cortamos a bolsa de valores, então a diferença fica no preço/desempenho, não na durabilidade)
- Fonte: n17ro + decisão hoje

### 7.4 🎨 Mercado financeiro / Bolsa de valores — CORTADO

- 🎨 **NÃO** implementar. Preços fixos por tier.
- Fonte: decisão hoje

---

## 8. PISTAS

### 8.1 📜 Origem dos dados

- 25 pistas importadas do TUMFTM/racetrack-database (LGPL-3.0, OpenStreetMap)
- Traçado SVG + extensão em km do CSV
- Nomes canônicos de exibição (ex: "Red Bull Ring")
- Fonte: `pistas_reais_db.py` + `importar_todas_pistas.py`

### 8.1.1 🎨 Dobrar catálogo com pistas espelhadas — DECIDIDO

- Objetivo: chegar a **50 pistas** dobrando as 25 atuais
- Cada pista real gera uma versão espelhada (traçado invertido, SVG virado horizontalmente)
- **Influências invertidas:** na espelhada, **Câmbio e Suspensão trocam de valor** entre si — tanto a **letra ideal** (câmbio↔suspensão) quanto a **influência** (C↔S)
- Motor, pneu, combustível, engenheiro permanecem iguais
- Nome da convenção a definir (item pendente)
- Implementação: o `popular_categorias_pistas.py --espelhadas` já trata isso
- Fonte: decisão hoje

### 8.2 📜/⚠️ Influências — RANGE EM CONFLITO

- Cada pista tem influência para: Motor, Câmbio, Suspensão, Pneu, Combustível (G), Engenheiro (10 = neutro)
- Valor > 10 = componente importa MAIS; < 10 = importa MENOS
- ⚠️ **CONFLITO ABERTO:** o dia 7 definiu range **7-15**, mas a Planilha Ayres canônica usa range **5-15** (ex: Detroit P=15, Fuji S=5, Shangai E=5/G=6, Monaco M=6/G=15).
- **DECISÃO PENDENTE (item 11 da seção 14):**
  - **A)** usar valores reais Ayres (5-15)
  - **B)** clampar em 7-15 (`popular_categorias_pistas.py --clamp`)
  - **C)** reescalar
- Fonte: `como.txt` + `Sem título 1.docx` + Planilha Ayres

### 8.3 📜 Categoria ideal (câmbio/suspensão) — CAUSA DO BUG IDENTIFICADA

- Cada pista tem 1 letra ideal pra câmbio e 1 pra suspensão (A-J). Escolher o modelo certo (50-900) = acerto perfeito no tempo de volta
- 🐛 **BUG ATUAL:** todas as pistas aparecem "câmbio A / susp. B" porque as categorias **nunca foram populadas** (ficaram no default)
- ✅ **SOLUÇÃO (Opção A, decidido hoje):** popular com os dados canônicos da Ayres via `popular_categorias_pistas.py`
- Pistas sem correspondência na Ayres (modernas): definir lógica caso a caso depois
- Fonte: `como.txt` + Planilha Ayres + decisão hoje

### 8.4 📜 Influências canônicas — agora TODAS conhecidas

- Antes só o A1-Ring estava confirmado. Agora temos as **48 pistas** da Ayres (ver 8.7)
- A1-Ring (Red Bull Ring): M9 C8 S7 P11 G12 E14, câmbio A / susp B, boxes 14s ✅ confirmado

### 8.5 📜 Cálculo de voltas da corrida

- Distância alvo 290-320 km, máx 79 voltas: `voltas = round(305 / extensão_km)`, limitado a 79
- Fonte: `pistas_reais_db.py`
- Nota: a Ayres traz o nº de voltas de referência por pista (ver 8.7), útil pra validar

### 8.6 📜 Temperatura por trecho

- 4 trechos de tamanho variável (ver 5.1), cada um com temperatura e mm de chuva próprios
- Fonte: `como.txt` + admin_pista_editar

### 8.7 📜 TABELA CANÔNICA DAS 48 PISTAS (Planilha Ayres v5.12)

Formato: **Câm** = câmbio ideal · **Sus** = suspensão ideal · **Box** = tempo boxes (s) · influências **M C S P G E** (F/freio omitido, é DLC) · **km** e **Voltas** de referência.

| # | Pista (Ayres) | Câm | Sus | Box | M | C | S | P | G | E | km | Voltas |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|--:|--:|
| 1 | A1-Ring, Áustria (=Red Bull Ring) | A | B | 14 | 9 | 8 | 7 | 11 | 12 | 14 | 307.1 | 71 |
| 2 | Sakhir, Bahrein | I | F | 12 | 12 | 14 | 11 | 9 | 7 | 10 | 304.5 | 57 |
| 3 | Aida, Japão | B | F | 11 | 11 | 13 | 9 | 12 | 7 | 8 | 277.7 | 75 |
| 4 | Barcelona, Espanha | D | H | 14 | 9 | 10 | 12 | 9 | 10 | 11 | 307.3 | 65 |
| 5 | Bathurst, Austrália | G | A | 11 | 9 | 8 | 13 | 14 | 10 | 7 | 310.6 | 50 |
| 6 | Brands Hatch, Grã-Bretanha | F | H | 17 | 6 | 9 | 12 | 13 | 11 | 10 | 315.5 | 75 |
| 7 | Brno, Rep. Tcheca | C | F | 14 | 7 | 11 | 9 | 7 | 13 | 14 | 307.1 | 57 |
| 8 | Buenos Aires, Argentina | J | I | 13 | 13 | 9 | 11 | 7 | 11 | 9 | 306.6 | 72 |
| 9 | Detroit, EUA | A | B | 10 | 8 | 6 | 9 | 15 | 12 | 10 | 253.4 | 63 |
| 10 | Dijon, França | E | H | 17 | 11 | 9 | 8 | 14 | 6 | 12 | 307.0 | 79 |
| 11 | Donington, Grã-Bretanha | A | D | 12 | 7 | 9 | 13 | 8 | 14 | 10 | 305.7 | 76 |
| 12 | Estoril, Portugal | H | I | 15 | 11 | 8 | 12 | 8 | 13 | 9 | 305.2 | 70 |
| 13 | Hockenheim, Alemanha | B | F | 11 | 13 | 8 | 10 | 13 | 8 | 9 | 307.1 | 45 |
| 14 | Hungaroring, Hungria | I | I | 11 | 12 | 14 | 6 | 13 | 8 | 8 | 305.5 | 77 |
| 15 | Indianapolis, EUA | D | C | 17 | 8 | 8 | 8 | 15 | 12 | 10 | 306.6 | 73 |
| 16 | Interlagos, Brasil | B | E | 12 | 11 | 13 | 11 | 11 | 6 | 8 | 305.9 | 71 |
| 17 | Jacarepaguá, Brasil | E | B | 11 | 11 | 10 | 7 | 10 | 9 | 11 | 306.9 | 61 |
| 18 | Jerez, Espanha | J | A | 12 | 9 | 11 | 15 | 11 | 8 | 7 | 306.4 | 69 |
| 19 | Kyalami, África do Sul | G | F | 10 | 14 | 8 | 8 | 10 | 13 | 8 | 306.8 | 72 |
| 20 | Long Beach, EUA | F | A | 14 | 7 | 11 | 11 | 14 | 9 | 9 | 258.7 | 79 |
| 21 | Magny Cours, França | C | B | 12 | 12 | 6 | 12 | 8 | 13 | 9 | 305.8 | 72 |
| 22 | Melbourne, Austrália (=Albert Park) | A | H | 11 | 10 | 7 | 7 | 14 | 12 | 11 | 307.6 | 58 |
| 23 | Monte Carlo, Mônaco | E | G | 12 | 6 | 9 | 8 | 13 | 15 | 10 | 262.8 | 78 |
| 24 | Montreal, Canadá (=Gilles Villeneuve) | B | D | 11 | 12 | 10 | 7 | 8 | 12 | 12 | 305.0 | 69 |
| 25 | Monza, Itália | A | B | 17 | 14 | 14 | 8 | 11 | 6 | 8 | 306.7 | 53 |
| 26 | Nogaro, França | A | E | 13 | 13 | 11 | 14 | 9 | 7 | 7 | 287.1 | 79 |
| 27 | Nurburgring, Europa | F | F | 11 | 12 | 14 | 6 | 6 | 9 | 14 | 305.2 | 67 |
| 28 | Oesterreichring, Áustria | G | C | 14 | 7 | 7 | 14 | 12 | 12 | 10 | 308.9 | 52 |
| 29 | Paul Ricard, França | C | G | 13 | 11 | 12 | 6 | 12 | 9 | 11 | 305.0 | 79 |
| 30 | Phoenix, EUA | B | B | 13 | 14 | 12 | 6 | 6 | 13 | 11 | 293.9 | 79 |
| 31 | Ruapuna, Nova Zelândia | C | E | 17 | 6 | 14 | 13 | 7 | 8 | 12 | 280.4 | 78 |
| 32 | San Marino, Imola | H | D | 8 | 11 | 9 | 10 | 8 | 11 | 11 | 305.6 | 62 |
| 33 | Sepang, Malásia | H | A | 16 | 9 | 6 | 15 | 10 | 11 | 10 | 310.4 | 55 |
| 34 | Silverstone, Grã-Bretanha | F | C | 15 | 10 | 10 | 9 | 9 | 7 | 15 | 308.3 | 60 |
| 35 | Spa, Bélgica | E | G | 9 | 6 | 7 | 13 | 14 | 11 | 9 | 306.6 | 44 |
| 36 | Suzuka, Japão | J | A | 10 | 11 | 14 | 10 | 8 | 11 | 7 | 301.6 | 53 |
| 37 | Tacna, Peru | I | I | 18 | 10 | 13 | 10 | 8 | 13 | 7 | 264.5 | 79 |
| 38 | Fuji Speedway, Japão | G | H | 13 | 13 | 12 | 5 | 10 | 7 | 8 | 314.8 | 69 |
| 39 | Interlagos 89, Brasil | E | E | 12 | 13 | 15 | 9 | 11 | 7 | 5 | 500.7 | 64 |
| 40 | Shangai, China | H | B | 9 | 15 | 7 | 11 | 8 | 6 | 5 | 305.3 | 56 |
| 41 | Indianápolis Oval, EUA | I | A | 9 | 11 | 12 | 13 | 8 | 9 | 8 | 800.0 | 200 |
| 42 | Istanbul, Turquia | H | C | 13 | 13 | 11 | 7 | 10 | 9 | 8 | 304.1 | 57 |
| 43 | Tallinn, Estônia | G | G | 12 | 9 | 9 | 7 | 10 | 13 | 13 | 309.6 | 52 |
| 44 | Virtasalmi, Finlândia | H | C | 11 | 7 | 11 | 7 | 14 | 10 | 12 | 276.5 | 79 |
| 45 | Zandvoort, Holanda | F | E | 15 | 9 | 12 | 12 | 6 | 8 | 14 | 301.8 | 71 |
| 46 | Zeltweg, Áustria | B | B | 19 | 10 | 11 | 13 | 9 | 9 | 8 | 252.8 | 79 |
| 47 | Adelaide, Austrália | C | D | 13 | 7 | 8 | 14 | 11 | 9 | 11 | 298.6 | 79 |
| 48 | Porto 58, Portugal | I | H | 8 | 15 | 13 | 8 | 10 | 9 | 11 | 407.4 | 55 |

**Correspondências com as pistas do nosso banco (TUMFTM):** Albert Park=Melbourne, Monza=Monza, Interlagos=Interlagos, Bahrain=Sakhir, Brands Hatch=Brands Hatch, Gilles Villeneuve=Montreal, Zandvoort=Zandvoort, Barcelona-Catalunya=Barcelona, Spa-Francorchamps=Spa, Hockenheimring=Hockenheim, Hungaroring=Hungaroring, Indianapolis=Indianapolis, Nürburgring=Nurburgring, Red Bull Ring=A1-Ring, Sepang=Sepang.

**Sem correspondência (pistas modernas, precisam de lógica manual):** Autódromo Hermanos Rodríguez (México), Circuit of the Americas (Austin), Moscow Raceway, Motorsport Arena Oschersleben, Norisring — *(confirmar lista completa das 25)*.

**Arquivos de apoio gerados:** `dados_pistas_ayres.py` (dados canônicos) + `popular_categorias_pistas.py` (script que popula o banco, corrige o bug do A/B, e trata espelhadas com `--espelhadas`).

---

## 9. DESENVOLVIMENTO (CHASSI + AERO)

### 9.1 📜 Regras

- Chassi e aero projetados pelo Engenheiro; cada um 0-100%
- Em construção só vale na PRÓXIMA temporada
- Pra próxima temporada: engenheiro contratado + chassi 100% + aero 100%
- Jogador novo: chassi + aero nível 1, 100%, grátis
- Fonte: `como.txt` + `Sem título 1.docx`

### 9.2 📜 Performance no tempo de volta

- Chassi nível 1: -0.2s/volta → nível 10: -2.0s/volta
- Aero nível 1: -0.1s/volta → nível 10: -1.0s/volta
- Escala linear, multiplicada pelo % aplicado
- Fonte: `constantes.py`

---

## 10. TEMPORADAS

### 10.1 📜 Regras

- Admin cria temporada + adiciona corridas na ordem
- Só 1 temporada ativa; ativar uma desativa a anterior
- Ao desativar, aplica desenvolvimento (chassi+aero) de quem cumpriu requisitos
- Fonte: `Sem título 1.docx` + `models_temporada.py`

### 10.2 📜 Sistema de grupos (classes)

- Hierarquia: C1G1 (topo) → C2G1-2 → C3G1-4 → C4G1-8...
- 20 pilotos por grupo; 2 primeiros sobem, últimos 4 (17-20) descem
- Fonte: `como.txt` — **❓ não implementado** (hoje só campos texto livre)

---

## 11. TREINAMENTO DE BOX

### 11.1 📜 Regras

- Reduz tempo de pit e chance de quebra (10% → 2%)
- Efeito imediato, 0-100%, com custo/tempo por avanço
- Fonte: `como.txt` + `TreinamentoBox`

---

## 12. FEATURES DO MANUAL AINDA NÃO IMPLEMENTADAS

### 12.1 🔴 CRÍTICO — MVP jogável
- [ ] **Popular categorias ideais das pistas** (corrigir bug A/B) — script pronto, falta rodar
- [ ] **Treino Livre real** volta a volta com feedback e "salvar ajuste"
- [ ] **Persistir estratégia** no banco (hoje só sessão)
- [ ] **Tela "Próxima Corrida"** com pista, clima, categorias, cálculos
- [ ] **Interface de pit stops** com combos progressivos (ver 4.1.3)
- [ ] **Dobrar catálogo de pistas** com versões espelhadas (ver 8.1.1)

### 12.2 🟡 IMPORTANTE
- [ ] Sistema de duplas (parceria entre pilotos)
- [ ] Patrocinadores (5 contratos, prêmio por corrida)
- [ ] Empréstimo bancário e agiota
- [ ] Poupança (associados, 3%/corrida)
- [ ] Reparo de peças / Devolução de peças
- [ ] Prêmio final de campeonato (individual + equipe)
- [ ] Sistema de classes/grupos automático

### 12.3 🟢 NICE TO HAVE
- [ ] Análise da Corrida (volta a volta pós-corrida)
- [ ] Comunicados e Notícias / Bastidores / Mensagens entre pilotos

### 12.4 🔮 DLC FUTURO
- [ ] Freio como componente completo
- [ ] Chuva e mm de água por trecho
- [ ] Estrategista contratado (4.3)
- [ ] Contratos de fornecedor por temporada (`models_contrato.py`, falta integrar)

### 12.5 ❌ CORTADO
- Bolsa de valores / mercado financeiro (7.4)

---

## 13. HISTÓRICO DE DECISÕES

### Dia 7 (`Sem título 1.docx`)
- ✅ Influência das pistas 1-30 → 7-15
- ✅ Fornecedores no formulário ordenados por custo
- ✅ 100 fornecedores renumerados #1-#100 por custo
- ✅ Bug do "#" corrigido
- ✅ Influências do Red Bull Ring gravadas
- ✅ Freio = DLC futuro

### Hoje
- ✅ Acordo de trabalho: manual + planilhas canônicos; IA para e avisa em divergência
- ✅ Criado `regras.md`
- ✅ **Engenheiro OBRIGATÓRIO** (conta nova vem com nível 1)
- 🟡 A REVER: premiação de quem abandona (hoje 0/0)
- ✅ Treino Livre: fluxo Opção A (1 clique = 1 volta)
- ✅ Treino Livre: simula carro a 100%
- ✅ Treino Livre: ao salvar, libera botão pro Treino Oficial com sugestão de combustível
- 🟡 A DECIDIR: horário programado do Treino Oficial
- ✅ Estratégia de pit: combos progressivos
- ✅ Estrategista = DLC futuro
- ✅ Trechos de temperatura de tamanho variável
- ✅ Combustível zerado = abandono
- ✅ Durabilidade de pneus por modelo (tabela padrão, sem variação entre fornecedores)
- ✅ Mercado financeiro CORTADO
- ✅ Pistas espelhadas (câmbio↔suspensão trocam letra e influência C↔S)
- ✅ **Categorias ideais das pistas: Opção A (dados canônicos Ayres)** — identificado bug do A/B (nunca populado), script `popular_categorias_pistas.py` criado
- ✅ **Extraída a tabela canônica das 48 pistas** da Planilha Ayres → seção 8.7
- ⚠️ **CONFLITO ABERTO:** influências reais Ayres são 5-15, mas dia 7 definiu 7-15 (decisão pendente, item 11)

---

## 14. PRÓXIMAS DECISÕES A TOMAR

1. **Quantos sliders no Treino Livre?** (3, 4 ou 5?)
2. **Formato do feedback** (só frase, só %, ou os dois)
3. **Salvar ajuste do treino livre** (por pista? global? por corrida?)
4. **Aerofólios são AJUSTES 1-99 ou PEÇAS nível 1-10?**
5. **Peso do combustível** (afeta tempo por volta ou só define quantas dá?)
6. **Chuva entra no MVP?**
7. **Sistema de classes/grupos automático entra no MVP?**
8. **Premiação de quem abandona** (opções em 1.4)
9. **Horário programado do Treino Oficial** (solo? scheduler? automático? bloqueio?) (4.1.2)
10. **Nome da versão espelhada das pistas** (8.1.1)
11. **Range das influências: usar Ayres 5-15 (A), clampar 7-15 (B) ou reescalar (C)?** (8.2)
12. **Lógica pras pistas modernas sem dado Ayres** (Hermanos Rodríguez, COTA, Moscow, Oschersleben, Norisring...) (8.3)
