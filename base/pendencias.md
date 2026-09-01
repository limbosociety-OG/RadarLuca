# Pendências de verificação

Nada daqui vira peça, boletim ou parecer sem confirmação em fonte primária, com data.

Este arquivo guarda a **prosa** da pendência: o que falta, onde procurar, por que importa.
O estado por tese vive em `base/teses.json`, nos campos `verificacao`, `verificado_em` e
`pendencia` — é de lá que o mapa e o portal tiram a marca ⚠️. Os dois andam juntos: fechou
aqui, muda lá e roda `python3 scripts/gerar.py`.

`python3 scripts/doctor.py` cobra reverificação de tese parada há mais de 30 dias.

---

## Resolvido

**01/09/2026 — ARE 1.593.784/SC, Tema 1.455 (IPTU por área).** A divergência entre
1.593.784 e 1.593.384 nos materiais antigos está resolvida: **1.593.784** é o correto.
Rel. Min. Dias Toffoli, Plenário Virtual, sessão encerrada em 05/08/2026, unânime, negado
provimento ao recurso do município de Chapecó (LC municipal 639/2018, alíquota de 1% a
partir de 400 m² de área construída). Confirmado no portal de repercussão geral do STF
(incidente 7524215) e no comunicado oficial da Corte.

Varredura de 01/09/2026: não resta nenhuma ocorrência de `1.593.384` no repositório. E o
gate de compliance agora confere toda citação de processo contra a ficha de verificação da
peça, o que fecha a porta por onde esse erro entrou.

---

## Aberto

- **STJ Tema 1.372** — ICMS-DIFAL fora da base do PIS/Cofins. Notícia de tese fixada em
  20/08/2026 com modulação a partir de 15/03/2017. **Nada disso está confirmado.** Conferir
  o acórdão e a redação exata da modulação, e refazer a aritmética do corte contra o
  quinquênio antes de qualquer peça — se o corte for mesmo 15/03/2017, ele é praticamente
  inerte para quem ajuíza hoje, e é essa leitura que vale como produto.
- **STJ Tema 1.412** — bonificações e descontos comerciais. Adiado, suspensão nacional
  ativa. Confirmar nova data.
- **STJ Tema 1.244** — PIS/Cofins-Importação, GATT, ZFM. Resultado da sessão de 20/08/2026
  não confirmado.
- **ADIs 6399 / 6403 / 6415** — voto de qualidade no CARF. Resultado não confirmado. Não
  está em `teses.json` porque nem a existência do julgamento foi verificada.
- **NFS-e** — correção de prazo para 01/10/2026, conferir no ato conjunto RFB/CGIBS.
- **Lei 15.270/2025 (retenção de 10% sobre dividendos)** — status do recurso da PGFN contra
  a liminar do TRF-4 e se há repetição do entendimento em outros tribunais. Pauta de maior
  apelo para sócios; não publicar sem o mapa de litigância atualizado.

## Dívida de fonte primária

Vinte e sete das vinte e oito teses de `base/teses.json` estão marcadas `a_confirmar`,
quase todas porque a fonte anotada é secundária (boletim de banca, portal de notícia) e
nunca foi cotejada com a origem. Não é alarme: é o retrato honesto do acervo migrado do
chat. Cada `pendencia` diz o que falta naquela tese.

A ordem de ataque não é alfabética. Confirmar primeiro o que está a um passo de virar peça
ou parecer: Tema 1.372, Tema 1.244, Tema 118, Editais 9 e 10/2026 (prazo com data certa) e
Lei 15.270/2025.
