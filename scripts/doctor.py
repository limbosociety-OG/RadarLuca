#!/usr/bin/env python3
"""Confere o estado do repositório antes de confiar nele.

    python3 scripts/doctor.py

Sai 1 se houver bloqueio. Avisos não derrubam. Rode depois de clonar em máquina
nova, antes de publicar, e sempre que algo parecer fora do lugar.
"""
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
JANELA_PENDENCIA = 30       # dias antes de cobrar reverificação de uma tese
JANELA_RADAR = 14           # dias sem item novo antes de cobrar uma varredura
JANELA_TERMOMETRO = 7       # validade da medição do X; igual à do painel
MAGICOS_FONTE = (b"\x00\x01\x00\x00", b"true", b"ttcf", b"OTTO")
EM_CI = bool(os.environ.get("CI"))

erros, avisos, oks = [], [], []


def erro(m):
    erros.append(m)


def aviso(m):
    avisos.append(m)


def ok(m):
    oks.append(m)


def git(*a):
    try:
        return subprocess.run(["git", *a], cwd=RAIZ, capture_output=True,
                              text=True, timeout=20).stdout
    except Exception:
        return ""


# ------------------------------------------------------------------ 1. sigilo
def checar_sigilo():
    versionados = [l for l in git("ls-files").splitlines() if l.startswith("privado/")]
    if versionados:
        erro("privado/ está versionado: " + ", ".join(versionados[:5]))
    else:
        ok("privado/ fora do versionamento")

    gi = (RAIZ / ".gitignore").read_text(encoding="utf-8") if (RAIZ / ".gitignore").exists() else ""
    if "privado/" not in gi:
        erro(".gitignore não cobre privado/")

    hook = RAIZ / ".githooks" / "pre-commit"
    if not hook.exists():
        erro(".githooks/pre-commit não existe — a trava de sigilo sumiu do repositório")
    elif EM_CI:
        # Em CI não há clone de trabalho para proteger: o que importa é o hook
        # existir no repositório, e o próprio workflow refaz a checagem de sigilo.
        ok(".githooks/pre-commit versionado (CI: não se cobra instalação local)")
    elif git("config", "core.hooksPath").strip() != ".githooks":
        erro("hook de pré-commit não instalado neste clone — `git add -f privado/…` "
             "passaria. Rode: sh scripts/instalar-hooks.sh")
    else:
        ok("hook de pré-commit ativo")

    cfg = RAIZ / ".claude" / "settings.json"
    if cfg.exists():
        try:
            d = json.loads(cfg.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            # JSON torto aqui não é detalhe: o Claude Code pode descartar o bloco
            # inteiro de permissões, e aí some junto o deny de Read(privado/**).
            erro(f"settings.json não é JSON válido ({e}) — com ele quebrado, as regras "
                 f"de permissão podem não valer nenhuma. Vírgula sobrando antes de `]` "
                 f"é a causa mais comum ao remover uma linha.")
            return
        deny = d.get("permissions", {}).get("deny", [])
        # `Bash(git push:*)` saiu do deny por decisão consciente sobre o remoto,
        # conforme o README. Não é regra faltando; não cobrar.
        for regra in ("Read(privado/**)", "Bash(git add -f:*)"):
            if regra not in deny:
                aviso(f"settings.json sem a regra de deny `{regra}`")


# ------------------------------------------------------------------ 2. skills
def checar_skills():
    """Mais de uma skill de carrossel no ambiente é situação normal aqui: são
    identidades visuais diferentes, e a escolha é editorial. O que este check
    faz é dizer qual vale DENTRO deste repositório, e apontar cópia antiga do
    mesmo sistema — que é o caso perigoso, porque as duas se parecem."""
    nossa = RAIZ / ".claude" / "skills"
    nomes_locais = set()
    for s in sorted(nossa.glob("*/SKILL.md")):
        m = re.search(r"^name:\s*(\S+)", s.read_text(encoding="utf-8"), re.M)
        nome = m.group(1) if m else s.parent.name
        nomes_locais.add(nome)
        if nome != s.parent.name:
            erro(f"skill {s.parent.name}: frontmatter diz `name: {nome}` — "
                 f"nome e diretório precisam bater, senão colide com skill instalada")
    ok(f"skills deste repositório (as que valem aqui): {', '.join(sorted(nomes_locais))}")

    # Cópia antiga do MESMO sistema visual do repositório. Perigosa justamente
    # por ser parecida: a peça sai quase igual, sem gate novo e sem ficha com prazo.
    COPIA_ANTIGA = {"carrossel-tributario": "carrossel", "radar-juridico": "radar"}
    # Identidade visual diferente, que existe de propósito e não se mexe daqui.
    OUTRA_IDENTIDADE = {
        "producao-carrossel": "Moody Blue #21324C + off-white, Cormorant Garamond / "
                              "Italiana / Instrument, seis batidas",
    }

    copias, outras = [], []
    for base in (pathlib.Path.home() / ".claude" / "skills",
                 pathlib.Path.home() / ".claude" / "plugins"):
        if not base.exists():
            continue
        for s in base.glob("**/SKILL.md"):
            nome = s.parent.name
            if nome in COPIA_ANTIGA:
                copias.append((nome, COPIA_ANTIGA[nome]))
            elif nome in OUTRA_IDENTIDADE:
                outras.append((nome, OUTRA_IDENTIDADE[nome]))

    for nome, daqui in sorted(set(copias)):
        aviso(f"`{nome}` instalada na conta é cópia antiga de `{daqui}`, "
              f"fora do Obsidian Chrome: sem legenda no gate, "
              f"sem prazo de validade na ficha, sem fontes versionadas. "
              f"Neste repositório vale `{daqui}` — peça no chat pelo nome.")
    for nome, ident in sorted(set(outras)):
        ok(f"`{nome}` no ambiente: outra identidade ({ident}). "
           f"Coexiste de propósito — não é para remover, e não é a deste projeto.")


# ------------------------------------------------------------------ 3. derivados
def checar_derivados():
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "gerar.py"), "--check"],
                       cwd=RAIZ, capture_output=True, text=True)
    if r.returncode != 0:
        erro("mapa e portal desatualizados em relação a base/teses.json — "
             "rode `python3 scripts/gerar.py`")
    else:
        ok("mapa e portal em dia com base/teses.json")


# ------------------------------------------------------------------ 4. fontes
def checar_fontes():
    d = RAIZ / ".claude" / "skills" / "carrossel" / "assets" / "fonts"
    # Obsidian Chrome (design/obsidian-chrome): Jost, Poppins, Archivo, Cormorant.
    esperadas = ["Jost.ttf", "Poppins-Medium.ttf", "Poppins-SemiBold.ttf",
                 "Archivo.ttf", "Archivo-Italic.ttf", "CormorantGaramond.ttf"]
    ruins = []
    for n in esperadas:
        f = d / n
        if not f.exists():
            ruins.append(f"{n}: ausente")
        elif f.stat().st_size < 20000 or f.read_bytes()[:4] not in MAGICOS_FONTE:
            ruins.append(f"{n}: arquivo inválido")
    if ruins:
        erro("fontes do carrossel: " + "; ".join(ruins))
    else:
        ok(f"{len(esperadas)} fontes do carrossel íntegras")

    # O painel também não busca fonte na rede: as woff2 são embutidas por gerar.py.
    pf = RAIZ / "portal" / "assets" / "fonts"
    faltam = [n for n in ("Jost.woff2", "Archivo.woff2", "Poppins-Medium.woff2",
                          "Poppins-SemiBold.woff2", "CormorantGaramond-LM.woff2")
              if not (pf / n).exists() or (pf / n).read_bytes()[:4] != b"wOF2"]
    if faltam:
        erro("fontes do painel ausentes ou inválidas: " + ", ".join(faltam))
    else:
        ok("5 fontes do painel vendorizadas, o painel não busca nada na rede")

    html = (RAIZ / "portal" / "radar.html").read_text(encoding="utf-8")
    if "fonts.googleapis" in html or "fonts.gstatic" in html:
        erro("o painel voltou a referenciar o CDN de fontes — offline ele cai para "
             "fonte de sistema")


# ------------------------------------------------------------------ 5. peças
def checar_pecas():
    gate = RAIZ / ".claude" / "skills" / "carrossel" / "scripts" / "compliance.py"
    pastas = sorted(p for p in (RAIZ / "pecas").glob("*") if p.is_dir())
    if not pastas:
        aviso("nenhuma peça em pecas/")
        return
    for p in pastas:
        rot = p / "roteiro.json"
        if not rot.exists():
            erro(f"{p.name}: sem roteiro.json")
            continue
        r = subprocess.run([sys.executable, str(gate), str(rot)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            erro(f"{p.name}: compliance reprovado\n      "
                 + "\n      ".join(l for l in r.stdout.splitlines() if l.strip()))
        else:
            ok(f"{p.name}: compliance aprovado")
        for img in sorted((p / "png").glob("*.png")):
            if img.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
                aviso(f"{p.name}/png/{img.name}: extensão .png mas o arquivo é outro "
                      f"formato (JPEG recomprime o grão do fundo escuro e cria banda)")


# ------------------------------------------------------------------ 6. pendências
def checar_pendencias():
    d = json.loads((RAIZ / "base" / "teses.json").read_text(encoding="utf-8"))
    hoje = datetime.date.today()
    velhas = []
    for t in d["teses"]:
        if t["verificacao"] == "confirmado":
            continue
        idade = (hoje - datetime.date.fromisoformat(t["verificado_em"])).days
        if idade > JANELA_PENDENCIA:
            velhas.append(f"{t['tema']} ({idade}d)")
    naoconf = sum(1 for t in d["teses"] if t["verificacao"] != "confirmado")
    if velhas:
        aviso(f"{len(velhas)} teses `a confirmar` há mais de {JANELA_PENDENCIA} dias: "
              + ", ".join(velhas[:8]) + ("…" if len(velhas) > 8 else ""))
    ok(f"{len(d['teses'])} teses no acervo, {naoconf} marcadas `a confirmar`")


# ------------------------------------------------------------------ 6b. radar
def checar_radar():
    """A camada de notícia envelhece mais rápido que a de teses. Painel de radar
    parado é pior que painel vazio: passa a impressão de que nada se moveu."""
    r = json.loads((RAIZ / "base" / "radar.json").read_text(encoding="utf-8"))
    hoje = datetime.date.today()

    itens = r.get("itens", [])
    if not itens:
        aviso("base/radar.json sem itens — a linha do tempo do painel abre vazia. "
              "Peça `radar` no chat.")
    else:
        ultimo = max(datetime.date.fromisoformat(i["data"]) for i in itens)
        idade = (hoje - ultimo).days
        naoconf = sum(1 for i in itens if i.get("verificacao") != "confirmado")
        if idade > JANELA_RADAR:
            aviso(f"último item do radar é de {ultimo} ({idade} dias). "
                  f"Rode o radar antes de tratar o painel como atual.")
        ok(f"{len(itens)} itens no radar, o mais recente de {ultimo} "
           f"({naoconf} a confirmar)")

    term = r.get("termometro") or {}
    if not term.get("medido_em"):
        ok("termômetro do X sem medição — o painel diz isso na cara, que é a resposta "
           "certa quando não há reação verificável")
    else:
        idade = (hoje - datetime.date.fromisoformat(term["medido_em"])).days
        if idade > JANELA_TERMOMETRO:
            aviso(f"termômetro do X medido há {idade} dias "
                  f"(teto de {JANELA_TERMOMETRO}) — o painel já o mostra como histórico")
        else:
            ok(f"termômetro do X medido há {idade} dias, dentro da validade")


# ------------------------------------------------------------------ 7. testes
def checar_testes():
    t = RAIZ / ".claude" / "skills" / "carrossel" / "scripts" / "testa_compliance.py"
    if not t.exists():
        aviso("sem suíte de teste do gate")
        return
    r = subprocess.run([sys.executable, str(t)], capture_output=True, text=True)
    if r.returncode != 0:
        erro("suíte do gate de compliance falhando:\n      "
             + "\n      ".join(l for l in r.stdout.splitlines() if "FALHOU" in l))
    else:
        ok(r.stdout.strip().splitlines()[-1] + " no gate de compliance")


# ------------------------------------------------------------------ 4b. sistema visual
def checar_sistema():
    """O template do carrossel carrega cópia dos tokens do Obsidian Chrome, porque
    o build embute tudo num HTML só. Cópia diverge em silêncio: aqui ela é
    conferida, token a token, contra design/obsidian-chrome/tokens/."""
    ds = RAIZ / "design" / "obsidian-chrome" / "tokens"
    tpl = RAIZ / ".claude" / "skills" / "carrossel" / "assets" / "template.html"
    if not ds.is_dir():
        erro("design/obsidian-chrome/ ausente — o sistema visual travado não está no repositório")
        return
    decl = re.compile(r"(--[a-z0-9-]+)\s*:\s*([^;]+);")
    fonte = {}
    for css in ("palette.css", "fields.css", "type.css"):
        for k, v in decl.findall((ds / css).read_text(encoding="utf-8")):
            fonte[k] = " ".join(v.split("/*")[0].split())
    copia = {k: " ".join(v.split()) for k, v in decl.findall(tpl.read_text(encoding="utf-8"))}
    diverge = sorted(k for k in copia if k in fonte and copia[k] != fonte[k])
    if diverge:
        erro("template do carrossel diverge de design/obsidian-chrome nos tokens: "
             + ", ".join(diverge))
    else:
        ok(f"template do carrossel em dia com o Obsidian Chrome "
           f"({sum(1 for k in copia if k in fonte)} tokens conferidos)")


def main():
    for fn in (checar_sigilo, checar_skills, checar_derivados, checar_fontes,
               checar_sistema, checar_pecas, checar_pendencias, checar_radar, checar_testes):
        try:
            fn()
        except Exception as e:  # um check quebrado não pode esconder os outros
            erro(f"{fn.__name__} quebrou: {type(e).__name__}: {e}")

    print("RADAR TRIBUTÁRIO — diagnóstico\n")
    for m in oks:
        print(f"  ok      {m}")
    for m in avisos:
        print(f"  aviso   {m}")
    for m in erros:
        print(f"  ✗       {m}")
    print()
    if erros:
        print(f"{len(erros)} bloqueio(s), {len(avisos)} aviso(s).")
        return 1
    print(f"sem bloqueios, {len(avisos)} aviso(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
