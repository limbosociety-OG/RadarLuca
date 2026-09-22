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
import hashlib
import html
import json
import math
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

# Obsidian Chrome: Jost no display, Poppins no versalete, Archivo no texto,
# Cormorant Garamond só no monograma do selo e na citação.
FONTES = {
    "Jost.ttf": "ofl/jost/Jost%5Bwght%5D.ttf",
    "Poppins-Medium.ttf": "ofl/poppins/Poppins-Medium.ttf",
    "Poppins-SemiBold.ttf": "ofl/poppins/Poppins-SemiBold.ttf",
    "Archivo.ttf": "ofl/archivo/Archivo%5Bwdth,wght%5D.ttf",
    "Archivo-Italic.ttf": "ofl/archivo/Archivo-Italic%5Bwdth,wght%5D.ttf",
    "CormorantGaramond.ttf": "ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
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
        face("Jost", "Jost.ttf", "100 900"),
        face("Poppins", "Poppins-Medium.ttf", "500"),
        face("Poppins", "Poppins-SemiBold.ttf", "600"),
        face("Archivo", "Archivo.ttf", "100 900"),
        face("Archivo", "Archivo-Italic.ttf", "100 900", "italic"),
        face("Cormorant Garamond", "CormorantGaramond.ttf", "300 700"),
    ])


# ------------------------------------------------------------------ texto
def rico(t):
    """**negrito** e *itálico*, com escape antes para não injetar marcação."""
    t = html.escape(t or "")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t, flags=re.S)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t, flags=re.S)
    return t.replace("\n", "<br>")


# ------------------------------------------------------------------ selo
def selo(anel, inferior, marca, tamanho=168, anel_interno=False):
    """O selo do Obsidian Chrome em SVG estático: anel, texto no arco superior e
    no inferior, monograma em Cormorant no centro. O encaixe do texto no arco
    roda no navegador (script do template), como no componente Seal.jsx."""
    uid = "s" + hashlib.md5(f"{anel}|{inferior}|{marca}".encode()).hexdigest()[:8]
    gap, rx = 0.24, 48
    trx, brx = rx - 9, rx - 3.5
    arco_sup, arco_inf = math.pi * trx * 0.94, math.pi * brx * 0.86

    def texto(t, path, arco):
        t = html.escape(t.upper())
        estilo = (f"font-family:var(--face-spec);font-size:6.2px;font-weight:500;"
                  f"letter-spacing:{gap}em")
        return (f'<text x="0" y="-200" fill="none" style="{estilo}">{t}</text>'
                f'<text data-arco="{arco:.3f}" data-gap="{gap}" fill="#F2F1EF" '
                f'style="{estilo}"><textPath href="#{path}" startOffset="50%" '
                f'text-anchor="middle">{t}</textPath></text>')

    linhas = [l for l in re.split(r"\n|\|", marca or "") if l]
    fs = tamanho * 0.34 / max(1, len(linhas) * 0.72)
    interno = (f'<circle cx="50" cy="50" r="{rx - 3}" fill="none" stroke="#F2F1EF" '
               f'stroke-width=".5"/>' if anel_interno else "")
    svg = (f'<svg viewBox="0 0 100 100" width="{tamanho}" height="{tamanho}" aria-hidden="true">'
           f'<circle cx="50" cy="50" r="{rx}" fill="none" stroke="#F2F1EF" stroke-width="1"/>'
           f'{interno}<defs>'
           f'<path id="{uid}t" fill="none" d="M {50 - trx},50 A {trx},{trx} 0 0 1 {50 + trx},50"/>'
           f'<path id="{uid}b" fill="none" d="M {50 - brx},50 A {brx},{brx} 0 0 0 {50 + brx},50"/>'
           f'</defs>'
           + (texto(anel, uid + "t", arco_sup) if anel else "")
           + (texto(inferior, uid + "b", arco_inf) if inferior else "")
           + "</svg>")
    miolo = "".join(f"<span>{html.escape(l)}</span>" for l in linhas)
    return (f'<div class="selo" style="width:{tamanho}px;height:{tamanho}px">{svg}'
            f'<div class="marca" style="font-size:{fs:.2f}px">{miolo}</div></div>')


def caps(txt, cls=""):
    return f'<div class="caps {cls}">{rico(txt)}</div>'


def linha(esq, dir_):
    return (f'<div class="linha caps"><span class="esq">{rico(esq)}</span>'
            f'<span class="regua-f"></span><span class="dir">{rico(dir_)}</span></div>')


def cantos():
    return "".join(f'<span class="tick {c}"></span>' for c in ("tl", "tr", "bl", "br"))


# ------------------------------------------------------------------ blocos
def render_bloco(b):
    t = b.get("tipo")

    if t == "kicker":
        return caps(b["texto"], "kicker bloco")

    if t == "manchete":
        txt = b["texto"]
        cls = " curta" if len(txt) < 34 else ""
        out = f'<h1 class="bloco{cls}">{rico(txt)}</h1>'
        if b.get("filete"):
            out += '<div class="filete"></div>'
        return out

    if t == "regua":
        return '<div class="regua bloco"></div>'

    if t == "paragrafo":
        return f'<p class="corpo bloco">{rico(b["texto"])}</p>'

    if t == "citacao":
        return f'<blockquote class="bloco">\u201c{rico(b["texto"])}\u201d</blockquote>'

    if t == "mono":
        return f'<div class="mono bloco">{rico(b["texto"])}</div>'

    if t == "duo":
        # alerta = laje escura (o que pesa); ok = placa com marcas de registro
        cols = "".join(
            f'<div class="tile{" plate" if c.get("tom", "ok") == "ok" else ""}">'
            + (cantos() if c.get("tom", "ok") == "ok" else "")
            + caps(c["rotulo"], "rot")
            + f'<div class="num">{rico(c["numero"])}</div>'
            f'<div class="txt">{rico(c.get("texto", ""))}</div>'
            + (f'<span class="tag caps {c.get("tom", "ok")}">{rico(c["tag"])}</span>'
               if c.get("tag") else "")
            + "</div>"
            for c in b["colunas"])
        return f'<div class="duo bloco">{cols}</div>'

    if t == "caixas":
        out = []
        for it in b["itens"]:
            ok = it.get("tom", "ok") == "ok"
            linhas = "".join(f"<p>{rico(l)}</p>" for l in it["linhas"])
            out.append(f'<div class="tile caixa{" plate" if ok else ""}">'
                       f'{cantos() if ok else ""}{caps(it["rotulo"], "rot")}{linhas}</div>')
        return f'<div class="caixas bloco">{"".join(out)}</div>'

    if t == "numerada":
        itens = "".join(
            f'<div class="item"><div class="n">{i:02d}</div><div>'
            f'<h2>{rico(it["titulo"])}</h2><p>{rico(it.get("texto", ""))}</p>'
            f"</div></div>"
            for i, it in enumerate(b["itens"], 1))
        return f'<div class="bloco">{itens}</div>'

    if t == "prazo":
        total, mortas = b.get("total", 6), b.get("vencidas", 1)
        cels = "".join(f'<i class="{"morta" if i < mortas else "viva"}"></i>'
                       for i in range(total))
        return (f'<div class="bloco"><div class="prazo">{cels}</div>'
                f'<div class="prazo-rot caps"><span>{rico(b.get("esq", ""))}</span>'
                f'<span>{rico(b.get("centro", ""))}</span>'
                f'<span>{rico(b.get("dir", ""))}</span></div></div>')

    sys.exit(f"ERRO: tipo de bloco desconhecido: {t!r}. "
             "Tipos válidos estão em references/editorial.md.")


# Campo de luz por papel da tela. O roteiro pode trocar com `campo` e `veu`,
# mas só por um campo do sistema — cor chapada improvisada não existe aqui.
CAMPOS = {"blob", "wash", "cone", "corner", "sky", "horizon", "onyx", "slab", "paper"}
VEUS = {"bottom", "top", "left", "nenhum"}


def campo_da_tela(s):
    if s.get("capa"):
        padrao = ("corner", "bottom")
    elif s.get("fecho"):
        # o blob acende a base; o véu de baixo protege aviso e rodapé
        padrao = ("blob", "bottom")
    elif s.get("tema", "claro") == "claro":
        padrao = ("paper", "nenhum")
    else:
        padrao = ("slab", "nenhum")
    campo = s.get("campo", padrao[0])
    veu = s.get("veu", padrao[1] if campo == padrao[0] else "nenhum")
    if campo not in CAMPOS:
        sys.exit(f"ERRO: campo {campo!r} não existe no sistema. Válidos: {sorted(CAMPOS)}")
    if veu not in VEUS:
        sys.exit(f"ERRO: véu {veu!r} não existe no sistema. Válidos: {sorted(VEUS)}")
    if campo == "paper" and s.get("tema") == "escuro":
        sys.exit("ERRO: tela `escuro` com campo `paper` — o papel é o único campo claro.")
    if campo != "paper" and s.get("tema", "claro") == "claro" and "campo" in s:
        sys.exit("ERRO: tela `claro` só usa o campo `paper`.")
    return campo, veu


def render_slide(s, n, total, formato):
    campo, veu = campo_da_tela(s)
    extra = " capa" if s.get("capa") else ""
    extra += " fecho" if s.get("fecho") else ""
    extra += " story" if formato == "story" else ""
    classes = f"slide campo-{campo}{extra}"
    camada = f'<div class="veu veu-{veu}"></div>' if veu != "nenhum" else ""

    topo = linha(s.get("eyebrow_esq", ""), s.get("eyebrow_dir", ""))

    selo_html = ""
    if s.get("capa") or s.get("fecho"):
        cfg = s.get("selo") or {}
        if s.get("fecho"):
            padrao = ("Luca Martins", "Direito Tributário", "LM", True)
        else:
            padrao = (s.get("eyebrow_dir", ""), s.get("eyebrow_esq", ""), "§", True)
        selo_html = ('<div class="selo-placa">'
                     + selo(cfg.get("anel", padrao[0]), cfg.get("anel_inferior", padrao[1]),
                            cfg.get("marca", padrao[2]), 168,
                            cfg.get("anel_interno", padrao[3]))
                     + "</div>")

    corpo = "".join(render_bloco(b) for b in s["blocos"])
    # capa e fecho empurram o texto para a base, abaixo do selo; o resto centra
    alinhar = s.get("alinhar") or ("base" if (s.get("capa") or s.get("fecho")) else "centro")
    alinhar = {"topo": "", "centro": " centro", "base": " base"}.get(alinhar, "")

    # O board de aplicação — o que lista checagens — carrega o aviso.
    aviso = ""
    if any(b.get("tipo") == "numerada" for b in s["blocos"]):
        aviso = caps("Conteúdo informativo · não constitui consulta", "aviso")

    pag = f"{n:02d} / {total:02d}"
    if s.get("capa"):
        # No story não há "arrastar": o avanço é toque.
        esq = "Arraste" if formato == "feed" else "Luca Martins · Advogado"
    elif s.get("fecho"):
        esq = "Luca Martins · Advogado · OAB/RJ 274.439"
    else:
        esq = "Luca Martins · Advogado"

    return (f'<section class="{classes}">{camada}{topo}{selo_html}'
            f'<div class="miolo{alinhar}">{corpo}</div>'
            f'{aviso}{linha(esq, pag)}</section>')


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
        pg.wait_for_function("window.__selos === true", timeout=15000)
        pg.wait_for_timeout(200)
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
