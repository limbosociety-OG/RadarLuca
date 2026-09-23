#!/usr/bin/env python3
"""Acompanhamento dos processos de carteira — busca sozinha, grava só no disco.

    python3 scripts/processos.py --adicionar 0000000-00.0000.8.19.0001 [...]
    python3 scripts/processos.py              # busca e regrava o painel
    python3 scripts/processos.py --agenda     # imprime a linha do cron

Duas fontes públicas, sem credencial pessoal:

  * DJEN (comunicaapi.pje.jus.br) — o Diário de Justiça Eletrônico Nacional.
    Busca por OAB e por número de processo. É INTIMAÇÃO: abre prazo. Processo
    em que você for intimado e que não estiver na lista entra sozinho.
  * DataJud (api-publica.datajud.cnj.jus.br) — metadados e movimentação.
    É MOVIMENTAÇÃO: chega com dias de atraso e não abre prazo. Serve de contexto.

O painel mostra as duas separadas, porque confundir uma com a outra é o erro
que não se repete. O script não calcula prazo: contagem tem três famílias e
depende do ato. Prazo contado vai para `privado/prazos.js`.

Tudo o que este script lê e escreve fica em `privado/`, que não é versionado,
é barrado pelo hook de pré-commit e não entra em variante publicável:

  privado/processos.json        a lista (você edita, ou usa --adicionar)
  privado/processos-cache.json  o histórico acumulado de intimações
  privado/processos.js          o que o painel do disco lê (<script src>)

Roda na sua máquina, não na rotina da nuvem: a rotina não tem `privado/` e
não deve ter. A automação é o cron local (`--agenda`).
"""
import argparse
import datetime
import html
import json
import os
import pathlib
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
# RADAR_PRIVADO só existe para teste; em uso, é sempre privado/ do repositório
PRIVADO = pathlib.Path(os.environ.get("RADAR_PRIVADO") or RAIZ / "privado")
LISTA = PRIVADO / "processos.json"
CACHE = PRIVADO / "processos-cache.json"
SAIDA = PRIVADO / "processos.js"

DJEN = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
DATAJUD = "https://api-publica.datajud.cnj.jus.br/api_publica_{alias}/_search"
# Chave PÚBLICA do DataJud, divulgada pelo CNJ na wiki da API
# (datajud-wiki.cnj.jus.br/api-publica/acesso). O CNJ troca de tempos em tempos:
# se o DataJud começar a responder 401, pegue a nova lá e ponha em
# privado/processos.json, campo "datajud_chave".
CHAVE_DATAJUD = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="

JANELA_PRIMEIRA = 90     # dias de DJEN na primeira busca
SOBREPOSICAO = 5         # dias de folga em cada busca seguinte
NOVA_HORAS = 72          # intimação capturada há menos disso aparece como nova
MOVIMENTOS = 20          # movimentos por processo no painel
TEXTO_MAX = 2500         # caracteres do teor da intimação guardados

UF_TJ = {"01": "ac", "02": "al", "03": "ap", "04": "am", "05": "ba", "06": "ce",
         "07": "dft", "08": "es", "09": "go", "10": "ma", "11": "mt", "12": "ms",
         "13": "mg", "14": "pa", "15": "pb", "16": "pr", "17": "pe", "18": "pi",
         "19": "rj", "20": "rn", "21": "rs", "22": "ro", "23": "rr", "24": "sc",
         "25": "se", "26": "sp", "27": "to"}

MODELO = {
    "_leia": "Carteira. Fica em privado/, nunca entra em commit. "
             "Campos por processo: numero (obrigatório), apelido, notas.",
    "oab": {"numero": "274439", "uf": "RJ"},
    "processos": [],
}


# ------------------------------------------------------------------ número CNJ
def digitos(n):
    return re.sub(r"\D", "", n or "")


def mascara(n):
    d = digitos(n)
    if len(d) != 20:
        return n
    return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:]}"


def dv_confere(n):
    """Dígito verificador da Resolução CNJ 65/2008 (módulo 97)."""
    d = digitos(n)
    if len(d) != 20:
        return False
    base = int(d[:7] + d[9:] + "00")
    return 98 - base % 97 == int(d[7:9])


def alias_datajud(n):
    d = digitos(n)
    j, tr = d[13], d[14:16]
    if j == "8":
        return "tj" + UF_TJ[tr] if tr in UF_TJ else None
    if j == "4":
        return f"trf{int(tr)}" if tr != "90" else None
    if j == "5":
        return f"trt{int(tr)}"
    if j == "3":
        return "stj"
    return None


def sigla(n):
    a = alias_datajud(n)
    return a.upper() if a else "?"


# ------------------------------------------------------------------ rede
def pedir(url, corpo=None, cabecalhos=None, tentativas=3):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    h = {"User-Agent": "RadarJuridico/1.0 (acompanhamento processual)",
         "Accept": "application/json"}
    if dados is not None:
        h["Content-Type"] = "application/json"
    h.update(cabecalhos or {})
    ctx = ssl.create_default_context()
    ultimo = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, data=dados, headers=h,
                                         method="POST" if dados else "GET")
            with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            ultimo = f"HTTP {e.code}"
            if e.code in (401, 403, 404):
                break
            time.sleep(2 ** (i + 1) * (3 if e.code == 429 else 1))
        except Exception as e:  # rede, TLS, JSON
            ultimo = type(e).__name__ + (f": {e}" if str(e) else "")
            time.sleep(2 ** (i + 1))
    raise RuntimeError(ultimo or "falha sem detalhe")


def data10(v):
    """DataJud mistura `2019-03-01T...` e `20190301000000`; o painel quer AAAA-MM-DD."""
    v = str(v or "")
    if re.match(r"^\d{8}", v):
        return f"{v[:4]}-{v[4:6]}-{v[6:8]}"
    return v[:10]


def limpar_texto(t):
    t = re.sub(r"<br\s*/?>|</p>", "\n", t or "", flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"[ \t ]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()


def buscar_djen(params):
    """Todas as páginas de uma consulta ao DJEN."""
    itens, pagina = [], 1
    while pagina <= 20:
        q = dict(params, pagina=pagina, itensPorPagina=100)
        url = DJEN + "?" + urllib.parse.urlencode(q)
        r = pedir(url)
        lote = r.get("items") or []
        itens += lote
        if len(lote) < 100:
            break
        pagina += 1
        time.sleep(1)
    return itens


def intimacao(item, agora):
    num = item.get("numeroprocessocommascara") or mascara(item.get("numero_processo", ""))
    return {
        "id": str(item.get("id") or item.get("hash") or ""),
        "processo": mascara(num),
        "data": (item.get("data_disponibilizacao") or item.get("datadisponibilizacao") or "")[:10],
        "tribunal": item.get("siglaTribunal") or "",
        "tipo": item.get("tipoComunicacao") or "Comunicação",
        "documento": item.get("tipoDocumento") or "",
        "orgao": item.get("nomeOrgao") or "",
        "classe": item.get("nomeClasse") or "",
        "texto": limpar_texto(item.get("texto"))[:TEXTO_MAX],
        "link": item.get("link") or "",
        "destinatarios": [d.get("nome", "") for d in (item.get("destinatarios") or [])][:6],
        "capturada": agora,
    }


def buscar_datajud(numero, chave):
    alias = alias_datajud(numero)
    if not alias:
        raise RuntimeError("tribunal fora do DataJud")
    r = pedir(DATAJUD.format(alias=alias),
              {"size": 5, "query": {"match": {"numeroProcesso": digitos(numero)}}},
              {"Authorization": "APIKey " + chave})
    hits = [h.get("_source", {}) for h in r.get("hits", {}).get("hits", [])]
    if not hits:
        return None
    # um mesmo número pode ter um registro por grau; o painel mostra todos os
    # movimentos juntos e diz de que grau veio cada um
    ref = max(hits, key=lambda s: s.get("dataHoraUltimaAtualizacao") or "")
    movs = []
    for s in hits:
        for m in s.get("movimentos") or []:
            comp = [c.get("nome") or c.get("descricao") or ""
                    for c in m.get("complementosTabelados") or []]
            movs.append({"data": data10(m.get("dataHora")), "nome": m.get("nome") or "",
                         "complemento": "; ".join(c for c in comp if c),
                         "grau": s.get("grau") or ""})
    movs.sort(key=lambda m: m["data"], reverse=True)
    return {
        "classe": (ref.get("classe") or {}).get("nome", ""),
        "orgao": (ref.get("orgaoJulgador") or {}).get("nome", ""),
        "grau": ", ".join(sorted({s.get("grau", "") for s in hits if s.get("grau")})),
        "assuntos": [a.get("nome", "") for a in (ref.get("assuntos") or []) if isinstance(a, dict)][:4],
        "ajuizamento": data10(ref.get("dataAjuizamento")),
        "atualizado_fonte": data10(ref.get("dataHoraUltimaAtualizacao")),
        "movimentos": movs[:MOVIMENTOS],
    }


# ------------------------------------------------------------------ arquivos
def ler(p, padrao):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return padrao


def gravar(p, dados):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(dados if isinstance(dados, str)
                   else json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def conferir_privado():
    """Recusa gravar se privado/ estiver versionado ou fora do .gitignore."""
    if os.environ.get("RADAR_PRIVADO"):
        return
    gi = (RAIZ / ".gitignore").read_text(encoding="utf-8") if (RAIZ / ".gitignore").exists() else ""
    if "privado/" not in gi:
        sys.exit("ERRO: .gitignore não cobre privado/. Não gravo carteira num lugar versionável.")


# ------------------------------------------------------------------ comandos
def adicionar(numeros):
    conferir_privado()
    cfg = ler(LISTA, json.loads(json.dumps(MODELO)))
    ja = {digitos(p["numero"]) for p in cfg["processos"]}
    ruins = [n for n in numeros if not dv_confere(n)]
    if ruins:
        sys.exit("ERRO: dígito verificador não confere — número copiado errado? "
                 + ", ".join(ruins) + "\nNada foi gravado.")
    novos = 0
    for n in numeros:
        if digitos(n) in ja:
            continue
        cfg["processos"].append({"numero": mascara(n), "apelido": "", "notas": ""})
        ja.add(digitos(n))
        novos += 1
    gravar(LISTA, cfg)
    print(f"{novos} processo(s) novo(s) em {LISTA.relative_to(RAIZ) if LISTA.is_relative_to(RAIZ) else LISTA}"
          f" · {len(cfg['processos'])} na lista")


def atualizar(so_local=False):
    conferir_privado()
    if not LISTA.exists():
        sys.exit("Sem privado/processos.json. Comece com:\n"
                 "  python3 scripts/processos.py --adicionar <número> [<número> ...]")
    cfg = ler(LISTA, MODELO)
    cache = ler(CACHE, {"intimacoes": {}, "datajud": {}, "ultima_djen": None})
    agora = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    hoje = datetime.date.today()
    erros = []

    lista = {digitos(p["numero"]): p for p in cfg.get("processos", []) if p.get("numero")}
    for d, p in lista.items():
        if not dv_confere(d):
            erros.append(f"{mascara(d)}: dígito verificador não confere — conferir o número")

    if not so_local:
        # 1. DJEN — por OAB (descobre processo novo) e por número (pega intimação
        #    dirigida a outro advogado do mesmo processo)
        ini = hoje - datetime.timedelta(days=JANELA_PRIMEIRA)
        if cache.get("ultima_djen"):
            ini = max(ini, datetime.date.fromisoformat(cache["ultima_djen"])
                      - datetime.timedelta(days=SOBREPOSICAO))
        janela = {"dataDisponibilizacaoInicio": ini.isoformat(),
                  "dataDisponibilizacaoFim": hoje.isoformat()}
        consultas = []
        oab = cfg.get("oab") or {}
        if oab.get("numero"):
            consultas.append(("OAB " + oab["numero"] + "/" + oab.get("uf", ""),
                              dict(janela, numeroOab=digitos(oab["numero"]), ufOab=oab.get("uf", ""))))
        consultas += [(mascara(d), dict(janela, numeroProcesso=d)) for d in lista]
        djen_ok = True
        primeira = not cache.get("ultima_djen")
        for rotulo, q in consultas:
            try:
                for item in buscar_djen(q):
                    it = intimacao(item, agora)
                    chave = it["id"] or (it["processo"] + it["data"] + it["texto"][:80])
                    if chave not in cache["intimacoes"]:
                        if primeira and it["data"]:
                            # na primeira busca tudo é inédito; "nova" fica para
                            # o que foi disponibilizado nos últimos dias de fato
                            it["capturada"] = it["data"] + "T00:00-03:00"
                        cache["intimacoes"][chave] = it
            except Exception as e:
                djen_ok = False
                erros.append(f"DJEN ({rotulo}): {e}")
            time.sleep(1)
        if djen_ok:
            cache["ultima_djen"] = hoje.isoformat()

    # processo que apareceu no DJEN pela OAB e não está na lista entra sozinho
    descobertos = {}
    for it in cache["intimacoes"].values():
        d = digitos(it["processo"])
        if len(d) == 20 and d not in lista:
            descobertos[d] = {"numero": mascara(d), "apelido": "", "notas": "", "origem": "djen"}

    if not so_local:
        chave = cfg.get("datajud_chave") or CHAVE_DATAJUD
        for d in list(lista) + list(descobertos):
            try:
                r = buscar_datajud(d, chave)
                cache["datajud"][d] = {"em": agora, "dados": r}
            except Exception as e:
                erros.append(f"DataJud ({mascara(d)}): {e} — mantido o último retrato")
            time.sleep(0.5)

    gravar(CACHE, cache)

    # 2. o que o painel lê
    limite_nova = datetime.datetime.now().astimezone() - datetime.timedelta(hours=NOVA_HORAS)
    por_proc = {}
    for it in cache["intimacoes"].values():
        por_proc.setdefault(digitos(it["processo"]), []).append(it)
    saida = []
    for d, p in list(lista.items()) + list(descobertos.items()):
        dj = (cache["datajud"].get(d) or {})
        dados = dj.get("dados") or {}
        ints = sorted(por_proc.get(d, []), key=lambda i: i["data"], reverse=True)
        for i in ints:
            try:
                i["nova"] = datetime.datetime.fromisoformat(i["capturada"]) >= limite_nova
            except ValueError:
                i["nova"] = False
        saida.append({
            "numero": mascara(d), "tribunal": sigla(d),
            "apelido": p.get("apelido", ""), "notas": p.get("notas", ""),
            "origem": p.get("origem", "lista"),
            "dv": dv_confere(d),
            "classe": dados.get("classe", ""), "orgao": dados.get("orgao", ""),
            "grau": dados.get("grau", ""), "assuntos": dados.get("assuntos", []),
            "ajuizamento": dados.get("ajuizamento", ""),
            "atualizado_fonte": dados.get("atualizado_fonte", ""),
            "consultado": dj.get("em", ""),
            "no_datajud": bool(dados) if dj else None,
            "movimentos": dados.get("movimentos", []),
            "intimacoes": ints[:30],
        })
    js = ("// GERADO por scripts/processos.py — carteira, não versionar, não editar.\n"
          "window.PROCESSOS_PRIVADOS = "
          + json.dumps({"atualizado": agora, "oab": cfg.get("oab"), "erros": erros,
                        "processos": saida}, ensure_ascii=False, indent=1) + ";\n")
    gravar(SAIDA, js)
    novas = sum(1 for p in saida for i in p["intimacoes"] if i.get("nova"))
    print(f"{len(saida)} processos · {novas} intimação(ões) nova(s) · "
          f"{len(descobertos)} descoberto(s) pelo DJEN · {len(erros)} erro(s)")
    for e in erros:
        print("  ! " + e)
    return 0


def agenda():
    py = sys.executable or "python3"
    script = pathlib.Path(__file__).resolve()
    log = PRIVADO / "processos.log"
    print("# Duas vezes por dia útil, às 7h e às 13h. Cole com `crontab -e`:")
    print(f'0 7,13 * * 1-5 cd "{RAIZ}" && "{py}" "{script}" >> "{log}" 2>&1')
    print("\n# No macOS, se o cron não tiver acesso à pasta, dê 'Acesso Total ao Disco'"
          " a /usr/sbin/cron em Ajustes > Privacidade e Segurança.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--adicionar", nargs="+", metavar="NÚMERO",
                    help="põe processo(s) na lista de privado/processos.json")
    ap.add_argument("--agenda", action="store_true", help="imprime a linha do cron")
    ap.add_argument("--so-local", action="store_true",
                    help="não consulta a rede; só regrava o painel a partir do cache")
    a = ap.parse_args()
    if a.agenda:
        return agenda()
    if a.adicionar:
        adicionar(a.adicionar)
        return 0
    return atualizar(a.so_local)


if __name__ == "__main__":
    sys.exit(main())
