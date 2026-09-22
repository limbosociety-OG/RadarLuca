# Luca Martins — Obsidian Chrome

Sistema visual extraído das placas de referência: obsidiana profunda, cromo em ascensão, luz direcional e grade densa de mosaico. Nada de espaço em branco generoso — o branco é tático.

## Princípios
- **Grade densa.** Mosaico de 12 colunas, calha de 10px, conteúdo até a borda.
- **Luz direcional.** Todo fundo é um campo de luz (blob, cone, wash, corner, sky, horizon), nunca uma cor chapada sem intenção.
- **Tipografia por contraste.** Display leve (200–300) em escala grande contra versalete 500 com tracking largo.
- **Selo circular.** O dispositivo de marca e de rotulagem — texto no anel, marca no centro.
- **Cantos registrados.** Marcas de registro estruturam a placa.
- **Quadrado por padrão.** Raio zero em tudo; só o selo é redondo.

## Components
- **Field** — campos de luz direcional; base de todo fundo.
- **Seal** — selo circular com texto no anel e marca central.
- **Mosaic** / **Tile** — grade densa de mosaico.
- **Plate** — placa com marcas de registro nos cantos.
- **Statement** — escala tipográfica (hero, display, statement, lead, caps, ring).
- **Figure** — numeral sobredimensionado em peso leve.
- **SpecLine** — linha de especificação em versalete com régua.

## Tokens
`styles.css` importa `tokens/`: fonts, palette, type, layout, fields, motion, base.

## Estado
Design **travado** em 10 set 2026 — ver `CLAUDE.md` para os invariantes. O template `Boletim Judicial` é a referência canônica de aplicação.
