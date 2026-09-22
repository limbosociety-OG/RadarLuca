#!/usr/bin/env python3
"""Fecha o ciclo do painel online: repositório → painel, depois de importado
o que foi editado nele.

    python3 scripts/sincronizar.py

A rotina diária roda, nesta ordem:

  1. lê o documento `painel/estado` do banco do Artifact (ArtifactData `get`)
     e, se ele existir, `python3 scripts/importar.py <arquivo> --aplicar`
     — ANTES do radar, porque a exclusão de tese só é segura contra a mesma
     versão do acervo de que o painel partiu;
  2. roda o radar (skill `radar`), que atualiza base/radar.json e base/teses.json;
  3. roda ESTE script: carimba a versão do acervo se algo em base/ mudou,
     regrava mapa e portal, gera portal/online.html e passa o doctor;
  4. commit e push no branch principal, republica o Artifact e, se o
     documento do banco não mudou desde a leitura do passo 1, apaga-o —
     o que ele tinha já está no repositório e na página nova.

A URL do painel e o branch principal ficam em `portal/online.json`.
"""
import datetime
import json
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TESES = RAIZ / "base" / "teses.json"
CONFIG = RAIZ / "portal" / "online.json"


def rodar(*args):
    r = subprocess.run([sys.executable, *map(str, args)], cwd=RAIZ,
                       capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
        sys.exit(f"ERRO: {' '.join(map(str, args))} falhou")
    return r.stdout


def base_mudou():
    r = subprocess.run(["git", "status", "--porcelain", "--", "base/"], cwd=RAIZ,
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def main():
    # clone novo não tem o hook, e o doctor reprova sem ele
    subprocess.run(["sh", "scripts/instalar-hooks.sh"], cwd=RAIZ, capture_output=True)
    if base_mudou():
        # A versão é a semente do painel: é por ela que a página sabe que o
        # repositório trouxe acervo novo. Carimbo com hora, porque a rotina
        # pode rodar mais de uma vez no mesmo dia.
        d = json.loads(TESES.read_text(encoding="utf-8"))
        d["versao"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
        TESES.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"acervo carimbado: versão {d['versao']}")
    else:
        print("base/ sem mudança: versão mantida")

    rodar("scripts/gerar.py")
    rodar("scripts/publicar.py", "--online")
    doc = subprocess.run([sys.executable, "scripts/doctor.py"], cwd=RAIZ,
                         capture_output=True, text=True)
    print(doc.stdout.strip().splitlines()[-1])
    if doc.returncode != 0:
        print(doc.stdout, file=sys.stderr)
        sys.exit("ERRO: doctor com bloqueio — não publicar nem commitar")

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    print(f"\npronto para publicar portal/online.html em {cfg['url']}")
    print(f"branch principal: {cfg['branch']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
