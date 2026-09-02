#!/usr/bin/env python3
"""Gera a variante de celular do painel, para publicar como Artifact.

    python3 scripts/publicar.py

Escreve `portal/celular.html` a partir de `portal/radar-tributario.html`. Mesma
fonte, mesmo sistema visual — o que muda é o que não faz sentido no telefone:

  * fora o `<!DOCTYPE>`, `<html>`, `<head>` e `<body>`: o Artifact envolve a página
  * fora `privado/prazos.js`: prazo de carteira não sai do disco, nunca
  * somente leitura: sem editar, criar, excluir, importar ou zerar

O terceiro ponto é o que importa. O painel do disco já guarda edição no
localStorage até ser importada; um segundo lugar gravável, no celular, com
armazenamento próprio, criaria uma terceira cópia que nunca volta para o
repositório. No telefone se consulta.
"""
import datetime
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "portal" / "radar-tributario.html"
DESTINO = RAIZ / "portal" / "celular.html"

SO_LEITURA = """
/* ---------- variante de celular: consulta, não edição ---------- */
#nova-tese,#novo-boletim,#nova-aula,#novo-estudo,#exportar,#importar,#zerar,
.ficha-pe,.mini,#aviso-semente,#aviso-sujo,dialog,.backlog input[type=checkbox]{
  display:none!important}
.edai-txt,.boletim-corpo,.aula-notas,.backlog .txt{cursor:default}
.edai-txt:hover,.aula-notas:hover{background:transparent}
.instantaneo{font-family:var(--mono);font-size:11px;line-height:1.6;color:var(--ink2);
  background:var(--indigo-soft);border:1px solid #C3C9E0;border-radius:3px;
  padding:10px 13px;margin:18px 0 0}
.instantaneo b{color:var(--indigo)}
@media (max-width:720px){
  .masthead{padding:26px 0 18px}
  .abas{gap:0;overflow-x:auto;-webkit-overflow-scrolling:touch;flex-wrap:nowrap}
  .aba{white-space:nowrap;font-size:13px;padding:10px 12px}
  .sub{gap:6px 16px;font-size:11px}
  .prazo-lista,.grade,.term-grade{grid-template-columns:1fr}
  .linha{padding-left:20px}
  .ev::before{left:-19px}
}
"""


def main():
    if not ORIGEM.exists():
        sys.exit(f"ERRO: {ORIGEM} não existe. Rode scripts/gerar.py antes.")
    s = ORIGEM.read_text(encoding="utf-8")

    # 1. prazo de carteira não viaja
    s = re.sub(r'<script src="\.\./privado/prazos\.js"[^>]*></script>\n*', "", s)
    # O que vaza é CARREGAMENTO ou DADO, não menção. `PRAZOS_PRIVADOS`, a classe
    # `.pz.privado` e o texto que explica a pasta continuam — sem o arquivo,
    # ficam inertes. O que não pode existir é algo que traga a pasta para dentro.
    carrega = re.findall(r'(?:src|href)\s*=\s*["\'][^"\']*privado/[^"\']*|'
                         r'fetch\s*\(\s*["\'][^"\']*privado/', s)
    if carrega:
        sys.exit("ERRO: a variante publicável carrega privado/: " + "; ".join(carrega))
    if re.search(r"PRAZOS_PRIVADOS\s*=\s*\[\s*\{", s):
        sys.exit("ERRO: prazo de carteira embutido na variante publicável.")

    # 2. o Artifact fornece o esqueleto do documento
    s = re.sub(r"<!DOCTYPE html>\s*", "", s, flags=re.I)
    # `\s*>` e não `[^>]*>`: sem isso, `</?head[^>]*>` também casa
    # `<header class="masthead">` e come o cabeçalho da página.
    s = re.sub(r"</?html(?:\s[^>]*)?>\s*", "", s, flags=re.I)
    s = re.sub(r"</?head\s*>\s*", "", s, flags=re.I)
    s = re.sub(r"</?body(?:\s[^>]*)?>\s*", "", s, flags=re.I)
    if "<header" not in s or 'class="masthead"' not in s:
        sys.exit("ERRO: o cabeçalho da página se perdeu na conversão.")
    s = re.sub(r'<meta charset[^>]*>\s*|<meta name="viewport"[^>]*>\s*', "", s, flags=re.I)

    # 3. somente leitura
    s = s.replace(' contenteditable="true"', "")
    # No ÚLTIMO </style>: o primeiro é o bloco de fontes, e regra que entra antes
    # da folha principal perde a cascata sem avisar.
    corte = s.rindex("</style>")
    s = s[:corte] + SO_LEITURA + s[corte:]

    # No Artifact o <title> é o nome na galeria e na aba. Nome, não legenda.
    s = re.sub(r"<title>.*?</title>", "<title>Radar Tributário</title>", s, flags=re.S)

    hoje = datetime.date.today().isoformat()
    s = s.replace('<div id="aviso-armazenamento"></div>',
                  f'<div class="instantaneo"><b>Instantâneo de consulta</b> — gerado em '
                  f'{hoje} a partir do repositório, sem a camada privada. Para editar, '
                  f'anotar ou registrar aula, use o painel no computador; esta página '
                  f'não grava nada.</div>\n<div id="aviso-armazenamento"></div>', 1)

    DESTINO.write_text(s, encoding="utf-8")
    kb = DESTINO.stat().st_size / 1024
    print(f"escrito {DESTINO.relative_to(RAIZ)} ({kb:.0f} KB) — publique com o Artifact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
