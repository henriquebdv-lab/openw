# Open Wheel Strategy — PONTO DE RETOMADA
> **Como usar num chat novo:** cole ESTE arquivo + o `regras.md` +
> o `openwheel_py.txt` (e o `openwheel_html.txt` se precisar de telas)
> na primeira mensagem. Diga: "Vamos continuar o Open Wheel Strategy
> de onde paramos, seguindo o CONTINUAR_AQUI.md."
>
> **Última sessão:** 25/07/2026

---

## ✅ FEITO NA SESSÃO DE 25/07/2026 (tudo testado e funcionando)

### 1. PNEU NO FORMATO "MARCA — VALOR" — CONCLUÍDO ✅
- `gerar_pneus` (`seed_fornecedores.py`) agora grava `categoria_chuva="seco"` fixo. 
- A condição de pista (seco/molhada/encharcada) passou a vir puramente do modelo 50-900 escolhido por corrida.
- No jogo, o pneu exibe apenas "Pneu — marca — R$ valor".

### 2. CORREÇÕES DE PISTA E BALANCEAMENTO — CONCLUÍDO ✅
- Criado e executado o script `popular_pistas_modernas.py` para injetar os dados canônicos das 7 pistas modernas.
- Painel de Administração (`admin_configuracoes`) atualizado para permitir a edição direta de:
  - **Prêmio por Vitória (1º Lugar)**
  - **Multiplicador de Consumo**
  - **Chance de Quebra Base e Mínima**

---

## 🔴 PRÓXIMO EPIC: REDESENHO DO FLUXO DE CORRIDA (Planejado)

> Design estrutural definido. Mudança dividida em etapas incrementais.

### O fluxo correto (resumo)
1. **Prep do JOGADOR:** Minha Equipe -> Treino Livre -> Treino Oficial -> Classificação (escolhas independentes de combustível e tipo de pneu por fase). Na Classificação, o jogador **salva a estratégia**.
2. **TRAVA:** O piloto só corre se tiver a estratégia salva.
3. **AUTOMÁTICO por horário:** O sistema executará o Qualy e a Corrida sozinho de acordo com o calendário do Admin.

### Etapas planejadas:
- [ ] **Etapa 1:** Ajustar telas de Classificação e Corrida para modo *somente leitura* no menu do jogador, removendo botões de disparo de lá e centralizando o disparo manual provisório exclusivamente no `/admin`.
- [ ] **Etapa 2:** Criar o modelo de Calendário/Agenda no Admin.
- [ ] **Etapa 3:** Sistema de grupos de 20 + fila de espera.
- [ ] **Etapa 4:** Agendador (qualy/corrida automáticos por horário).
- [ ] **Etapa 5:** Promoção/rebaixamento dinâmico (pirâmide) no fim da temporada.

---

## ⚙️ REGRAS DE TRABALHO COM LA IA
- Arquivos completos, KISS/DRY, sem inventar regras e sem alterar o padrão `registrar(app)`.