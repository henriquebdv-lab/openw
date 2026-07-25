# PROMPT — Continuar o Open Wheel Strategy

> **Como usar:** cole ESTE prompt inteiro na IA. Se ela NÃO tiver acesso aos
> arquivos do projeto, anexe também: `openwheel_py.txt`, `openwheel_html.txt`,
> `regras.md` e o `CONTINUAR_AQUI.md`.

---

## 1. QUEM VOCÊ ESTÁ AJUDANDO E COMO

Estou desenvolvendo um jogo web de gerenciamento de F1 chamado **"Open Wheel
Strategy"**, em **Python (Flask + SQLAlchemy + SQLite)**. Trabalho em duas
máquinas (Windows e Linux Mint) e versiono no GitHub.

**REGRAS DE TRABALHO (obrigatórias, siga à risca):**
- Me entregue **SEMPRE o arquivo COMPLETO, pronto pra substituir**. NUNCA me
  peça pra "procurar a linha X" ou colar trechos soltos.
- Se a mudança for numa função autocontida, pode me devolver a **função inteira**
  completa, mas deixe claro qual arquivo e onde.
- Siga **KISS e DRY**. Nada de sobre-engenharia.
- **NÃO invente** colunas de banco, rotas ou regras que não existem. Se tiver
  dúvida, me pergunte ANTES de codar.
- Explique de forma **direta e curta** o que mudou (sou objetivo, tenho TDAH).
- Antes de mexer, **confirme que entendeu** relendo o material (regras.md).

---

## 2. ARQUITETURA ATUAL (já refatorada, NÃO quebrar)

O `app.py` foi **desmembrado** de 1000+ linhas para ~137 linhas. As rotas agora
vivem em arquivos pequenos dentro da pasta `rotas/`, usando o padrão
`registrar(app)` (NÃO Blueprint puro).

**MOTIVO CRÍTICO:** com `registrar(app)` os NOMES das rotas continuam idênticos
(`login`, `minha_equipe`, `corrida_view`...), então os `url_for(...)` dos
templates continuam funcionando. **Se você usar Blueprint, quebra tudo.** NÃO
mude o padrão.

Estrutura:
```
openwheel/
├── app.py                 (enxuto: cria app, filtros, contexto, CLI, registra rotas)
├── extensoes.py           (oauth, migrate, login_requerido, admin_requerido)
├── fornecedores_config.py (FORNECEDORES_CONFIG + categorias)
├── rotas/
│   ├── __init__.py        (chama registrar() de cada área)
│   ├── auth.py  equipe.py  desenvolvimento.py  treino.py
│   ├── corrida.py  temporada.py  admin.py
└── (models.py, models_temporada.py, carro.py, corrida.py, seed_fornecedores.py,
    pistas_reais_db.py, progressao.py, etc. — inalterados)
```

---

## 3. O QUE JÁ FOI FEITO (não precisa refazer)

1. ✅ **Desmembramento do app.py** em `rotas/` — testado, nenhuma tela quebrada.
2. ✅ **Login Google** — funcionando (cada máquina tem seu `.env` local, que
   está no `.gitignore`).
3. ✅ **Engenheiro nível 1 automático** na conta nova (grátis; entrega chassi e
   aero nível 1). O chassi NÃO é mais fornecedor.
4. ✅ **Categorias das pistas** populadas com dados canônicos (Planilha Ayres).
5. ✅ **Pneu sem condição no fornecedor**: a função `gerar_pneus` do
   `seed_fornecedores.py` agora grava `categoria_chuva="seco"` fixo. A condição
   (seco/molhada/encharcada) vem do MODELO 50-900 escolhido por corrida, não do
   fornecedor. No jogo o pneu aparece só como **"Pneu — marca — R$ valor"**.

---

## 4. O QUE FALTA FAZER (tarefas desta rodada)

Trate cada item como uma tarefa separada. Para CADA arquivo alterado, me devolva
o arquivo COMPLETO. Se algum item depender de decisão minha, PERGUNTE antes.

### TAREFA A — Limpar "Categoria: seco" da tela Minha Equipe
No template `templates/minha_equipe.html`, no card do PNEU, existe a linha:
`Categoria: {{ carro.pneu.categoria_chuva|default('seco') }}`
Ela não faz mais sentido (pneu não tem condição no fornecedor). **Remova essa
linha do card do pneu** (deixe só o nome do fornecedor). Não mexa nos outros
cards (motor, câmbio, suspensão etc.). Me devolva o `minha_equipe.html` completo.

### TAREFA B — 7 pistas modernas SEM dado canônico
Há 7 pistas que não têm dado na Planilha Ayres e precisam de valores. Regras:
manter 10 = neutro, range de influências 5–15 (ou 7–15 se as regras.md exigirem
— VERIFIQUE isso nas regras antes). Definir, para cada pista: categoria de
câmbio (A–J), categoria de suspensão (A–J), tempo de box (segundos) e as 6
influências (M/C/S/P/G/E). As pistas são:
- Circuit of the Americas
- Autódromo Hermanos Rodríguez
- Moscow Raceway
- Norisring
- Motorsport Arena Oschersleben
- Sochi Autodrom
- Yas Marina Circuit

**IMPORTANTE:** NÃO grave nada ainda. Primeiro me **apresente uma proposta de
tabela** com os valores sugeridos e a justificativa curta de cada um (ex.:
"Monza-like: reta longa → motor alto, freio/curva baixo"). Só depois que eu
aprovar, você cria um script `popular_pistas_modernas.py` (nos mesmos moldes do
`popular_categorias_pistas.py`/`seed_influencias_pistas.py` já existentes) para
gravar no banco `pistas_reais.db`.

### TAREFA C — Config de balanceamento editável no admin (verificar se já existe)
Quero que os parâmetros de balanceamento (economia/desenvolvimento/treino/pit)
sejam **editáveis pelo admin**, não ficarem "chumbados" no código. **ATENÇÃO:**
já existe uma tela `admin_configuracoes` e um model `Configuracao` — então parte
disso PODE já estar pronto. Antes de codar: **leia o que já existe e me diga o
que já está editável e o que ainda está hardcoded.** Se faltar algo, proponha o
plano antes de implementar.

---

## 5. O QUE EU NÃO QUERO MEXER AGORA

- ❌ **Bug do banco (chassi / NOT NULL)**: existe um `corrigir_banco.py` pronto
  pra remover a trava `NOT NULL` da coluna `chassi_fornecedor_id`. **Decidi NÃO
  rodar isso agora.** Não me proponha mexer no schema do banco nesta rodada.

---

## 6. O QUE EU QUERO QUE VOCÊ ME ENTREGUE (nesta ordem)

1. **Confirmação de entendimento**: um resumo curto (5–8 linhas) do que você
   entendeu que precisa ser feito, provando que leu o contexto.
2. **Verificação de regras**: releia o `regras.md`. Liste (em bullets) as regras
   que impactam as tarefas A, B e C — principalmente sobre pneu, influências das
   pistas (range 5–15 vs 7–15) e balanceamento. Se encontrar qualquer
   contradição entre o código atual e o `regras.md`, aponte.
3. **Tarefa A**: o `minha_equipe.html` completo, já corrigido.
4. **Tarefa B**: a proposta de tabela das 7 pistas (SEM gravar ainda).
5. **Tarefa C**: o diagnóstico do que já é editável vs hardcoded + plano.
6. **Resumo final no padrão do nosso `.md`** (ver seção 7 abaixo): atualize o
   `CONTINUAR_AQUI.md` marcando o que foi feito nesta sessão e o que ficou
   pendente, no mesmo formato/emojis que já usamos.

---

## 7. PADRÃO DO RESUMO .md (CONTINUAR_AQUI.md)

Use exatamente este estilo (títulos com emoji, seções claras, checklist):

```
# Open Wheel Strategy — PONTO DE RETOMADA
> Última sessão: DD/MM/AAAA

## ✅ FEITO NESTA SESSÃO (testado)
- item ...

## 🟡 PENDÊNCIAS
- item ...

## 📋 DECISÕES DE REGRA TOMADAS
1. ...

## ⚙️ REGRAS DE TRABALHO COM A IA
- arquivos completos, KISS/DRY, não inventar, etc.

## 🎯 PRÓXIMOS PASSOS
- [ ] ...
```

---

## 8. FLUXO DE TESTE (combinamos assim)

Você me entrega os arquivos completos → **eu testo na minha máquina** → eu te
digo o que funcionou e te devolvo os arquivos que modifiquei pra você conferir.
Então: entregue arquivos completos, um por vez quando fizer sentido, e sempre me
diga como testar (o que rodar, o que clicar) e o que esperar de resultado.

---

## 9. LEMBRETE DE GIT (fim de cada sessão)
```
git pull
git add .
git commit -m "descricao - feito no Windows"   (ou "- feito no Linux")
git push
```
Repositório: https://github.com/henriquebdv-lab/openw
Obs.: o `.env` está no `.gitignore` (credenciais NÃO sobem — é o certo).
```
```
