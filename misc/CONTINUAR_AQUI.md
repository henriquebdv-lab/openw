# Open Wheel Strategy — PONTO DE RETOMADA (continuar depois)

> **Como usar num chat novo:** cole ESTE arquivo + o `regras.md` +
> o `openwheel_py.txt` (e o `openwheel_html.txt` se precisar de telas)
> na primeira mensagem. Diga: "Vamos continuar o Open Wheel Strategy
> de onde paramos, seguindo o CONTINUAR_AQUI.md."
>
> **Última sessão:** 24/07/2026

---

## ✅ FEITO NA SESSÃO DE 24/07/2026 (tudo testado e funcionando)

### 1. DESMEMBRAMENTO DO app.py — CONCLUÍDO ✅
- **O que era:** `app.py` com 1000+ linhas e ~30 rotas (uma "tripa" só).
- **O que virou:** `app.py` enxuto (~137 linhas) + rotas divididas em
  arquivos pequenos dentro da pasta `rotas/`.
- **Padrão usado:** `registrar(app)` (NÃO Blueprint puro).
  - Motivo: Blueprint mudaria o nome das rotas (login → auth.login) e
    quebraria TODOS os `url_for(...)` dos templates. Com `registrar(app)`
    os nomes das rotas continuam IDÊNTICOS → nenhum template mudou.
- **Testado:** app sobe, registra as 33 rotas, comandos CLI (init-db,
  tornar-admin) OK, e o Henrique confirmou: "nenhuma tela quebrada".

#### Estrutura nova de arquivos
```
openwheel/
├── app.py                 ← ~137 linhas: cria app, filtros, contexto, CLI, registra rotas
├── extensoes.py           ← oauth, migrate, login_requerido, admin_requerido
├── fornecedores_config.py ← FORNECEDORES_CONFIG + CATEGORIAS_PISTA/CHUVA
├── rotas/
│   ├── __init__.py        ← chama registrar() de cada área (NOME: dois underscores de cada lado)
│   ├── auth.py            ← home, registrar, login, login google + callback, logout
│   ├── equipe.py          ← minha_equipe, editar_equipe, resetar_equipe
│   ├── desenvolvimento.py ← desenvolvimento_view, treinamento_view
│   ├── treino.py          ← treino_livre, ranking, treino_oficial
│   ├── corrida.py         ← estrategia_corrida, classificacao, corrida (+ helpers)
│   ├── temporada.py       ← temporada, pistas_reais
│   └── admin.py           ← todas as rotas /admin
└── (resto IGUAL: models.py, carro.py, corrida.py, seed_fornecedores.py, etc.)
```
> ⚠️ NÃO foram alterados: models.py, models_temporada.py, carro.py,
> corrida.py (raiz), config.py, seed_fornecedores.py, templates, etc.
> Só o app.py foi fatiado.

### 2. LOGIN GOOGLE NO LINUX — RESOLVIDO ✅
- **Sintoma:** erro `invalid_client / OAuth client was not found` no Linux.
- **Causa:** o `.env` (com GOOGLE_CLIENT_ID/SECRET) está no `.gitignore`,
  então NÃO veio no `git pull`. No Windows funcionava porque o `.env`
  existe lá.
- **Solução:** criar o `.env` manualmente na máquina Linux, copiando as
  credenciais do `.env` do Windows. (Cada máquina tem seu `.env` local.)

### 3. ADMIN CRIADO ✅
- `henriquebettegaclaro@gmail.com` virou admin (via `flask tornar-admin`).

---

## 🖥️ AMBIENTE DE TRABALHO (2 máquinas)

- **Windows (PC casa):** RX 6800 16GB, Ryzen 7 2700X, 16GB RAM.
  Onde o login Google já funcionava.
- **Linux (notebook):** Linux Mint, Dell E6440, i5 4ª gen, 8GB RAM.
  Onde configuramos o `.env`, o desmembramento e o LM Studio.
- **Git:** repositório https://github.com/henriquebdv-lab/openw
  - Email git: `256236843+henriquebdv-lab@users.noreply.github.com`
  - Convenção nova de commit: adicionar "- feito no Windows" / "- feito no Linux".
  - PUSH: se der erro de credencial no terminal (vscode-git .sock),
    fazer o push pelo botão Sync/Push do VS Code (reautoriza a sessão).

### Comandos úteis (fim/começo de sessão)
```bash
git pull                          # começo (traz o que fez na outra máquina)
git add . && git commit -m "..."  # salva
git push                          # envia (ou pelo botão do VS Code)
```

### Gerar os TXT do projeto (pra colar em chat novo)
```bash
# Python (inclui a pasta rotas/):
find . -name "*.py" -not -path "./.venv/*" -not -path "./migrations/*" | sort | while read f; do echo "===== ${f#./} ====="; cat "$f"; echo ""; done > openwheel_py.txt

# HTML (templates):
find templates -name "*.html" | sort | while read f; do echo "===== $f ====="; cat "$f"; echo ""; done > openwheel_html.txt
```

---

## 🟡 PENDÊNCIAS (não feitas ainda)

### A. BUG do banco (chassi) — PULADO por decisão do Henrique
- Erro `NOT NULL constraint failed: carros_jogadores.chassi_fornecedor_id`
  ao criar equipe (banco antigo tem a trava; código novo manda None).
- Solução pronta era rodar `corrigir_banco.py` UMA VEZ pra remover a trava.
- STATUS: Henrique optou por NÃO mexer no banco por enquanto.
  (A função minha_equipe já está com `chassi_fornecedor_id=None`, versão limpa.)

### B. seed_fornecedores.py — gerar_pneus neutro
- Fazer pneus NOVOS nascerem neutros ("seco") ao gerar fornecedores no admin.
- Os pneus ATUAIS já foram neutralizados (neutralizar_pneu.py rodado).

### C. 7 pistas modernas SEM dado canônico
- Definir câmbio/suspensão/box/influências (proposta existe, não aprovada).
- Circuit of the Americas, Hermanos Rodríguez, Moscow Raceway, Norisring,
  Oschersleben, Sochi, Yas Marina.

### D. Config de balanceamento editável no admin (ideia aprovada, fazer depois)

---

## 📋 DECISÕES DE REGRA JÁ TOMADAS (do histórico anterior)

1. ✅ Categorias das pistas = Opção A (dados canônicos Ayres, range 5-15 real).
2. ✅ Pneu é NEUTRO — condição vem do modelo 50-900, não do fornecedor.
3. ✅ Engenheiro nível 1 automático na conta nova (grátis, não escolhido).
4. ✅ Chassi/aero projetados pelo engenheiro (não são fornecedor).
5. ✅ Desmembrar app.py em arquivos pequenos — FEITO nesta sessão.

---

## ⚙️ REGRAS DE TRABALHO COM A IA (reforçadas)
- SEMPRE entregar arquivos COMPLETOS, prontos pra substituir (nunca pedaços
  ou "procure a linha X").
- Henrique não é avançado em terminal/Linux/SSH — dar passo a passo claro.
- KISS/DRY. Explicações diretas.

---

## 🎯 PRÓXIMOS PASSOS SUGERIDOS (quando voltar)
- [ ] Fazer o `git push` do desmembramento (se ainda não subiu).
- [ ] Escolher a próxima pendência: B (pneu neutro), C (7 pistas) ou D (config admin).
- [ ] (Opcional/curiosidade) Setup de IA local no PC de casa (LM Studio + Cline
      com Qwen2.5 Coder 14B) — só exploração, não faz parte do jogo.
