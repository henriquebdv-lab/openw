# Open Wheel Strategy — PONTO DE RETOMADA

> **Como usar num chat novo:** cole ESTE arquivo + o `regras.md` +
> o `openwheel_py.txt` (e o `openwheel_html.txt` se precisar de telas).
>
> **Última sessão:** 26/07/2026

---

## ✅ FEITO E FUNCIONANDO (testado)

### Base sólida (sessões anteriores)
- app.py desmembrado em `rotas/` (padrão registrar, NÃO Blueprint).
- Login Google (cada máquina tem seu `.env`).
- Quick wins: pneu "marca — valor", engenheiro obrigatório, pane seca = abandono.
- 7 pistas modernas + config de balanceamento no admin.

### Sessão 26/07 (dia grande)
- **models.py recuperado** do desastre (commit 41b5cb7) + testado.
- **Etapa 1 do Parc Fermé COMPLETA:** tabela SetupFimDeSemana criada; tela
  "Montagem Fim de Semana" mostra a pista da vez + categorias ideais; jogador
  escolhe MOTOR + CÂMBIO + SUSPENSÃO (modelos 50-900) e salva/persiste. ✅
- **Estratégia limpa:** removidos os configs de Motor/Câmbio/Suspensão/Injeção
  do topo (contrariavam o parc fermé). Sobrou só o Plano de Stints (pneu +
  combustível por stint), Pit Wall, validação de voltas e botão "+Stint". ✅
- **Quick wins da estratégia:** validação de voltas (planejadas vs pista, alerta
  colorido) + botão "+Stint" desabilita no limite. ✅
- **base.html** recriado em UTF-8 (acentos/emojis corrigidos). ✅
- **Combustível removido** da tela de montar equipe (rota usa TANQUE cheio padrão). ✅
- **Flash de confirmação** funciona via base.html (verde). ✅

---

## 🔴 PRÓXIMO PASSO: Parc Fermé — ETAPA 2 (o travamento)

> A Etapa 1 salva mas AINDA DEIXA editar à vontade (esperado). A Etapa 2 é
> travar de verdade.

- [ ] Ao salvar: mostrar AVISO de confirmação:
  "⚠️ Ao salvar, seu carro entra em PARC FERMÉ. Motor, câmbio e suspensão ficam
  travados pro fim de semana. Romper o lacre depois custa R$ 1.000 e você larga
  em último. Tem certeza?" [Sim] [Cancelar]
- [ ] Depois de salvo = TRAVAR (não deixa mais editar até a corrida rodar).
- [ ] Mostrar visualmente que está "em parc fermé" (ex: cadeado 🔒, campos
  desabilitados, botão "Romper lacre").
- Precisa de um campo de estado (ex: `travado` na SetupFimDeSemana) — quando
  for mexer no models.py, SÓ adicionar a coluna (não reescrever o arquivo).

### Etapas seguintes do Parc Fermé (depois da 2)
- [ ] Etapa 3: Romper o lacre (taxa R$ 1.000 + larga em último).
- [ ] Etapa 4: Pular a quali (liberado só quando o lacre foi rompido).
- [ ] Etapa 5: montar_carro puxar motor/câmbio/suspensão do SetupFimDeSemana
  (hoje ainda pega do CarroJogador) + limpar setups no fim da temporada.

---

## 🧪 PRIORIDADE ALTA: TESTES AUTOMÁTICOS + SEED DE TESTE
> Henrique está de saco cheio de recriar cadastro/admin/temporada a cada teste.
> DUAS soluções (conversar sobre isso no início de amanhã):

### A. Script "seed de teste" (resolve o saco cheio IMEDIATO)
- [ ] Criar `seed_teste.py` que, de uma vez, monta um ambiente de teste pronto:
  - Cria os 2 usuários admin (já como admin, sem precisar tornar-admin na mão).
  - Gera os fornecedores.
  - Cria uma temporada com algumas corridas.
  - (Opcional) já monta uma equipe de teste.
- Assim, depois de recriar o banco: `python seed_teste.py` e está tudo pronto.
- Fim de recriar tudo na mão toda vez. 🎯

### B. Testes automáticos (pytest) — a rede de segurança
- [ ] `pip install pytest`
- [ ] Suíte cobrindo idealmente CADA função importante. Prioridade:
  - Login (senha certa/errada)
  - montar_carro() não quebra
  - custo_total_contratos / custo_total_montagem
  - Stints salvam e leem (EstrategiaStint)
  - SetupFimDeSemana salva/lê (motor+câmbio+susp)
  - Validação de voltas
- [ ] Regra de ouro: rodar `pytest` ANTES de commitar mudança da IA.
- Obs: o Chief Engineer (Claude) pode ESCREVER e TESTAR a suíte no sandbox e
  entregar pronta pro Henrique só rodar.

---

## 🟡 PENDÊNCIAS DO TREINO LIVRE (conectam com parc fermé)
- [ ] NÃO pedir câmbio/suspensão/motor de novo no treino livre (já travados no
  parc fermé). O treino deve USAR o setup travado.
- [ ] Dropdown de pista: mostrar só a pista do fim de semana (proxima_corrida),
  sem dropdown com todas.
- [ ] Treino livre volta a volta (hoje roda tudo de uma vez). Interativo.
- [ ] Rever "combustível a carregar" no treino (se faz sentido ali).
- Obs: feedback do piloto JÁ existe (base boa).

---

## 🔵 ÉPICO GRANDE (arquitetura — depois)
- [ ] Calendário/Agenda no admin (ex: Seg/Qua/Sex, 19h qualy, 20h corrida).
- [ ] Agendador automático (qualy/corrida rodam sozinhos no horário).
      Pra TESTAR sem esperar: manter botão manual "rodar agora" no /admin.
- [ ] Grupos de 20 + fila de espera.
- [ ] Pirâmide: promoção/rebaixamento (quem sobe = quem desce, dinâmico).
- [ ] Classificação/Corrida em modo somente-leitura pro jogador; disparo só /admin.

---

## 🎨 DEPOIS (finalização)
- [ ] Refatoração de CSS: tirar style="" inline -> tema.css. JUNTO com isso,
  fazer o flash sumir sozinho após alguns segundos (JS). (Cuidado: IA adora
  quebrar layout nessa refatoração — fazer por partes, testando visual.)
- [ ] UX/UI command center (imagem do carro no box, painéis).
- [ ] Sprites de carro vista de cima (base recolorível) pro replay da corrida.

---

## 🔑 DEFINIÇÃO: onde cada MODELO (50-900) é escolhido
| Componente  | Onde escolhe              | Comportamento |
|-------------|---------------------------|---------------|
| Motor       | Parc Fermé (Montagem FDS) | TRAVA |
| Câmbio      | Parc Fermé (Montagem FDS) | TRAVA |
| Suspensão   | Parc Fermé (Montagem FDS) | TRAVA |
| Pneu        | Estratégia (por stint)    | VARIA |
| Combustível | Estratégia (por stint)    | VARIA |
| Injeção     | NÃO EXISTE                | removido |

---

## 🔒 DESIGN DO PARC FERMÉ (referência)
- Trava MOTOR + CÂMBIO + SUSPENSÃO (as peças/modelos) pro fim de semana.
- Pneu e combustível ficam livres (variam por stint na estratégia).
- Primeira coisa do FDS: montar o carro. Sem montar = sem carro. Precisa de $.
- Setup errado NÃO impede correr (anda, mas perde décimos / fica lento).
- RÍGIDO: salvou, travou. Só corrige rompendo o lacre.
- Romper o lacre: taxa R$ 1.000 + larga em último.
- Se rompeu o lacre: libera pular a quali (que gasta pneu/combustível), já que
  vai largar em último de qualquer forma.
- Persistência: tabela SetupFimDeSemana (equipe_id, corrida_id, modelo_motor,
  modelo_cambio, modelo_suspensao, criado_em). Limpar no fim da temporada.

---

## ⚙️ REGRAS DE TRABALHO COM A IA
- Arquivos COMPLETOS (nunca "procure a linha X"). KISS/DRY.
- NÃO reescrever arquivo inteiro quando o pedido é adicionar algo pequeno
  (lição do models.py). No models.py: SÓ adicionar coluna/tabela, nunca refazer.
- NÃO inventar regras/colunas/rotas. Perguntar antes.
- Manter padrão registrar(app) (não Blueprint). Não quebrar url_for.
- Salvar tudo em UTF-8 (projeto teve mojibake).
- Chief Engineer (Claude) valida models/arquivos no sandbox ANTES do Henrique
  aplicar/recriar banco.

---

## 🖥️ AMBIENTE
- Windows (PC casa): RX 6800 16GB, Ryzen 7 2700X, 16GB.
- Linux (notebook): Mint, Dell E6440, i5 4ª gen, 8GB.
- Git: https://github.com/henriquebdv-lab/openw (.env no .gitignore).
- Commit bom de referência (models.py original): 41b5cb7.

### Recriar banco (quando muda tabela/coluna)
```
copy jogo.db jogo_backup.db
del jogo.db
python criar_banco.py
```
Depois (o que dá SACO CHEIO — resolver com seed_teste.py):
registrar 2 emails -> flask tornar-admin <email> -> gerar fornecedores ->
recriar temporada. ← AUTOMATIZAR ISSO É PRIORIDADE.

### Gerar os TXT (Windows PowerShell)
```powershell
Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '\\migrations\\' } | Sort-Object FullName | ForEach-Object { "===== $($_.FullName.Replace($PWD.Path + '\', '')) ====="; Get-Content $_.FullName; "" } | Out-File -Encoding utf8 openwheel_py.txt
Get-ChildItem -Path templates -Recurse -Filter *.html | Sort-Object FullName | ForEach-Object { "===== $($_.FullName.Replace($PWD.Path + '\', '')) ====="; Get-Content $_.FullName; "" } | Out-File -Encoding utf8 openwheel_html.txt
```

---

## 🎯 COMEÇAR AMANHÃ POR:
1. Conversar sobre TESTES + criar o `seed_teste.py` (mata o saco cheio de
   recriar cadastro/admin/temporada). PRIORIDADE.
2. Depois: Parc Fermé Etapa 2 (travamento + aviso de confirmação).
