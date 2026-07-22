# Open Wheel Strategy — Contexto do Projeto (dia 2 de dev)

> **Se você está começando um chat novo com uma IA, cole este arquivo inteiro
> na primeira mensagem. Ele contém tudo que a IA precisa saber pra continuar
> de onde paramos.**

---

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

---

## Sobre o projeto

- **Nome:** Open Wheel Strategy
- **Tipo:** Jogo de gerenciamento de equipes de monopostos, jogado no navegador
- **Stack:** Python + Flask + SQLAlchemy + SQLite + Flask-Migrate
- **Local:** `E:\openwheel\`
- **Desenvolvedor:** Henrique (Curitiba, PR)
- **Referências locais:** manual (como.txt) + planilhas de referência técnica

---

## Regra de ouro do banco

**NUNCA APAGAR o `jogo.db` SEM AUTORIZAÇÃO.** Migrações via Flask-Migrate.

---

## Preferências do desenvolvedor

- Prefere arquivos completos, não trechos pra editar manualmente
- Plain text, sem HTML no meio, sem negrito excessivo
- Objetivo e direto
- Passo-a-passo pra troubleshooting
- Português brasileiro
- Aceita quando IA admite erro, se frustra com repetição de erros

---

## O que foi feito HOJE (dia 22/07)

### Fase visual (frontend)

1. **Novo `base.html` + `tema.css`** com identidade dark, sidebar lateral,
   topbar "CENTRO DE COMANDO"
2. **`home.html`** com hero + cards de status + atalhos rápidos
3. **`login.html` + `registrar.html`** no visual do tema, card escuro centralizado
4. **`minha_equipe.html`** com hero da equipe + 7 cards de equipamentos +
   aviso de desempenho oculto
5. **`equipes.html`** (criar equipe) com hero, cards agrupados,
   contratos obrigatórios separados de engenheiro opcional

### Correções de regra

6. **Sistema de pontuação corrigido**: 40/35/32/29/26/24/22/20/18/16/14/12/10/8/6/5/4/3/2/1
7. **Premiação em R$ por corrida** (individual): 12k → 5.5k
8. **Curva suave de desgaste do pneu**: começa a perder tempo a partir de 70%,
   estoura em 100%
9. **Chance de quebra de peças**: 10% base, reduz até 2% com treinamento de box
10. **Chassi + Aerodinâmica projetados pelo Engenheiro** (NÃO é fornecedor):
    - `FornecedorChassi` removido do formulário
    - Jogador novo recebe chassi + aero de nível 1 grátis
    - Desenvolvimento agora tem 2 barras separadas (chassi e aero)
    - Só passa a valer na PRÓXIMA temporada
    - Requisitos para próxima temporada: engenheiro + chassi 100% + aero 100%
11. **`.env` + `python-dotenv`** para Google OAuth funcionar sem expor credenciais

### Descobertas importantes sobre regras (via planilha e FAQ)

12. **Influências por pista NÃO são 1-30**. São **7 a 15** no jogo original:
    - Ex: A1-Ring: M9 C8 S7 P11 G12 E14 F5
    - Ex: Adelaide: M7 C8 S14 P11 G09 E11 F...
13. **Influência baixa = componente pouco importa nessa pista**
    (motor infl 1 = jogador com motor #3 e motor #10 fazem tempos parecidos)
14. **7 componentes com influência** (M, C, S, P, G, E, **F**) — Freio ainda não
    implementado como fornecedor separado
15. **Fornecedores originais eram 10 níveis × 10 modelos** (xx-50 a xx-900):
    - Contrato anual = nível de fornecedor
    - Compra por corrida = modelo dentro do nível
    - Modelo xx-50 = mais rápido, dura menos
    - Modelo xx-900 = mais lento, dura mais
    - Isso NÃO foi implementado ainda
16. **Frases de feedback do piloto** existem no original (>100 frases,
    marcadores em negrito indicam "passou do ideal, volte")
    - Vamos criar frases próprias (não copiar)
17. **Treino livre real**: jogador escolhe pneu + gasolina + sliders,
    sistema calcula quantas voltas dá, roda todas com feedback
    - Não é "clica no botão e vê o tempo" como está hoje

---

## O que já estava funcionando (dias anteriores)

### Autenticação
- Login/registro email/senha ou Google OAuth
- Sistema de admin

### Jogador
- Criar/editar equipe (agora sem chassi)
- Treino livre (5 sliders) — versão simplificada, precisa refazer
- Treino oficial
- Estratégia da corrida (rudimentar)
- Desenvolvimento (agora 2 barras: chassi + aero)
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
- Formato `1:30.234`
- **Curva suave de desgaste** (NOVO)
- **Chance de quebra** (NOVO)

### Temporada
- Admin cria com calendário
- 1 ativa por vez
- Ranking com pontos e prêmios (CORRIGIDO)
- Custo_montagem debitado por corrida
- Custo_temporada debitado ao contratar
- **Fim de temporada aplica chassi/aero desenvolvido** (NOVO)

### Fornecedores
- 100 por categoria (motor, combustível, pneu, câmbio, suspensão, engenheiro)
- FornecedorChassi mantido no banco por legado (não usado)
- 10 tiers × 10 fornecedores por tier
- Nomes gerados aleatoriamente (não canônicos)

### Admin
- Sidebar fixa
- CRUD fornecedores, pistas, temporadas, configurações
- Gerencia usuários (grupo, classe, admin)
- Desativar temporada aplica desenvolvimento

---

## Sistemas numéricos definidos

### Pontuação (CORRIGIDO hoje)
Individual: 40/35/32/29/26/24/22/20/18/16/14/12/10/8/6/5/4/3/2/1

### Prêmio em R$ (individual, IMPLEMENTADO)
1º R$12.000 → 20º R$5.500

### Chassi/Aero (IMPLEMENTADO)
- Nível 1: chassi -0.2s / aero -0.1s
- Nível 10: chassi -2.0s / aero -1.0s
- Escala linear

### Orçamento inicial
- R$ 55.000 configurável

### Quebra mecânica
- 10% base, 2% mínimo (com treino 100%)

---

## O que está para fazer na PRÓXIMA SESSÃO

### 🔴 Prioridade imediata (deixamos parado ontem)

1. **Corrigir formulário criar equipe:**
   - Já removi campo orçamento
   - Já ajustei texto sobre engenheiro
   - Mas ainda: reordenar fornecedores no select

2. **Reformar fornecedores:**
   - Renumerar #1 a #100 em ordem crescente de custo
   - Decidir: manter "furadas/achados" ou eliminar?
   - Nome consistente com posição na lista

3. **Ajustar range de influência das pistas:**
   - Hoje: 1-30 (errado)
   - Correto: 7-15
   - Mudar validação no formulário admin_pista_editar.html

4. **Popular as 25 pistas com valores canônicos:**
   - Pistas disponíveis (com SVG): Austin, BrandsHatch, Budapest, Catalunya,
     Hockenheim, IMS, Melbourne, MexicoCity, Montreal, Monza, MoscowRaceway,
     Norisring, Nuerburgring, Oschersleben, Sakhir, SaoPaulo, Sepang, Shanghai,
     Silverstone, Sochi, Spa, Spielberg, Suzuka, YasMarina, Zandvoort
   - Colocar valores certos onde eu tenho da planilha
   - Deixar neutro (10) onde não tenho, jogador ajusta depois

5. **DECISÃO PENDENTE**: Adiciona coluna F (Freio) na pista? Ou espera
   implementar FornecedorFreio primeiro? — Henrique não respondeu

### 🟡 Feature grande pendente: Treino Livre real

- Jogador escolhe pneu + gasolina no início
- Sistema calcula quantas voltas dá
- Sistema simula cada volta com feedback (frases genéricas nossas)
- Persiste no banco (`ResultadoTreinoLivre`)
- Tela pública tipo ranking do treino livre por grupo+classe

### 🟢 Regras confirmadas mas não implementadas

- **FornecedorFreio** como componente separado (com categoria + influência F na pista)
- **Xx-50 a xx-900** (10 modelos dentro de cada nível de fornecedor)
- **Frases de feedback do piloto** (criar do zero, ~50 frases)
- **Aderência de pneu por temperatura** (10 categorias, matriz)
- **Sistema de duplas** (fase inteira)
- **Prêmio final de campeonato** (bonus no ranking final da temporada)

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

## Como voltar aqui amanhã

1. Cola este arquivo na primeira mensagem
2. "Este é o contexto do Open Wheel Strategy. Vamos continuar de onde
   paramos. Prioridade: item X."
3. Cola arquivos que a IA pedir (models.py, app.py, etc)

---

## Arquivos entregues HOJE

Todos estão nos ZIPs baixados. Se você perdeu, cola os que ainda tem
e pede pra IA regerar.

**Últimos ZIPs entregues:**
- `openwheel_layout_v4_1.zip` (base.html, tema.css, login, registrar, home)
- `openwheel_chassi_aero.zip` (constantes, models, carro, equipamentos,
  progressao, app, equipes.html, desenvolvimento.html)
- Arquivos soltos: pontuacao.py, corrida.py (correções de regra)

---

## Estado emocional do projeto

Dia 6 do desenvolvimento. Projeto avançou muito:
- Backend sólido
- Frontend com identidade visual
- Regras corretas do manual quase todas
- Descobertas importantes sobre profundidade do jogo original

Riscos:
- Não terminar as regras antes de partir pra features novas
- Tela de treino livre real é grande, precisa fazer com foco
- Fornecedores no formato xx-50/xx-900 é o próximo grande refactor

Recomendação: fechar as 4 prioridades imediatas antes de mexer em features.
"Este é o contexto do Open Wheel Strategy. Vamos continuar. Prioridade: refatorar fornecedores pra ter 10 modelos internos (xx-50 a xx-900) e implementar consumo/durabilidade por modelo."