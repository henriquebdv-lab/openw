# Open Wheel Strategy — PONTO DE RETOMADA

> **Como usar num chat novo:** cole ESTE arquivo + o `regras.md` +
> o `openwheel_py.txt` (e o `openwheel_html.txt` se precisar de telas)
> na primeira mensagem. Diga: "Vamos continuar o Open Wheel Strategy
> de onde paramos, seguindo o CONTINUAR_AQUI.md."
>
> **Última sessão:** 25/07/2026

---

## ✅ FEITO E FUNCIONANDO

### Sessão 24/07
- **Desmembramento do app.py** de 1000+ linhas para ~137, com rotas na pasta
  `rotas/` (padrão `registrar(app)`, NÃO Blueprint — nomes de rota iguais, então
  nenhum template quebrou). Testado.
- **Login Google no Linux** resolvido (era o `.env` faltando; cada máquina tem o seu).
- **Admin** criado (`henriquebettegaclaro@gmail.com`).

### Sessão 25/07
- **Pneu no formato "marca — valor"**: `gerar_pneus` (`seed_fornecedores.py`)
  grava `categoria_chuva="seco"` fixo. A condição vem do modelo 50-900, não do
  fornecedor. No jogo aparece só "Pneu — marca — R$ valor".
- **7 pistas modernas**: criado e executado `popular_pistas_modernas.py` com os
  dados canônicos. ⚠️ CONFERIR se os valores ficaram coerentes (10=neutro,
  range 5-15; validar numa pista conhecida tipo Red Bull Ring).
- **Config no admin** (`admin_configuracoes`) expandida — agora edita:
  Prêmio por Vitória (1º), Multiplicador de Consumo, Chance de Quebra Base/Mínima.

---

## 🔴 EPICO GRANDE: REDESENHO DO FLUXO DE CORRIDA (próximo)

> Design estrutural definido. Mudança de ARQUITETURA — fazer por ETAPAS, uma por
> vez, cada uma testável.

### O fluxo correto (resumo)
1. **Prep do JOGADOR:** Minha Equipe (monta carro) → Treino Livre → Treino
   Oficial → Classificação. Em CADA fase escolhe combustível + tipo de pneu
   (escolhas independentes). Na Classificação define e **SALVA a estratégia**.
2. **TRAVA:** o piloto só corre SE tiver estratégia salva (senão fica de fora).
3. **AUTOMÁTICO por horário:** o ADMIN define um calendário (ex: Seg/Qua/Sex,
   19h qualy, 20h corrida). O SISTEMA roda sozinho:
   - 19h → QUALY automático → gera o grid de cada grupo.
   - 20h → CORRIDA automática de cada grupo (só quem salvou estratégia).
4. **Resultado** (prêmios + pontos) → **Temporada** (ranking por grupo/divisão).
5. **Fim da temporada:** promoção/rebaixamento (pirâmide).

### DECISÃO sobre Classificação e Corrida (importante — a IA já confundiu isso)
- **AS TELAS** de Classificação (grid) e Corrida (resultado) ficam **VISÍVEIS**
  no menu pra TODOS, em modo **somente leitura** (pra acompanhar). NÃO esconder.
- **BOTÕES de disparo** (rodar qualy/corrida) NÃO aparecem nas telas do jogador.
- **Disparo manual = SÓ no /admin** (provisório, opção A), até o agendador
  automático (Etapa 4) ficar pronto.

### Sistema de grupos (pirâmide / séries)
- 20 pilotos por grupo. Grupo novo abre só quando enche 20 (fila de espera).
- Divisões em pirâmide: Div 1 (1 grupo, topo, só desce), Div 2 (mais grupos),
  base mais larga embaixo. Promoção/rebaixamento no fim da temporada.
- REGRA DE OURO: em cada fronteira, QUEM SOBE = QUEM DESCE (quantidade DINÂMICA,
  depende do nº de inscritos — não é número fixo). Base não desce; topo não sobe.

### Etapas de implementação (nesta ordem)
- [ ] **Etapa 1:** Classificação e Corrida em modo somente-leitura no menu do
      jogador; remover botões de disparo dessas telas; disparo manual só no /admin.
- [ ] **Etapa 2:** modelo de Calendário/Agenda + tela no admin.
- [ ] **Etapa 3:** grupos de 20 + fila de espera.
- [ ] **Etapa 4:** agendador (qualy/corrida automáticos por horário; ex APScheduler).
- [ ] **Etapa 5:** promoção/rebaixamento (pirâmide) no fim da temporada.
- [ ] **(cosmético, quando sobrar tempo):** refatorar CSS — tirar `style="..."`
      inline dos templates e centralizar em `static/css/tema.css`.

---

## 🟡 PENDÊNCIAS MENORES
- **A.** Limpar a linha "Categoria: seco" do card do pneu em `minha_equipe.html`
  (só o card do pneu; não mexer nos outros).
- **B.** Bug do banco (chassi/NOT NULL) — `corrigir_banco.py` pronto, mas
  DECIDIDO NÃO mexer no banco por enquanto.

---

## 📋 DECISÕES DE REGRA
1. Categorias das pistas = dados canônicos Ayres (range 5-15 real).
2. Pneu neutro no fornecedor — condição vem do modelo 50-900.
3. Engenheiro nível 1 automático na conta nova (grátis; entrega chassi/aero nv1).
4. Chassi NÃO é fornecedor (vem do engenheiro/Desenvolvimento).
5. app.py desmembrado (padrão registrar, não Blueprint).
6. Piloto só corre SE estratégia salva.
7. Combustível + pneu escolhidos por fase (livre/oficial/corrida).
8. Qualy e corrida automáticos por horário (admin define calendário).
9. Grupos de 20; grupo novo abre ao encher; fila de espera.
10. Pirâmide: quem sobe = quem desce (quantidade dinâmica).
11. Bolsa de Valores NÃO entra na versão inicial (fica pra depois).

---

## ⚙️ REGRAS DE TRABALHO COM A IA
- SEMPRE arquivos COMPLETOS, prontos pra substituir (nunca "procure a linha X").
- KISS / DRY. Explicações diretas e curtas.
- NÃO inventar regras/colunas/rotas. Perguntar ANTES se tiver dúvida.
- NÃO mexer no schema do banco sem autorização.
- NÃO trocar o padrão registrar(app) por Blueprint.
- Em tarefas grandes: fazer PLANO em etapas e só codar após aprovação.

---

## 🎮 REFERÊNCIA
Jogo base que inspirou: "estrategia" (menu em seções: Temporada/Verificações/
Colaboradores; tinha "Próxima Corrida", Design do Carro, Ranking, e uma Bolsa de
Valores — esta última fora da v1).

---

## 🖥️ AMBIENTE
- **Windows (PC casa):** RX 6800 16GB, Ryzen 7 2700X, 16GB RAM.
- **Linux (notebook):** Linux Mint, Dell E6440, i5 4ª gen, 8GB RAM.
- **Git:** https://github.com/henriquebdv-lab/openw
  - `.env` no `.gitignore` (credenciais não sobem).
  - Convenção de commit: "descrição - feito no Windows/Linux".
  - Push: se der erro de credencial no terminal, usar o botão Sync/Push do VS Code.

### Gerar os TXT do projeto (pra colar em chat novo)
Linux (bash):
```bash
find . -name "*.py" -not -path "./.venv/*" -not -path "./migrations/*" | sort | while read f; do echo "===== ${f#./} ====="; cat "$f"; echo ""; done > openwheel_py.txt
find templates -name "*.html" | sort | while read f; do echo "===== $f ====="; cat "$f"; echo ""; done > openwheel_html.txt
```
Windows (PowerShell):
```powershell
Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '\\migrations\\' } | Sort-Object FullName | ForEach-Object { "===== $($_.FullName.Replace($PWD.Path + '\', '')) ====="; Get-Content $_.FullName; "" } | Out-File -Encoding utf8 openwheel_py.txt
Get-ChildItem -Path templates -Recurse -Filter *.html | Sort-Object FullName | ForEach-Object { "===== $($_.FullName.Replace($PWD.Path + '\', '')) ====="; Get-Content $_.FullName; "" } | Out-File -Encoding utf8 openwheel_html.txt
```

---

## 🎯 PRÓXIMO PASSO
- [ ] Começar a **Etapa 1** do épico (telas somente-leitura + botão só no /admin).
