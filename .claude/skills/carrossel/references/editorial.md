# Editorial — roteiro, blocos e arquitetura

## Índice

1. Esquema do `roteiro.json`
2. Catálogo de blocos
3. Arquitetura de telas (8 telas, 6 telas, story)
4. Voz — manchete, corpo, microtipografia
5. Exemplo completo

---

## 1. Esquema do `roteiro.json`

```json
{
  "peca": "iptu-tema-1455",
  "publicado_em": "2026-08-20",
  "verificacao": {
    "processo":   { "valor": "ARE 1.593.784/SC", "estado": "confirmado", "fonte": "portal.stf.jus.br", "data": "2026-08-20" },
    "tema":       { "valor": "Tema 1.455 RG",    "estado": "confirmado", "fonte": "portal.stf.jus.br", "data": "2026-08-20" },
    "julgamento": { "valor": "05.08.2026",       "estado": "confirmado", "fonte": "portal.stf.jus.br", "data": "2026-08-20" },
    "acordao":    { "valor": "14.08.2026",       "estado": "confirmado", "fonte": "portal.stf.jus.br", "data": "2026-08-20" },
    "modulacao":  { "valor": "ausente",          "estado": "confirmado", "fonte": "inteiro teor",      "data": "2026-08-20" },
    "embargos":   { "valor": "prazo em curso",   "estado": "confirmado", "fonte": "andamento",         "data": "2026-08-20" }
  },
  "slides": [
    {
      "tema": "escuro",
      "eyebrow_esq": "RADAR TRIBUTÁRIO",
      "eyebrow_dir": "STF · TEMA 1.455",
      "blocos": [ ... ]
    }
  ]
}
```

Campos de raiz:

| campo | efeito |
|---|---|
| `peca` | Slug da peça. Bate com o nome da pasta em `pecas/`. |
| `publicado_em` | Opcional, `AAAA-MM-DD`. Presente = a peça já saiu, e a validade da ficha passa a ser medida contra esta data em vez de hoje. Ausente = peça em produção, ficha tem de estar fresca. |
| `verificacao` | A ficha de fatos. Ver `references/verificacao.md`. |
| `slides` | Lista ordenada de telas. |

Ao lado do `roteiro.json`, na mesma pasta, o gate exige `legenda.md`. Peça sem legenda não
renderiza: a legenda é publicada junto e circula sozinha em print.

Campos de slide:

| campo | efeito |
|---|---|
| `tema` | `"escuro"` ou `"claro"`. Define fundo, cor de texto e cor dos acentos. |
| `eyebrow_esq` | Linha mono superior esquerda. Na capa, o nome da série; nas demais, `NN — RÓTULO DA SEÇÃO`. O `NN` é escrito no roteiro (a numeração de seção é editorial, não automática). |
| `eyebrow_dir` | Linha mono superior direita, em cor de acento. Referência legal curta: `CF, ART. 156, §1º`, `CTN, ART. 168`, `TRÊS CHECAGENS`. |
| `capa` | `true` na primeira tela. Troca o rodapé direito por `ARRASTE →` e usa a assinatura longa. |
| `fecho` | `true` na última. Usa assinatura `ADVOGADO · DIREITO TRIBUTÁRIO`. |
| `blocos` | Lista ordenada de blocos (abaixo). |

A paginação (`03 / 08`) é calculada pelo script a partir do total de slides.

---

## 2. Catálogo de blocos

Cada bloco é um objeto com `tipo` e os campos que aquele tipo consome.

### `kicker`
Linha mono em cor de acento acima da manchete. Usada na capa e nas telas de virada.
```json
{ "tipo": "kicker", "texto": "JULGADO EM 05.08.2026 — UNÂNIME" }
```
No tema escuro sai em coral; no claro, em índigo.

### `manchete`
A linha grande, Bodoni Moda, peso 700. Uma a quatro linhas. Sem ponto final quando é
pergunta com `?`; com ponto final quando é afirmação — a peça inteira usa ponto final em
manchete afirmativa, e isso é parte do desenho.
```json
{ "tipo": "manchete", "texto": "Metro quadrado não mede capacidade de pagar.", "filete": true }
```
`filete: true` desenha o traço curto de acento abaixo. Usar quando a manchete abre uma
seção expositiva; omitir quando ela é seguida imediatamente por uma citação.

### `regua`
Linha horizontal fina de largura total. Separa manchete de conteúdo quando não há filete.
```json
{ "tipo": "regua" }
```

### `paragrafo`
Corpo em Spectral. Aceita `**negrito**` e `*itálico*`.
```json
{ "tipo": "paragrafo", "texto": "Muitos municípios criaram faixas: **passou de tantos metros, a alíquota sobe.**" }
```

### `citacao`
Bloco recuado com barra vertical de acento à esquerda, Spectral itálico, corpo maior.
Reservado para a tese fixada na letra e para a frase de fecho.
```json
{ "tipo": "citacao", "texto": "É inconstitucional a fixação, por lei municipal posterior à EC nº 29/2000, de alíquota do IPTU em razão da área do imóvel." }
```

### `mono`
Microtipografia cinza, IBM Plex Mono. Onde vivem processo, relator, datas, ressalvas e o
aviso do Provimento 205. Quebra de linha com `\n`.
```json
{ "tipo": "mono", "texto": "STF, Plenário Virtual, ARE 1.593.784/SC — Tema 1.455 de repercussão geral.\nRel. Min. Dias Toffoli · julgado em 05.08.2026 · acórdão publicado em 14.08.2026." }
```

### `duo`
Duas colunas comparativas separadas por régua vertical. Para a aritmética que expõe a
distorção.
```json
{ "tipo": "duo", "colunas": [
  { "rotulo": "GALPÃO NA PERIFERIA", "numero": "3.000 m²", "texto": "Área grande, valor por metro baixo.", "tag": "pagava mais", "tom": "alerta" },
  { "rotulo": "APARTAMENTO NA ORLA", "numero": "120 m²",  "texto": "Área pequena, valor por metro alto.", "tag": "pagava menos", "tom": "ok" }
] }
```
`tom`: `alerta` (rosa) ou `ok` (verde).

### `caixas`
Blocos empilhados de "continua válido" versus "não pode mais". O uso mais forte da peça:
delimita o alcance exato da decisão e evita que o leitor generalize.
```json
{ "tipo": "caixas", "itens": [
  { "rotulo": "CONTINUA VÁLIDO", "tom": "ok", "linhas": [
      "Alíquota maior conforme o **valor venal** do imóvel — progressividade.",
      "Alíquota diferente conforme **localização e uso** — seletividade."
  ]},
  { "rotulo": "NÃO PODE MAIS", "tom": "alerta", "linhas": [
      "A **metragem**, sozinha, definir a alíquota."
  ]}
] }
```

### `numerada`
Lista com numeral mono em índigo, título em Bodoni e descrição em Spectral. Para as
checagens que o leitor faz sozinho.
```json
{ "tipo": "numerada", "itens": [
  { "titulo": "A alíquota muda por faixa de metros?", "texto": "Está na lei do seu município, normalmente na tabela anexa ao Código Tributário municipal." }
] }
```

### `prazo`
A barra de prescrição: seis células, as primeiras `vencidas` hachuradas e as demais em
verde, com rótulos abaixo.
```json
{ "tipo": "prazo", "vencidas": 1, "total": 6,
  "esq": "já prescrito", "centro": "cinco anos ainda discutíveis →", "dir": "hoje" }
```

---

## 3. Arquitetura de telas

### Padrão — 8 telas, para decisão com desdobramento patrimonial

| # | tema | seção | função |
|---|---|---|---|
| 1 | escuro | — | Capa. Kicker com data e placar, manchete-pergunta, lead de três linhas. |
| 2 | claro | 01 — O QUE FOI DECIDIDO | A tese na letra. Citação + mono com processo, relator, datas, vinculação. |
| 3 | claro | 02 — TRADUZINDO | O que isso quer dizer em português. Aqui entra o `duo` com a aritmética. |
| 4 | claro | 03 — O LIMITE EXATO | `caixas`. O que continua válido e o que caiu. |
| 5 | claro | 04 — COMO SABER SE TE ALCANÇA | `numerada`. Checagens verificáveis pelo próprio leitor. |
| 6 | escuro | 05 — O QUE NINGUÉM FALOU | Modulação. O achado editorial da peça. |
| 7 | claro | 06 — A JANELA | Prescrição, `prazo`, o que fazer valer e até quando. |
| 8 | escuro | 07 — O QUE FICA | Citação de fecho, orientação genérica, aviso do Provimento 205. |

A tela 6 é o eixo. Se ela não tiver nada que o noticiário não disse, a peça é clipping —
e clipping não entra. Nesse caso, voltar ao passo 2 e trocar de ângulo ou de pauta.

### Story — 1080×1920

Mesma arquitetura, mesmo roteiro: `--formato story` renderiza as mesmas telas na altura de
story. O que muda é a caixa útil.

A moldura do Instagram cobre cerca de 230px no topo (nome, avatar, barra de progresso) e
210px na base (campo de resposta, ações). O template reserva 250px e 230px — manchete e
microtipografia ficam fora dessa faixa. Não é respiro estético; é a área que o app come.

Consequência editorial: **tela densa no feed fica apertada no story.** A escala tipográfica
sobe (manchete 66→76px, corpo 25→29px) e a área útil não acompanha na mesma proporção. Em
peça de oito telas com `caixas` ou `numerada` cheias, ou se corta item, ou se quebra a tela
em duas. Conferir tela a tela antes de publicar — o render não avisa quando estoura.

Na capa do story o rodapé traz a paginação em vez de `ARRASTE →`: no story o avanço é
toque, e mandar arrastar é instrução errada.

### Rápido — 6 telas, para pauta quente

Capa (escuro) → tese na letra (claro) → tradução (claro) → o que ninguém falou (escuro) →
janela (claro) → fecho (escuro). Corta a tela de limites e a de checagens. Velocidade
acima de completude: pauta quente perde valor em 48 horas.

---

## 4. Voz

**Manchete.** Carrega a consequência, em português corrente, tamanho de fala. Testa-se
assim: se a frase pudesse abrir uma matéria de jornal econômico, serve; se parece ementa,
não serve.

| ruim | boa |
|---|---|
| STF julga Tema 1.455 de repercussão geral | Seu IPTU foi calculado pelo tamanho do imóvel? |
| Da inconstitucionalidade da progressividade por área | Metro quadrado não mede capacidade de pagar. |
| Efeitos do acórdão e ausência de modulação | Não houve modulação de efeitos. |
| Prazo prescricional quinquenal do art. 168 | A decisão não devolve nada sozinha. |

**Corpo.** Frases curtas. Um raciocínio por parágrafo. Negrito só no que decide — em geral
uma expressão por tela, no máximo duas. Negrito espalhado deixa de sinalizar.

**Microtipografia.** Todo dado verificável desce para o mono cinza: número de processo,
órgão, relator, datas, dispositivo legal, ressalvas de aplicação. Isso libera o corpo do
texto para significar e mantém a peça auditável por quem quiser conferir.

**Legenda.** Três a cinco parágrafos curtos, mesma voz. Sem hashtag genérica de advogado,
sem chamada para DM, sem "salve este post". Termina em fato, nunca em oferta, e fecha com a
ressalva de caráter informativo — o gate exige, porque a legenda é o que sobrevive ao print
recortado, já sem as telas.

**O que não escrever, mesmo fora da lista do gate:** "importante ressaltar", "vale
destacar", "cumpre observar". Promessa de resultado em qualquer formulação. Análise de
caso concreto de cliente. Imperativo dirigido ao leitor ("confira", "corra", "não perca").

---

## 5. Exemplo completo

`references/exemplo-iptu.json` reproduz o carrossel do Tema 1.455 no formato de roteiro —
é a peça de referência do sistema. Ler ao escrever a primeira peça, e usar como gabarito
de densidade: quanto texto cabe por tela sem estourar o layout.
