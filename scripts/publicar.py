#!/usr/bin/env python3
"""Gera as variantes publicáveis do portal, para o Artifact.

    python3 scripts/publicar.py            # celular: consulta, somente leitura
    python3 scripts/publicar.py --online   # o painel online: edita e grava no banco

A variante online é a que fica no claude.ai e abre de qualquer lugar. Ela
grava no banco do próprio Artifact (capacidade `db`, documento
`painel/estado`) em vez do localStorage, e a rotina diária traz esse
documento de volta ao repositório (`scripts/sincronizar.py`). Sem a camada
privada, como a de celular.

Escreve `portal/celular.html` a partir de `portal/radar.html`. Mesma
fonte, mesmo sistema visual — o que muda é o que não faz sentido no telefone:

  * fora o `<!DOCTYPE>`, `<html>`, `<head>` e `<body>`: o Artifact envolve a página
  * fora `privado/prazos.js` e `privado/processos.js`: carteira não sai do disco.
    A aba Meus processos completa só nasce em file://; no painel online (--online)
    ela é outra, só número e link, lida do documento `carteira/processos` do banco
  * somente leitura: sem editar, criar, excluir, importar ou zerar

O terceiro ponto é o que importa. O painel do disco já guarda edição no
localStorage até ser importada; um segundo lugar gravável, no celular, com
armazenamento próprio, criaria uma terceira cópia que nunca volta para o
repositório. No telefone se consulta.
"""
import argparse
import datetime
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ORIGEM = RAIZ / "portal" / "radar.html"
DESTINO = RAIZ / "portal" / "celular.html"
DESTINO_ONLINE = RAIZ / "portal" / "online.html"

SO_LEITURA = """
/* ---------- variante de celular: consulta, não edição ---------- */
#nova-tese,#novo-boletim,#nova-aula,#novo-estudo,#exportar,#importar,#zerar,
.ts-acoes,#aviso-semente,#aviso-sujo,dialog,.rodape .acoes,
.backlog input[type=checkbox]{display:none!important}
.edai-txt,.aula-notas,.backlog .txt{cursor:default}
.edai-txt:empty{display:none}
.instantaneo{font-family:var(--dado);font-size:12px;line-height:1.65;color:var(--tinta2);
  border-left:1px solid var(--acento);padding:2px 0 2px 14px;margin:26px 0 0;max-width:74ch}
.instantaneo b{color:var(--acento)}
@media (max-width:860px){
  .topo{padding:20px 0 12px}
  .numeros{gap:12px;font-size:11px}
  .abas{gap:16px;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .filtros{gap:14px}
  .term-grade{grid-template-columns:1fr}
}
"""

ONLINE_CSS = """
/* ---------- painel online: grava no banco do Artifact ---------- */
#importar,#zerar,#exportar{display:none!important}
.instantaneo{font-family:var(--dado);font-size:12px;line-height:1.65;color:var(--tinta2);
  border-left:1px solid var(--acento);padding:2px 0 2px 14px;margin:26px 0 0;max-width:74ch}
.instantaneo b{color:var(--acento)}
.nuvem{font-family:var(--dado);font-weight:500;font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--tinta3)}
.nuvem.ok{color:var(--firme)} .nuvem.falha{color:var(--atencao)}
[data-armado]{color:var(--urgente)!important}
@media (max-width:860px){
  .topo{padding:20px 0 12px}
  .numeros{gap:12px;font-size:11px}
  .abas{gap:16px;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .filtros{gap:14px}
  .term-grade{grid-template-columns:1fr}
}
"""

# Troca o localStorage pelo banco. O localStorage continua como cache de
# primeira pintura; a fonte é o documento `painel/estado`.
ONLINE_JS = r"""
/* ---------- carteira online: só número e link ----------
   Decisão do titular (23/09/2026): no painel online a aba Meus processos lista
   número e link de consulta, nada mais. A lista vive no documento
   `carteira/processos` do banco, nunca no repositório; sem teor de intimação,
   cliente ou prazo, que continuam só em privado/, no disco. */
let carteiraRef=null, carteira=[];
const soDig=n=>String(n||'').replace(/\D/g,'');
function mascaraCNJ(n){ const d=soDig(n); return d.length!==20?n:`${d.slice(0,7)}-${d.slice(7,9)}.${d.slice(9,13)}.${d[13]}.${d.slice(14,16)}.${d.slice(16)}`; }
function dvCNJ(n){ const d=soDig(n); if(d.length!==20) return false;
  const b=BigInt(d.slice(0,7)+d.slice(9)+'00'); return 98n-b%97n===BigInt(d.slice(7,9)); }
function consultas(n){
  const d=soDig(n), l=[];
  if(d[13]==='8'&&d.slice(14,16)==='19'){
    l.push(d.startsWith('08')
      ? ['PJe TJRJ','https://tjrj.pje.jus.br/1g/ConsultaPublica/listView.seam']
      : ['consulta TJRJ','https://www3.tjrj.jus.br/consultaprocessual/']);
  }
  l.push(['DJEN','https://comunica.pje.jus.br/']);
  return l;
}
function abaCarteira(){
  if(document.getElementById('pane-processos')) return;
  const b=document.createElement('button');
  b.className='aba'; b.setAttribute('role','tab'); b.id='aba-processos'; b.dataset.pane='processos';
  b.setAttribute('aria-controls','pane-processos'); b.setAttribute('aria-selected','false'); b.tabIndex=-1;
  b.textContent='Meus processos';
  b.addEventListener('click',()=>trocarAba('processos'));
  document.querySelector('.abas').appendChild(b);
  const p=document.createElement('div');
  p.className='pane'; p.id='pane-processos'; p.setAttribute('role','tabpanel');
  p.setAttribute('aria-labelledby','aba-processos'); p.hidden=true;
  p.innerHTML=`<section class="secao">
      <h2>Processos <span id="r-processos"></span></h2>
      <p class="abertura">Número e link de consulta. Clicar no número copia; a consulta abre na página
        pública do tribunal. Intimação, teor e prazo ficam no painel do disco, que não sai do computador.</p>
      <div class="pr-cartoes" id="processos"></div>
      <div class="filtros" style="margin-top:22px">
        <input class="busca" id="novo-proc" type="text" inputmode="numeric" placeholder="0000000-00.0000.0.00.0000" aria-label="Número CNJ do processo">
        <button class="acao discreta" id="add-proc">acompanhar</button>
        <span class="pr-flag" id="erro-proc" role="status"></span>
      </div>
    </section>`;
  document.getElementById('pane-posfgv').after(p);
  document.getElementById('add-proc').addEventListener('click',adicionarProc);
  document.getElementById('novo-proc').addEventListener('keydown',e=>{ if(e.key==='Enter') adicionarProc(); });
  p.addEventListener('click',async e=>{
    const c=e.target.closest('[data-copiar]');
    if(c){ try{ await navigator.clipboard.writeText(c.dataset.copiar); c.dataset.antes=c.dataset.antes||c.textContent;
        c.textContent='copiado'; setTimeout(()=>{ c.textContent=c.dataset.antes; },1400); }
      catch(_){ const r=document.createRange(); r.selectNodeContents(c); const s=getSelection(); s.removeAllRanges(); s.addRange(r); } return; }
    const x=e.target.closest('[data-tirar]');
    if(x&&duplo(x)){ gravarCarteira(carteira.filter(q=>soDig(q.numero)!==x.dataset.tirar)); }
  });
  try{ if(localStorage.getItem(CHAVE+'-aba')==='processos') trocarAba('processos'); }catch(e){}
}
function desenharCarteira(){
  const alvo=document.getElementById('processos'); if(!alvo) return;
  document.getElementById('r-processos').textContent=carteira.length?plural(carteira.length,'processo','processos'):'';
  alvo.innerHTML=carteira.length?carteira.map(q=>`<article class="pr-c">
      <button class="pr-num" data-copiar="${esc(q.numero)}" title="copiar o número">${esc(q.numero)}</button>
      <div class="pr-meta">${soDig(q.numero)[13]==='8'&&soDig(q.numero).slice(14,16)==='19'?'TJRJ':''}${q.apelido?' · '+esc(q.apelido):''}</div>
      <div class="pr-ult">${consultas(q.numero).map(([n,u])=>`<a class="ligacao" href="${u}" target="_blank" rel="noopener">${n}</a>`).join(' &nbsp; ')}
        <button class="acao discreta" data-tirar="${soDig(q.numero)}" style="float:right">remover</button></div>
    </article>`).join(''):'<p class="vazio">Nenhum processo na lista.</p>';
}
async function gravarCarteira(lista){
  if(!carteiraRef) return;
  try{ await carteiraRef.set({processos:lista, alterado_em:new Date().toISOString()}); }
  catch(e){ document.getElementById('erro-proc').textContent='não gravou: sem permissão ou sem conexão'; }
}
function adicionarProc(){
  const campo=document.getElementById('novo-proc'), erro=document.getElementById('erro-proc');
  const n=campo.value.trim(); erro.textContent='';
  if(!dvCNJ(n)){ erro.textContent='dígito verificador não confere: número copiado errado?'; return; }
  if(carteira.some(q=>soDig(q.numero)===soDig(n))){ erro.textContent='já está na lista'; return; }
  campo.value=''; gravarCarteira([...carteira,{numero:mascaraCNJ(n),apelido:''}]);
}
function ligarCarteira(db){
  carteiraRef=db.doc('carteira/processos');
  carteiraRef.onSnapshot(snap=>{
    const d=snap.exists?snap.data():null;
    carteira=(d&&Array.isArray(d.processos))?d.processos.filter(q=>q&&q.numero):[];
    abaCarteira(); desenharCarteira();
  },()=>{});
}
/* ---------- nuvem: o banco do Artifact ---------- */
const EDITAVEIS=['teses','boletins','aulas','backlog','sujo','semente'];
let docRef=null, nuvem='conectando', timerNuvem=null, gravando=false, pendente=false,
    ultimoEnviado='', iniciado=false;
const camada=o=>{ const c={}; EDITAVEIS.forEach(k=>{ c[k]=o[k]===undefined?null:o[k]; }); return JSON.stringify(c); };
function agendarNuvem(){ if(!docRef) return; clearTimeout(timerNuvem); timerNuvem=setTimeout(enviarNuvem,700); }
async function enviarNuvem(){
  if(!docRef) return;
  if(gravando){ pendente=true; return; }
  const txt=camada(estado); if(txt===ultimoEnviado) return;
  gravando=true; nuvem='salvando'; avisarArmazenamento();
  try{ await docRef.set({...JSON.parse(txt), alterado_em:new Date().toISOString()});
       ultimoEnviado=txt; nuvem='salvo'; }
  catch(e){ nuvem = (e&&e.code==='invalid_argument') ? 'leitura' : 'falha'; }
  gravando=false; avisarArmazenamento();
  if(pendente){ pendente=false; enviarNuvem(); }
}
function aplicarNuvem(d){
  const pend=d&&d.sujo&&Object.keys(d.sujo).length;
  // documento de uma versão anterior do acervo, sem nada pendente: vale o repositório
  if(!d||(d.semente!==SEMENTE&&!pend)) return false;
  EDITAVEIS.forEach(k=>{ if(d[k]!=null) estado[k]=clonar(d[k]); });
  const daqui=new Set((PADRAO.aulas||[]).map(x=>x.id));
  estado.aulas=[...clonar(PADRAO.aulas||[]), ...(estado.aulas||[]).filter(x=>!daqui.has(x.id))];
  return true;
}
function duplo(b){
  // o visor do Artifact não mostra confirm(): o segundo toque confirma
  if(b.dataset.armado) return true;
  const antes=b.textContent; b.dataset.armado='1'; b.textContent='confirmar';
  setTimeout(()=>{ delete b.dataset.armado; b.textContent=antes; },4000);
  return false;
}
async function ligarNuvem(){
  let db=null;
  try{ db = window.claude && window.claude.use ? await window.claude.use('db') : null; }catch(e){ db=null; }
  if(!db){ nuvem='ausente'; avisarArmazenamento(); return; }
  docRef=db.doc('painel/estado');
  ligarCarteira(db);
  let primeiro=true;
  docRef.onSnapshot(snap=>{
    if(snap.metadata.hasPendingWrites) return;
    const d=snap.exists?snap.data():null;
    if(d&&camada(d)===ultimoEnviado){ primeiro=false; return; }
    const editando=(document.activeElement&&document.activeElement.isContentEditable)||dlg.open;
    if(editando&&!primeiro) return;
    const usou=aplicarNuvem(d);
    ultimoEnviado = usou ? camada(estado) : ultimoEnviado;
    if(primeiro){ primeiro=false; nuvem='salvo'; }
    salvarLocal(); desenhar();
  }, e=>{ nuvem='falha'; avisarArmazenamento(); });
}
"""


def troca(s, antes, depois, oque):
    if antes not in s:
        sys.exit(f"ERRO: o painel mudou e a variante online não achou {oque}. "
                 "Ajuste scripts/publicar.py.")
    return s.replace(antes, depois)


def online(s):
    """O painel editável no claude.ai: mesmo código, outra persistência."""
    s = troca(s, "function salvar(){\n  if(!temArmazenamento) return;",
              "function salvar(){\n  if(iniciado){ estado.sujo=estado.sujo||{}; estado.sujo.painel=1; "
              "agendarNuvem(); }\n  salvarLocal();\n}\nfunction salvarLocal(){\n"
              "  if(!temArmazenamento) return;", "salvar()")
    s = troca(s, "/* ---------- estado ---------- */", ONLINE_JS + "\n/* ---------- estado ---------- */",
              "o bloco de estado")
    for msg in ("'Remover esta tese do mapa?'", "'Excluir este boletim?'",
                "'Excluir esta aula do caderno?'", "'Remover este item do backlog?'"):
        s = troca(s, f"confirm({msg})", "duplo(b)", "a confirmação de exclusão")
    s = troca(s, """function avisarArmazenamento(){
  document.getElementById('aviso-armazenamento').innerHTML = temArmazenamento ? '' :""",
              """function avisarArmazenamento(){
  const r=document.getElementById('estado-nuvem');
  if(r){ const t={conectando:'conectando…',salvando:'salvando…',salvo:'salvo na nuvem',
      leitura:'somente leitura',falha:'sem conexão — ficou neste navegador',
      ausente:'sem banco — ficou neste navegador'}[nuvem]||nuvem;
    r.hidden=false; r.textContent=t; r.className='nuvem '+(nuvem==='salvo'?'ok':(nuvem==='falha'||nuvem==='ausente')?'falha':''); }
  document.getElementById('aviso-armazenamento').innerHTML =
    (nuvem==='falha'||nuvem==='ausente') ? '<div class="aviso">O painel não alcançou o banco. '
    +'O que você mudar agora fica só neste navegador até a conexão voltar.</div>' : '';
  return;
  document.getElementById('aviso-armazenamento').innerHTML = temArmazenamento ? '' :""", "o aviso de armazenamento")
    s = troca(s, """  alvo.innerHTML=`<div class="aviso"><b>${partes.join(' e ')}</b> só neste navegador.
    Isso some se você limpar os dados do site ou trocar de máquina.
    Clique <b>exportar json</b> no rodapé e rode <code>python3 scripts/importar.py &lt;arquivo&gt; --aplicar</code>.</div>`;""",
              """  alvo.innerHTML=`<div class="aviso info">Alterações salvas na nuvem, fora do repositório
    por enquanto. Entram no acervo na próxima sincronização diária.</div>`;""", "o aviso de edição local")
    s = troca(s, "if(!novas&&!edits){ alvo.innerHTML=''; return; }",
              "if(!edits){ alvo.innerHTML=''; return; }", "a contagem de edições")
    s = troca(s, "Tese criada aqui vive no navegador. Para versionar, exporte e rode scripts/importar.py.",
              "Fica salva na nuvem e entra no acervo na sincronização diária. Nada de cliente, "
              "processo de carteira ou prazo de intimação aqui: esta página vive no servidor do claude.ai.",
              "a dica do formulário de tese")
    # O que o painel do disco diz sobre si mesmo é falso aqui: ele não lê
    # privado/, não guarda no navegador e não é arquivo aberto do disco.
    s = troca(s, """<p class="abertura">Prazo com data certa, janela que fecha por prescrição, e o que estiver em
        <code>privado/prazos.js</code>, que fica no disco e nunca sai daqui.</p>""",
              """<p class="abertura">Prazos públicos do acervo: data certa ou janela que fecha por
        prescrição. Prazo de carteira não aparece aqui, por construção.</p>""", "a abertura de prazos")
    s = troca(s, """O campo de impacto é editável: o que você escrever
        aqui fica no navegador até voltar para o repositório.""",
              """O campo de impacto é editável: o que você escrever
        fica salvo na nuvem e entra no repositório na sincronização diária.""", "a abertura do mapa")
    s = troca(s, """<p class="abertura">A fonte é <code>base/posfgv/aulas.json</code>. Aula criada aqui vive no
        navegador até ser importada, e some se você limpar os dados do site.</p>""",
              """<p class="abertura">Aula registrada aqui fica salva na nuvem e entra no caderno do
        repositório na sincronização diária.</p>""", "a abertura das aulas")
    s = troca(s, """      <p><b>Este quadro não é ao vivo, e não dá para ser.</b> O painel é um arquivo aberto do disco:
      não há servidor para consultar o X, nem lugar seguro para guardar credencial num repositório
      que também abriga <code>privado/</code>.</p>""",
              """      <p><b>Este quadro não é ao vivo.</b> O painel não consulta o X: não há credencial
      nem raspagem.</p>""", "o termômetro vazio")
    s = troca(s, """+'Prazo público entra no campo <b>prazo</b> de base/teses.json. O de carteira, em privado/prazos.js, só no disco.</p>';""",
              """+'Prazo público entra no campo <b>prazo</b> do acervo.</p>';""", "o vazio de prazos")
    # exportar, importar e zerar são do painel do disco: aqui o banco é a
    # persistência, e o visor do Artifact não entrega download nem confirm()
    for bt in ('<button class="acao discreta" id="exportar">exportar json</button>',
               '<button class="acao discreta" id="importar">importar json</button>',
               '<button class="acao discreta" id="zerar">restaurar padrão</button>'):
        s = troca(s, bt, "", "os botões de arquivo")
    i, f = s.index("/* ---------- dados ---------- */"), s.index("/* ---------- início ---------- */")
    s = s[:i] + s[f:]
    s = troca(s, "/* ---------- início ---------- */\ncarregar();",
              "/* ---------- início ---------- */\ncarregar();\niniciado=true;\nligarNuvem();", "o início")
    corte = s.rindex("</style>")
    s = s[:corte] + ONLINE_CSS + s[corte:]
    brt = datetime.timezone(datetime.timedelta(hours=-3))  # Brasília, sem horário de verão
    agora = datetime.datetime.now(brt).strftime("%d/%m/%Y às %Hh%M")
    return troca(s, '<div id="aviso-armazenamento"></div>',
                 f'<div class="instantaneo"><b>Painel online</b> — acervo do repositório em '
                 f'{agora}, sem a camada privada. O que você editar aqui é salvo na nuvem e '
                 f'volta ao repositório na sincronização diária.</div>\n'
                 f'<div id="aviso-armazenamento"></div>', "o aviso de armazenamento")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--online", action="store_true",
                    help="painel editável, gravando no banco do Artifact")
    a = ap.parse_args()
    if not ORIGEM.exists():
        sys.exit(f"ERRO: {ORIGEM} não existe. Rode scripts/gerar.py antes.")
    s = ORIGEM.read_text(encoding="utf-8")
    # 1. carteira não viaja: nem prazo, nem processo
    s = re.sub(r'<script src="\.\./privado/[\w.-]+\.js"[^>]*></script>\n*', "", s)
    # O que vaza é CARREGAMENTO ou DADO, não menção. `PRAZOS_PRIVADOS`, a classe
    # `.pz.privado` e o texto que explica a pasta continuam — sem o arquivo,
    # ficam inertes. O que não pode existir é algo que traga a pasta para dentro.
    carrega = re.findall(r'(?:src|href)\s*=\s*["\'][^"\']*privado/[^"\']*|'
                         r'fetch\s*\(\s*["\'][^"\']*privado/', s)
    if carrega:
        sys.exit("ERRO: a variante publicável carrega privado/: " + "; ".join(carrega))
    if re.search(r"PRAZOS_PRIVADOS\s*=\s*\[\s*\{", s):
        sys.exit("ERRO: prazo de carteira embutido na variante publicável.")
    if re.search(r"PROCESSOS_PRIVADOS\s*=\s*\{", s):
        sys.exit("ERRO: processo de carteira embutido na variante publicável.")
    # a aba completa, de privado/, nunca nasce numa variante publicável
    s = troca(s, "const TEM_PROCESSOS=!!PROC||location.protocol==='file:';",
              "const TEM_PROCESSOS=false;", "a aba de processos do disco")

    # 2. o Artifact fornece o esqueleto do documento
    s = re.sub(r"<!DOCTYPE html>\s*", "", s, flags=re.I)
    # `\s*>` e não `[^>]*>`: sem isso, `</?head[^>]*>` também casa
    # `<header class="masthead">` e come o cabeçalho da página.
    s = re.sub(r"</?html(?:\s[^>]*)?>\s*", "", s, flags=re.I)
    s = re.sub(r"</?head\s*>\s*", "", s, flags=re.I)
    s = re.sub(r"</?body(?:\s[^>]*)?>\s*", "", s, flags=re.I)
    if "<header" not in s or 'class="topo"' not in s:
        sys.exit("ERRO: o cabeçalho da página se perdeu na conversão.")
    s = re.sub(r'<meta charset[^>]*>\s*|<meta name="viewport"[^>]*>\s*', "", s, flags=re.I)

    if a.online:
        s = online(s)
    else:
        # 3. somente leitura
        s = s.replace(' contenteditable="true"', "")
        # No ÚLTIMO </style>: o primeiro é o bloco de fontes, e regra que entra antes
        # da folha principal perde a cascata sem avisar.
        corte = s.rindex("</style>")
        s = s[:corte] + SO_LEITURA + s[corte:]

    # No Artifact o <title> é o nome na galeria e na aba. Nome, não legenda.
    s = re.sub(r"<title>.*?</title>", "<title>Radar Jurídico</title>", s, flags=re.S)

    hoje = datetime.date.today().isoformat()
    if not a.online:
        s = s.replace('<div id="aviso-armazenamento"></div>',
                      f'<div class="instantaneo"><b>Instantâneo de consulta</b> — gerado em '
                      f'{hoje} a partir do repositório, sem a camada privada. Para editar, '
                      f'anotar ou registrar aula, use o painel online; esta página '
                      f'não grava nada.</div>\n<div id="aviso-armazenamento"></div>', 1)

    destino = DESTINO_ONLINE if a.online else DESTINO
    destino.write_text(s, encoding="utf-8")
    kb = destino.stat().st_size / 1024
    print(f"escrito {destino.relative_to(RAIZ)} ({kb:.0f} KB) — publique com o Artifact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
