---
name: boletim
description: Produz o boletim semanal do Radar Tributário — varredura de STF, STJ, CARF, PGFN, Receita, CGIBS e legislação nova, com filtro de consequência prática e diff do mapa de teses. Use quando o pedido for "boletim", "radar da semana", "o que mudou", "fecha a semana" ou qualquer pedido de atualização periódica do acompanhamento tributário. Não use para produzir peça de Instagram, que é a skill `carrossel`.
---

# Boletim semanal

Teto de 600 palavras. Gravado em `boletins/AAAA-MM-DD.md`, data da sexta-feira de
fechamento. Semana fraca se declara fraca — inflar boletim destrói a utilidade do hábito.

## Antes de escrever

Ler `base/teses.json` (a fonte da verdade; `base/mapa-de-teses.md` é derivado dela) e
`base/pendencias.md`. O boletim é a varredura contra o que
já está mapeado: um item entra porque *moveu* algo do acervo, ou porque abre frente nova
que o acervo ainda não tem.

Buscar na web, com data, em cada fonte primária: portal de repercussão geral do STF, pauta
do Plenário e das Turmas, repetitivos e Informativo do STJ, acórdãos da Câmara Superior do
CARF, Soluções de Consulta Cosit e INs da Receita, pareceres SEI de dispensa de contestação
da PGFN, atos do CGIBS e atos conjuntos RFB/CGIBS, DOU. Secundárias para achar o que
escapou: JOTA, Conjur, Migalhas, Valor, boletins de bancas.

Status não confirmado não entra como fato. Entra como pendência, e vai para
`base/pendencias.md`.

## Estrutura

**1. O que mudou** — até 5 itens. Cada um: o fato em uma frase, o "e daí?" em duas. Se um
item não tem consequência prática, ele não é um item.

**2. Janela de oportunidade** — prazo com data certa, julgamento marcado, modulação que
fecha porta. Se não houver, escrever "nada esta semana" e seguir.

**3. Radar da próxima semana** — o que está pautado, com data.

**4. Para estudar** — um tema, com o porquê. De preferência algo que o backlog já pedia e
que a semana tornou urgente.

## Depois de escrever

Aplicar o diff no mesmo movimento — status que mudou, tese que foi fixada, tema novo que
entra. Editar `base/teses.json` e rodar `python3 scripts/gerar.py`, que regrava o mapa e a
semente do portal de uma vez. Não editar `base/mapa-de-teses.md` à mão: é derivado.
Item cujo resultado não foi confirmado em fonte primária entra como `"verificacao":
"a_confirmar"` com o texto do que falta, nunca como fato. Não oferecer para depois.

Se algum item passar nos seis critérios de pauta do `CLAUDE.md`, dizer isso ao fim do
boletim em uma linha — sem produzir a peça, que é decisão separada.
