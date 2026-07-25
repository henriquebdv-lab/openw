# Status do Projeto: Open Wheel Strategy
**Data da Revisão:** Julho de 2026

> Visão executiva do projeto. Para as regras completas, ver `regras.md`.
> Para o ponto de retomada detalhado, ver `CONTINUAR_AQUI.md`.

---

## 🟢 Concluído e Decidido

- **Arquitetura de Fornecedores:** 10 tiers, 100 por categoria, ordenados por
  preço, com performance oculta ("furadas" e "achados" implementados).
- **Engenharia Base:** Engenheiro tornou-se obrigatório (nível 1 inicial grátis).
  Chassi e Aerodinâmica atrelados ao nível do engenheiro — não são contratos de
  mercado.
- **Mecânica Base de Pistas:** 48 pistas originais mapeadas via Planilha Ayres.
  Suporte a trechos de temperatura dinâmicos e sistema de pistas "espelhadas".
- **Range de Influências das Pistas:** DECIDIDO pela Opção A — usar os valores
  reais da Ayres (5–15), sem clamp. (Encerra o antigo conflito 5-15 vs 7-15.)
- **Pneus:** fornecedor é neutro; a condição (seco/molhada/encharcada) vem do
  modelo 50–900 por corrida. `gerar_pneus` grava `categoria_chuva="seco"` fixo.
  No jogo aparece só "Pneu — marca — R$ valor".
- **Simplificações do MVP:** "Freio", "Estrategista" e mercado financeiro
  (bolsa de valores) foram removidos ou movidos para DLC.
- **Penalidades:** Pane seca (combustível zerado) gera abandono imediato, sem
  pit-stop salvador.
- **Arquitetura de Código:** `app.py` desmembrado em `rotas/` (padrão
  `registrar(app)`, não Blueprint) — telas todas funcionando.

---

## 🔴 Épico Estrutural (a maior peça que falta): Redesenho do Fluxo de Corrida

Mudança de arquitetura, a ser feita em ETAPAS incrementais:
1. **Telas somente-leitura:** Classificação (grid) e Corrida (resultado) ficam
   visíveis para todos apenas para acompanhar; o disparo manual fica só no
   `/admin` (provisório).
2. **Calendário/Agenda no Admin:** admin define dias/horários (ex: Seg/Qua/Sex,
   19h qualy, 20h corrida).
3. **Grupos de 20 + fila de espera:** grupo novo abre só ao encher 20.
4. **Agendador automático:** sistema roda qualy e corrida no horário, sozinho.
5. **Pirâmide (promoção/rebaixamento):** ao fim da temporada; quem sobe = quem
   desce (quantidade dinâmica conforme nº de inscritos).
- Regra-chave: o piloto **só corre se tiver a estratégia salva**.

---

## 🟡 Em Refinamento / A Implementar (Foco Atual)

1. **Minigame de Treino Livre:** experiência interativa (volta a volta),
   coletando feedback do piloto e ajustando setups antes de "salvar" o carro
   para o Treino Oficial.
2. **Interface de Estratégia:** combos progressivos de pit stops (pneu +
   combustível a cada parada).
3. **Correções de UI/Lógica:**
   - Tornar a contratação do Engenheiro obrigatória na interface HTML (hoje
     ainda mostra como "opcional").
   - Remover a lógica de pit-stop automático por falta de combustível no script
     de corrida (deve virar abandono).
   - Limpar a linha "Categoria: seco" do card do pneu em `minha_equipe.html`.
4. **Balanceamento das Pistas Modernas:** definir manualmente os valores das
   pistas sem dado na Ayres — Circuit of the Americas, Autódromo Hermanos
   Rodríguez, Moscow Raceway, Motorsport Arena Oschersleben e Norisring.
   (Um script `popular_pistas_modernas.py` foi iniciado — CONFERIR se os valores
   ficaram coerentes: 10 = neutro, range 5–15.)
5. **Premiação de quem abandona:** decidir a regra (hoje 0 pontos / 0 prêmio).

---

## ❓ Decisões de Design ainda em Aberto (do regras.md, seção 14)

- Quantos sliders no Treino Livre (3, 4 ou 5?).
- Como salvar o ajuste do Treino Livre (por pista? global? por corrida?).
- Aerofólios são ajustes 1–99 ou peças nível 1–10?
- Peso do combustível afeta o tempo por volta ou só a autonomia?
- Chuva entra no MVP?
- Horário programado do Treino Oficial (conecta com o épico do agendador).
