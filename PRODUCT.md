# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Um usuário só: Luca Martins, advogado tributarista (consultivo e contencioso) na Zveiter,
Rio de Janeiro, em pós-graduação em direito tributário desde setembro de 2026. Leitor
experiente — não precisa de explicação de conceito, precisa de estado atual verificado e de
consequência prática. Ninguém mais abre o painel: não há equipe, não há cliente, não há
visitante.

Usa o **celular ao longo do dia inteiro**, em janelas curtas, e o **computador durante
quase toda a tarde**, em sessão longa de trabalho — consulta de tese e prazo no meio de
parecer ou peça, caderno da pós, escolha de pauta.

## Product Purpose

Radar Jurídico: a superfície diária de um sistema de acompanhamento com três camadas —
**radar** (o que mudou, notícia jurídica em sete áreas), **base** (o acervo de teses
tributárias que acumula) e **aplicação** (carrossel de Instagram, boletim, estudo).

A primeira coisa que o painel entrega ao abrir, em até 10 segundos, é **o que vence
primeiro**: prazo com data certa e janela que se fecha por prescrição ou por modulação.
Notícia vem depois. Sucesso é abrir o painel e saber, antes de qualquer rolagem, se há algo
fechando esta semana.

## Positioning

Não é clipping. Todo item carrega o "e daí?" — cabe ação preventiva, abre repetição de
indébito, muda exposição, afeta contencioso em curso — e o que não foi confirmado em fonte
primária aparece marcado como tal, nunca como fato. Modulação de efeitos (presença,
ausência, data de corte) é tratada como informação de primeira ordem. O acervo é
versionado em repositório e se atualiza sozinho uma vez por dia.

## Operating Context

- **Duas superfícies do mesmo painel.** O painel online (Artifact privado no claude.ai,
  gerado por `scripts/publicar.py --online`) é a de uso: abre de qualquer lugar e grava
  edição no banco do Artifact. `portal/radar.html`, no disco, é o único lugar onde aparece
  prazo de carteira (`privado/prazos.js`).
- **Rotina diária às 07h de Brasília** traz as edições do painel ao repositório, roda o
  radar, regera e republica. O painel reflete a última rotina, não o minuto presente.
- **Fonte do conteúdo:** `base/teses.json` (acervo), `base/radar.json` (notícia e
  termômetro), `base/posfgv/aulas.json` (caderno). O bloco de dados do painel é gerado;
  mudança de layout entra em `portal/radar.html` e em `scripts/publicar.py`, nunca no
  `online.html`, que é regerado.
- **Três abas:** Notícias (sete áreas: tributário, empresarial, societário, imobiliário,
  civil, IA e tecnologia, atualidade), Tributário (o que vence primeiro, mapa de teses,
  termômetro do X, boletins) e pósFGV (caderno de aulas, backlog de estudo, fontes).
- **Momento de transição:** reforma do consumo (EC 132/2023, LC 214/2025) — 2026 é ano-teste
  de IBS/CBS, 2027 traz a CBS cheia. Dois sistemas tributários convivem no acervo.

## Capabilities and Constraints

- Editável no painel online: tese nova, edição de tese, status, "e daí?", boletim, aula,
  backlog, exclusão. Salva no banco do Artifact; entra no repositório na rotina diária.
- O visor do Artifact não mostra `alert`/`confirm`/`prompt` nem entrega download: exclusão
  é por dois toques, e não há exportar/importar no painel online.
- Página única, HTML/CSS/JS sem framework, fontes embutidas em woff2, sem rede. Tudo o que
  o painel mostra vem embutido na publicação ou do banco do Artifact.
- **Sigilo profissional:** dado de cliente, número de processo de carteira e prazo de
  intimação nunca entram no painel online nem no repositório — só em `privado/`, no disco.
- Termômetro do X não é ao vivo: medido pela rotina, datado, vira histórico após 7 dias;
  sem reação pública verificável, a seção fica vazia.
- Contagem de prazo tem três famílias que não se misturam: dias úteis judiciais (CPC arts.
  219/224), dias corridos civis/decadenciais, dias do processo administrativo fiscal
  (Decreto 70.235/72).

## Brand Commitments

- Nome: **Radar Jurídico**, assinado "Luca Martins · Advogado" (singular).
- Sistema visual travado: **Obsidian Chrome** (`design/obsidian-chrome/`, travado em
  10/09/2026), compartilhado com o carrossel de Instagram. As regras e os invariantes estão
  no `CLAUDE.md` do repositório e no de `design/obsidian-chrome/`.
- Voz: técnica, direta, sem preâmbulo; sem "importante ressaltar", "vale destacar",
  "cumpre observar".
- Compliance OAB (Provimento 205/2021) vale para tudo o que é publicável; o painel é
  interno, mas o que sai dele para o carrossel passa pelo gate.

## Evidence on Hand

- Acervo real: 28 teses em `base/teses.json` (quase todas marcadas "a confirmar"), 24
  notícias em sete áreas em `base/radar.json`, um boletim registrado.
- Uma peça publicada: carrossel do IPTU, Tema 1.455 (`pecas/2026-08-05-iptu-tema-1455/`).
- Não existe depoimento, métrica de uso, cliente ou benchmark. Não inventar.

## Product Principles

1. **O que vence primeiro vem antes de tudo.** Prazo e janela se fechando são a primeira
   leitura; notícia é a segunda.
2. **Estado verificado ou estado declarado.** Nada aparece como fato sem fonte e data;
   o "a confirmar" é visível, nunca escondido.
3. **Consequência, não manchete.** Item sem "e daí?" no eixo tributário não entra.
4. **Dois ritmos, um painel.** Triagem de segundos no celular, consulta longa no
   computador — o mesmo conteúdo precisa servir aos dois sem virar duas coisas.
5. **Sigilo por construção.** A camada de carteira não existe no painel online, e a
   interface não convida a digitá-la ali.
