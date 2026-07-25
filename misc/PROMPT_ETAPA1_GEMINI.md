# PROMPT — Etapa 1 (para Gemini Pro)

> Cole este prompt no Gemini Pro. Ele tem acesso ao projeto (ou anexe
> openwheel_py.txt e openwheel_html.txt + regras.md + CONTINUAR_AQUI.md).

---

## CONTEXTO
Projeto "Open Wheel Strategy" (Flask + SQLAlchemy + SQLite). O app.py já foi
desmembrado numa pasta `rotas/` com o padrão `registrar(app)` (NÃO use
Blueprint — mudaria os nomes das rotas e quebraria os `url_for` dos templates).

## REGRAS DE TRABALHO (obrigatórias)
- Me entregue SEMPRE o arquivo COMPLETO, pronto pra substituir. NUNCA "procure a linha X".
- KISS/DRY. NÃO invente rotas, colunas ou regras.
- NÃO altere o schema do banco.
- Antes de codar, me mostre o diagnóstico e ESPERE eu aprovar.
- Trabalhe UMA tarefa por vez.

---

## OBJETIVO DA ETAPA 1
Separar "ver/acompanhar" de "executar" nas telas de Classificação e Corrida:

1. **AS TELAS de Classificação (grid) e Corrida (resultado) devem ficar
   VISÍVEIS no menu para TODOS os jogadores, em modo SOMENTE LEITURA** (só pra
   acompanhar o grid de largada e o resultado da corrida). NÃO esconder essas
   telas do jogador.

2. **Remover os BOTÕES DE DISPARO das telas do jogador:**
   - Em `templates/classificacao.html` existe o botão "Rodar classificação
     (1 volta rápida por equipe)" — ele aparece pra todos. REMOVER esse botão
     da tela; deixar a tela só exibindo o grid (quando houver resultado).
   - Em `templates/corrida.html` existem os botões "Rodar corrida da temporada"
     e "Simular corrida" (hoje dentro de `{% if usuario_logado.eh_admin %}`).
     REMOVER esses botões desta tela; deixar a tela só exibindo o replay/
     resultado da corrida.

3. **Mover o disparo manual para a área /admin (provisório):**
   - Criar na Administração uma tela/seção "Dia de Corrida" (ou similar) com os
     botões que hoje estão em classificacao.html e corrida.html:
     rodar classificação, rodar corrida da temporada e simular corrida livre.
   - Esse disparo manual é PROVISÓRIO (mais pra frente vira automático por
     horário). Só admin acessa, dentro de /admin.
   - Adicionar o link dessa nova tela na sidebar do admin (`admin_base.html`).

## ARQUIVOS QUE PROVAVELMENTE MUDAM (confirme no diagnóstico)
- `rotas/corrida.py` — hoje as rotas `classificacao_view` e `corrida_view`
  fazem o POST de execução (com check de admin). Reorganizar: as telas do
  jogador viram somente-leitura (GET), e o disparo (POST) passa a viver em
  rota(s) dentro de /admin (em `rotas/admin.py`), protegidas por
  `admin_requerido`.
- `templates/classificacao.html` — remover botão de disparo; manter exibição do grid.
- `templates/corrida.html` — remover botões de disparo; manter replay/resultado.
- `rotas/admin.py` — adicionar a rota/tela de disparo manual (Dia de Corrida).
- `templates/admin_*.html` — nova tela de admin + link na sidebar (admin_base.html).

## CUIDADOS
- Os NOMES das rotas existentes (`classificacao_view`, `corrida_view`) NÃO devem
  sumir se algum template/menu usa `url_for` neles (o menu base.html e a home
  referenciam `classificacao_view`). Se você mover a execução pra novas rotas de
  admin, mantenha `classificacao_view`/`corrida_view` existindo como as telas de
  leitura.
- A lógica pesada de simular corrida (`_executar_corrida_e_persistir`,
  `_aplicar_dados_pista_no_carro`) deve ser REAPROVEITADA, não reescrita —
  só chamada a partir da nova rota de admin. KISS/DRY.

## O QUE ENTREGAR (nesta ordem)
1. DIAGNÓSTICO: liste exatamente onde estão hoje os botões de disparo e como as
   rotas `classificacao_view`/`corrida_view` estão estruturadas (GET vs POST).
   Confirme o plano de mover o POST pra /admin. ESPERE minha aprovação.
2. Depois de aprovado: entregue os arquivos COMPLETOS alterados, um por vez.
3. Para cada arquivo, diga COMO testar (o que acessar como jogador, o que
   acessar como admin) e o resultado esperado.
