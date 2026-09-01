# Protocolo de verificação

Nenhum campo desta ficha se preenche de memória. Cada um sai de busca na web com fonte
identificada e data da consulta — e quando a fonte primária não confirma, o estado é
`nao_confirmado`, não uma estimativa plausível.

## Ficha de fatos

| campo | o que confirmar | onde |
|---|---|---|
| `processo` | Classe e número completos, com a UF quando houver. Conferir dígito a dígito. | Portal do STF / STJ |
| `tema` | Número do tema de repercussão geral ou do repetitivo, e se a tese já foi fixada. | Portal de repercussão geral do STF · repetitivos do STJ |
| `orgao` | Plenário, Plenário Virtual, Seção, Turma, CSRF. Muda o peso do precedente. | Andamento |
| `julgamento` | Data da sessão em que se fixou a tese. | Andamento |
| `acordao` | Data da publicação. Enquanto não publicado, a tese circula por notícia — dizer isso. | DJe |
| `transito` | Transitou? Se não, a peça não pode falar em definitividade. | Andamento |
| `embargos` | Prazo em curso, opostos, ou julgados. Embargos pendentes podem trazer modulação. | Andamento |
| `modulacao` | Houve? Qual o marco temporal? Quais processos ressalvados? | Inteiro teor do acórdão |
| `suspensao` | Há determinação de suspensão nacional? Alcança o quê? | Decisão de afetação |

Cada campo é um objeto `{ "valor", "estado", "fonte", "data" }`. `data` é a data da
consulta, em `AAAA-MM-DD` — não a data do julgamento.

## Estados

- **`confirmado`** — fonte primária consultada, com data. Só este estado libera o render.
- **`nao_confirmado`** — buscou-se e não se achou. Escrever isso na peça se o fato for
  indispensável ("acórdão ainda não publicado"), ou trocar o ângulo se não for.
- **`conflitante`** — duas fontes divergem. Resolver antes de prosseguir; se não resolver,
  a peça não sai. Divergência mais comum: número de processo transcrito com erro por
  veículo de imprensa e depois replicado.

O gate de compliance lê esses estados no `roteiro.json` e falha o build fora de
`confirmado`. Isso é deliberado: a fricção existe para que a única saída seja voltar à
fonte, não seguir adiante.

## Validade — a ficha vence

`confirmado` sem data não é confirmação, e confirmação velha também não é. O gate exige
`fonte` e `data` em todo campo, e reprova qualquer ficha com **mais de 15 dias**.

Andamento, placar e pauta mudam toda semana: uma ficha de fevereiro renderizando em
setembro é exatamente o modo como um dado morto vira post. Vencida a janela, o caminho é
voltar à fonte primária e reescrever a data — não estender o prazo no script.

Peça já publicada leva `"publicado_em": "AAAA-MM-DD"` na raiz do roteiro. A partir daí a
janela é medida contra a publicação, e não contra hoje: renderizar de novo reproduz o que
saiu, sem reabrir a verificação. Para atualizar a peça, reverifique a ficha e mova a data.

## Coerência de citação

O gate extrai de cada slide e da legenda toda citação de `ARE`, `RE`, `REsp`, `AREsp`,
`EREsp`, `RMS`, `ADI`, `ADC`, `ADPF` e `Tema`, e confere contra a ficha. Número citado que
não está na ficha reprova a peça.

Não é burocracia: `ARE 1.593.384` circulou meses no lugar de `ARE 1.593.784`. Um dígito,
replicado de material em material, porque nada conferia o texto contra a ficha.

## Hierarquia de fontes

1. Portais do STF e do STJ, DJe, inteiro teor do acórdão, atos normativos no DOU.
2. Pareceres SEI da PGFN, Soluções de Consulta Cosit, atos do CGIBS, acórdãos da CSRF.
3. JOTA, Conjur, Migalhas, Valor, boletins de bancas.

Camada 3 serve para descobrir que algo aconteceu, nunca para afirmar o que aconteceu.
Notícia de julgamento sai antes do acórdão e frequentemente comprime a tese fixada num
resumo que não corresponde ao texto — e é a tese fixada, não o resumo, que vai na tela 2.

## Distinções que a peça precisa manter

Tese fixada com trânsito · tese fixada com embargos pendentes · julgamento em curso com
placar parcial · afetação sem julgamento · mera expectativa de pauta. As cinco situações
produzem manchetes diferentes, e colapsá-las é o erro mais comum em conteúdo jurídico de
rede social.

O mesmo vale para a força do precedente: repercussão geral e repetitivo vinculam;
decisão de turma do STJ, de TRF ou de câmara do CARF, não. Quando a peça for sobre
decisão não vinculante, isso precisa aparecer no corpo — não só no mono.
