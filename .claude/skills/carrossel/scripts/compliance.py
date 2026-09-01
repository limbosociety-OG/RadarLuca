#!/usr/bin/env python3
"""Gate de compliance — Provimento 205/2021 da OAB e verificação processual.

Roda antes do render. Falha o build; não sugere correção. Não tem bandeira de bypass:
se ele reprova, o caminho é reescrever o roteiro.

    python3 scripts/compliance.py caminho/para/roteiro.json

Checa, nesta ordem:
  1. ficha de verificação — todo campo `confirmado`, com fonte, data, e data dentro
     da janela (contada de hoje, ou de `publicado_em` quando a peça já saiu)
  2. coerência de citação — todo processo e tema citado na peça está na ficha
  3. léxico de captação — no roteiro E na legenda
  4. fecho — ressalva de caráter informativo no último slide e na legenda
"""
import datetime
import json
import pathlib
import re
import sys
import unicodedata

# Idade máxima de uma verificação, em dias. Status processual muda toda semana;
# ficha velha é ficha não verificada. Aumentar este número é afrouxar o gate.
JANELA_DIAS = 15

# ---------------------------------------------------------------- léxico
# Os padrões são escritos SEM ACENTO e casados contra texto já normalizado.
# Nunca passe um padrão por uma função de normalização: `.lower()` transforma
# `\S` em `\s` e `\B` em `\b`, invertendo o sentido do padrão em silêncio.
CAPTACAO = [
    (r"\brecupere\b|\brecuperem\b|\brecuperar seu\b|\brecupere o que\b",
     "imperativo de recuperação — oferta de resultado, art. 2º do Prov. 205"),
    (r"\bseu dinheiro\b|\bdinheiro de volta\b|\bde volta ao seu bolso\b",
     "apelo patrimonial direto ao leitor"),
    (r"\bvoce tem direito a receber\b|\bvoce tem direito ao?\b.{0,24}\brestitui",
     "afirmação de direito individual sem análise do caso — promessa de resultado"),
    (r"\bprocure um advogado\b|\bfale com um advogado\b|\bconsulte um especialista\b|"
     r"\bchame no direct\b|\bme chama no direct\b|\bentre em contato\b|\bfale comigo\b|"
     r"\bagende (uma )?(consulta|reuniao)\b|\bmande (uma )?mensagem\b|\bfaca uma consulta\b",
     "chamada para contato — captação de clientela"),
    (r"\bgarant\w*\s+(o|a|seu|sua)\s+(exito|resultado|restitui|devolu)",
     "promessa de resultado"),
    (r"\b(nao) perca\b|\bcorra\b|\bultima chance\b|\baproveite\b|\bgaranta ja\b|"
     r"\bnao deixe para\b",
     "urgência mercantil"),
    (r"\bclique\b|\blink na bio\b|\barrasta pra cima\b|\bsalve esse post\b|"
     r"\bcompartilh[ea]\b|\bmarque um amigo\b|\bcomente aqui\b|\bme segue\b",
     "chamada de conversão"),
    (r"\bmelhor (escritorio|advogado)\b|\bespecialista n[o]?\s*1\b|\blider em\b|"
     r"\bmaior escritorio\b",
     "autopromoção comparativa, vedada pelo Código de Ética"),
    (r"\bhonorarios? (a partir de|de apenas|gratis)\b|\bsem custo\b|"
     r"\bprimeira consulta gratuita\b|\bexito de \d+%",
     "mercantilização"),
    (r"\bmeu cliente\b|\bum cliente meu\b|\batendi um caso\b|\bcaso que patrocinei\b|"
     r"\bum caso da banca\b",
     "caso concreto de cliente — sigilo e vedação de uso publicitário"),
]

# Muleta retórica proibida no projeto — avisa, não bloqueia.
MULETAS = [r"importante ressaltar", r"vale destacar", r"cumpre observar",
           r"e importante lembrar", r"cabe salientar", r"nesse sentido, e"]

# O último slide carrega as duas: natureza informativa e a norma que a rege.
FECHO_SLIDE = [
    (r"provimento\s*205", "menção ao Provimento 205/2021 da OAB"),
    (r"carater (tecnico|informativo)|conteudo informativo|publicacao informativa",
     "declaração de caráter informativo"),
]
# A legenda viaja sozinha (print, repost) e precisa carregar ao menos a ressalva.
FECHO_LEGENDA = [r"carater (tecnico|informativo)", r"conteudo informativo",
                 r"publicacao informativa", r"provimento\s*205"]

# Classes processuais que, se citadas na peça, têm de estar na ficha de verificação.
CITACAO_PROCESSO = re.compile(
    r"\b(are|resp|aresp|eresp|rms|adi|adc|adpf|re)\s*n?[oº.]*\s*([\d][\d.]{4,})", re.I)
CITACAO_TEMA = re.compile(r"\btema\s*n?[oº.]*\s*([\d][\d.]*)", re.I)


def sem_acento(s):
    """Minúsculas sem acento. Só para TEXTO — nunca para padrão."""
    s = s.lower()
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def _conferir_lexico():
    """Padrão com acento nunca casaria: o texto chega normalizado. Falhar alto."""
    for grupo in (CAPTACAO, [(p, "") for p in MULETAS],
                  FECHO_SLIDE, [(p, "") for p in FECHO_LEGENDA]):
        for padrao, _ in grupo:
            if sem_acento(padrao) != padrao.lower():
                sys.exit(f"ERRO INTERNO: padrão com acento nunca casa: {padrao!r}")
            re.compile(padrao)


_conferir_lexico()


def so_digitos(s):
    return re.sub(r"\D", "", s or "")


def textos_do_slide(slide):
    """Extrai toda string editorial de um slide, recursivamente."""
    out = []

    def walk(node):
        if isinstance(node, str):
            out.append(node)
        elif isinstance(node, dict):
            for k, v in node.items():
                if k in ("tipo", "tom", "tema"):
                    continue
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(slide)
    return out


# ---------------------------------------------------------------- checagens
def data_de_referencia(r, erros, hoje):
    """Peça já publicada é história: a janela se mede contra a data da publicação,
    não contra hoje. Renderizar de novo reproduz o que saiu. Para atualizar a peça,
    reverifique a ficha e mova `publicado_em`."""
    bruto = r.get("publicado_em")
    if not bruto:
        return hoje
    try:
        quando = datetime.date.fromisoformat(bruto)
    except (TypeError, ValueError):
        erros.append(f"publicado_em `{bruto}` fora de AAAA-MM-DD")
        return hoje
    if quando > hoje:
        erros.append(f"publicado_em no futuro ({bruto})")
        return hoje
    return quando


def checar_verificacao(r, erros, hoje):
    ver = r.get("verificacao")
    if not ver:
        erros.append("bloco `verificacao` ausente — nenhuma peça sai sem ficha de fatos")
        return
    if "modulacao" not in ver:
        erros.append("verificacao.modulacao ausente — modulação é questão de primeira "
                     "ordem, precisa ser afirmada ou negada")
    for campo, dado in ver.items():
        d = dado or {}
        estado = d.get("estado")
        if estado != "confirmado":
            erros.append(f"verificacao.{campo}: estado `{estado or 'vazio'}` — só "
                         f"`confirmado` libera render (ver references/verificacao.md)")
            continue
        if not (d.get("fonte") and d.get("data")):
            erros.append(f"verificacao.{campo}: confirmado sem fonte e data")
            continue
        try:
            quando = datetime.date.fromisoformat(d["data"])
        except ValueError:
            erros.append(f"verificacao.{campo}: data `{d['data']}` fora de AAAA-MM-DD")
            continue
        idade = (hoje - quando).days
        if idade > JANELA_DIAS:
            erros.append(f"verificacao.{campo}: conferida há {idade} dias "
                         f"({d['data']}) — o teto é {JANELA_DIAS}. Andamento muda toda "
                         f"semana: voltar à fonte primária e reescrever a data")
        elif idade < 0:
            erros.append(f"verificacao.{campo}: data no futuro ({d['data']})")


def checar_citacoes(r, textos, erros):
    """Processo ou tema citado na peça que não está na ficha é erro de origem —
    é assim que um número errado de acórdão vira post publicado."""
    ver = r.get("verificacao") or {}
    valores = " ".join(str((v or {}).get("valor", "")) for v in ver.values())
    processos = {so_digitos(m) for m in re.findall(r"[\d][\d.]{4,}", valores)}
    temas = {so_digitos(m) for m in CITACAO_TEMA.findall(valores)}

    vistos = set()
    for onde, t in textos:
        for classe, num in CITACAO_PROCESSO.findall(t):
            d = so_digitos(num)
            if d and d not in processos and (onde, d) not in vistos:
                vistos.add((onde, d))
                erros.append(
                    f"{onde}: cita {classe.upper()} {num}, que não está na ficha de "
                    f"verificação. Ou o número está errado, ou a ficha está incompleta")
        for num in CITACAO_TEMA.findall(t):
            d = so_digitos(num)
            if d and temas and d not in temas and (onde, "T" + d) not in vistos:
                vistos.add((onde, "T" + d))
                erros.append(f"{onde}: cita Tema {num}, divergente do tema da ficha "
                             f"({(ver.get('tema') or {}).get('valor', '—')})")


def checar_lexico(textos, erros, avisos):
    for onde, t in textos:
        n = sem_acento(t)
        for padrao, razao in CAPTACAO:
            m = re.search(padrao, n)
            if m:
                erros.append(f'{onde}: "{m.group(0)}" — {razao}')
        for padrao in MULETAS:
            if re.search(padrao, n):
                avisos.append(f"{onde}: muleta retórica «{padrao}»")


def checar_fecho(slides, erros):
    if not slides:
        return
    ultimo = sem_acento(" ".join(textos_do_slide(slides[-1])))
    for padrao, oque in FECHO_SLIDE:
        if not re.search(padrao, ultimo):
            erros.append(f"slide final sem {oque}")


def checar_legenda(caminho, erros, avisos):
    """A legenda é publicada junto e circula sozinha. Passa pelo mesmo léxico."""
    leg = caminho.parent / "legenda.md"
    if not leg.exists():
        erros.append(f"legenda.md ausente em {leg.parent}/ — a legenda é parte da peça "
                     f"e é onde o chamado à ação costuma entrar")
        return
    texto = leg.read_text(encoding="utf-8").strip()
    if not texto:
        erros.append("legenda.md vazio")
        return
    checar_lexico([("legenda", texto)], erros, avisos)
    n = sem_acento(texto)
    if not any(re.search(p, n) for p in FECHO_LEGENDA):
        erros.append("legenda.md sem a ressalva de caráter informativo — ela viaja "
                     "sozinha em print e repost")
    if "#" in texto:
        avisos.append("legenda.md tem hashtag — o sistema editorial não usa hashtag "
                      "genérica de advogado")
    return texto


# ---------------------------------------------------------------- main
def checar(caminho, hoje=None):
    caminho = pathlib.Path(caminho)
    hoje = hoje or datetime.date.today()
    r = json.loads(caminho.read_text(encoding="utf-8"))
    erros, avisos = [], []

    checar_verificacao(r, erros, data_de_referencia(r, erros, hoje))

    slides = r.get("slides", [])
    if not slides:
        erros.append("nenhum slide no roteiro")

    textos = [(f"slide {i:02d}", t)
              for i, s in enumerate(slides, 1) for t in textos_do_slide(s)]

    legenda = checar_legenda(caminho, erros, avisos)
    if legenda:
        textos.append(("legenda", legenda))

    checar_citacoes(r, textos, erros)
    checar_lexico(textos, erros, avisos)
    checar_fecho(slides, erros)
    return erros, avisos


def main():
    if len(sys.argv) < 2:
        print("uso: compliance.py roteiro.json", file=sys.stderr)
        return 2

    erros, avisos = checar(sys.argv[1])

    for a in avisos:
        print(f"  aviso   {a}")

    if erros:
        print(f"\nCOMPLIANCE REPROVADO — {len(erros)} bloqueio(s):\n")
        for e in erros:
            print(f"  ✗ {e}")
        print("\nReescreva o roteiro. Não edite este script para acomodar a frase.")
        return 1

    print("compliance aprovado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
