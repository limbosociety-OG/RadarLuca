---
name: carrossel
description: Produz a peça publicável de Instagram sobre direito tributário no sistema visual travado de Luca Martins, o Obsidian Chrome — obsidiana #0A0A0A e campos de luz em cromo, selo circular, Jost / Poppins / Archivo / Cormorant Garamond, feed 1080×1350 e story 1080×1920. Use sempre que o pedido envolver carrossel, post, peça, slide, story ou conteúdo de Instagram sobre decisão do STF, STJ, CARF, PGFN, Receita, reforma tributária ou legislação nova — inclusive quando o pedido for só "faz um post sobre o Tema X", "transforma isso em carrossel" ou "leva pro feed". Inclui verificação processual obrigatória com prazo de validade, gate de compliance da OAB (Provimento 205/2021) sobre o roteiro E a legenda, e render determinístico com fontes vendorizadas. Esta é a skill de carrossel deste repositório. `producao-carrossel`, se existir no ambiente, é outra identidade visual (Moody Blue, Cormorant/Italiana/Instrument) que convive de propósito e não deve ser removida — apenas não é a deste projeto. `carrossel-tributario`, se existir, é cópia antiga desta skill, fora do Obsidian Chrome, e foi substituída por esta.
---

# Carrossel — Luca Martins

Uma peça só é publicável quando três coisas são verdadeiras ao mesmo tempo: os fatos
processuais estão confirmados em fonte primária e há pouco tempo, o texto não capta
clientela, e o visual é indistinguível das peças anteriores. Esta skill existe porque as
três falham de formas diferentes — a primeira por pressa, a segunda por reflexo de
copywriting, a terceira por reconstruir o design do zero a cada vez.

O pipeline é sequencial e não pula etapa:

```
1. VERIFICAR → 2. PAUTA → 3. ROTEIRO → 4. LEGENDA → 5. GATE → 6. RENDER → 7. DIFF
```

A legenda vem **antes** do gate, não depois: ela é publicada junto, circula sozinha em
print e repost, e é onde o chamado à ação costuma se infiltrar. O gate reprova a peça
inteira se ela faltar.

---

## 0. Antes de tudo, uma vez por máquina

```bash
python3 scripts/doctor.py       # a partir da raiz do repositório
```

Ele classifica o que está instalado no ambiente. Duas leituras diferentes:

- `producao-carrossel` → outra identidade visual, convive de propósito. **Não remover.** Só
  não é a deste projeto: aqui a peça sai no Obsidian Chrome (`design/obsidian-chrome/`).
- `carrossel-tributario` / `radar-juridico` → cópias antigas desta skill, fora do Obsidian
  Chrome e piores no processo. Use as do repositório.

Se houver dúvida sobre qual skill foi acionada, perguntar antes de renderizar. Peça
publicada no sistema errado não se corrige depois: ela já está no feed.

## 1. Verificar antes de escrever

Nada entra em roteiro sem estar confirmado. Ler `references/verificacao.md` e preencher a
ficha: número do processo, tema de repercussão geral ou repetitivo, órgão julgador, data
do julgamento, data de publicação do acórdão, trânsito, embargos pendentes, e — sempre —
se houve modulação de efeitos.

Cada campo recebe `estado` (`confirmado`, `nao_confirmado` ou `conflitante`), `fonte` e
`data` da consulta. O gate exige três coisas por campo:

- estado `confirmado`;
- fonte e data preenchidas;
- **data com no máximo 15 dias.** Andamento muda toda semana; ficha velha é ficha não
  verificada. Peça já publicada carrega `"publicado_em": "AAAA-MM-DD"` e aí a janela é
  medida contra essa data — renderizar de novo reproduz o que saiu.

O gate também confere **coerência de citação**: todo `ARE`, `RE`, `REsp`, `ADI`, `ADC` ou
`Tema` citado no roteiro ou na legenda tem de constar da ficha. Foi exatamente assim que
`1.593.384` circulou no lugar de `1.593.784` — um dígito, replicado por meses.

A regra parece rígida porque o custo é assimétrico: um número de processo errado num
carrossel publicado é um erro que circula com o nome do advogado colado nele.

## 2. Filtro de pauta

Testar o tema contra os seis critérios do projeto: relevância, presença no X agora,
recência, implicação jurídica, aplicação às áreas de atuação, urgência. Tema que não passa
não vira post — dizer isso ao usuário em vez de produzir peça fraca. A escassez de
postagem faz parte da marca.

Se passar, escolher o ângulo. O ângulo quase nunca é a manchete do noticiário; é o que o
noticiário deixou de fora. No carrossel do IPTU, o noticiário parou em "prefeitura não
pode cobrar mais caro por imóvel grande" e a peça inteira se organizou em torno de "e o
que eu já paguei?" — modulação, prescrição, janela.

## 3. Roteiro

Escrever `pecas/AAAA-MM-DD-slug/roteiro.json`. Esquema, tipos de bloco e arquitetura de
telas em `references/editorial.md` — ler antes do primeiro roteiro, reler ao usar um bloco
pela primeira vez.

O essencial, para não abrir o arquivo em pauta simples:

**Ritmo de fundo.** `escuro` é obsidiana e carrega voz editorial: capa (campo `corner`),
o achado que ninguém publicou (`slab`), fecho (`blob`). `claro` é o papel (`paper`) e
carrega exposição técnica: a tese na letra, a tradução, os limites, as checagens. Tudo papel
vira apostila; tudo obsidiana vira manifesto. Todo fundo é campo de luz do sistema — o
build recusa campo que não exista em `design/obsidian-chrome/tokens/fields.css`.

**Numeração.** A capa não é seção. A seção `01` fica na tela 2. A paginação do rodapé é
calculada pelo script — não escrever à mão.

**Manchete carrega consequência, nunca citação.** "Metro quadrado não mede capacidade de
pagar" é manchete. "ARE 1.593.784/SC" é mono no rodapé, em cinza.

**Responder "e daí?" até a tela 4.** Se o leitor chegou à quarta tela sem saber por que
aquilo mexe com o bolso dele, o roteiro está errado — não o design.

**Modulação é questão de primeira ordem.** Toda peça sobre precedente precisa de uma tela
dedicada a se houve modulação e ao que isso faz com o passado.

## 4. Legenda

`legenda.md`, ao lado do roteiro. Três a cinco parágrafos curtos, mesma voz do carrossel,
sem hashtag genérica de advogado, sem chamada para DM. Termina em fato, nunca em oferta.

Fecha com a ressalva de caráter informativo — o gate exige, porque a legenda é o que
sobrevive ao print recortado.

## 5. Gate

```bash
python3 .claude/skills/carrossel/scripts/compliance.py pecas/.../roteiro.json
```

Falha o build e **não tem bandeira de bypass**. Checa ficha de verificação (estado, fonte,
data, validade), coerência de citação, léxico de captação no roteiro e na legenda, e o
fecho do Provimento 205/2021 no último slide e na legenda.

Quando reprovar, reescrever. Não desativar, não editar a lista de termos para acomodar uma
frase: se uma frase bate na lista, quase sempre ela está mesmo dirigindo um chamado ao
leitor, e a reescrita melhora a peça.

O limite prático: o texto descreve **o que a decisão significa**, não **o que o leitor
deve fazer**. "Quem não pede, não recebe" descreve o art. 168 do CTN. "Procure um advogado
e recupere seu dinheiro" capta clientela. A distância é curta e é ali que mora o
Provimento 205.

A suíte que prova que o gate morde:

```bash
python3 .claude/skills/carrossel/scripts/testa_compliance.py
```

Mexeu no léxico ou na ficha? Roda. Um gate que ninguém testa degrada em silêncio.

## 6. Render

```bash
python3 .claude/skills/carrossel/scripts/build.py pecas/.../roteiro.json \
        --out pecas/.../saida --formato feed     # ou story, ou ambos
```

Roda o gate, confere as fontes vendorizadas e renderiza via Playwright:
`slide-NN.png` em 1080×1350, `story-NN.png` em 1080×1920. O story usa padding de 250px no
topo e 230px na base — é a faixa que a moldura do Instagram cobre, não é respiro estético.

**O build não baixa fonte.** Os seis arquivos do Obsidian Chrome (Jost, Poppins 500 e 600,
Archivo e itálica, Cormorant Garamond) estão versionados em `assets/fonts/`. Se
alguma estiver ausente, truncada ou não for arquivo de fonte, o build para e diz como
restaurar. Nunca renderizar com fallback de sistema: a inconsistência é permanente no feed.

Para apontar outro Chromium: `CHROMIUM_EXECUTAVEL=/caminho/chrome`.

Depois do render, apresentar os PNGs na ordem das telas.

## 7. Diff do acervo

Toda peça publicada alimenta o acervo. O ciclo é radar → conteúdo → acervo e só fecha com
o diff aplicado — **no mesmo movimento, não depois**:

1. editar `base/teses.json` (status, resumo, `edai`, `verificacao`, `verificado_em`);
2. rodar `python3 scripts/gerar.py`, que regrava `base/mapa-de-teses.md` e a semente do
   portal;
3. gravar `publicado_em` no `roteiro.json`.

Não editar `base/mapa-de-teses.md` nem o bloco gerado do portal à mão: a próxima geração
sobrescreve.

**Alerta de alinhamento** quando o tema tocar área em que o escritório atua, conforme a
política de redes da casa.

---

## Arquivos

- `references/editorial.md` — esquema do `roteiro.json`, catálogo de blocos, arquiteturas
  de 8 e de 6 telas, exemplos de manchete boa e ruim.
- `references/verificacao.md` — protocolo de checagem processual, ficha de fatos, validade.
- `assets/template.html` — o sistema visual, feed e story, com os tokens copiados de
  `design/obsidian-chrome/`. Não editar por peça; layout novo vira bloco novo, documentado
  em `editorial.md`. Mudança de sistema começa em `design/obsidian-chrome/`, nunca aqui.
- `scripts/compliance.py` — o gate. Sem bypass.
- `scripts/testa_compliance.py` — a prova de que o gate morde.
- `scripts/build.py` — gate, fontes, montagem e render.
