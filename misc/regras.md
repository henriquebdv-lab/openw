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
- `Planilha Ayres (v5.12).xls` — lista completa das 47 pistas (nome, tamanho, voltas, categoria ideal, entrada/saída boxes, influências M/C/S/P/G/E/F)
- `Sem título 1.docx` — histórico de decisões do projeto (dia 7)

## 0.1 ⚠️ RESTRIÇÃO DE PROPRIEDADE INTELECTUAL

**A nossa versão NÃO pode usar:**

- Nome "Estratégia F1" ou similares (usar sempre "Open Wheel Strategy")
- Nomes de fornecedores canônicos: ZIPADNOR, POKGAST, VOECONO, ZURK, MIDILU, CEXUQE, WOVADA, COTASU, POKGAST, JOVOLT, xx-50 até xx-900 como nome de produto
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

- Motor, combustível, pneu, câmbio e suspensão são **contratos anuais obrigatórios**
- Engenheiro é opcional, mas necessário pra desenvolver chassi/aero
- **Não podem ser rescindidos durante a temporada** (contratos anuais)
- Fonte: `como.txt` ("os contratos para a temporada atual não podem ser rescindidos")

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
- Fonte: `como.txt` (Resultado da Corrida para Pilotos) + `pontuacao.py` já implementado

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

- Fonte: `como.txt` (Premiações Finais por temporada)
- Status: **❓ PENDENTE** — não implementado ainda

---

## 2. FORNECEDORES

### 2.1 🎨 Estrutura (nossa versão)

- **100 fornecedores por categoria** (motor, combustível, pneu, câmbio, suspensão, engenheiro)
- **10 tiers × 10 fornecedores por tier**
- Dentro de cada tier: 2 "furadas" (parecem baratas, rendem pouco), 2 "achados" (ótimo custo/benefício), 6 "normais"
- **Furadas e achados ficam embaralhados**, o jogador não sabe qual é qual (essa é a graça)
- Numeração `#1` (mais barato) até `#100` (mais caro) — reflete só o custo, NÃO a qualidade
- Nomes gerados aleatoriamente (nada de ZIPADNOR/POKGAST)
- Fonte: `Sem título 1.docx` + `seed_fornecedores.py`

### 2.2 📜 Chassi e Aerodinâmica

- **NÃO são fornecedores contratados**
- São projetados pelo Engenheiro contratado
- Jogador novo recebe chassi + aero nível 1, 100% aplicado, **grátis**
- Fonte: `como.txt` (Contratos/Engenheiros) + decisão do dia 7

### 2.3 📜 Freio

- Existe no jogo original com 5º slot de ajuste no treino livre
- 🎨 **Nossa decisão:** freio fica como **DLC futuro**, NÃO entra no MVP
- MVP continua com 6 componentes: Motor, Câmbio, Suspensão, Pneu, Combustível (Gasolina), Engenheiro
- Pistas NÃO têm coluna F por enquanto
- Fonte: `Sem título 1.docx` (decisão do dia 7)

---

## 3. TREINO LIVRE

### 3.1 📜 Manual original

- 5 ajustes: **Câmbio, Suspensão, Freio, Aerofólio Dianteiro, Aerofólio Traseiro**
- Cada ajuste vale de **1 a 99**
- Cada ajuste tem um valor ideal por pista (o jogador não sabe qual)
- Piloto faz 1 volta, sistema mostra tempo + frase de feedback do piloto
- Jogador ajusta os valores e faz outra volta
- Repetição até acabar combustível OU pneu OU jogador decidir salvar
- **Botão "Salvar ajuste"** — o ajuste salvo é o que vai pra corrida
- Fonte: `como.txt` (Treino Livre)

### 3.2 ❓ Adaptação pra nossa versão (PENDENTE)

- Como freio é DLC futuro (regra 2.3), sobram **4 ajustes** no MVP: Câmbio, Suspensão, Aerofólio Dianteiro, Aerofólio Traseiro?
- OU 3 ajustes (câmbio, suspensão, aero único)?
- OU mantém os 5 e desabilita o slider de freio?
- **Decisão: aguardando**

### 3.3 📜 Feedback do piloto

- Frases originais (nossas, não copiadas)
- Por faixa de erro (-98 a +98)
- Faixas típicas: perfeito (0-3), quase (4-12), leve (13-28), médio (29-50), grande (51-74), extremo (75-98)
- Vocabulário difere por componente (câmbio: curta/longa, suspensão: mole/dura, freio: baixo/alto)
- Fonte: `feedback_piloto.py` já implementado + planilha n17ro

### 3.4 📜 Voltas do treino livre

- Limite: **combustível carregado** e **desgaste do pneu**
- Se combustível zerar OU pneu chegar em 100%, treino acaba
- Pneu e combustível usados no treino livre são **diferentes** dos da corrida
- Fonte: `como.txt` ("Se o combustível terminar ou o pneu chegar ao seu limite, significa que não poderá mais fazer voltas")

### 3.5 ❓ Fluxo interativo (PENDENTE)

- **Opção A:** Cada clique = 1 volta. Ajusta sliders. Clica de novo.
- **Opção B:** Define quantas voltas quer rodar (ex: 5). Sistema roda essas 5 e mostra feedback.
- **Opção C:** Híbrido — define lote, pode interromper.
- **Decisão: aguardando**

### 3.6 ❓ Salvar o ajuste (PENDENTE)

- Precisa criar tabela nova? (`AjusteSalvo` — 1 por equipe por pista? ou 1 por equipe atual?)
- Ajuste salvo vira setup padrão da próxima corrida
- **Decisão: aguardando**

---

## 4. TREINO OFICIAL E ESTRATÉGIA

### 4.1 📜 Treino Oficial

- Só pode ser feito **depois** de salvar o ajuste do treino livre
- Motor, câmbio e suspensão já estão montados
- Jogador define agora o **pneu** e **combustível** pra corrida
- Também define **em qual volta será o 1º pit stop**
- É uma volta única (qualifying)
- Fonte: `como.txt` (Treino Oficial)

### 4.2 📜 Estratégia de Corrida

- Última etapa antes da corrida
- Define pneu e combustível a colocar em cada pit stop
- Pode escolher fazer múltiplos pit stops
- Pode escolher "Parar no Fim" pra não fazer mais paradas
- Convenção: pit stop na volta 15 = entra nos boxes no fim da volta 14, sai no início da 15
- Fonte: `como.txt` (Estratégia de Corrida)

### 4.3 📜 Estrategista contratado

- Opcional, custa R$ 200
- Dá uma sugestão de estratégia
- Não é muito bom (não ganha corrida com ele)
- Fonte: `como.txt` (Estrategista)
- Status: parcialmente implementado em `estrategia.py`

---

## 5. CORRIDA

### 5.1 📜 Volta a volta

- Cada volta: calcula tempo baseado em setup + fornecedores + influências da pista + desgaste do pneu + variação aleatória
- 4 trechos com temperaturas diferentes (25% das voltas cada)
- Consumo por volta debitado do tanque
- Desgaste do pneu acumulado por volta

### 5.2 📜 Pit stop

- Base: tempo específico da pista (`tempo_pit_stop_segundos`)
- Reduzido pelo **Treinamento de Boxes** (0-100%)
- Sem treino: tempo cheio; treino 100%: mínimo definido no admin
- Fonte: `como.txt` (Entrada/Saída Boxes) + `corrida.py` já implementado

### 5.3 📜 Abandono

- **Pneu estoura** = abandono imediato quando desgaste ≥ 100%
- **Quebra mecânica** = sorteio no início da corrida
  - Sem treino de box: 10% de chance
  - Treino 100%: 2% de chance
  - Escala linear
- Fonte: `como.txt` (dicas) + `Sem título 1.docx`

### 5.4 📜 Combustível

- Tanque máximo: **150 litros**
- Se acabar: pit stop automático (não é abandono)
- Também tem consumo na volta de qualifying (1 volta descontada)
- Fonte: `como.txt` (observações)

---

## 6. DESGASTE DO PNEU

### 6.1 📜 Fórmula base

- Desgaste por volta = `desgaste_base_pneu × fator_temperatura × fator_engenheiro × fator_modelo`
- Fator temperatura: cresce a partir de 20°C (referência = 0), cada grau adiciona/reduz 1% (`DESGASTE_POR_GRAU_FRACAO = 0.01`)
- Fonte: `constantes.py` + tabela do `como.txt`

### 6.2 📜 Tabela de referência (planilha n17ro)

| Temp °C | Desgaste extra m/km |
|---------|---------------------|
| -2°C    | -220 m/km           |
| 0°C     | -200 m/km           |
| 10°C    | -100 m/km           |
| 20°C    | 0 m/km (neutro)     |
| 30°C    | +100 m/km           |
| 40°C    | +200 m/km           |
| 45°C    | +250 m/km           |

- Fonte: `estrategiaf1_2005_byn17ro.xls`
- Status: 🎨 nossa versão usa fórmula proporcional simplificada (não a tabela literal)

### 6.3 📜 Penalidade por desgaste

- 0-70%: sem penalidade
- 70-85%: leve (até 1.5s)
- 85-95%: médio (até 5s)
- 95-100%: pesado (até 12s)
- ≥100%: pneu estoura (15s + abandono)
- Fonte: `carro.py` (função `penalidade_desgaste_pneu`)

---

## 7. CATEGORIAS A-J E MODELOS xx-50/xx-900

### 7.1 📜 Mapeamento

| Modelo | Letra | Uso                           |
|--------|-------|-------------------------------|
| xx-50  | A     | Câmbio/Suspensão (mais leve)  |
| xx-100 | B     |                               |
| xx-200 | C     |                               |
| xx-300 | D     |                               |
| xx-400 | E     |                               |
| xx-500 | F     |                               |
| xx-600 | G     | Molhada (pneu)                |
| xx-700 | H     |                               |
| xx-800 | I     | Encharcada (pneu)             |
| xx-900 | J     | (mais pesado)                 |

- Câmbio/Suspensão: cada pista pede uma letra ideal (ex: "AB" = câmbio A, suspensão B)
- Pneu: 50-500 = seco, 600-700 = molhada, 800-900 = encharcada
- Fonte: `como.txt` (Tabelas de Dados)

### 7.2 🎨 Como aplicamos na nossa versão

- Jogador contrata **1 fornecedor por temporada** (motor, pneu, combustível, câmbio, suspensão, engenheiro)
- A cada corrida escolhe qual **modelo (50-900) usar de cada componente**
- Modelo baixo (50): mais rápido, dura/rende menos
- Modelo alto (900): mais lento, dura/rende mais
- Câmbio/suspensão: modelo define a letra A-J que faz match com a pista
- Pneu: modelo define a condição de pista (seco/molhada/encharcada)
- Fonte: `Sem título 1.docx` + `modelos_componente.py` + `carro.py`

---

## 8. PISTAS

### 8.1 📜 Origem dos dados

- 25 pistas importadas do TUMFTM/racetrack-database (licença LGPL-3.0, dados do OpenStreetMap)
- Traçado SVG + extensão em km calculada do CSV
- Nomes canônicos de exibição (ex: "Red Bull Ring", não "Spielberg")
- Fonte: `pistas_reais_db.py` + `importar_todas_pistas.py`

### 8.2 📜 Influências

- Cada pista tem influência 7-15 (10 = neutro) para: Motor, Câmbio, Suspensão, Pneu, Combustível (G), Engenheiro
- Valor > 10 = componente importa MAIS nessa pista
- Valor < 10 = componente importa MENOS
- Fonte: `como.txt` (Influência) + `Sem título 1.docx` (range 7-15 confirmado)

### 8.3 📜 Categoria ideal

- Cada pista tem 1 letra ideal pra câmbio e 1 letra ideal pra suspensão (A-J)
- Escolher o modelo certo (via 50-900) = acerto perfeito no tempo de volta
- Fonte: `como.txt` (Categoria de Peças)

### 8.4 📜 Influências canônicas conhecidas

- **Red Bull Ring** (= A1-Ring, Áustria): M9 C8 S7 P11 G12 E14
- Demais 24 pistas: neutro (10 em tudo) até serem preenchidas
- Fonte: `como.txt` (exemplo A1-Ring) + `seed_influencias_pistas.py`

### 8.5 📜 Cálculo de voltas da corrida

- Distância alvo: **290-320 km**, máximo 79 voltas
- `voltas = round(305 / extensão_km)`, limitado a 79
- Fonte: `pistas_reais_db.py` (função `calcular_numero_voltas`)

### 8.6 📜 Temperatura por trecho

- Corrida dividida em 4 trechos (25% das voltas cada)
- Cada trecho pode ter temperatura diferente
- Fonte: `como.txt` (Sobre a temperatura) + admin_pista_editar já implementado

---

## 9. DESENVOLVIMENTO (CHASSI + AERO)

### 9.1 📜 Regras

- Chassi e aero são projetados pelo Engenheiro contratado
- Cada um vai de 0 a 100%
- O que está EM CONSTRUÇÃO só passa a valer NA PRÓXIMA temporada
- Pra participar da próxima temporada: **engenheiro contratado + chassi 100% + aero 100%**
- Jogador novo: chassi + aero de nível 1, 100% aplicado, grátis
- Fonte: `como.txt` + `Sem título 1.docx`

### 9.2 📜 Performance no tempo de volta

- Chassi nível 1: -0.2s/volta | Chassi nível 10: -2.0s/volta
- Aero nível 1: -0.1s/volta | Aero nível 10: -1.0s/volta
- Escala linear entre 1 e 10
- Multiplicado pelo % aplicado
- Fonte: `constantes.py`

---

## 10. TEMPORADAS

### 10.1 📜 Regras

- Admin cria uma temporada com nome
- Admin adiciona corridas na ordem (calendário)
- **Só 1 temporada ativa por vez**
- Ativar uma desativa a anterior
- Ao desativar uma temporada, o desenvolvimento (chassi+aero em construção) é aplicado a todos os jogadores que cumpriram os requisitos
- Fonte: `Sem título 1.docx` + `models_temporada.py` já implementado

### 10.2 📜 Sistema de grupos (classes)

- Estrutura hierárquica: C1G1 (topo, 1 grupo), C2G1-G2, C3G1-G4, C4G1-G8, etc.
- Cada grupo: 20 pilotos
- Em cada grupo: 2 primeiros promovidos, últimos 4 (17-20) rebaixados
- Fonte: `como.txt` (Modelo da Estrutura de Classes e Grupos)
- Status: **❓ PENDENTE** — não implementado, hoje temos só campos `grupo` e `classe` em texto livre no `Usuario`

---

## 11. TREINAMENTO DE BOX

### 11.1 📜 Regras

- Treina a equipe de mecânicos
- Reduz tempo de pit stop (do máximo configurado até o mínimo)
- Reduz chance de quebra mecânica (10% → 2%)
- Efeito imediato (a partir da próxima corrida)
- 0% a 100%, com custo e tempo por avanço
- Fonte: `como.txt` (Dicas) + já implementado em `TreinamentoBox`

---

## 12. FEATURES DO MANUAL AINDA NÃO IMPLEMENTADAS

Ordem sugerida pra atacar (ainda a decidir):

### 12.1 🔴 CRÍTICO — MVP jogável
- [ ] **Treino Livre real** volta a volta com feedback e "salvar ajuste"
- [ ] **Persistir estratégia** no banco (hoje só sessão)
- [ ] **Tela "Próxima Corrida"** com pista, clima, categorias, cálculos

### 12.2 🟡 IMPORTANTE — completa a experiência
- [ ] **Sistema de duplas** (fase 2 — parceria entre pilotos)
- [ ] **Patrocinadores** (5 contratos, prêmio por corrida)
- [ ] **Bolsa de valores** (variação de preço dos itens)
- [ ] **Empréstimo bancário** e agiota
- [ ] **Poupança** (associados, 3%/corrida)
- [ ] **Reparo de peças** (motor/câmbio usado, custa menos que novo)
- [ ] **Devolução de peças** (só associados)
- [ ] **Prêmio final de campeonato** (1º = R$ 100.000, etc.)
- [ ] **Sistema de classes/grupos automático** (promoção/rebaixamento entre temporadas)

### 12.3 🟢 NICE TO HAVE — polimento
- [ ] Análise da Corrida (histórico volta a volta pós-corrida)
- [ ] Comunicados e Notícias
- [ ] Bastidores (mini fórum por grupo)
- [ ] Bolsa de Valores com histórico
- [ ] Mensagens entre pilotos (sistema C:G:N)

### 12.4 🔮 DLC FUTURO (fora do MVP)
- [ ] **Freio** como componente completo (fornecedor + influência na pista + slider no treino)
- [ ] **Chuva** e cálculo de mm de água por trecho
- [ ] **Contratos de fornecedor por temporada** já codados em `models_contrato.py`, falta integrar nas rotas

---

## 13. HISTÓRICO DE DECISÕES

### Dia 7 (dia atual do log em `Sem título 1.docx`)
- ✅ Range de influência das pistas mudou de 1-30 pra 7-15
- ✅ Fornecedores no formulário de criar equipe ordenados por custo
- ✅ 100 fornecedores por categoria renumerados #1-#100 por custo
- ✅ Bug do "#" sem número corrigido
- ✅ Influências canônicas do Red Bull Ring gravadas
- ✅ Freio decidido como DLC futuro

### Hoje (definição das regras de trabalho)
- ✅ Acordo: manual (`como.txt`) + planilhas são fontes canônicas
- ✅ Acordo: onde manual é omisso ou usuário não lembra, decide-se em conversa e vira regra
- ✅ Acordo: quando pedido contraria manual, IA para e avisa
- ✅ Criado este arquivo `regras.md` como registro oficial

---

## 14. PRÓXIMAS DECISÕES A TOMAR

Em ordem de urgência:

1. **Quantos sliders no Treino Livre?** (3, 4 ou 5?)
2. **Fluxo do Treino Livre** (volta única por clique / lote / híbrido)
3. **Formato do feedback** (só frase, só %, ou os dois)
4. **Salvar ajuste do treino livre** (por pista? global? por corrida?)
5. **Aerofólios são AJUSTES 1-99 ou PEÇAS nível 1-10?**
6. **Peso do combustível** (afeta tempo por volta ou só define quantas dá?)
7. **Chuva entra no MVP?**
8. **Sistema de classes/grupos automático entra no MVP?**
