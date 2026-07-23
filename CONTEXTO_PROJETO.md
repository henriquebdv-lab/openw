# Open Wheel Strategy — Contexto do Projeto (dia 7 de dev)

**Se você está começando um chat novo com uma IA, cole este arquivo inteiro
na primeira mensagem. Ele contém tudo que a IA precisa saber pra continuar
de onde paramos.**

> DICA IMPORTANTE PRA COLAR ARQUIVOS: anexar arquivo grande às vezes chega
> CORTADO pra IA. Colar o texto direto no chat vem inteiro. Pra arquivos
> grandes (models.py, app.py, seeds), prefira copiar/colar o texto.

## ⚠️ Regra de propriedade intelectual

O nome do jogo é **Open Wheel Strategy** — referência genérica à categoria de
monopostos, não a marca registrada.
**A IA NÃO PODE usar:**
- Nomes de outros jogos por nome
- Nomes canônicos herdados (ZIPADNOR, POKGAST, MIDILU, JOVOLT, xx-50 até xx-900)
- Nomes de pilotos, engenheiros ou frases de feedback específicas herdados de outros jogos
- Nomes de autores de planilhas de referência
- Referências a "F1" ou similares (usar "monoposto", "openwheel")
**A IA PODE usar:**
- Sistemas de pontos e valores (padrões públicos)
- Fórmulas matemáticas
- Estruturas de dados (níveis, categorias A-J, etc)
- Nomes de pistas de corrida reais (fatos históricos)
- Dados técnicos objetivos de pistas reais

## Sobre o projeto
- **Nome:** Open Wheel Strategy
- **Tipo:** Jogo de gerenciamento de equipes de monopostos, jogado no navegador
- **Stack:** Python + Flask + SQLAlchemy + SQLite + Flask-Migrate
- **Local:** E:\openwheel\
- **Desenvolvedor:** Henrique (Curitiba, PR)
- **Referências locais:** manual (como.txt) + planilhas de referência técnica

## Arquitetura de bancos (IMPORTANTE)
São DOIS bancos SQLite separados:
- **jogo.db** — dados dinâmicos do jogo (usuários, equipes, fornecedores,
  resultados). Acessado via SQLAlchemy (models.py).
- **pistas_reais.db** — dados estáticos das 25 pistas reais (SVG, comprimento,
  influências). Acessado via sqlite3 PURO (pistas_reais_db.py), NÃO usa
  SQLAlchemy. Tabela: `pistas_reais`. Origem dos dados: TUMFTM
  racetrack-database (LGPL-3.0), importado via importar_todas_pistas.py.

## Regra de ouro do banco

**NUNCA APAGAR o jogo.db SEM AUTORIZAÇÃO.** Migrações via Flask-Migrate.
Seeds de fornecedor NUNCA apagam fornecedor em uso: deletam só os não-usados
e DESATIVAM (ativo=False) os que estão em uso por algum jogador.

## Preferências do desenvolvedor
- Prefere arquivos completos, não trechos pra editar manualmente
- Não gosta de caçar linha pra colar; quer o arquivo inteiro pronto
- Plain text, sem HTML no meio, sem negrito excessivo
- Objetivo e direto, respostas rápidas e completas
- Passo-a-passo pra troubleshooting
- Português brasileiro
- Aceita quando IA admite erro, se frustra com repetição de erros

---

## ✅ O QUE FOI FEITO HOJE (dia 7 — as 4 prioridades imediatas fechadas)

### ✅ A) Range de influência das pistas corrigido
- Formulário admin_pista_editar.html: validação mudou de min=1/max=30
  para **min=7/max=15** nos 6 campos de influência
- Cabeçalho do card atualizado explicando a escala 7-15
- Mantidos os 6 componentes M/C/S/P/G/E (sem Freio)

### ✅ B) Fornecedores ordenados por custo no formulário criar equipe
- equipes.html: adicionado `|sort(attribute='custo_temporada')` nos 6
  selects (motor, combustível, pneu, câmbio, suspensão, engenheiro)
- Dropdown agora sai do mais barato ao mais caro
- Resolvido só no template, sem tocar no app.py

### ✅ C) Renumeração dos 100 fornecedores por custo + 2 bugs corrigidos
- **Bug 1 corrigido:** gerar_nome_item/gerar_nome_pessoa terminavam em "#"
  SEM número (todos os fornecedores ficavam sem número). Agora o nome sai
  correto: "TurboRacing #1", "PowerMotors #2", etc.
- **Bug 2 corrigido:** numeração agora é aplicada DEPOIS de ordenar por
  custo (função _renumerar_por_custo), então o número bate com o preço.
- **Regra confirmada:** número reflete APENAS o custo (#1 = mais barato,
  #100 = mais caro). NÃO indica qualidade. Furadas/achados continuam
  embaralhadas de propósito — a graça de escolher no escuro fica intacta.
- **popular_banco() reescrito** (o final do arquivo original tinha vindo
  cortado): deleta não-usados, desativa em uso, insere os novos, commit.

### ✅ D) Influências canônicas gravadas nas pistas
- Pistas já estavam importadas no pistas_reais.db (25 pistas, nomes de
  exibição oficiais tipo "Red Bull Ring", não "Spielberg").
- Script seed_influencias_pistas.py grava só os valores da planilha:
  **Red Bull Ring (= A1-Ring): M9 C8 S7 P11 G12 E14**
- Demais 24 pistas ficam neutras (10 em tudo). Ajuste manual no admin.
- Script NÃO cria nem apaga pistas, só atualiza influências via as
  funções do próprio pistas_reais_db.py.

### ✅ DECISÃO DO FREIO (resolvida — era a pendência do dia anterior)
- Freio fica como **expansão futura ("DLC")**, NÃO entra no MVP.
- MVP continua com 6 componentes: M/C/S/P/G/E.
- Pistas NÃO têm coluna F por enquanto.
- **Design da versão simples do freio (pra quando for implementar):**
  - 1 fornecedor de freio por temporada (contrato anual, igual motor/pneu)
  - Influência F por pista, faixa 7-15 (só mais uma coluna)
  - Nível 1-10, afeta o tempo de volta como os outros
  - Entra na chance de quebra (soma no cálculo de 10% base)
  - Custo de temporada debita ao contratar
  - SEM temperatura/categoria térmica (isso é coisa de jogo 3D, não texto)
  - Quando o refactor xx-50/xx-900 acontecer, freio entra junto
  - O que muda quando virar DLC:
    1. Novo model FornecedorFreio (cópia do FornecedorMotor)
    2. Coluna influencia_freio na Pista
    3. Campo fornecedor_freio_id na Equipe
    4. Freio entra no loop de cálculo de tempo de volta e quebra

### Arquivos entregues HOJE
- admin_pista_editar.html (prioridade A)
- equipes.html (prioridade B)
- seed_fornecedores.py (prioridade C — reescrito completo)
- seed_influencias_pistas.py (prioridade D — script novo)

---

## O que já estava funcionando (dias anteriores)

### Autenticação
- Login/registro email/senha ou Google OAuth (.env + python-dotenv)
- Sistema de admin

### Jogador
- Criar/editar equipe (sem chassi — chassi é do engenheiro)
- Treino livre (5 sliders) — versão simplificada, precisa refazer
- Treino oficial
- Estratégia da corrida (rudimentar)
- Desenvolvimento (2 barras: chassi + aero)
- Treinamento de Box

### Corrida
- Simulação volta a volta
- Pit stop com tempo específico da pista
- 4 trechos de temperatura
- Volta de qualifying descontando tanque
- DL e DF
- Consumo L/km × tamanho da pista
- Categorias A-J de câmbio/suspensão
- Categoria de chuva do pneu
- Influências M/C/S/P/G/E por pista
- Tanque máx 150L
- Formato 1:30.234
- Curva suave de desgaste do pneu (começa a perder a partir de 70%)
- Chance de quebra de peças (10% base, 2% mínimo com treino de box)

### Temporada
- Admin cria com calendário; 1 ativa por vez
- Ranking com pontos e prêmios
- Custo_montagem debitado por corrida; custo_temporada ao contratar
- Fim de temporada aplica chassi/aero desenvolvido

### Fornecedores
- 100 por categoria (motor, combustível, pneu, câmbio, suspensão, engenheiro)
- FornecedorChassi mantido no banco por legado (não usado)
- 10 tiers × 10 fornecedores por tier
- Nomes gerados aleatoriamente (não canônicos), numerados #1-#100 por custo

### Admin
- Sidebar fixa
- CRUD fornecedores, pistas, temporadas, configurações
- Gerencia usuários (grupo, classe, admin)
- Desativar temporada aplica desenvolvimento

### Chassi/Aero
- Projetados pelo Engenheiro (NÃO é fornecedor)
- Jogador novo recebe chassi + aero nível 1 grátis
- 2 barras separadas de desenvolvimento (chassi e aero)
- Só passa a valer na PRÓXIMA temporada
- Requisitos p/ próxima temporada: engenheiro + chassi 100% + aero 100%

---

## Sistemas numéricos definidos

### Pontuação (individual)
40/35/32/29/26/24/22/20/18/16/14/12/10/8/6/5/4/3/2/1

### Prêmio em R$ (individual)
1º R$12.000 → 20º R$5.500

### Chassi/Aero
- Nível 1: chassi -0.2s / aero -0.1s
- Nível 10: chassi -2.0s / aero -1.0s
- Escala linear

### Orçamento inicial
- R$ 55.000 configurável

### Quebra mecânica
- 10% base, 2% mínimo (com treino de box 100%)

### Influência das pistas
- Faixa 7-15 (10 = neutro). Baixo = componente importa pouco.
- Red Bull Ring canônico: M9 C8 S7 P11 G12 E14. Resto neutro (10).

---

## O que está para fazer na PRÓXIMA SESSÃO

### 🟡 Feature grande pendente: Treino Livre real
- Jogador escolhe pneu + gasolina no início
- Sistema calcula quantas voltas dá
- Sistema simula cada volta com feedback (frases genéricas nossas)
- Persiste no banco (ResultadoTreinoLivre)
- Tela pública tipo ranking do treino livre por grupo+classe

### 🟢 Regras confirmadas mas não implementadas
- **FornecedorFreio** como componente separado (design já definido acima)
- **Xx-50 a xx-900**: cada fornecedor tem 10 modelos (jogador escolhe por corrida)
  - Modelo baixo = rápido mas dura menos; alto = lento mas dura mais
  - Contrato anual = 1 fornecedor; compra por corrida = 1 modelo
  - Este é o PRÓXIMO GRANDE REFACTOR
- **Categorias A-J = modelos 50-900** literalmente (câmbio/suspensão)
- **Frases de feedback do piloto** (criar do zero, ~20 faixas por componente)
- **Aderência de pneu por temperatura** (10 categorias, matriz)
- **Sistema de duplas** (fase inteira)
- **Prêmio final de campeonato** (bonus no ranking final da temporada)
- **Popular influências das outras 24 pistas** conforme forem saindo da
  planilha (hoje só Red Bull Ring tem valor canônico)

### 🔵 Roadmap longo
- Estratégia com 8 pit stops planejáveis
- Poupança (3%/corrida)
- Empréstimo bancário
- Patrocinadores
- Estrategista contratado
- Bolsa de valores
- Sistema associado
- Sistema divisões automático (subir/descer entre temporadas)

---

## Arquivos-chave do projeto (E:\openwheel\)
- app.py (47 KB) — rotas Flask
- models.py (18 KB) — models SQLAlchemy do jogo.db
- pistas_reais_db.py (9 KB) — acesso sqlite3 puro ao pistas_reais.db
- importar_todas_pistas.py — importa CSVs do TUMFTM pro pistas_reais.db
- converter_pista_real.py — converte coordenadas CSV em SVG path
- seed_fornecedores.py — gera os 100 fornecedores por categoria
- seed_influencias_pistas.py — grava influências canônicas nas pistas
- corrida.py, pontuacao.py, progressao.py, constantes.py — lógica de jogo
- equipamentos.py, equipe.py, carro.py, carro_visual.py — modelo de domínio
- jogo.db (284 KB) — banco principal
- pistas_reais.db (420 KB) — banco de pistas (25 pistas importadas)

## Como voltar aqui amanhã
- Cola este arquivo na primeira mensagem
- "Este é o contexto do Open Wheel Strategy. Vamos continuar de onde
  paramos. Prioridade: [Treino Livre real / refactor xx-50-900 / etc]"
- Cola (copiar/colar, não anexar) os arquivos que a IA pedir

## Estado do projeto
Dia 7. As 4 prioridades imediatas foram fechadas. Backend sólido,
frontend com identidade visual, regras do manual quase todas corretas.
Próximo foco recomendado: Treino Livre real (feature grande, fazer com
calma) OU o refactor dos modelos xx-50/xx-900 (o maior pendente).
