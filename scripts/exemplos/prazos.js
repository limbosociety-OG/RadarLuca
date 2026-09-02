// Prazos de carteira. Copie para `privado/prazos.js` e edite lá.
//
// `privado/` está no .gitignore, no deny de leitura do settings.json e barrado
// pelo hook de pré-commit — inclusive contra `git add -f`. Este arquivo nunca
// entra em commit e nunca vai para remoto.
//
// É .js e não .json de propósito: o painel abre por file://, onde fetch() de
// outro arquivo é bloqueado pelo navegador, mas <script src> funciona.
//
// Sem o arquivo, o painel funciona igual — só não sabe da sua semana.
window.PRAZOS_PRIVADOS = [
  {
    data: "2026-09-15",              // AAAA-MM-DD. Prazo já vencido some da lista.
    oque: "Contrarrazões — prazo em dias úteis, conferir no andamento",
    processo: "0000000-00.0000.0.00.0000",
    orgao: "TRF-2"
  }
];
