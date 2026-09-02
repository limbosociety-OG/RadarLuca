#!/usr/bin/env python3
"""Traz de volta para o repositório o que foi editado no painel.

    python3 scripts/importar.py ~/Downloads/radar-tributario-2026-09-02.json
    python3 scripts/importar.py <arquivo> --aplicar

O painel abre por file:// e não pode escrever em disco: ele exporta um JSON.
Este script fecha o ciclo — sem ele, anotação feita no painel vive só no
navegador e some ao limpar dados do site ou trocar de máquina.

Escreve em `base/teses.json` (edai, backlog, boletins) e em
`base/posfgv/aulas.json` (o caderno). Sem `--aplicar`, só mostra o que mudaria.
"""
import argparse
import collections
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TESES = RAIZ / "base" / "teses.json"
AULAS = RAIZ / "base" / "posfgv" / "aulas.json"


def ler(p):
    return json.loads(p.read_text(encoding="utf-8"),
                      object_pairs_hook=collections.OrderedDict)


def gravar(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def corta(s, n=68):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1] + "…"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", help="o json exportado pelo painel")
    ap.add_argument("--aplicar", action="store_true",
                    help="sem isto, só mostra o que mudaria")
    a = ap.parse_args()

    exp = ler(pathlib.Path(a.arquivo))
    if "teses" not in exp:
        sys.exit("Esse arquivo não tem o formato do painel. Use o botão `exportar json`.")

    teses, aulas = ler(TESES), ler(AULAS)
    mudancas = []

    # 1. "e daí?" — o campo que é editável no painel e gerado do teses.json
    por_id = {t["id"]: t for t in teses["teses"]}
    for t in exp["teses"]:
        alvo = por_id.get(t.get("id"))
        if alvo and (t.get("edai") or "") != (alvo.get("edai") or ""):
            mudancas.append(("tese " + t["id"], "edai", corta(alvo.get("edai")),
                             corta(t.get("edai"))))
            alvo["edai"] = t.get("edai", "")

    # 2. backlog e boletins, que também vivem no teses.json
    for chave in ("backlog", "boletins"):
        antes = json.dumps(teses.get(chave), ensure_ascii=False, sort_keys=True)
        depois = json.dumps(exp.get(chave, teses.get(chave)), ensure_ascii=False,
                            sort_keys=True)
        if antes != depois:
            n_a, n_d = len(teses.get(chave, [])), len(exp.get(chave, []))
            mudancas.append((chave, "lista", f"{n_a} itens", f"{n_d} itens"))
            teses[chave] = exp[chave]

    # 3. o caderno da pós, que é o que mais dói perder
    antes = {x["id"]: x for x in aulas["aulas"]}
    depois = exp.get("aulas", [])
    novas = [x for x in depois if x["id"] not in antes]
    editadas = [x for x in depois if x["id"] in antes
                and json.dumps(x, ensure_ascii=False, sort_keys=True)
                != json.dumps(antes[x["id"]], ensure_ascii=False, sort_keys=True)]
    for x in novas:
        mudancas.append(("aula nova", x.get("data", "?"), "—", corta(x.get("titulo"))))
    for x in editadas:
        mudancas.append(("aula " + x["id"], x.get("data", "?"), "editada",
                         corta(x.get("titulo"))))
    if novas or editadas:
        aulas["aulas"] = depois

    if not mudancas:
        print("Nada a importar: o painel está igual ao repositório.")
        return 0

    print(f"{len(mudancas)} alteração(ões) do painel:\n")
    for onde, campo, antes_v, depois_v in mudancas:
        print(f"  {onde} · {campo}")
        print(f"      antes:  {antes_v}")
        print(f"      depois: {depois_v}")

    if not a.aplicar:
        print("\nNada foi escrito. Para aplicar:")
        print(f"  python3 scripts/importar.py {a.arquivo} --aplicar")
        return 0

    gravar(TESES, teses)
    gravar(AULAS, aulas)
    print(f"\nEscrito em {TESES.relative_to(RAIZ)} e {AULAS.relative_to(RAIZ)}.")
    print("Agora rode: python3 scripts/gerar.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
