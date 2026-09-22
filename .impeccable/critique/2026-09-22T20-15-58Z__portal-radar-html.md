---
target: painel online
total_score: 21
max_score: 40
na_heuristics: 
p0_count: 1
p1_count: 3
timestamp: 2026-09-22T20-15-58Z
slug: portal-radar-html
---
Method: dual-agent (A: design review · B: detector + browser). Surface: painel online (portal/online.html, gerado de portal/radar.html por publicar.py --online).

## Heurísticas — 21/40 (Aceitável)
1 Visibilidade 2 — "salvo na nuvem" só no rodapé (14k px no celular); selo "2" sem rótulo; sem retorno após excluir/status.
2 Mundo real 3 — "corte" do cabeçalho é a semente, não corte de modulação; datas ISO e por extenso misturadas.
3 Controle 1 — "cancelar" do diálogo não fecha (type=submit + required); sem desfazer.
4 Consistência 2 — "remover" 1 toque vs "excluir" 2; status ciclo cego vs select.
5 Prevenção 2 — status muda com um toque; arme de 4 s.
6 Reconhecimento 2 — próximo status invisível; sem busca de tese.
7 Eficiência 1 — sem atalhos; busca só em Notícias; ~100 Tabs até a tese 20.
8 Estética 3 — 34 placeholders "Anote aqui…" e texto de sistema.
9 Recuperação 2 — aviso "sem banco" fora da primeira tela.
10 Ajuda 3 — aberturas úteis, mas falsas na versão online.

## Especificidade
Componentes autorais (linha .pz, versalete, Jost 200). Estrutura genérica: toda seção no mesmo molde. Modulação sem campo; placar só cor, placarNota em tooltip.
Detector (analisador completo, cópia no scratchpad; caminho original DEGRADED): 280 undersized-ui-text 10–10.5px, 53 tiny-text 11px, side-tab em .pz (redundante com numeral colorido), skipped-heading h1→h3, line-length ~87 em p.resumo. low-contrast #0a0a0a/#111a25 = falso positivo (@media print).

## Prioridades
[P0] "O que vence primeiro" não é a primeira leitura: abre em Notícias; prazos na aba Tributário; selo "2" sem rótulo e divergente de "3 frentes". Fix: faixa "vence primeiro" acima das abas em todas as abas (1–3 prazos compactos, toque leva à seção); selo rotulado e coerente. → layout, clarify
[P1] Sem desfazer/retorno; cancelar quebrado; status cego; remover 1 toque. Edição vira repositório às 07h. Fix: formnovalidate/type=button no cancelar; "tese excluída · desfazer" 8 s; escolha de status nomeada; remover em 2 toques; foco no próximo cartão. → harden
[P1] Texto de disco falso no online: privado/prazos.js na abertura de prazos; "fica no navegador" em mapa e aulas; termômetro "arquivo aberto do disco". Fix: publicar.py --online troca textos; prazos: "Prazos públicos do acervo. Prazo de carteira não aparece aqui, por construção." → clarify
[P1] Consulta rápida de tese: busca só em Notícias; placar só cor; modulação sem campo; processo e "conferido em" colados. Fix: busca de teses (tema/processo/título, atalho /); placar em texto; linha de modulação em versalete; data por extenso. Campo estruturado de modulação = decisão do usuário (teses.json). → layout, typeset
[P2] --tinta3 3.66:1 em 145 textos 10–12px na aba Tributário; "Jurídico" 2.69:1 sobre a luz no desktop; 141 alvos <44px no celular (.ts-acoes 31×16, excluir a 20px de status). Fix: tinta3→tinta2 nessa camada; piso 11–12px; alvos 44px por padding. → adapt, polish

## Personas
Alex: sem atalhos; abas sem tablist/setas; foco 1px e quase invisível em contenteditable; cancelar preso.
Casey: primeira tela é notícia; abas no alto; alvos 16–20px colados; save invisível ao editar; nova tese no fim de 14k px.
Sam: 3.66:1 em texto pequeno; placar só cor; abas sem role=tab; labels sem for; selo sem nome acessível.
Luca 16h: seis passos até placar/modulação do Tema 118; "conferido em" em baixo contraste.

## Menores
Carimbo em UTC (usar Brasília, "atualizado há X h"); "janela aberta" colide com "janela contínua"; 4 contagens iguais no cabeçalho; termômetro explica o sistema diariamente; .nt-edai e .secao duplicados; "corte" quebra linha no celular.

## Perguntas
1. Por que o "vence primeiro" é seção e não o cabeçalho?
2. Excluir tese deveria sair da lista e morar em "editar" com desfazer?
3. Modulação como campo estruturado alimentando a lista de prazos?
