#!/usr/bin/env python3
"""Traz de volta para o repositório o que foi editado no painel.

    python3 scripts/importar.py ~/Downloads/radar-tributario-2026-09-02.json
    python3 scripts/importar.py <arquivo> --aplicar

O painel abre por file:// e não pode escrever em disco: ele exporta um JSON.
Este script fecha o ciclo — sem ele, anotação feita no painel vive só no
navegador e some ao limpar dados do site ou trocar de máquina.

Escreve em `base/teses.json` (teses — nova, editada, status, excluída —,
backlog, boletins) e em
`base/posfgv/aulas.json` (o caderno). Sem `--aplicar`, só mostra o que mudaria.
"""
import argparse
import collections
import datetime
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

    # 1. teses — o painel online edita, cria, muda status e exclui.
    # No painel o bloco vem pelo NOME e a fonte já resolvida em URL; aqui
    # voltam a id de bloco e ao atalho `@...` quando a URL é a do atalho.
    bloco_id = {b["nome"]: b["id"] for b in teses["blocos"]}
    atalho = {u: "@" + k for k, u in teses["atalhos_de_fonte"].items()}
    por_id = {t["id"]: t for t in teses["teses"]}
    CAMPOS = ("titulo", "tribunal", "tema", "status", "resumo", "edai", "fonte", "bloco")

    def do_painel(campo, v):
        v = v or ""
        if campo == "bloco":
            return bloco_id.get(v, v)
        if campo == "fonte":
            return atalho.get(v, v)
        return v

    vistos = set()
    for t in exp["teses"]:
        vistos.add(t.get("id"))
        alvo = por_id.get(t.get("id"))
        if alvo is None:
            bloco = do_painel("bloco", t.get("bloco"))
            if bloco not in bloco_id.values():
                bloco = teses["blocos"][0]["id"]
            nova = collections.OrderedDict(
                id=t["id"], bloco=bloco, tribunal=t.get("tribunal", ""),
                tema=t.get("tema", ""), processo=t.get("processo", ""),
                titulo=t.get("titulo", ""), resumo=t.get("resumo", ""),
                status=t.get("status", "curso"), placar=None,
                edai=t.get("edai", ""), fonte=do_painel("fonte", t.get("fonte")),
                verificacao="a_confirmar",
                verificado_em=t.get("verificadoEm") or t.get("verificado_em")
                or datetime.date.today().isoformat(),
                pendencia=t.get("pendencia") or "Criada no painel, sem checagem em fonte primária.")
            teses["teses"].append(nova)
            mudancas.append(("tese nova " + t["id"], "—", "—", corta(nova["titulo"])))
            continue
        for campo in CAMPOS:
            if campo not in t:
                continue
            v = do_painel(campo, t.get(campo))
            if v != (alvo.get(campo) or ""):
                mudancas.append(("tese " + t["id"], campo, corta(alvo.get(campo)), corta(v)))
                alvo[campo] = v

    # Exclusão só vale se o painel partiu da mesma versão do acervo: se o
    # repositório ganhou tese depois, ela não está no painel e não foi excluída.
    if exp.get("semente") == teses.get("versao"):
        for t in list(teses["teses"]):
            if t["id"] not in vistos:
                teses["teses"].remove(t)
                mudancas.append(("tese " + t["id"], "excluída", corta(t.get("titulo")), "—"))

    # 2. backlog e boletins, que também vivem no teses.json
    # o painel recebe o boletim com a fonte já resolvida; volta ao atalho
    for b in exp.get("boletins", []):
        if "fonte" in b:
            b["fonte"] = atalho.get(b["fonte"], b["fonte"])
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
