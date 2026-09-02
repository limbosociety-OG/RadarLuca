#!/usr/bin/env python3
"""Gera o acervo derivado a partir de `base/teses.json`.

    python3 scripts/gerar.py            # regrava os arquivos derivados
    python3 scripts/gerar.py --check    # não escreve; sai 1 se estiver desatualizado

Derivados:
  base/mapa-de-teses.md          — o mapa em prosa, para leitura e para o Claude
  portal/radar-tributario.html   — a semente do painel, entre marcadores

O arquivo-fonte é `base/teses.json`. Editar um derivado à mão é trabalho perdido:
a próxima geração sobrescreve.
"""
import argparse
import base64
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FONTE = RAIZ / "base" / "teses.json"
FONTE_RADAR = RAIZ / "base" / "radar.json"
FONTE_AULAS = RAIZ / "base" / "posfgv" / "aulas.json"
MAPA = RAIZ / "base" / "mapa-de-teses.md"
PORTAL = RAIZ / "portal" / "radar-tributario.html"

FONTES_DIR = RAIZ / "portal" / "assets" / "fonts"
F_ABRE = "/* FONTES:INICIO — geradas de portal/assets/fonts por scripts/gerar.py */"
F_FECHA = "/* FONTES:FIM */"

ABRE = "/* GERADO:INICIO — não editar à mão. Fonte: base/teses.json (scripts/gerar.py) */"
FECHA = "/* GERADO:FIM */"

SINAL = {"iminente": "🔴", "curso": "🟡", "fixada": "🟢", "afetado": "⚪"}
ROTULO = {"iminente": "janela aberta", "curso": "em curso",
          "fixada": "tese fixada", "afetado": "afetado"}
MES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def carregar():
    d = json.loads(FONTE.read_text(encoding="utf-8"))
    validar(d)
    r = json.loads(FONTE_RADAR.read_text(encoding="utf-8"))
    validar_radar(r, d)
    a = json.loads(FONTE_AULAS.read_text(encoding="utf-8"))
    ids = {t["id"] for t in d["teses"]}
    ruins = [f"{au.get('id','?')} → {i}" for au in a["aulas"]
             for i in au.get("teses", []) if i not in ids]
    if ruins:
        sys.exit("base/posfgv/aulas.json aponta para tese inexistente: " + ", ".join(ruins))
    return d, r, a


def validar(d):
    """Falha cedo e alto: dado torto aqui contamina mapa e portal de uma vez."""
    erros = []
    ids_bloco = {b["id"] for b in d["blocos"]}
    vistos = set()
    for t in d["teses"]:
        onde = f"tese {t.get('id', '?')}"
        if t["id"] in vistos:
            erros.append(f"{onde}: id repetido")
        vistos.add(t["id"])
        if t["bloco"] not in ids_bloco:
            erros.append(f"{onde}: bloco `{t['bloco']}` não existe")
        if t["status"] not in SINAL:
            erros.append(f"{onde}: status `{t['status']}` inválido")
        if t.get("verificacao") not in ("confirmado", "a_confirmar"):
            erros.append(f"{onde}: verificacao precisa ser `confirmado` ou `a_confirmar`")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", t.get("verificado_em", "")):
            erros.append(f"{onde}: verificado_em ausente ou fora de AAAA-MM-DD")
        if t.get("verificacao") == "a_confirmar" and not t.get("pendencia"):
            erros.append(f"{onde}: marcada `a_confirmar` sem dizer o que falta confirmar")
        f = t.get("fonte", "")
        if f.startswith("@") and f[1:] not in d["atalhos_de_fonte"]:
            erros.append(f"{onde}: atalho de fonte `{f}` não existe")
        pz = t.get("prazo")
        if pz:
            if pz.get("tipo") not in ("data_certa", "rolante"):
                erros.append(f"{onde}: prazo.tipo precisa ser `data_certa` ou `rolante`")
            if pz.get("tipo") == "data_certa" and not re.fullmatch(
                    r"\d{4}-\d{2}-\d{2}", pz.get("data") or ""):
                erros.append(f"{onde}: prazo de data certa sem data em AAAA-MM-DD")
            if not pz.get("oque"):
                erros.append(f"{onde}: prazo sem dizer o que vence")
    if erros:
        print("base/teses.json inválido:\n", file=sys.stderr)
        for e in erros:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)


def validar_radar(r, d):
    """A camada de notícia tem a mesma régua da de teses: item sem consequência
    prática não entra, e o que não foi confirmado se declara."""
    erros = []
    ids_tese = {t["id"] for t in d["teses"]}
    vistos = set()
    for it in r["itens"]:
        onde = f"radar {it.get('id', '?')}"
        if it["id"] in vistos:
            erros.append(f"{onde}: id repetido")
        vistos.add(it["id"])
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", it.get("data", "")):
            erros.append(f"{onde}: data ausente ou fora de AAAA-MM-DD")
        if not it.get("edai"):
            erros.append(f"{onde}: sem `e daí?` — notícia sem consequência prática "
                         f"não entra no radar, vira clipping")
        if it.get("verificacao") not in ("confirmado", "a_confirmar"):
            erros.append(f"{onde}: verificacao precisa ser `confirmado` ou `a_confirmar`")
        if it.get("verificacao") == "a_confirmar" and not it.get("pendencia"):
            erros.append(f"{onde}: `a_confirmar` sem dizer o que falta")
        if it.get("tese") and it["tese"] not in ids_tese:
            erros.append(f"{onde}: aponta para tese `{it['tese']}`, que não existe")
        f = it.get("fonte", "")
        if f.startswith("@") and f[1:] not in d["atalhos_de_fonte"]:
            erros.append(f"{onde}: atalho de fonte `{f}` não existe")

    term = r.get("termometro") or {}
    if term.get("assuntos") and not term.get("medido_em"):
        erros.append("termometro: tem assunto e não tem `medido_em`. Medição sem data "
                     "não é medição — o painel precisa poder envelhecer o dado à vista")
    for a in term.get("assuntos", []):
        if a.get("tese") and a["tese"] not in ids_tese:
            erros.append(f"termometro «{a.get('assunto','?')}»: tese inexistente")

    if erros:
        print("base/radar.json inválido:\n", file=sys.stderr)
        for e in erros:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)


def url(d, f):
    return d["atalhos_de_fonte"][f[1:]] if f.startswith("@") else f


def mes_ano(iso):
    a, m, _ = iso.split("-")
    return f"{MES[int(m) - 1]}/{a}"


# ------------------------------------------------------------------ mapa .md
def gerar_mapa(d):
    L = [f"<!-- GERADO por scripts/gerar.py a partir de base/teses.json. Não editar à mão. -->",
         "", "# Mapa de Teses", "",
         f"**Corte:** {d['corte']} · **versão:** {d['versao']}", "",
         d["preambulo"], "",
         "**Legenda de status:** 🔴 julgamento iminente ou janela fechando · 🟡 em curso, "
         "sem data · 🟢 tese fixada · ⚪ afetado, aguardando", "",
         "**Legenda de verificação:** ✅ confirmado em fonte primária, com data · "
         "⚠️ a confirmar — não usar em peça, boletim ou parecer.", "", "---", ""]

    for i, b in enumerate(d["blocos"], 1):
        doBloco = [t for t in d["teses"] if t["bloco"] == b["id"]]
        if not doBloco:
            continue
        L += [f"## {i}. {b['titulo']}", ""]
        if b.get("nota"):
            L += [b["nota"], ""]
        L += ["| | Tema | Objeto | Situação |", "|---|---|---|---|"]
        for t in doBloco:
            marca = "✅" if t["verificacao"] == "confirmado" else "⚠️"
            proc = t.get("processo", "")
            ref = f"**{t['tema']}**" + (f" ({proc})" if proc and proc != t["tema"] else "")
            sit = t["resumo"].replace("\n", " ")
            L.append(f"| {SINAL[t['status']]}{marca} | {t['tribunal']} — {ref} "
                     f"| {t['titulo']} | {sit} |")
        L.append("")
        for t in doBloco:
            if t.get("edai"):
                L += [f"**{t['tema']} — e daí?** {t['edai']}", ""]
        for t in doBloco:
            if t["verificacao"] != "confirmado":
                L += [f"> ⚠️ **{t['tema']}** — a confirmar: {t['pendencia']} "
                      f"(última checagem: {t['verificado_em']})", ""]
        if b.get("acao"):
            L += [f"**Ponto de ação.** {b['acao']}", ""]
        L += ["---", ""]

    L += ["## Fontes de monitoramento", "",
          "**Primárias:** " + " · ".join(d["fontes_monitoramento"]["primarias"]) + ".", "",
          "**Secundárias:** " + " · ".join(d["fontes_monitoramento"]["secundarias"]) + ".",
          "", "---", "", "## Backlog de estudo", ""]
    for n, e in enumerate(d["backlog"], 1):
        L.append(f"{n}. {'~~' + e['txt'] + '~~' if e['feito'] else e['txt']}")
    L += ["", "---", "",
          "## Como este arquivo se atualiza", "",
          "Ele não se edita: edita-se `base/teses.json` e roda-se `python3 scripts/gerar.py`.",
          "O mesmo comando regrava a semente do painel em `portal/radar-tributario.html`,",
          "e é isso que impede o mapa e o portal de divergirem.", ""]
    return "\n".join(L)


# ------------------------------------------------------------------ semente do portal
def gerar_semente(d, r, a):
    nome = {b["id"]: b["nome"] for b in d["blocos"]}
    teses = [{
        "id": t["id"], "bloco": nome[t["bloco"]], "tribunal": t["tribunal"],
        "tema": t["tema"], "processo": t.get("processo", ""), "status": t["status"],
        "titulo": t["titulo"], "resumo": t["resumo"], "fonte": url(d, t.get("fonte", "")),
        "placar": t.get("placar"), "placarNota": t.get("placarNota", ""),
        "edai": t.get("edai", ""), "verificacao": t["verificacao"],
        "prazo": t.get("prazo"),
        "pendencia": t.get("pendencia", ""), "verificadoEm": t["verificado_em"],
        "atualizado": mes_ano(t["verificado_em"]),
    } for t in d["teses"]]

    padrao = {
        "semente": d["versao"],
        "teses": teses,
        "boletins": [{**b, "fonte": url(d, b.get("fonte", ""))} for b in d["boletins"]],
        "aulas": a["aulas"],
        "backlog": d["backlog"],
        "radar": [{**it, "fonte": url(d, it.get("fonte", ""))} for it in r["itens"]],
        "termometro": r["termometro"],
    }
    j = lambda o: json.dumps(o, ensure_ascii=False, indent=1)
    return "\n".join([
        ABRE,
        f"const SEMENTE={json.dumps(d['versao'])};",
        f"const CORTE={json.dumps(d['corte'])};",
        f"const BLOCOS={j([b['nome'] for b in d['blocos']])};",
        f"const PADRAO={j(padrao)};",
        f"const FONTES_FIXAS={j(d['fontes_fixas'])};",
        f"const TRANSICAO={j(d['transicao'])};",
        FECHA,
    ])


# O painel não busca fonte na rede. Era a única dependência externa que sobrava,
# e num arquivo aberto do disco ela significa cair para fonte de sistema offline.
# A folha do painel pede `font-stretch:88%` e `92%` no wordmark e nos títulos.
# Sem o descritor de largura, o navegador entende que a face só cobre 100% e
# cai para fallback em silêncio — que é o modo como uma fonte some sem erro.
FACES = [
    ("Bricolage Grotesque", "BricolageGrotesque.woff2", "400 800", "normal", "85% 100%"),
    ("Spectral", "Spectral-Regular.woff2", "400", "normal", None),
    ("Spectral", "Spectral-SemiBold.woff2", "600", "normal", None),
    ("Spectral", "Spectral-Italic.woff2", "400", "italic", None),
    ("IBM Plex Mono", "IBMPlexMono.woff2", "400 600", "normal", None),
]


def gerar_fontes():
    linhas = [F_ABRE]
    for fam, arq, peso, estilo, largura in FACES:
        f = FONTES_DIR / arq
        if not f.exists():
            sys.exit(f"ERRO: fonte do painel ausente: {f}")
        b64 = base64.b64encode(f.read_bytes()).decode()
        larg = f"font-stretch:{largura};" if largura else ""
        linhas.append(f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,"
                      f"{b64}) format('woff2');font-weight:{peso};font-style:{estilo};"
                      f"{larg}font-display:swap}}")
    linhas.append(F_FECHA)
    return "\n".join(linhas)


def injetar_entre(html, abre, fecha, conteudo, oque):
    if abre not in html or fecha not in html:
        sys.exit(f"ERRO: marcadores de {oque} ausentes em {PORTAL}")
    i, f = html.index(abre), html.index(fecha) + len(fecha)
    return html[:i] + conteudo + html[f:]


def injetar(html, semente):
    return injetar_entre(html, ABRE, FECHA, semente, "dados")


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="não escreve; sai 1 se algum derivado estiver desatualizado")
    a = ap.parse_args()

    d, r, au = carregar()
    saidas = {
        MAPA: gerar_mapa(d),
        PORTAL: injetar(injetar_entre(PORTAL.read_text(encoding="utf-8"),
                                      F_ABRE, F_FECHA, gerar_fontes(), "fontes"),
                        gerar_semente(d, r, au)),
    }

    if a.check:
        velhos = [p for p, novo in saidas.items()
                  if not p.exists() or p.read_text(encoding="utf-8") != novo]
        if velhos:
            print("Derivados desatualizados em relação a base/teses.json:", file=sys.stderr)
            for p in velhos:
                print(f"  ✗ {p.relative_to(RAIZ)}", file=sys.stderr)
            print("\nRode: python3 scripts/gerar.py", file=sys.stderr)
            return 1
        print("derivados em dia")
        return 0

    for p, novo in saidas.items():
        p.write_text(novo, encoding="utf-8")
        print(f"escrito {p.relative_to(RAIZ)}")
    naoconf = sum(1 for t in d["teses"] if t["verificacao"] != "confirmado")
    med = (r.get("termometro") or {}).get("medido_em") or "nunca medido"
    print(f"{len(d['teses'])} teses · {naoconf} marcadas `a confirmar` · "
          f"{len(r['itens'])} itens no radar · {len(au['aulas'])} aulas · "
          f"termômetro: {med}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
