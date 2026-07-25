# Open Wheel Strategy — PONTO DE RETOMADA

> **Como usar num chat novo:** cole ESTE arquivo + o `regras.md` +
> o `openwheel_py.txt` (e o `openwheel_html.txt` se precisar de telas)
> na primeira mensagem. Diga: "Vamos continuar o Open Wheel Strategy
> de onde paramos, seguindo o CONTINUAR_AQUI.md."
>
> **Última sessão:** 25/07/2026

---

## ✅ FEITO E FUNCIONANDO

### 1. DESMEMBRAMENTO DO app.py — CONCLUÍDO ✅
- `app.py` saiu de 1000+ linhas para ~137 linhas.
- Rotas divididas na pasta `rotas/` usando o padrão `registrar(app)`
  (NÃO Blueprint — os nomes das rotas continuam iguais, então nenhum
  template quebrou). Testado: nenhuma tela quebrada.

Estrutura:
```
openwheel/
├── app.py                 (enxuto)
├── extensoes.py           (oauth, migrate, login_requerido, admin_requerido)
├── fornecedores_config.py (FORNECEDORES_CONFIG + categorias)
├── rotas/
│   ├── __init__.py  auth.py  equipe.py  desenvolvimento.py
│   ├── treino.py  corrida.py  temporada.py  admin.py
└── (models.py, models_temporada.py, carro.py, corrida.py,
    seed_fornecedores.py, pistas_reais_db.py, progressao.py... inalterados)
```

### 2. LOGIN GOOGLE NO LINUX — RESOLVIDO ✅
- Era o `.env` faltando no Linux (está no `.gitignore`, não veio no pull).
- Solução: criar o `.env` local em cada máquina, copiando as credenciais.

### 3. ADMIN CRIADO ✅
- `henriquebettegaclaro@gmail.com` virou admin (via `flask tornar-admin`).

### 4. PNEU no formato "marca — valor" — FEITO e TESTADO ✅
- `gerar_pneus` (seed_fornecedores.py) agora grava `categoria_chuva="seco"`
  fixo. A condição vem do modelo 50-900, não do fornecedor.
- No jogo o pneu aparece só como "Pneu — marca — R$ valor".
- ⚠️ Pra valer: rodar "Gerar fornecedores" no /admin (afeta só os pneus NOVOS;
  os atuais já estavam ok pelo neutralizar_pneu.py).

---

## 🔴 EPICO GRANDE: REDESENHO DO FLUXO DE CORRIDA (não iniciado)

> Design completo definido em 25/07. Ver `PROMPT_DESIGN_FLUXO.md` e as imagens
> de fluxograma. É uma mudança de ARQUITETURA — fazer por ETAPAS, não de uma vez.

### O fluxo correto (resumo)
1. **Prep do JOGADOR:** Minha Equipe (monta carro) -> Treino Livre -> Treino
   Oficial -> Classificação. Em CADA fase escolhe combustível + tipo de pneu
   (escolhas independentes). Na Classificação define e **SALVA a estratégia**.
2. **TRAVA:** o piloto só corre SE tiver estratégia salva (senão fica de fora).
3. **AUTOMÁTICO por horário:** o ADMIN define um calendário (ex: Seg/Qua/Sex,
   19h qualy, 20h corrida). O SISTEMA roda sozinho:
   - 19h -> QUALY automático -> gera o grid de cada grupo.
   - 20h -> CORRIDA automática de cada grupo (só quem salvou estratégia).
4. **Resultado** (prêmios + pontos) -> **Temporada** (ranking por grupo/divisão).
5. **Fim da temporada:** promoção/rebaixamento (pirâmide).

### Sistema de grupos (pirâmide / séries)
- 20 pilotos por grupo. Grupo novo abre só quando enche 20 (fila de espera).
- Divisões em pirâmide: Div 1 (1 grupo, topo, só desce), Div 2 (mais grupos),
  Div 3/4... (base mais larga).
- Promoção/rebaixamento no fim da temporada.
- REGRA DE OURO: em cada fronteira, QUEM SOBE = QUEM DESCE (quantidade DINÂMICA,
  depende do nº de inscritos — não é número fixo).

### Problemas do código ATUAL (a corrigir)
- Classificação aparece DEPOIS da Corrida (deveria ser ANTES).
- Corrida e Classificação são disparadas MANUALMENTE pelo admin (deveria ser
  automático por horário).

### Componentes técnicos que faltam
1. Tabela de **Calendário/Agenda** (admin cadastra dias + horários).
2. **Agendador (scheduler)** no servidor (ex: APScheduler) que dispara
   qualy/corrida no horário.
3. Lógica de **grupos + pirâmide** (dividir em 20, fila de espera,
   promoção/rebaixamento dinâmico).

### Etapas de implementação (fazer nesta ordem, uma por vez)
- [ ] **Etapa 1:** corrigir ordem do menu (Classificação antes de Corrida) +
      esconder essas telas do jogador comum.
- [ ] **Etapa 2:** modelo de Calendário/Agenda + tela no admin.
- [ ] **Etapa 3:** sistema de grupos de 20 + fila de espera.
- [ ] **Etapa 4:** agendador (qualy/corrida automáticos por horário).
- [ ] **Etapa 5:** promoção/rebaixamento (pirâmide) no fim da temporada.

---

## 🟡 OUTRAS PENDÊNCIAS (menores)

### A. Limpar "Categoria: seco" da tela Minha Equipe
- No `minha_equipe.html`, remover a linha "Categoria: seco" do card do pneu
  (não faz mais sentido). Só o card do pneu; não mexer nos outros.

### B. 7 pistas modernas SEM dado canônico
- Definir câmbio/suspensão/box/influências (manter 10=neutro, range 5-15 —
  CONFERIR no regras.md se é 5-15 ou 7-15). Pistas: Circuit of the Americas,
  Hermanos Rodríguez, Moscow Raceway, Norisring, Oschersleben, Sochi, Yas Marina.
- Fazer proposta de tabela ANTES de gravar; só popular após aprovação.

### C. Config de balanceamento editável no admin
- Já existe `admin_configuracoes` + model `Configuracao` — verificar o que já é
  editável vs hardcoded antes de mexer.

### D. Bug do banco (chassi / NOT NULL) — PULADO por decisão
- `corrigir_banco.py` pronto pra remover a trava NOT NULL do chassi.
- Decidi NÃO mexer no banco por enquanto.

---

## 📋 DECISÕES DE REGRA TOMADAS

1. ✅ Categorias das pistas = Opção A (dados canônicos Ayres, range 5-15 real).
2. ✅ Pneu é NEUTRO no fornecedor — condição vem do modelo 50-900.
3. ✅ Engenheiro nível 1 automático na conta nova (grátis, entrega chassi/aero nv1).
4. ✅ Chassi NÃO é fornecedor (vem do engenheiro/Desenvolvimento).
5. ✅ Desmembrar app.py em rotas/ (padrão registrar, não Blueprint) — FEITO.
6. 🆕 Piloto só corre SE estratégia salva.
7. 🆕 Combustível + pneu escolhidos por fase (livre/oficial/corrida).
8. 🆕 Qualy e corrida AUTOMÁTICOS por horário (admin define calendário).
9. 🆕 Grupos de 20; grupo novo abre ao encher; fila de espera.
10. 🆕 Pirâmide: quem sobe = quem desce (quantidade dinâmica).

---

## ⚙️ REGRAS DE TRABALHO COM A IA
- SEMPRE arquivos COMPLETOS, prontos pra substituir (nunca "procure a linha X").
- KISS / DRY. Explicações diretas e curtas.
- NÃO inventar regras/colunas/rotas. Perguntar ANTES se tiver dúvida.
- NÃO mexer no schema do banco sem autorização.
- NÃO trocar o padrão registrar(app) por Blueprint.

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

## 🎯 PRÓXIMOS PASSOS SUGERIDOS
- [ ] Aplicar/commitar o seed_fornecedores.py (pneu) se ainda não subiu.
- [ ] Pendências menores A (Minha Equipe), B (7 pistas), C (config admin).
- [ ] Começar o ÉPICO do redesenho pela Etapa 1 (mais simples e segura).
