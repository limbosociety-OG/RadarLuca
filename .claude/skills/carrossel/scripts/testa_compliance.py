#!/usr/bin/env python3
"""Prova que o gate morde. Roda sem rede e sem Playwright.

    python3 scripts/testa_compliance.py

Cada caso monta uma peça mínima em diretório temporário e afirma que o gate
reprova (ou aprova) pelo motivo certo. Um gate que ninguém testa é um gate que
degrada em silêncio — foi exatamente assim que a normalização do padrão passou.
"""
import copy
import datetime
import json
import pathlib
import re
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import compliance  # noqa: E402

HOJE = datetime.date(2026, 9, 1)
ONTEM = (HOJE - datetime.timedelta(days=2)).isoformat()

FECHO_OK = ("Conteúdo informativo, de caráter técnico, sem análise de caso concreto.\n"
            "Publicação nos termos do Provimento 205/2021 da OAB.")
LEGENDA_OK = ("O STF fixou a tese em 05/08/2026, sem modulação de efeitos.\n\n"
              "ARE 1.593.784/SC — Tema 1.455.\n\n" + FECHO_OK)


def ficha(**troca):
    base = {c: {"valor": v, "estado": "confirmado", "fonte": "portal.stf.jus.br",
                "data": ONTEM}
            for c, v in (("processo", "ARE 1.593.784/SC"), ("tema", "Tema 1.455 RG"),
                         ("julgamento", "05.08.2026"), ("modulacao", "ausente"))}
    for k, v in troca.items():
        base[k] = {**base.get(k, {}), **v} if v else base.get(k)
    return base


def roteiro(slides=None, **troca):
    r = {"peca": "teste", "verificacao": ficha(), "slides": slides or [
        {"tema": "escuro", "capa": True,
         "blocos": [{"tipo": "manchete", "texto": "Uma manchete qualquer."}]},
        {"tema": "escuro", "fecho": True, "blocos": [{"tipo": "mono", "texto": FECHO_OK}]},
    ]}
    r.update(troca)
    return r


def rodar(r, legenda=LEGENDA_OK):
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "roteiro.json"
        p.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        if legenda is not None:
            (p.parent / "legenda.md").write_text(legenda, encoding="utf-8")
        return compliance.checar(p, hoje=HOJE)


CASOS = []


def caso(nome):
    def reg(fn):
        CASOS.append((nome, fn))
        return fn
    return reg


def bloqueia(erros, agulha):
    assert any(agulha in e for e in erros), \
        f"esperava bloqueio com «{agulha}», veio: {erros or 'nada'}"


def passa(erros):
    assert not erros, f"esperava aprovação, veio: {erros}"


@caso("peça íntegra passa")
def _():
    passa(rodar(roteiro())[0])


@caso("captação: chamada para contato")
def _():
    r = roteiro()
    r["slides"][0]["blocos"][0]["texto"] = "Fale comigo para saber mais."
    bloqueia(rodar(r)[0], "captação de clientela")


@caso("captação: acento não escapa do léxico")
def _():
    r = roteiro()
    r["slides"][0]["blocos"][0]["texto"] = "Agende uma reunião hoje."
    bloqueia(rodar(r)[0], "captação de clientela")


@caso("captação na legenda também bloqueia")
def _():
    bloqueia(rodar(roteiro(), legenda="Procure um advogado.\n" + FECHO_OK)[0],
             "legenda")


@caso("legenda ausente bloqueia")
def _():
    bloqueia(rodar(roteiro(), legenda=None)[0], "legenda.md ausente")


@caso("legenda sem ressalva bloqueia")
def _():
    bloqueia(rodar(roteiro(), legenda="Só o fato, sem ressalva nenhuma.")[0],
             "sem a ressalva")


@caso("verificação não confirmada bloqueia")
def _():
    r = roteiro()
    r["verificacao"]["julgamento"]["estado"] = "nao_confirmado"
    bloqueia(rodar(r)[0], "só `confirmado` libera render")


@caso("verificação vencida bloqueia")
def _():
    r = roteiro()
    r["verificacao"]["processo"]["data"] = "2026-06-01"
    bloqueia(rodar(r)[0], "o teto é")


@caso("peça publicada mede a janela contra a publicação")
def _():
    r = roteiro(publicado_em="2026-06-05")
    for c in r["verificacao"].values():
        c["data"] = "2026-06-01"
    passa(rodar(r)[0])


@caso("modulação ausente da ficha bloqueia")
def _():
    r = roteiro()
    del r["verificacao"]["modulacao"]
    bloqueia(rodar(r)[0], "modulacao ausente")


@caso("processo citado fora da ficha bloqueia")
def _():
    r = roteiro()
    r["slides"][0]["blocos"][0]["texto"] = "Decisão no ARE 1.593.384/SC."
    bloqueia(rodar(r)[0], "não está na ficha de verificação")


@caso("tema divergente da ficha bloqueia")
def _():
    r = roteiro()
    r["slides"][0]["blocos"][0]["texto"] = "Julgado no Tema 1.445."
    bloqueia(rodar(r)[0], "divergente do tema da ficha")


@caso("fecho sem Provimento 205 bloqueia")
def _():
    r = roteiro()
    r["slides"][-1]["blocos"][0]["texto"] = "Conteúdo informativo."
    bloqueia(rodar(r)[0], "Provimento 205")


@caso("muleta retórica avisa, não bloqueia")
def _():
    r = roteiro()
    r["slides"][0]["blocos"][0]["texto"] = "Importante ressaltar que a tese é nova."
    erros, avisos = rodar(r)
    passa(erros)
    assert any("muleta" in a for a in avisos), avisos


@caso("padrão do léxico jamais é normalizado")
def _():
    for padrao, _ in compliance.CAPTACAO:
        assert padrao == padrao.lower() or not re.search(r"\\[SDWB]", padrao), padrao
        assert compliance.sem_acento(padrao) == padrao.lower(), padrao


def main():
    falhas = 0
    for nome, fn in CASOS:
        try:
            fn()
            print(f"  ok      {nome}")
        except AssertionError as e:
            falhas += 1
            print(f"  FALHOU  {nome}\n          {e}")
    print(f"\n{len(CASOS) - falhas}/{len(CASOS)} casos")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
