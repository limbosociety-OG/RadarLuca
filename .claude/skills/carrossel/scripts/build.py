#!/usr/bin/env python3
"""Monta e renderiza o carrossel a partir do roteiro.json.

    python3 scripts/build.py roteiro.json --out ./saida
    python3 scripts/build.py roteiro.json --out ./saida --formato ambos

Etapas, nesta ordem e sem bandeira de bypass:
    compliance -> fontes vendorizadas -> HTML -> PNG

Formatos: `feed` 1080×1350 (padrão), `story` 1080×1920, `ambos`.
Saída: `slide-NN.png` para feed, `story-NN.png` para story.

Chromium: usa o do Playwright. Para apontar outro binário,
`CHROMIUM_EXECUTAVEL=/caminho/para/chrome`.
"""
import argparse
import base64
import html
import json
import os
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTES_DIR = RAIZ / "assets" / "fonts"

FORMATOS = {"feed": (1080, 1350, "slide"), "story": (1080, 1920, "story")}

# Assinaturas de arquivo de fonte aceitas. Um HTML de erro salvo com nome .ttf
# passa em qualquer checagem de tamanho — não passa nesta.
MAGICOS = (b"\x00\x01\x00\x00", b"true", b"ttcf", b"OTTO")

FONTES = {
    "BodoniModa.ttf": "ofl/bodonimoda/BodoniModa%5Bopsz,wght%5D.ttf",
    "BodoniModa-Italic.ttf": "ofl/bodonimoda/BodoniModa-Italic%5Bopsz,wght%5D.ttf",
    "Spectral-Regular.ttf": "ofl/spectral/Spectral-Regular.ttf",
    "Spectral-SemiBold.ttf": "ofl/spectral/Spectral-SemiBold.ttf",
    "Spectral-Italic.ttf": "ofl/spectral/Spectral-Italic.ttf",
    "IBMPlexMono.ttf": "ofl/ibmplexmono/IBMPlexMono-Regular.ttf",
}
ORIGEM = "https://raw.githubusercontent.com/google/fonts/main/"


# ------------------------------------------------------------------ fontes
def conferir_fontes():
    """As fontes são vendorizadas e versionadas. O build NÃO baixa nada.

    Render com fonte errada produz inconsistência permanente no feed, e um
    download silencioso no meio do build é justamente como uma fonte errada
    entra sem ninguém ver. Faltou arquivo: para, e diz onde buscar."""
    faltando = []
    for nome in FONTES:
        alvo = FONTES_DIR / nome
        if not alvo.exists():
            faltando.append(f"{nome}: ausente")
        elif alvo.stat().st_size < 20000:
            faltando.append(f"{nome}: {alvo.stat().st_size} bytes — truncado")
        elif alvo.read_bytes()[:4] not in MAGICOS:
            faltando.append(f"{nome}: não é arquivo de fonte (assinatura inválida)")
    if faltando:
        linhas = "\n".join(f"  ✗ {f}" for f in faltando)
        recup = "\n".join(f"  curl -Lo {FONTES_DIR / n} {ORIGEM}{c}"
                          for n, c in FONTES.items())
        sys.exit(
            f"BUILD INTERROMPIDO — fontes vendorizadas inválidas:\n{linhas}\n\n"
            "Não existe fallback de sistema aqui: a peça sairia com desenho de letra\n"
            "diferente das anteriores e a inconsistência é permanente no feed.\n"
            "Restaure os arquivos a partir do versionamento (`git checkout -- "
            f"{FONTES_DIR.relative_to(RAIZ.parent.parent.parent)}`) ou, em último caso:\n"
            f"{recup}")


def fontface():
    def b64(n):
        return base64.b64encode((FONTES_DIR / n).read_bytes()).decode()

    def face(fam, arq, peso="400", estilo="normal"):
        return (f"@font-face{{font-family:'{fam}';src:url(data:font/ttf;base64,"
                f"{b64(arq)}) format('truetype');font-weight:{peso};"
                f"font-style:{estilo};font-display:block}}")

    return "\n".join([
        face("Bodoni Moda", "BodoniModa.ttf", "400 900"),
        face("Bodoni Moda", "BodoniModa-Italic.ttf", "400 900", "italic"),
        face("Spectral", "Spectral-Regular.ttf", "400"),
        face("Spectral", "Spectral-SemiBold.ttf", "600"),
        face("Spectral", "Spectral-Italic.ttf", "400", "italic"),
        face("IBM Plex Mono", "IBMPlexMono.ttf", "400"),
    ])


# ------------------------------------------------------------------ texto
def rico(t):
    """**negrito** e *itálico*, com escape antes para não injetar marcação."""
    t = html.escape(t or "")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t, flags=re.S)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t, flags=re.S)
    return t.replace("\n", "<br>")


# ------------------------------------------------------------------ blocos
def render_bloco(b):
    t = b.get("tipo")

    if t == "kicker":
        return f'<div class="kicker">{rico(b["texto"])}</div>'

    if t == "manchete":
        txt = b["texto"]
        cls = " curta" if len(txt) < 34 else ""
        out = f'<h1 class="bloco{cls}">{rico(txt)}</h1>'
        if b.get("filete"):
            out += '<div class="filete"></div>'
        return out

    if t == "regua":
        return '<div class="regua"></div>'

    if t == "paragrafo":
        return f'<p class="corpo bloco">{rico(b["texto"])}</p>'

    if t == "citacao":
        return f'<blockquote class="bloco">{rico(b["texto"])}</blockquote>'

    if t == "mono":
        return f'<div class="mono bloco">{rico(b["texto"])}</div>'

    if t == "duo":
        cols = "".join(
            f'<div><div class="rot">{rico(c["rotulo"])}</div>'
            f'<div class="num">{rico(c["numero"])}</div>'
            f'<div class="txt">{rico(c.get("texto",""))}</div>'
            + (f'<span class="tag {c.get("tom","ok")}">{rico(c["tag"])}</span>'
               if c.get("tag") else "")
            + "</div>"
            for c in b["colunas"])
        return f'<div class="duo bloco">{cols}</div>'

    if t == "caixas":
        out = []
        for it in b["itens"]:
            linhas = "".join(f"<p>{rico(l)}</p>" for l in it["linhas"])
            out.append(f'<div class="caixa {it.get("tom","ok")}">'
                       f'<div class="rot">{rico(it["rotulo"])}</div>{linhas}</div>')
        return f'<div class="bloco">{"".join(out)}</div>'

    if t == "numerada":
        itens = "".join(
            f'<div class="item"><div class="n">{i:02d}</div><div>'
            f'<h2>{rico(it["titulo"])}</h2><p>{rico(it.get("texto",""))}</p>'
            f"</div></div>"
            for i, it in enumerate(b["itens"], 1))
        return f'<div class="bloco">{itens}</div>'

    if t == "prazo":
        total, mortas = b.get("total", 6), b.get("vencidas", 1)
        cels = "".join(f'<i class="{"morta" if i < mortas else "viva"}"></i>'
                       for i in range(total))
        return (f'<div class="bloco"><div class="prazo">{cels}</div>'
                f'<div class="prazo-rot"><span>{rico(b.get("esq",""))}</span>'
                f'<span>{rico(b.get("centro",""))}</span>'
                f'<span>{rico(b.get("dir",""))}</span></div></div>')

    sys.exit(f"ERRO: tipo de bloco desconhecido: {t!r}. "
             "Tipos válidos estão em references/editorial.md.")


def render_slide(s, n, total, formato):
    tema = s.get("tema", "claro")
    extra = " capa" if s.get("capa") else ""
    extra += " story" if formato == "story" else ""
    classes = f"slide {tema}{extra}"

    topo = (f'<div class="topo"><span class="esq">{rico(s.get("eyebrow_esq",""))}</span>'
            f'<span class="dir">{rico(s.get("eyebrow_dir",""))}</span></div>'
            '<div class="fio"></div>')

    corpo = "".join(render_bloco(b) for b in s["blocos"])
    alinhar = " topo-alinhado" if s.get("alinhar") == "topo" else ""

    papel = "Advogado · Direito Tributário" if s.get("fecho") else "Advogado"
    # No story não há "arrastar": o avanço é toque, e a paginação vale nos dois.
    if s.get("capa") and formato == "feed":
        pag = '<span class="pag arraste">ARRASTE →</span>'
    else:
        pag = f'<span class="pag">{n:02d} / {total:02d}</span>'

    return (f'<section class="{classes}">{topo}'
            f'<div class="miolo{alinhar}">{corpo}</div>'
            f'<div class="fio" style="margin:0 0 22px"></div>'
            f'<div class="pe"><div><div class="marca">Luca Martins</div>'
            f'<div class="papel">{papel}</div></div>{pag}</div></section>')


# ------------------------------------------------------------------ render
def renderizar(roteiro, out, formato, doc_base):
    largura, altura, prefixo = FORMATOS[formato]
    slides = roteiro["slides"]
    total = len(slides)
    corpo = "\n".join(render_slide(s, i, total, formato)
                      for i, s in enumerate(slides, 1))
    doc = doc_base.replace("__SLIDES__", corpo)
    pagina = out / f"_peca-{formato}.html"
    pagina.write_text(doc, encoding="utf-8")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        opcoes = {"args": ["--force-color-profile=srgb", "--font-render-hinting=none"]}
        if os.environ.get("CHROMIUM_EXECUTAVEL"):
            opcoes["executable_path"] = os.environ["CHROMIUM_EXECUTAVEL"]
        nav = p.chromium.launch(**opcoes)
        pg = nav.new_page(viewport={"width": largura, "height": altura},
                          device_scale_factor=1)
        pg.goto(pagina.resolve().as_uri())
        pg.wait_for_timeout(900)
        alvos = pg.query_selector_all(".slide")
        for i, el in enumerate(alvos, 1):
            el.screenshot(path=str(out / f"{prefixo}-{i:02d}.png"))
        nav.close()
    print(f"{total} telas em {formato} {largura}×{altura} → {out}/{prefixo}-NN.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    ap.add_argument("--out", default="./saida")
    ap.add_argument("--formato", choices=["feed", "story", "ambos"], default="feed")
    a = ap.parse_args()

    gate = subprocess.run([sys.executable, str(RAIZ / "scripts" / "compliance.py"),
                           a.roteiro])
    if gate.returncode != 0:
        sys.exit(gate.returncode)

    conferir_fontes()
    roteiro = json.loads(pathlib.Path(a.roteiro).read_text(encoding="utf-8"))
    doc_base = (RAIZ / "assets" / "template.html").read_text(encoding="utf-8")
    doc_base = doc_base.replace("__FONTFACE__", fontface())

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for f in (["feed", "story"] if a.formato == "ambos" else [a.formato]):
        renderizar(roteiro, out, f, doc_base)


if __name__ == "__main__":
    main()
