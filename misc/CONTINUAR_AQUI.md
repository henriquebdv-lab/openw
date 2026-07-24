# Open Wheel Strategy — PONTO DE RETOMADA (continuar amanhã)

> **Como usar amanhã:** cole ESTE arquivo + o `regras.md` + o `openwheel_tudo.txt`
> na primeira mensagem do chat novo. Diga: "Vamos continuar o Open Wheel Strategy
> de onde paramos, seguindo o CONTINUAR_AQUI.md."
>
> **Data desta sessão:** 23/07/2026

---

## 🔴 PRIMEIRA COISA A FAZER AMANHÃ (bug ativo bloqueando o jogo)

### BUG: IntegrityError ao criar equipe
- **Sintoma:** ao criar equipe nova, erro `NOT NULL constraint failed: carros_jogadores.chassi_fornecedor_id`
- **Causa:** o banco `jogo.db` foi criado antes da mudança "chassi não é mais fornecedor".
  A coluna `chassi_fornecedor_id` ainda tem trava `NOT NULL` no banco físico, mas o
  código novo manda `None` (porque chassi agora vem do engenheiro/Desenvolvimento).
- **SOLUÇÃO LIMPA (decidida, ainda NÃO aplicada):** rodar `corrigir_banco.py` UMA VEZ
  pra remover a trava NOT NULL do banco. Depois disso a função `minha_equipe` fica
  limpa (chassi = None, sem gambiarra).

### `corrigir_banco.py` (criar na raiz e rodar `python corrigir_banco.py`)

```python
import sqlite3, shutil

shutil.copy("jogo.db", "jogo_backup_chassi.db")
print("[OK] Backup: jogo_backup_chassi.db")

con = sqlite3.connect("jogo.db")
cur = con.cursor()

cur.executescript("""
PRAGMA foreign_keys=off;

ALTER TABLE carros_jogadores RENAME TO _carros_old;

CREATE TABLE carros_jogadores (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    orcamento FLOAT,
    motor_fornecedor_id INTEGER NOT NULL,
    combustivel_fornecedor_id INTEGER NOT NULL,
    pneu_fornecedor_id INTEGER NOT NULL,
    chassi_fornecedor_id INTEGER,
    cambio_fornecedor_id INTEGER NOT NULL,
    suspensao_fornecedor_id INTEGER NOT NULL,
    engenheiro_fornecedor_id INTEGER,
    combustivel_carregado FLOAT,
    cor_primaria VARCHAR(7),
    cor_secundaria VARCHAR(7),
    modelo_motor INTEGER,
    modelo_combustivel INTEGER,
    modelo_pneu INTEGER,
    modelo_cambio INTEGER,
    modelo_suspensao INTEGER
);

INSERT INTO carros_jogadores SELECT * FROM _carros_old;
DROP TABLE _carros_old;

PRAGMA foreign_keys=on;
""")

con.commit()
con.close()
print("[OK] Trava NOT NULL do chassi removida.")
```

- Depois de rodar: a função `minha_equipe` deve usar `chassi_fornecedor_id=None`
  (versão limpa, SEM a gambiarra de "pegar primeiro chassi legado").
- ⚠️ Reiniciar o Flask depois de rodar.

---

## 🟢 O QUE JÁ FOI FEITO E ESTÁ FUNCIONANDO (nesta sessão)

### 1. Categorias ideais das pistas — CORRIGIDO ✅
- **Bug antigo:** todas as pistas apareciam "câmbio A / susp. B" (nunca populado).
- **Solução aplicada:** rodou `popular_categorias_pistas.py --apply` com os dados
  canônicos da Planilha Ayres (Opção A, range REAL 5-15, sem clamp).
- **Resultado:** 18 pistas casadas com dado canônico + 7 modernas sem dado.
- Red Bull Ring confirmado: M9 C8 S7 P11 G12 E14 ✅
- Arquivos criados: `dados_pistas_ayres.py`, `popular_categorias_pistas.py`.

### 2. Engenheiro nível 1 automático — FEITO (mas ver bug acima) ✅
- `equipes.html`: removido o dropdown de engenheiro (não é mais escolhido).
- `minha_equipe` (app.py): atribui engenheiro nível 1 automático + cria
  Desenvolvimento nível 1 (chassi/aero 100% grátis).
- ⚠️ Mas a criação de equipe ainda quebra pelo bug do chassi (resolver com
  `corrigir_banco.py` acima).

### 3. Pneu neutro (sem categoria de chuva) — FEITO ✅
- **Decisão (Opção A):** fornecedor de pneu é NEUTRO. A condição
  (seco/molhada/encharcada) vem do MODELO 50-900 escolhido por corrida.
- Rodou `neutralizar_pneus.py` → todos os pneus do banco viraram "seco".
- `equipes.html`: dropdown do pneu agora mostra só "Nome — R$ valor"
  (removido o "— seco" e o "/ temp.", e escondido o "#N" via `.split(' #')[0]`).

### 4. Reset de equipe — FUNCIONOU ✅
- Rodou `resetar_equipe.py` (com backup) pra limpar a equipe "roda" antiga.

---

## 🟡 PENDENTE DE APLICAR (arquivos prontos, faltou colar/testar)

### A. `seed_fornecedores.py` — função `gerar_pneus` (NÃO aplicado ainda)
- Motivo: fazer pneus NOVOS nascerem neutros ("seco") no futuro.
- Só importa quando clicar em "gerar fornecedores" no admin de novo.
- Como já rodou o `neutralizar_pneus.py`, os pneus ATUAIS já estão neutros.
- **Amanhã:** pedir o `seed_fornecedores.py` COMPLETO com a correção (o
  `gerar_pneus` deve gravar `categoria_chuva="seco"` fixo, sem embaralhar).

### B. `equipes.html` — versão final
- Já foi colada a versão que esconde `#N`, remove "seco" e "/ temp.".
- Confirmar amanhã que o dropdown ficou "GripTraction — R$ 4.300".

---

## 🏗️ GRANDE DECISÃO TOMADA: DESMEMBRAR O app.py (fazer amanhã)

### Por quê
- `app.py` tem 1000+ linhas com ~30 rotas. Editar função por função é frágil,
  não é KISS, e obriga a "caçar linha" (que o Henrique odeia).
- Solução: quebrar em **Blueprints do Flask** — cada área vira um arquivo
  pequeno (~100-150 linhas). Aí toda mudança = 1 arquivo pequeno COMPLETO.

### Estrutura alvo
```
openwheel/
├── app.py                 ← ~40 linhas: cria app, registra blueprints
├── extensoes.py           ← db, oauth, migrate (evita import circular)
├── rotas/
│   ├── __init__.py
│   ├── auth.py            ← login, registro, google, logout
│   ├── equipe.py          ← minha_equipe, editar_equipe, resetar_equipe
│   ├── desenvolvimento.py ← desenvolvimento_view, treinamento_view
│   ├── treino.py          ← treino_livre, treino_oficial, ranking
│   ├── corrida.py         ← estrategia_corrida, corrida, classificacao
│   ├── temporada.py       ← temporada, pistas_reais
│   └── admin.py           ← todas as rotas /admin
└── (resto igual: models.py, carro.py, corrida.py, etc.)
```

### Ordem de execução amanhã
1. **PRIMEIRO:** rodar `corrigir_banco.py` (desbloqueia o jogo).
2. Confirmar que criar equipe funciona.
3. **DEPOIS:** desmembrar o app.py com calma, arquivo por arquivo,
   cada um COMPLETO (não em pedaços).
4. Testar que nada quebrou após cada blueprint.

### ⚠️ Regra de trabalho reforçada nesta sessão
- **SEMPRE mandar arquivos COMPLETOS**, nunca pedaços/funções soltas.
- O Henrique tem TDAH, não curte caçar linha, e prefere KISS/DRY.
- Quando mexer no app.py atual (antes de desmembrar), avisar que é temporário.

---

## 📋 DECISÕES DE REGRA TOMADAS NESTA SESSÃO (já refletidas ou a refletir no regras.md)

1. ✅ **Categorias das pistas = Opção A** (dados canônicos Ayres, range 5-15 real).
2. ✅ **Pneu é NEUTRO** — condição vem do modelo 50-900, não do fornecedor.
3. ✅ **Engenheiro nível 1 automático** na conta nova (grátis, não escolhido).
4. ✅ **Desconto de renovação de contrato** (canônico, confirmado no manual):
   proposta = 15% base + 5%/temporada de fidelidade, teto 30%, vale pra todos
   + engenheiro. (Números a confirmar/gravar no regras.md.)
5. ✅ **Config de balanceamento editável no admin** (ideia aprovada, fazer depois):
   parâmetros de economia/corrida/pit numa tabela Configuracao, não hardcoded.
6. ✅ **Desmembrar app.py em blueprints** (decisão de arquitetura, fazer amanhã).

### 7 pistas modernas SEM dado canônico (decidir os valores)
Proposta feita (à mão, não canônica, mantendo 10=neutro e range 5-15):
- Circuit of the Americas: Câm D / Sus F / Box 13 / M11 C11 S10 P9 G8 E12
- Autódromo Hermanos Rodríguez: Câm C / Sus E / Box 12 / M8 C10 S9 P12 G14 E10
- Moscow Raceway: Câm E / Sus E / Box 13 / M10 C10 S10 P10 G9 E12
- Norisring: Câm B / Sus C / Box 15 / M13 C7 S8 P14 G10 E9
- Motorsport Arena Oschersleben: Câm G / Sus H / Box 12 / M8 C13 S12 P8 G9 E11
- Sochi Autodrom: Câm D / Sus I / Box 11 / M11 C12 S13 P8 G7 E10
- Yas Marina Circuit: Câm E / Sus F / Box 12 / M12 C11 S9 P10 G8 E11
- **STATUS:** proposta não aprovada ainda. Decidir amanhã e criar script pra popular.

---

## 📁 ARQUIVOS CRIADOS NESTA SESSÃO (guardar no projeto)

| Arquivo | Função | Status |
|---|---|---|
| `regras.md` | Regras canônicas do jogo | ✅ no GitHub |
| `dados_pistas_ayres.py` | Dados canônicos das 48 pistas Ayres | ✅ criado |
| `popular_categorias_pistas.py` | Popula categorias/influências das pistas | ✅ rodado --apply |
| `neutralizar_pneus.py` | Zera categoria_chuva dos pneus pra "seco" | ✅ rodado |
| `resetar_equipe.py` | Apaga equipe do usuário (com backup) | ✅ rodado |
| `corrigir_banco.py` | Remove trava NOT NULL do chassi | ⏳ FAZER AMANHÃ 1º |

---

## 🎯 CHECKLIST DE AMANHÃ (ordem exata)

- [ ] 1. Rodar `corrigir_banco.py` (desbloqueia criação de equipe)
- [ ] 2. Deixar `minha_equipe` com `chassi_fornecedor_id=None` (versão limpa, sem gambiarra)
- [ ] 3. Reiniciar Flask e criar equipe de teste → confirmar que funciona
- [ ] 4. Conferir saldo (engenheiro nível 1 deve ser GRÁTIS — não descontar do orçamento)
- [ ] 5. Confirmar dropdown do pneu ("Nome — R$ valor", sem #N, sem seco)
- [ ] 6. Começar o desmembramento do app.py em blueprints (arquivos completos)
- [ ] 7. (Quando der) aplicar `seed_fornecedores.py` completo com gerar_pneus neutro
- [ ] 8. (Quando der) decidir valores das 7 pistas modernas

---

## 💾 LEMBRETE DE GIT (fim de cada sessão)

```bash
git add .
git commit -m "descricao do que fez"
git push
```

E no começo (em casa ou trabalho):
```bash
git pull
```

- Email do git já configurado: `256236843+henriquebdv-lab@users.noreply.github.com`
- Repositório: https://github.com/henriquebdv-lab/openw
