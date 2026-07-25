# PROMPT — Redesenho do Fluxo de Corrida do Open Wheel Strategy

> **Como usar:** cole este prompt inteiro na IA. Se ela nao tiver acesso aos
> arquivos, anexe tambem: `openwheel_py.txt`, `openwheel_html.txt`, `regras.md`
> e o `CONTINUAR_AQUI.md`.

---

## 1. CONTEXTO E COMO TRABALHAR COMIGO

Estou desenvolvendo um jogo web de gerenciamento de F1 chamado "Open Wheel
Strategy", em Python (Flask + SQLAlchemy + SQLite). O app.py ja foi desmembrado
numa pasta rotas/ usando o padrao registrar(app) (NAO use Blueprint - mudaria os
nomes das rotas e quebraria os url_for dos templates).

REGRAS DE TRABALHO (obrigatorias):
- Entregue SEMPRE arquivos COMPLETOS, prontos pra substituir. NUNCA me peca pra
  "procurar a linha X".
- KISS e DRY. Nada de sobre-engenharia.
- NAO invente regras, colunas ou rotas. Se tiver duvida, PERGUNTE antes.
- Explicacoes diretas e curtas (tenho TDAH, sou objetivo).
- Antes de codar, confirme que entendeu o design abaixo.
- NAO mexa no schema do banco sem eu autorizar (ha um bug de chassi/NOT NULL que
  decidi NAO tratar agora).

---

## 2. O PROBLEMA ATUAL (o que esta errado hoje)

Menu atual: Painel, Minha Equipe, Desenvolvimento, Treinamento, Treino Livre,
Treino Oficial, Estrategia, Corrida, Classificacao, Temporada, Pistas, Admin.

Problemas:
1. A Classificacao (grid de largada) aparece DEPOIS da Corrida - esta invertido.
   A classificacao (qualifying) define de onde cada um larga, entao vem ANTES.
2. Corrida e Classificacao sao disparadas MANUALMENTE (o admin clica). No design
   correto, isso deve ser AUTOMATICO por horario.
3. O jogador ve "Corrida" no menu, dando a impressao de que ele dispara a
   corrida - mas quem "roda" deve ser o sistema, no horario agendado.

---

## 3. O FLUXO CORRETO (o que eu QUERO)

### Fase 1 - Preparacao (acoes do JOGADOR)
1. Minha Equipe = montar/salvar o carro (contratos: motor, pneu, cambio,
   suspensao etc.). Base fixa.
2. Treino Livre - testa setup. Escolhe combustivel + tipo de pneu SO pra esse
   treino.
3. Treino Oficial - ajusta pra corrida. Escolhe combustivel + tipo de pneu DE
   NOVO (escolha independente).
4. Classificacao (prep do jogador) - poe pneu + combustivel de novo, define e
   SALVA a estrategia (inclui os modelos 50-900).

IMPORTANTE: combustivel + tipo de pneu sao escolhidos SEPARADAMENTE em cada fase
(livre, oficial, corrida). Nao e a mesma escolha reaproveitada.

### Trava (condicao obrigatoria)
5. O piloto SO participa da corrida SE tiver a estrategia SALVA. Sem estrategia
   salva = fica de fora (nao corre).

### Fase 2 - Execucao AUTOMATICA por horario (o SISTEMA faz sozinho)
6. O ADMIN define um CALENDARIO fixo. Ex: corridas Seg/Qua/Sex; 19h = Qualy,
   20h = Corrida.
7. Chega 19h -> o SISTEMA roda o QUALY automaticamente e gera o GRID DE LARGADA
   de cada grupo. (Ninguem clica - e por horario.)
8. Chega 20h -> o SISTEMA roda a CORRIDA automaticamente, para cada grupo, com o
   grid + as estrategias salvas. So entram os pilotos que salvaram.

### Fase 3 - Resultado e ciclo
9. Resultado de cada corrida - premios ($) + pontos da temporada.
10. Temporada - ranking de cada grupo/divisao.
11. Fim da temporada -> promocao/rebaixamento entre divisoes (piramide abaixo).
12. Novos inscritos entram na fila de espera; comeca nova temporada.

---

## 4. SISTEMA DE GRUPOS (piramide / series)

- Cada corrida tem no maximo 20 pilotos = 1 grupo.
- Quando um grupo enche (20), um novo grupo e criado. Novos inscritos vao pra uma
  FILA DE ESPERA: um grupo novo so "abre" quando enche 20.
- Grupos organizados em DIVISOES, como piramide/series do futebol:
  - Divisao 1 (topo): 1 grupo. Nao sobe; so desce.
  - Divisao 2: mais grupos. Sobe pra Div 1, desce pra Div 3.
  - Divisao 3, 4...: cada nivel abaixo tem MAIS grupos (base larga).
- Promocao/rebaixamento no fim da temporada, com base no ranking de cada grupo.

REGRA DE OURO do balanceamento:
- Em cada fronteira entre duas divisoes: quem SOBE = quem DESCE (troca 1:1 em
  quantidade), senao o grupo de destino nao fecha os 20.
- A quantidade exata que sobe/desce e DINAMICA: depende de quantos inscritos
  existem. NAO e numero fixo.
- Efeito desejado: como a base tem mais grupos, subir fica cada vez mais dificil
  quanto mais perto do topo.

---

## 5. IMPLICACAO TECNICA (o que provavelmente falta no codigo)

Mudanca GRANDE de arquitetura. Preciso de 3 componentes novos:
1. Calendario/Agenda (tabela nova): admin cadastra dias e horarios dos eventos.
2. Agendador (scheduler) no servidor que dispara qualy e corrida nos horarios,
   sem intervencao manual (ex: APScheduler no Flask, ou equivalente mais simples
   e KISS pro meu caso - SQLite, 1 app Flask).
3. Logica de grupos + piramide: dividir pilotos em grupos de 20, rodar 1 corrida
   por grupo, aplicar promocao/rebaixamento (dinamico) no fim da temporada, e
   gerenciar a fila de espera.

---

## 6. O QUE EU QUERO QUE VOCE ME ENTREGUE (nesta ordem)

1. Confirmacao de entendimento (8-10 linhas): reescreva com suas palavras o fluxo
   pra provar que entendeu.
2. Verificacao de regras: releia o regras.md e liste (bullets) as regras que
   impactam este redesenho (estrategia obrigatoria, escolha por fase, pontuacao,
   premios, grupos/divisoes). Diga o que NAO esta documentado ainda (piramide,
   calendario automatico).
3. Diagnostico do codigo atual: como Corrida e Classificacao funcionam hoje
   (manuais? admin-only?); o que da pra reaproveitar (models Temporada,
   CorridaAgendada, ResultadoCorrida...); o que NAO existe e precisa criar
   (calendario, scheduler, grupos).
4. PLANO DE IMPLEMENTACAO EM ETAPAS pequenas (a parte mais importante): quebre a
   mudanca em passos incrementais, do mais simples ao mais complexo, cada um
   testavel isoladamente. Para cada etapa: objetivo, arquivos afetados, como
   testar. NAO code tudo de uma vez - so o plano primeiro. Sugestao de ordem:
   - Etapa 1: corrigir ORDEM no menu (Classificacao antes de Corrida) + esconder
     essas telas do jogador comum.
   - Etapa 2: modelo de Calendario/Agenda + tela no admin.
   - Etapa 3: sistema de grupos de 20 + fila de espera.
   - Etapa 4: agendador (qualy/corrida por horario).
   - Etapa 5: promocao/rebaixamento (piramide) no fim da temporada.
5. So depois que eu aprovar o plano, codamos UMA etapa por vez, sempre com
   arquivos completos.
6. Resumo final no padrao do CONTINUAR_AQUI.md, adicionando este redesenho como
   epico novo, com as etapas como checklist.

---

## 7. FLUXO DE TESTE (combinado)
Voce entrega arquivos completos -> eu testo na minha maquina -> te devolvo o que
modifiquei pra voce conferir. Sempre me diga COMO testar e o que esperar.

## 8. GIT
git pull / git add . / git commit -m "descricao - feito no Windows|Linux" / git push
Repositorio: https://github.com/henriquebdv-lab/openw
(.env esta no .gitignore - credenciais nao sobem, e o certo.)
