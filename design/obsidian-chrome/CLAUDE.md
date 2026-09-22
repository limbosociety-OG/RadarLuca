# Regras do projeto

## Design travado (10 set 2026)
O sistema **Obsidian Chrome** e o template `templates/boletim-judicial/` estão TRAVADOS.
Não redesenhar, não reordenar, não "melhorar" sem pedido explícito.

Invariantes:
- Selo: anel duplo, arco superior + inferior legíveis, monograma serifado (Cormorant) centrado, branco pleno.
  Capa e fechamento usam o mesmo selo: **168px, mesma altura (239px do topo)**.
- Todo board é 1080×1350, padding 76px, cabeçalho (rótulo · régua · número) no topo e rodapé no pé.
- Fundos só a partir dos campos de luz (`--field-*`); nada de cor chapada improvisada.
- Raio zero em tudo; só o selo é redondo/oval.
- Versalete em Poppins 500, tracking 0.2em, 17px nos rótulos; display em Jost 200–300.
- OAB/RJ 274.439 no rodapé do fechamento; aviso "conteúdo informativo · não constitui consulta" no board de aplicação.
- `style` em `<x-import>` não aplica margem — envolver em `<div>` quando precisar deslocar.

Alterações permitidas sem aviso: apenas texto/conteúdo editorial dentro da estrutura existente.
