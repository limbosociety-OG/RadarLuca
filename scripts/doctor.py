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
MAGICOS_FONTE = (b"\x00\x01\x00\x00", b"true", b"ttcf", b"OTTO")

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

    if git("config", "core.hooksPath").strip() != ".githooks":
        erro("hook de pré-commit não instalado — `git add -f privado/…` passaria. "
             "Rode: sh scripts/instalar-hooks.sh")
    else:
        ok("hook de pré-commit ativo")

    cfg = RAIZ / ".claude" / "settings.json"
    if cfg.exists():
        d = json.loads(cfg.read_text(encoding="utf-8"))
        deny = d.get("permissions", {}).get("deny", [])
        for regra in ("Read(privado/**)", "Bash(git push:*)", "Bash(git add -f:*)"):
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
        aviso(f"`{nome}` instalada na conta é cópia antiga do mesmo sistema visual "
              f"de `{daqui}`. Some no feed, difere no processo: sem legenda no gate, "
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
    esperadas = ["BodoniModa.ttf", "BodoniModa-Italic.ttf", "Spectral-Regular.ttf",
                 "Spectral-SemiBold.ttf", "Spectral-Italic.ttf", "IBMPlexMono.ttf"]
    ruins = []
    for n in esperadas:
        f = d / n
        if not f.exists():
            ruins.append(f"{n}: ausente")
        elif f.stat().st_size < 20000 or f.read_bytes()[:4] not in MAGICOS_FONTE:
            ruins.append(f"{n}: arquivo inválido")
    if ruins:
        erro("fontes vendorizadas: " + "; ".join(ruins))
    else:
        ok(f"{len(esperadas)} fontes vendorizadas íntegras")


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


def main():
    for fn in (checar_sigilo, checar_skills, checar_derivados, checar_fontes,
               checar_pecas, checar_pendencias, checar_testes):
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
