# Open Wheel Strategy — PONTO DE RETOMADA (documento ÚNICO e vivo)

> **Como usar num chat novo:** cole ESTE arquivo + o `regras.md` +
> o `openwheel_py.txt` (e `openwheel_html.txt` se precisar de telas).
> Este é o ÚNICO arquivo de retomada — edite este, não crie versões novas.
>
> **Última atualização:** 27/07/2026

---

## ✅ FEITO E FUNCIONANDO (testado)

### Base
- app.py desmembrado em `rotas/` (padrão registrar(app), NÃO Blueprint).
- Login Google (cada máquina tem seu `.env`).
- Quick wins: pneu "marca — valor", engenheiro obrigatório, pane seca = abandono.
- 7 pistas modernas + config de balanceamento no admin.
- models.py estabilizado (commit de referência 41b5cb7).

### Parc Fermé + Preparação
- Parc Fermé Etapa 1+2: tabela SetupFimDeSemana (motor+câmbio+suspensão 50-900 +
  campo travado). Tela "Montagem Fim de Semana" com aviso de confirmação + trava.
- Estratégia limpa (removidos configs de motor/câmbio/susp/injeção do topo).
- Treino Livre INTERATIVO: usa setup travado (read-only), só a pista do FDS,
  auto-redireciona se não montou. 3 sliders (Câmbio/Suspensão/Aerofólio, 1-99;
  5 na estrutura). Ideal secreto por pista (IdealPistaSlider). Feedback do piloto
  + % de acerto. Desgaste PESA no tempo. Exibe VIDA do pneu (100→0).
- Treino Oficial = "Salvar dados da Classificação" (tabela DadosClassificacao).
  Simulação genérica 82.0s removida.
- Estratégia persistida no banco (EstrategiaStint), não mais só na sessão.

### Corrida / Admin
- Admin "Dia de Corrida": painel de status (Parc Fermé/Quali/Stints) + disparo
  manual de classificação e corrida só pras equipes elegíveis.
- seed_teste.py: 2 admins (Razor, senha 123456) + fornecedores + TEMPORADA 1 (10
  corridas) + equipe dos admins + 40 BOTS prontos pra correr (grid cheio).
- Replay da Corrida FASE 1 (tabela de posições volta a volta) funcionando + link
  na sidebar.
- base.html UTF-8; combustível removido da tela de montar equipe; flash verde ok.

---

## 🔴 MOTOR — FECHAR ANTES DE ABRIR FEATURE NOVA
> Decisão do Henrique (27/07): não adianta feature nova (duplas/prêmios) com o
> motor incompleto. Fechar o núcleo primeiro.

- [ ] REPLAY FASE 3 (o que o Henrique QUER ver): carros se movendo no traçado da
      pista (sprites + SVG/mapa da pista + animação). Hoje só tem a TABELA de
      posições (Fase 1). É o "sonho" do replay — mais complexo.
- [ ] BUG: corrida avança sozinha (marcou corridas como executadas sem ter rodado
      com equipe; ficou na 3ª sem resultado). Não avançar/marcar executada sem
      equipe elegível que realmente correu.
- [ ] INCONSISTÊNCIA: a classificação inclui equipe "FORA" (filtro de
      elegibilidade diferente da corrida). Aplicar o MESMO filtro na quali.
- [ ] Replay guarda só a ÚLTIMA corrida (ultimo_replay.json sobrescreve). Pra ver
      replays antigos: salvar 1 por corrida (coluna JSON na CorridaAgendada, ou
      replay_etapa_N.json).
- [ ] CSS da tela admin poluído (sem estilo, ✅/❌ soltos) — arrumar visual.

### Fases da visualização do replay (do Henrique)
1. Fase 1: tabela de tempos volta a volta — ✅ FEITO
2. Fase 2: tempos + narração/comentários dos pilotos — pendente
3. Fase 3: carros (sprites IA) se movendo na pista — pendente (o "sonho")

---

## 🆕 FEATURES NOVAS (SÓ depois do motor fechar)
- [ ] Parc Fermé Etapa 3: Romper o Lacre (taxa R$ 1.000 + largar em último).
- [ ] Parc Fermé Etapa 4: Pular a Quali (liberado só se o lacre foi rompido).
- [ ] Parc Fermé Etapa 5: montar_carro puxar motor/câmbio/suspensão do
      SetupFimDeSemana + limpar setups no fim da temporada.
- [ ] Premiação de abandono: decidir (0 / valor mínimo / proporcional às voltas).
- [ ] Sistema de Duplas (parceria entre pilotos na fase de equipe).

---

## 🧪 TESTES AUTOMÁTICOS (quando voltar ao tema)
- Já existe pasta `tests/`. Expandir com pytest: login, montar_carro, custos,
  stints, SetupFimDeSemana, DadosClassificacao, validação de voltas, desgaste
  pesa no tempo, motor/pneu afetam tempo+consumo.
- Regra de ouro: rodar `pytest` ANTES de commitar mudança da IA.
- Lição: testes no sandbox já pegaram bug real (desgaste não pesava no tempo).

---

## 🔵 ÉPICO GRANDE (arquitetura — bem depois)
- [ ] Calendário/Agenda no admin (ex: Seg/Qua/Sex, 19h qualy, 20h corrida).
- [ ] Agendador automático (qualy/corrida rodam sozinhos no horário).
      Pra testar sem esperar: botão manual "rodar agora" no /admin (já existe).
- [ ] Grupos de 20 + fila de espera.
- [ ] Pirâmide: promoção/rebaixamento (quem sobe = quem desce, dinâmico).
- Obs: o ranking do treino livre (hoje vazio) depende dos GRUPOS.

---

## 🎨 DEPOIS (finalização)
- [ ] Refatoração de CSS: tirar style="" inline → tema.css. JUNTO: flash sumir
      sozinho após alguns segundos. Fazer por partes, testando visual.
- [ ] UX/UI command center (imagem do carro no box, painéis).
- [ ] Sprites de carro vista de cima (base recolorível) — usados na Fase 3 do replay.

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
- Trava MOTOR + CÂMBIO + SUSPENSÃO (peças/modelos) pro fim de semana.
- Pneu e combustível ficam livres (variam por stint na estratégia).
- 1ª coisa do FDS: montar o carro. Sem montar = sem carro. Precisa de $.
- Setup errado NÃO impede correr (anda, mas perde décimos).
- RÍGIDO: salvou, travou. Só corrige rompendo o lacre.
- Romper o lacre: taxa R$ 1.000 + larga em último.
- Se rompeu o lacre: libera pular a quali.
- Tabelas: SetupFimDeSemana, DadosClassificacao. Limpar no fim da temporada.

---

## 🎚️ MECÂNICA DO AJUSTE FINO (detalhe em MECANICA_AJUSTE_CARRO.md)
- Sliders 1-99. Cada pista tem valor ideal secreto por slider.
- Fórmula: ideal = BASE(aleatório fixo por pista) + INFLUENCIA + CONTRATO
  (Fase 2, peso 0 agora), clamp 1-99.
- Feedback por faixa de erro (frases NOSSAS) + % geral de acerto.
- 3 sliders visíveis, 5 na estrutura (+AeroD/T, Freio DLC).

---

## ⚙️ REGRAS DE TRABALHO COM A IA
- Arquivos COMPLETOS (nunca "procure a linha X"). KISS/DRY.
- models.py: SÓ adicionar coluna/tabela no final. NUNCA reescrever o arquivo.
- NÃO inventar regras/colunas/rotas. Perguntar antes.
- Manter padrão registrar(app) (não Blueprint). Não quebrar url_for.
- Salvar tudo em UTF-8 (projeto teve mojibake).
- Chief Engineer (Claude) valida models/arquivos no sandbox ANTES de aplicar.
- FECHAR o que está aberto antes de abrir frente nova (lição: abrir muita frente
  ao mesmo tempo gerou confusão e sensação de "não anda").
- Documentos vivos: este + regras.md + MECANICA_AJUSTE_CARRO.md. Editar incremental.

---

## 🖥️ AMBIENTE
- Windows (PC casa): RX 6800 16GB, Ryzen 7 2700X, 16GB.
- Linux (notebook): Mint, Dell E6440, i5 4ª gen, 8GB.
- Git: https://github.com/henriquebdv-lab/openw (.env e client_secret no .gitignore).
- ⚠️ SEGURANÇA: o client_secret do Google vazou no chat — considerar revogar/gerar
  novo no Google Cloud Console.

### Recriar banco (quando muda tabela/coluna)
```
copy jogo.db jogo_backup.db
del jogo.db
python criar_banco.py
python seed_teste.py
```

### Gerar TXT (Windows PowerShell)
```powershell
Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch '\\.venv\\' -and $_.FullName -notmatch '\\migrations\\' } | Sort-Object FullName | ForEach-Object { "===== $($_.FullName.Replace($PWD.Path + '\', '')) ====="; Get-Content $_.FullName; "" } | Out-File -Encoding utf8 openwheel_py.txt
Get-ChildItem -Path templates -Recurse -Filter *.html | Sort-Object FullName | ForEach-Object { "===== $($_.FullName.Replace($PWD.Path + '\', '')) ====="; Get-Content $_.FullName; "" } | Out-File -Encoding utf8 openwheel_html.txt
```

---

## 🎮 REFERÊNCIA
Jogo base: "estrategia" (F1). Piloto do Henrique: **Razor**. Bolsa de Valores
CORTADA da v1.

---

## 🎯 PRÓXIMO PASSO (decisão do Henrique: MOTOR primeiro)
1. Corrigir o BUG da corrida avançar sozinha (corrompe a temporada) OU
2. Fazer o REPLAY FASE 3 (carros na pista).
Só depois de fechar o motor: features novas (duplas/prêmios/parc fermé 3-4).
