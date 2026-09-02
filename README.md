# Radar Tributário — repositório

Portal permanente de atualização, acervo e produção editorial em direito tributário.
Sai do Projeto no chat e passa a viver em disco, versionado.

## Instalar

```bash
# 1. Node 18+ e Claude Code
npm install -g @anthropic-ai/claude-code

# 2. Playwright (render dos carrosséis)
pip3 install playwright
python3 -m playwright install chromium

# 3. Hooks do repositório (trava de sigilo)
sh scripts/instalar-hooks.sh

# 4. Conferir o estado
python3 scripts/doctor.py

# 5. Abrir
claude
```

`CLAUDE.md` é lido em toda sessão. É onde vivem as instruções que estavam nas Instruções do
Projeto **mais** a camada de memória que o Projeto injetava sozinho — identidade visual,
voz editorial, aprendizados. Nada disso viaja automaticamente; por isso está escrito.

## Rodar

| O que | Como |
|---|---|
| Diagnóstico do repositório | `python3 scripts/doctor.py` |
| Boletim da semana | `claude` → "boletim" |
| Estudar um tema | `claude` → "estuda modulação de efeitos" |
| Carrossel | `claude` → "faz a peça sobre o Tema X" |
| Regerar mapa e portal | `python3 scripts/gerar.py` |
| Conferir se estão em dia | `python3 scripts/gerar.py --check` |
| Só o gate da OAB | `python3 .claude/skills/carrossel/scripts/compliance.py pecas/.../roteiro.json` |
| Testar o próprio gate | `python3 .claude/skills/carrossel/scripts/testa_compliance.py` |
| Só o render | `python3 .claude/skills/carrossel/scripts/build.py pecas/.../roteiro.json --out ./saida --formato ambos` |
| Painel | abrir `portal/radar-tributario.html` no navegador |

## Estrutura

```
CLAUDE.md                   instruções permanentes — leia antes de mexer em qualquer coisa
base/teses.json             A FONTE DA VERDADE do acervo
base/mapa-de-teses.md       gerado de teses.json — não editar à mão
base/pendencias.md          a prosa do que ainda não foi confirmado
base/posfgv/                caderno da pós
boletins/                   um arquivo por semana
pecas/AAAA-MM-DD-slug/      roteiro.json, legenda.md, png/
portal/                     painel HTML; o bloco de dados é gerado de teses.json
privado/                    NÃO VERSIONADO — carteira, prazos, sigilo
scripts/                    gerar.py · doctor.py · instalar-hooks.sh
.githooks/                  pre-commit: trava de sigilo e de consistência
.claude/skills/             carrossel · radar · boletim
```

## Uma fonte, dois derivados

O acervo vive em `base/teses.json`. `scripts/gerar.py` regrava, a partir dele,
`base/mapa-de-teses.md` e o bloco de dados do painel, entre os marcadores
`/* GERADO:INICIO */` e `/* GERADO:FIM */`.

Editar um derivado à mão é trabalho perdido. O hook de pré-commit reprova commit em que os
derivados estejam atrasados — que é o que impedia mapa e painel de divergirem. Eles já
tinham divergido: o mapa dizia "pautado para 20/08" de temas cuja sessão já havia
acontecido.

O painel guarda as edições de quem o usa (o "e daí?", boletins, caderno de aulas) no
`localStorage` do navegador. Quando o repositório traz uma semente mais nova, ele avisa e
deixa escolher entre adotar o mapa novo ou seguir com o seu — boletins, aulas e backlog
ficam preservados nos dois caminhos. Antes de adotar, `exportar json`.

## Verificação

Toda tese carrega `verificacao` (`confirmado` ou `a_confirmar`), `verificado_em` e, quando
pendente, o texto do que falta. Marca ⚠️ no mapa e no painel. Não é enfeite: **o acervo
migrado do chat tem 27 de 28 teses com fonte secundária nunca cotejada com a origem**, e a
marca existe para que isso não vire peça por distração.

`scripts/doctor.py` cobra reverificação de tese parada há mais de 30 dias.

## Regras do repositório

**`privado/` não entra em commit.** Três camadas, porque as duas primeiras têm furo
conhecido: `.gitignore` (não segura `git add -f`), `deny` de `Read` em
`.claude/settings.json` (não alcança o Bash), e o hook `.githooks/pre-commit`, que barra
qualquer caminho sob `privado/` no índice — com ou sem `-f`. O hook é a que vale; instale.

Conferência manual: `git ls-files | grep privado` tem que voltar vazio.

`git push` esteve no `deny` das permissões até a decisão consciente de qual remoto recebe
o quê. Está liberado para `limbosociety-og/radarluca`. A pergunta que justificava a trava
segue valendo a cada remoto novo: repositório de banca com dado de carteira dentro é
problema de sigilo, não de git.

**Ao editar `.claude/settings.json`, valide o JSON.** Remover uma linha de lista costuma
deixar vírgula sobrando antes do `]`, e aí o arquivo inteiro fica inválido — o risco não é
perder a regra que você tirou, é perder *todas*, inclusive o `deny` de `Read(privado/**)`.
`python3 scripts/doctor.py` reprova arquivo que não faz parse.

**Fontes vendorizadas.** `assets/fonts/` contém Bodoni Moda, Spectral e IBM Plex Mono
(OFL). O build **não baixa fonte**: confere existência, tamanho e assinatura de arquivo, e
para se algo estiver errado. Não substituir por fonte de sistema em nenhuma hipótese.

**O gate não tem bypass.** `compliance.py` reprova e o build morre. Ele lê o roteiro e a
legenda, exige ficha de verificação com no máximo 15 dias, e confere toda citação de
processo contra a ficha. `testa_compliance.py` prova que ele morde — rode ao mexer no
léxico.

## Skills

Este repositório tem três: `carrossel`, `radar`, `boletim`. Os nomes batem com os
diretórios, de propósito — nenhum deles colide com skill instalada na conta.

**Duas identidades visuais convivem, e isso é escolha, não defeito.**

| | sistema | onde vive |
|---|---|---|
| **Deste projeto** | `#17181D` / `#E6E9EE`, Bodoni Moda · Spectral · IBM Plex Mono. É o do carrossel do Tema 1.455. | `.claude/skills/carrossel` |
| **A outra** | Moody Blue `#21324C` + off-white, Cormorant Garamond · Italiana · Instrument, seis batidas. | `producao-carrossel`, na conta |

`producao-carrossel` **não é para remover**. Ela só não é a deste repositório: quando a peça
for daqui, é o sistema do IPTU que vale.

Caso diferente: `carrossel-tributario` e `radar-juridico`, se aparecerem, são cópias antigas
**do mesmo sistema daqui** — parecidas no feed, piores no processo (sem legenda no gate, sem
prazo de validade na ficha, sem fontes versionadas). Prefira as do repositório; pedir pelo
nome (`carrossel`, `radar`) resolve.

`python3 scripts/doctor.py` classifica o que está instalado e diz qual é qual.

## Migração — o que ficou para trás

O Projeto no chat tinha duas skills de carrossel. Elas não eram duplicatas: eram
**identidades diferentes**, e continuam sendo. Este repositório carrega uma delas — a do
carrossel do Tema 1.455, com o stack Bodoni/Spectral/Plex. A outra, `producao-carrossel`,
segue viva na conta e intocada.

O que veio junto foi o formato story 1080×1920, que só a outra tinha implementado. Foi
portado para o template daqui, na tipografia daqui, e está documentado em
`references/editorial.md` — inclusive a faixa que a moldura do Instagram cobre.
