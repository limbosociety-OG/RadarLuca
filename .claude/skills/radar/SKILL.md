---
name: radar
description: Varredura de notícia jurídica brasileira (STJ, STF, TJRJ, ConJur, Migalhas, JOTA, Receita Federal) com filtro editorial de seis critérios e relatório estruturado de pauta. Use sempre que o pedido for "radar", "radar do dia", "radar tributário", "o que saiu hoje", "tem pauta?", "varre as fontes", "o que está fervendo", ou qualquer pedido de levantamento de decisão, julgamento, tese firmada, súmula, informativo ou movimentação normativa para virar conteúdo. Use também quando o pedido for de checagem de uma notícia jurídica específica antes de publicar. Não use para redigir a peça final, porque o radar entrega matéria-prima e recomendação enquanto a produção do carrossel é a skill `carrossel`. Esta é a skill de radar deste repositório: se o ambiente tiver `radar-juridico`, é uma cópia antiga desta mesma e foi substituída por ela.
---

# Radar jurídico

Levanta matéria-prima de pauta e devolve um relatório que separa o que está confirmado do que não está. O radar não escreve conteúdo. Ele decide o que merece virar conteúdo e entrega a decisão fundamentada.

O erro que este procedimento existe para evitar: um dado inventado ou uma decisão mal lida derruba a peça inteira e a autoridade junto. Autoridade construída em cima de erro factual não é autoridade, é passivo.

## Régua de veracidade (acima de tudo o resto)

Nada verificável é chutado, estimado ou presumido. Cada afirmação do relatório cai em um de três estados, e o estado aparece no texto:

- **Confirmado** — localizado em fonte primária ou em fonte secundária confiável que cita a fonte primária. Vai para o relatório com a fonte anotada.
- **Não localizado** — procurado, não encontrado. Vai para o relatório marcado `[[VERIFICAR: o que falta]]`. Nunca vira afirmação.
- **Desconhecido** — fora do alcance da busca. Dito na cara: "não consigo confirmar".

Vale para número de processo, data de julgamento, redação de dispositivo, valor, prazo, relator, órgão julgador, tese firmada e repercussão. Na dúvida entre publicar com lacuna e não publicar, não publica.

Notícia jurídica brasileira circula com erro de origem em volume relevante, inclusive em portais grandes. Manchete não é dispositivo. Antes de tratar uma tese como firmada, conferir na origem (STJ, STF, DOU, portal do órgão).

## Procedimento

### 1. Varredura

Ler `base/teses.json` e `base/pendencias.md` antes de buscar: item que já está no acervo entra no radar porque *moveu*, não porque existe. Buscar nas fontes de `references/fontes.md`. Rodar buscas separadas por fonte e por tema — busca combinada devolve resultado raso para todos.

Cobertura mínima de um radar do dia:
- Informativo de jurisprudência mais recente do STJ e do STF
- Repetitivos e repercussão geral com movimentação na semana
- ConJur, Migalhas e JOTA nas últimas 24 a 48 horas
- Receita Federal e, quando o tema for reforma do consumo, os atos do comitê gestor
- Publicação em Diário Oficial quando o item for normativo

Quando a data importa (e quase sempre importa), incluir o ano corrente na query. Query de 2 a 6 palavras, específica. Se a busca não retorna, reformular com outros termos, não repetir a mesma.

### 2. Filtro de seis critérios

Cada item candidato passa pelos seis. O filtro é eliminatório, não ponderado: item que falha em relevância ou em implicação jurídica concreta sai, por melhor que esteja nos outros.

1. **Relevância** — atinge quem? Se atinge só o operador do direito, é tema de tribunal, não de conteúdo.
2. **Presença pública agora** — está sendo discutido? Ver item 5 abaixo antes de afirmar qualquer coisa aqui.
3. **Recência** — quantos dias? Item com mais de duas semanas precisa de gancho novo para justificar.
4. **Implicação jurídica concreta** — existe dispositivo, tese ou consequência operativa? "Discussão em curso" e "tendência" não passam.
5. **Aderência aos eixos** — empresarial e civil (núcleo); crise político-jurídica lida pela lente patrimonial; tributário e patrimonial. Item que não encaixa em nenhum sai.
6. **Urgência ou intensidade** — tem prazo correndo, janela de adequação, efeito imediato?

Não existe item de manutenção de feed. Se nenhum candidato passa, o relatório diz que não há pauta hoje. Isso é resultado válido: a escassez é parte do posicionamento, silêncio é escolha e não falha de calendário.

### 3. Ângulo

Item aprovado precisa de ângulo, não de resumo. O resumo já circulou. O que não circulou é a consequência operativa: prazo, prova, garantia do juízo, modulação, quem paga a conta, o que muda no contrato que já está assinado.

Em matéria tributária isso é a diferença central. O especialista tributário cobre a tese. Quase ninguém cobre o que acontece com a tese dentro do processo. Perseguir esse terreno.

Se o ângulo encontrado é o mesmo que qualquer advogado escreveria, o item ainda não está pronto. Volta para a busca ou vai para a lista de descartados com o motivo anotado.

### 4. Termômetro

O X mede opinião pública virtual, nada além disso. Verificar se há reação pública real antes de afirmar que há.

Se não houver reação verificável, a seção Termômetro sai inteira do relatório. Não vira estimativa, não vira "provavelmente repercutiu". Ausência de dado é ausência de seção.

### 5. Gate OAB e gate escritório

Antes de recomendar publicação, checar:

- Sem promessa ou garantia de resultado
- Sem caso concreto de cliente, nem anonimizado de forma reconhecível
- Sem sensacionalismo, sem tabela de honorários, sem comparação com outros profissionais
- Fato noticiado e opinião técnica separados de forma visível
- Sem targeting de caso de terceiro identificável

Item que toca área em que o escritório Z atua, ou parte que a casa representa, vai para o relatório com marca de **alinhamento interno prévio**. Na dúvida, não publica.

## Formato do relatório

Usar este template. Seções vazias saem, não viram placeholder.

```
# RADAR — [data]

## Confirmados
Para cada item:
**[Título curto do item]**
- O que é: [1 a 2 frases, fato apenas]
- Fonte: [órgão, número, data, link]
- Implicação operativa: [o que muda na prática]
- Ângulo: [o que ninguém está cobrindo]
- Eixo: [1 / 2 / 3]
- Filtro: [quais dos seis critérios sustentam, quais são fracos]
- Gate: [livre / alinhamento interno prévio — motivo]

## A verificar
[[VERIFICAR: o que falta e onde procurar]] para cada item incompleto

## Descartados
[Item] — [motivo objetivo, qual critério falhou]

## Termômetro
[Só aparece se houver reação pública verificável, com a fonte da verificação]

## Recomendação
[Publica / não publica / segura para verificação. Se publica: qual item, qual eixo, por quê.]
```

## Antes de entregar

Rodar estas quatro perguntas. Falhou uma, refaz:

1. Todo dado do relatório tem fonte anotada, ou está marcado `[[VERIFICAR]]`?
2. O ângulo é operativo, ou é resumo com outra roupa?
3. Os descartados têm motivo objetivo, ou foram descartados por preguiça de busca?
4. O termômetro tem lastro, ou está estimando?
