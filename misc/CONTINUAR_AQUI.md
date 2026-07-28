# Open Wheel Strategy — PONTO DE RETOMADA (documento ÚNICO e vivo)

> Cole ESTE arquivo + regras.md + openwheel_py.txt (e openwheel_html.txt/openwheel_css.txt se precisar).
> ÚNICO arquivo de retomada — edite este, não crie versões novas.
> Última atualização: 28/07/2026

---

## ✅ FEITO E FUNCIONANDO (testado)

### Base
- app.py desmembrado em rotas/ (padrão registrar(app), NÃO Blueprint).
- Login por email/senha + Google (cada máquina tem seu .env).
- Quick wins: pneu "marca — valor", pane seca = abandono.
- models.py estável (ref commit 41b5cb7).

### Parc Fermé + Preparação (fases 1 e 2)
- SetupFimDeSemana (motor+câmbio+suspensão 50-900 + campo travado).
- Tela "Montagem Fim de Semana": aviso de confirmação + trava (parc fermé rígido).
- Treino Livre INTERATIVO: usa setup travado, só a pista do FDS, auto-redireciona.
  3 sliders (1-99, 5 na estrutura), ideal secreto por pista (IdealPistaSlider),
  feedback do piloto + % de acerto, desgaste pesa no tempo, exibe VIDA do pneu.
- Treino Oficial = "Salvar dados da Classificação" (DadosClassificacao).
- Estratégia de stints persistida no banco (EstrategiaStint) + Pit Wall + validação de voltas.

### Corrida / Admin
- Admin "Dia de Corrida": painel de status + disparo manual, com TRAVAS confirmadas
  (não roda sem classificar, não roda sem equipe elegível, limpa grid após corrida).
- seed_teste.py: 1 admin (henriquebdv@gmail.com / 123456, Razor) + fornecedores +
  TEMPORADA 1 (10 corridas) + equipe do admin + 19 bots (grid de 20).
- BOTS HONESTOS: montados COMO JOGADOR — pegam os fornecedores MAIS BARATOS +
  orçamento DEBITADO (55k − contratos). Não "roubam" mais → tempos parelhos na 1ª temporada.
- Replay Fase 1 (tabela volta a volta) funcionando + link na sidebar.

### Refatoração de CSS (Lotes 1-5 COMPLETA)
- Estrutura: variaveis.css, base.css, componentes.css, formularios.css + telas/*.css.
- Zero style inline, zero Bootstrap, cores em variáveis, espaçamentos globais (ows-mt-*/mb-*).
- Base pro futuro "menu de cores" (tudo em variáveis CSS).
- Padronizado o menu admin (admin_usuarios e admin_temporada_editar agora usam admin_base).

---

## 🔴 PENDENTE / PRÓXIMOS PASSOS

### 🔧 Lógica dos DOIS ENGENHEIROS (decidido 28/07, falta implementar no código)
> Regra completa no regras.md seção 9.
- Conceito: engenheiro ATUAL (corre, 100%) + engenheiro PRÓXIMA (opcional, contrata e
  desenvolve durante a temporada).
- Virada: PRÓXIMA vira ATUAL com o % atingido; slot próxima zera; contrata um novo.
- Sem contratar/desenvolver: recebe eng nv1 DESCONTADO do orçamento + 50% performance
  + punição ESCONDIDA de +chance de quebra.
- ⚠️ CÓDIGO: hoje models.py tem UM engenheiro/desenvolvimento por equipe. Precisa de
  DOIS slots (atual + próxima). Reverter o "engenheiro obrigatório" do equipes.html.
- ❓ PENDENTE: (9.4) tempo pra desenvolver chassi+aero 100% cabe numa temporada?
- ❓ PENDENTE: (9.5) valor do +chance de quebra da punição.

### 🏎️ Replay Fase 3 (o que o Henrique quer ver)
- Hoje só a TABELA volta a volta (Fase 1). Falta a animação dos CARROS na pista
  (faixa vertical, líder no topo, outros pelo gap, boxes à esquerda, abandono à direita).
- NUNCA foi feita (não está no git). É feature nova a construir.

### 🐛 Login (erro de autenticação)
- Deu "erro de autenticação" no teste. Provável: botão Google (OAuth/.env no Linux).
- Solução provável: usar login normal (email/senha 123456), não o Google.
- Pendente confirmar/corrigir (precisa ver rotas/auth.py).

### 🎨 Verificar CSS antigo
- Conferir se ainda existe static/css/tema.css e tema_v3.css (versões velhas com cor
  hardcoded) e se o base.html NÃO os linka mais. Se sim, remover/apagar.

---

## 🔵 ÉPICO GRANDE (arquitetura — depois)
- [ ] Calendário/Agenda no admin + agendador automático (qualy/corrida por horário).
      Provisório: botão manual "Dia de Corrida" já existe.
- [ ] Grupos de 20 + fila de espera. Pirâmide (sobe = desce, dinâmico).
- [ ] Ranking por grupo/classe (o do treino livre depende disso).

---

## 🎨 DEPOIS (finalização)
- [ ] Menu de temas/cores no admin (variáveis CSS já preparadas).
- [ ] Testes automáticos (pytest).
- [ ] Manual/tutorial próprio do jogador (reescrito, sem copiar o como.txt).
- [ ] Sistema de duplas.

---

## 🔑 DECISÕES-CHAVE (resumo — detalhe no regras.md)
- Modelos 50-900: Motor/Câmbio/Suspensão travam no Parc Fermé; Pneu/Combustível variam por stint.
- Parc Fermé RÍGIDO: salvou travou. Romper lacre = R$1.000 + larga último. Se rompeu, pode pular quali.
- Combustível: consumo_qualifying CORRETO (regra 5.4). Jogador calcula pra (voltas + 1 do quali).
- Influências das pistas: Ayres 5-15 (conflito encerrado).
- Bots: os mais baratos + orçamento debitado (como jogador).
- Engenheiro atual NÃO obrigatório; ciclo de 2 engenheiros (ver seção 9 do regras.md).
- Bolsa de valores: CORTADA da v1.

---

## ⚙️ REGRAS DE TRABALHO COM A IA
- Arquivos COMPLETOS (nunca "procure a linha X"). PARÂMETRO ZERO de trecho solto.
- models.py: SÓ adicionar coluna/tabela. NUNCA reescrever o arquivo.
- NÃO inventar regras/colunas/rotas. Perguntar antes.
- Manter padrão registrar(app) (não Blueprint). Não quebrar url_for. UTF-8.
- FECHAR o que está aberto antes de abrir frente nova.
- Prompts/documentos: gerar como ARQUIVO (.md), não texto solto na tela.
- Chief Engineer (Claude) valida no sandbox antes de aplicar mudança grande.
- Documentos vivos: este + regras.md + MECANICA_AJUSTE_CARRO.md. Editar incremental.

---

## 🖥️ AMBIENTE
- Windows (PC casa): RX 6800 16GB, Ryzen 7 2700X, 16GB.
- Linux (notebook): Mint, Dell E6440, i5 4ª gen, 8GB. Usar python3 (ou ativar .venv).
- Git: https://github.com/henriquebdv-lab/openw (.env e client_secret no .gitignore).
- ⚠️ client_secret do Google vazou no chat — considerar revogar/gerar novo.

### Recriar banco (Linux)
```
cp jogo.db jogo_backup.db
rm jogo.db
python3 criar_banco.py
python3 seed_teste.py
```
(No Windows: copy / del / python)

### Gerar TXT (Linux) — cola UM comando por vez
```
find . -name "*.py" -not -path "./.venv/*" -not -path "./migrations/*" | sort | while read f; do echo "===== ${f#./} ====="; cat "$f"; echo ""; done > openwheel_py.txt
find templates -name "*.html" | sort | while read f; do echo "===== $f ====="; cat "$f"; echo ""; done > openwheel_html.txt
find static -name "*.css" | sort | while read f; do echo "===== $f ====="; cat "$f"; echo ""; done > openwheel_css.txt
```

---

## 🎯 COMEÇAR PRÓXIMA SESSÃO POR (sugestão):
1. Aplicar/testar o seed com bots honestos (20 no grid, tempos parelhos).
2. Resolver o login (email/senha vs Google).
3. Decidir: implementar os 2 engenheiros OU fazer o Replay Fase 3 (carros na pista).
