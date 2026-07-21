# Open Wheel Strategy — Contexto do Projeto

> **Se você está começando um chat novo com uma IA, cole este arquivo inteiro
> na primeira mensagem. Ele contém tudo que a IA precisa saber pra continuar
> de onde paramos, sem perder decisões e sem quebrar código existente.**

---

## Sobre o projeto

- **Nome:** Open Wheel Strategy
- **Tipo:** Jogo de gerenciamento de F1, jogado no navegador
- **Stack:** Python + Flask + SQLAlchemy + SQLite + Flask-Migrate
- **Inspiração:** Jogo antigo "Estratégia F1" (manual guardado em `como.txt`)
- **Fonte de dados canônicos:** Planilha do jogador "AYRES" (`Planilha Ayres (v5.12).xls`) - documenta cálculos originais
- **Desenvolvedor:** Henrique (Curitiba, PR)
- **Local do projeto no PC:** `E:\openwheel\`

## Regra de ouro do banco de dados

**NUNCA APAGAR O `jogo.db` SEM AUTORIZAÇÃO.** Ele tem usuários reais.
Toda alteração de schema deve ser feita via `flask db migrate` + `flask db upgrade`,
que preservam os dados. A única exceção foi hoje, quando o próprio Henrique
autorizou apagar pra fazer o rename de `EquipeDB` → `CarroJogador`.

## Preferências do desenvolvedor (do usuário)

- Prefere baixar arquivos completos, não trechos pra colar manualmente
- Prefere plain text — sem HTML no meio de texto, sem negrito excessivo
- Prefere respostas objetivas e diretas
- Prefere passo-a-passo claro pra troubleshooting técnico
- Sem familiaridade forte com Linux/SSH
- Aceita quando a IA admite erro, fica frustrado com repetição de erros
- Só português brasileiro

## Arquitetura atual do projeto

### Bancos de dados (2)

1. **`jogo.db`** — banco principal, gerenciado pelo Flask-Migrate/Alembic
2. **`pistas_reais.db`** — banco separado, gerenciado por SQL cru
   Contém as 50+ pistas reais importadas via `importar_todas_pistas.py`

### Arquivos Python principais (raiz)

- `app.py`, `models.py`, `models_temporada.py`, `equipamentos.py`, `carro.py`
- `corrida.py`, `classificacao.py`, `estrategia.py`, `progressao.py`
- `pistas_reais_db.py`, `converter_pista_real.py`, `importar_todas_pistas.py`
- `pontuacao.py`, `seed_fornecedores.py`, `constantes.py`, `config.py`

### Tabelas do banco principal

- `Usuario` (com `grupo` e `classe`)
- `CarroJogador` (antes `EquipeDB`) — 1 por usuário
- `Fornecedor{Motor,Combustivel,Pneu,Chassi,Cambio,Suspensao,Engenheiro}`
- `Configuracao` (singleton com `orcamento_inicial`)
- `Desenvolvimento`, `TreinamentoBox`
- `ResultadoClassificacao`, `ResultadoCorrida`
- `Temporada`, `CorridaAgendada`

## O que já está funcionando ✅

### Autenticação
- Login/registro por email/senha ou Google OAuth
- Sistema de admin
- Rota `/admin/usuarios` pra grupo/classe

### Jogador
- Criar/editar equipe
- Treino livre (5 sliders) — simulado, não fica no banco
- Treino oficial (depende do livre)
- Estratégia da corrida (rudimentar)
- Desenvolvimento e Treinamento de Box (0-100%)

### Corrida
- Simulação volta a volta
- Pit stop com tempo específico da pista
- 4 trechos de temperatura
- Volta de qualifying descontando tanque
- DL e DF (diferença líder / carro da frente)
- Consumo L/km × tamanho da pista
- Categorias A-J de câmbio/suspensão
- Categoria de chuva do pneu (seco/interm/chuva)
- Influências M/C/S/P/G/E por pista (falta F de Freio)
- Pneu que passa desgaste → abandono (deveria só ficar lento)
- Tanque máx 150L
- Formato `1:30.234`

### Temporada
- Admin cria com calendário
- Só 1 ativa por vez
- Ranking com pontos (25/18/... hoje - INCORRETO)
- Custo_montagem debitado por corrida
- Custo_temporada debitado ao contratar

### Fornecedores
- 100 fornecedores em 10 tiers
- Furadas/achados dentro do tier
- Categorias A-J e chuva distribuídas
- Nomes #1 (pior) a #100 (melhor)
- Não apaga em uso, só desativa
- Orçamento inicial R$ 55.000 configurável

### Admin
- Painel com sidebar fixa (CONFLITO com base.html pendente)
- CRUD fornecedores, pistas, temporadas, configurações
- Gerencia usuários

## Decisões tomadas

### Equipe vs Dupla
- "Equipe" hoje = carro individual de 1 jogador (`CarroJogador`)
- "Dupla" = 2 jogadores humanos que se juntam (a implementar)
- Cada jogador da dupla continua individual
- Único vínculo: nome + soma dos pontos pra ranking de duplas
- Vínculo termina no fim da temporada
- Prêmio final dividido em 2

### Convite de dupla
- Só entre mesmo grupo + mesma classe
- Nome proposto por quem convida
- Se não roda 3 corridas → parceiro desfaz
- Admin desfaz manualmente
- Solo permitido (só perde prêmio de equipe)

### Trocar fornecedor
- Durante temporada ativa: BLOQUEADO
- Entre temporadas: livre, pagando custo_temporada de novo

### Reset de conta
- Rota `/minha-equipe/resetar` (backend feito)
- Permitido durante temporada com aviso forte

### Pontuação (CORRIGIR - hoje está errada)
- **HOJE**: 25/18/15/12/10/8/6/4/2/1 (F1 atual — errado)
- **CORRETO (do como.txt E confirmado pela planilha AYRES)**:
  - Individual: 40/35/32/29/26/24/22/20/18/16/14/12/10/8/6/5/4/3/2/1
  - Equipe: 20/19/18/17/16/15/14/13/12/11/10/9/8/7/6/5/4/3/2/1
  - Todos os 20 pontuam

### Premiação em R$ (nova - da planilha AYRES)
**Individual (piloto):**
- 1º: R$12.000, 2º: R$11.000, 3º: R$10.500, 4º: R$10.000
- 5º: R$9.500, 6º: R$9.200, 7º: R$8.900, 8º: R$8.600
- 9º: R$8.300, 10º: R$8.000, 11º: R$7.700, 12º: R$7.400
- 13º: R$7.100, 14º: R$6.800, 15º: R$6.500, 16º: R$6.200
- 17º: R$6.000, 18º: R$5.800, 19º: R$5.650, 20º: R$5.500

**Equipa (só top 10 recebem):**
- 1º: R$4.000, 2º: R$3.000, 3º: R$2.500, 4º: R$1.500
- 5º: R$1.250, 6º: R$1.000, 7º: R$750, 8º: R$500
- 9º: R$400, 10º: R$250, 11º-20º: R$0

## Descobertas da Planilha AYRES (fonte canônica)

### 1. FREIO é fornecedor separado! (NOVO)
- Hoje freio é só um ajuste do treino livre
- Deveria ser um contrato como motor/pneu/etc
- Nomes canônicos: SAMUVE, TABOTE, JOVOLT, NERIFO...
- Custo nível 1: R$13.856, nível 100: R$1.429.294
- 10 categorias A-J: Extra Baixa, Super Baixa, Baixa, Média Baixa, Média,
  Média Alta, Alta, Super Alta, Extra Alta, "Não Existe"
- Precisa criar `FornecedorFreio` + `CarroJogador.freio_fornecedor_id`
- Precisa adicionar coluna `influencia_freio` (F) na tabela de pistas

### 2. Sistema de fornecedores por níveis
- Estrutura real: 100 níveis, cada nível tem 10 modelos xx-50 até xx-900
- Ex: Motor nível 1 = "ZIPADNOR" com modelos:
  xx-50 (0.698 HP), xx-100 (0.749), xx-200 (0.811), ..., xx-900 (1.3 HP)
- Motor nível 100 = "JESONHOS" xx-50 (1.3) até xx-900 (2.75)
- Custos crescem exponencialmente por nível

### 3. Nomes canônicos dos fornecedores
Ver arquivos anexos. Alguns exemplos:
- **Motores (níveis 1-10)**: ZIPADNOR, POKGAST, VOECONO, ZURK, JOFUIONT,
  KIKELOV, GEDUCA, DOMUJA, LAIKA, NINDEC
- **Câmbios**: CEXUQE, VULOSA, COVIXO, LEDAQU, ZOKECE, BOJUNA, FOPILU...
- **Suspensões**: WOVADA, JEJIFO, KOCOBA, BUJANU, QEDEWI, BICOTI, LEFUMA...
- **Pneus**: MIDILU, BONUQI, FAKOJO, KAMOFU, BUCUGE, KITOVI, CELAJE...
- **Combustíveis**: COTASU, DAWIDA, FUQAQI, BOTIVI, BEWOGA...
- **Freios**: SAMUVE, TABOTE, JOVOLT, NERIFO, WUZWUZ, JENIHU...
- **Engenheiros (pessoas)**: Carlos Afonso, Conceição Silva, Mendes Souza...

### 4. Aderência de pneu por temperatura
- Tabela matriz enorme na planilha
- Cada tipo de pneu (Extra Macio, Duro, Chuva Normal, etc) tem curva
- Vira fator multiplicativo no tempo de volta
- Categorias reais de pneu (10, não 3 como hoje):
  1. Extra Macio, 2. Super Macio, 3. Macio, 4. Duro, 5. Super Duro,
  6. Extra Duro, 7. Macio Chuva Normal, 8. Duro Chuva Normal,
  9. Macio Chuva Forte, 10. Duro Chuva Forte

### 5. Curva suave de desgaste do pneu
- Volta 1-20: 1x tempo
- Volta 30: 1.01x
- Volta 40: 1.04x
- Volta 60: 1.15x
- Depois disso: pneu estoura

### 6. Treinamento de PILOTO (separado do treino de box!)
- Existe além do treinamento de boxes
- Custos exponenciais: nível 1 = R$250, nível 50 = R$290.977, nível 100 = R$34.449.030
- Tem 4 componentes: Seca Prático (27%), Seca Teórico (16%),
  Molhada Prático (14%), Molhada Teórico (8%)

### 7. Treinamento de BOXES com 5 componentes
- Reabastecimento
- Retirada do Pneu
- Colocação do Pneu
- Levantar o Carro
- Abaixar o Carro
- Média dos 5 = tempo total do pit stop
- Custos: nível 1 = R$50, nível 100 = R$252.500

### 8. Estratégia com até 8 pit stops planejáveis
- Cada pit: qual pneu + em qual volta
- Estratégia de combustível separada

### 9. Frases de feedback do piloto (>100!)
Piloto/engenheiro fala com jogador após treino livre. Exemplos:
- "A suspensão está quase ideal, só firmar um pouco mais!" (0.09)
- "Nem Schumacher conseguiria guiar o carro com esse ajuste!" (0.65)
- "Freios? Que Freios?!" (0.28)
- "Está bem próximo do ideal, da próxima você consegue!" (0.03)
- "Este ajuste está cômico!" (0.32)
Cada frase tem um "peso" que representa distância do ideal

### 10. 47 pistas com dados canônicos completos
Cada pista tem: nome, país, tamanho (m), voltas ideais, câmbio ideal (letra),
suspensão ideal (letra), tempo pit (segundos), influências M/C/S/P/G/E/F

Exemplos:
- A1-Ring, Áustria: 307.1 km, 71 voltas, câmbio A, susp B, pit 14s, infl 9/8/7/11/12/14/5
- Sepang, Malásia: 310.4 km, 55 voltas, câmbio H, susp A, pit 16s, infl 9/6/15/10/11/10/6
- Interlagos: 305.9 km, 71 voltas, câmbio B, susp E, pit 12s, infl 11/13/11/11/6/8/12
- Monaco: 262.8 km, 78 voltas, câmbio E, susp G, pit 12s, infl 6/9/8/13/15/10/13
- Monza: 306.7 km, 53 voltas, câmbio A, susp B, pit 17s, infl 14/14/8/11/6/8/9
- Spa, Bélgica: 306.6 km, 44 voltas, câmbio E, susp G, pit 9s, infl 6/7/13/14/11/9/11

## Pendências pra próxima sessão

### 🔴 Prioridade máxima (visual bloqueado)

1. **Conflito de sidebar admin** — precisa ver `base.html` do jogador. Decidir:
   esconde sidebar principal em telas admin, ou junta tudo?

2. **Templates do jogador**:
   - `equipes.html`: remover campo orçamento, mostrar contratos/sobra
   - `minha_equipe.html`: botão editar (só entre temporadas), botão reset
   - `editar_equipe.html`: bloqueado se temporada ativa

### 🔴 Corrigir sistema de pontuação e prêmios

3. **Trocar `pontuacao.py`** pra 40/35/32/29/26/24/22/20/18/16/14/12/10/8/6/5/4/3/2/1
4. **Adicionar prêmios em R$** por corrida (individual + equipe)
5. **Adicionar ranking de equipe** separado do ranking individual

### 🟡 Novidades da planilha AYRES

6. **Adicionar FornecedorFreio** — nova tabela, novo FK em CarroJogador
7. **Adicionar coluna `influencia_freio`** (F) em pistas_reais
8. **Popular pistas_reais.db** com os dados exatos das 47 pistas AYRES
9. **Curva suave de desgaste do pneu** (lento antes de estourar)
10. **Frases de feedback do piloto** pós-treino livre (>100 frases)

### 🟢 Regras novas do como.txt

11. **Chance de quebra de peças** (10% inicial, reduz com treino)
12. **Desenvolvimento vale só pra PRÓXIMA temporada**
13. **Chassis desenvolvido = requisito pra próxima temporada**
14. **Motor definido pela estratégia** (estoque de peças por corrida)
15. **Multa proporcional ao rescindir patrocínio** (futuro)

### 🟢 Sistema de Duplas (fase inteira)

16. Criar tabelas `Dupla`, `MembroDupla`, `ConviteDupla`
17. Rotas: `/dupla/convidar`, `/dupla/convites`, `/dupla`
18. Rota admin pra desfazer qualquer dupla
19. Contador `corridas_nao_rodadas` (regra do 3)
20. Integrar no ranking da temporada
21. Prêmio final dividido em 2

### 🔵 Roadmap longo (candidatos futuros)

- Sistema fornecedor 100 níveis × 10 modelos xx-50 a xx-900 (grande refactor)
- Nomes canônicos AYRES em vez de "PowerSystems #47"
- Categorias reais de pneu (10, não 3): Extra Macio, Super Macio... Chuva Forte
- Aderência de pneu por temperatura (matriz)
- Reparo/devolução de peças (só associados)
- Empréstimo bancário (6% juros por corrida, R$40k)
- Agiota (20% juros, R$10k)
- Poupança (3% rendimento por corrida)
- Patrocinadores (até 5, R$ por corrida)
- Estrategista contratado (R$200/corrida)
- Bolsa de valores (preços variam entre corridas)
- Sistema associado vs comum
- Coordenadas C:G:N (classe:grupo:número)
- Estratégia com 8 pit stops planejáveis
- Tela treino livre estilo Estratégia F1 (tabela todos pilotos + DL/DF)
- Sistema automático de subir/descer divisões
- Item 3 do escopo antigo: Pit stop planejado
- Treinamento de PILOTO separado do de boxes (com 4 componentes)
- Treinamento de boxes com 5 componentes (Reabast/Retirar/Colocar/Levantar/Abaixar)

### 🐛 Pequenos ajustes

- Substituir texto "Gerar 500" no botão do painel admin — gera 100 agora
- Confirmar selects em ordem crescente de custo
- Filtro Jinja `dinheiro` já existe, usar em todos os lugares

## Como voltar aqui

Se você (Henrique) está lendo isso num chat novo:

1. Cola este arquivo inteiro na primeira mensagem
2. Diz: "Este é o contexto do meu projeto. Podemos continuar do item X."
3. Prepara pra colar arquivos que a IA pedir:
   - `models.py` (mais atualizado)
   - `app.py` (mais atualizado)
   - `templates/base.html` (nunca foi visto)
   - `templates/minha_equipe.html` (se modificado)
   - `como.txt` (o manual)
   - `Planilha Ayres (v5.12).xls` (fonte canônica)

## Arquivos entregues nas últimas sessões

**Última sessão (20/07/2026):**
- Raiz: `models.py`, `seed_fornecedores.py`, `app.py`
- Templates: `admin_base.html` (NOVO), `admin_dashboard.html`,
  `admin_configuracoes.html`, `admin_usuarios.html`, `admin_pistas_reais.html`,
  `admin_pista_editar.html`, `admin_temporadas.html`, `admin_temporada_editar.html`,
  `admin_fornecedor_lista.html`, `admin_fornecedor_editar.html`

**Sessões anteriores:**
- `constantes.py`, `pistas_reais_db.py`, `carro.py`, `corrida.py`
- `models_temporada.py`, `pontuacao.py`
- `temporada.html`, `editar_equipe.html`, `corrida.html`, `classificacao.html`
