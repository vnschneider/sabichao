export const REPOSITORIO = "https://github.com/vnschneider/sabichao";

const origem = typeof window !== "undefined" && window.location.origin.startsWith("http")
  ? window.location.origin
  : "https://sabichao.fabitz.com.br";

export const INSTALACAO = {
  windows: {
    rotulo: "Windows",
    comando: `powershell -ExecutionPolicy ByPass -c "irm ${origem}/install.ps1 | iex"`,
    dica: "Abra o PowerShell pelo menu Iniciar, cole o comando e tecle Enter.",
  },
  unix: {
    rotulo: "macOS e Linux",
    comando: `curl -LsSf ${origem}/install.sh | sh`,
    dica: "Abra o Terminal, cole o comando e tecle Enter. Nao pede senha de administrador.",
  },
};

export const RECURSOS = [
  {
    titulo: "Notas e boletim",
    texto: "Veja suas notas do semestre, boletim completo e historico academico, tudo numa conversa.",
    icone: "notas",
  },
  {
    titulo: "Projetos de pesquisa",
    texto: "Consulte seus projetos de pesquisa, extensao e ensino: equipe, cronograma, relatorios e pendencias.",
    icone: "projetos",
  },
  {
    titulo: "Relatorios",
    texto: "Receba orientacao para escrever relatorios parciais e finais seguindo as normas FAPEMA e IFMA.",
    icone: "relatorios",
  },
  {
    titulo: "Matricula e curriculo",
    texto: "Acompanhe suas matriculas por periodo, atividades complementares, estagios e curriculo Lattes.",
    icone: "matricula",
  },
];

export const PASSOS = [
  {
    titulo: "Instalar",
    texto: "Um comando no terminal. O instalador cuida do Python, do navegador e conecta aos seus apps de IA.",
    icone: "instalar",
  },
  {
    titulo: "Logar",
    texto: "Uma janela do SUAP abre no navegador para voce entrar. Sua senha nunca sai do navegador.",
    icone: "logar",
  },
  {
    titulo: "Perguntar",
    texto: "No Claude, Gemini ou outro app de IA, pergunte sobre suas notas, projetos ou relatorios.",
    icone: "perguntar",
  },
  {
    titulo: "Consultar",
    texto: "O Sabichao busca no SUAP e traz os dados organizados para o assistente responder.",
    icone: "consultar",
  },
];

export const APPS = [
  { nome: "Claude Desktop", logo: "/logos/claude.svg" },
  { nome: "Claude Code", logo: "/logos/claude.svg" },
  { nome: "Codex", logo: "openai" },
  { nome: "Gemini CLI", logo: "/logos/gemini.svg" },
  { nome: "OpenCode", logo: "terminal" },
];

export const GARANTIAS = [
  {
    titulo: "Nao ve sua senha",
    texto: "Voce entra no SUAP numa janela do navegador. So a sessao fica guardada, no cofre de senhas do sistema.",
    icone: "senha",
  },
  {
    titulo: "Somente leitura",
    texto: "O Sabichao consulta seus dados mas nunca altera nada no SUAP. As rotas de escrita sao bloqueadas.",
    icone: "leitura",
  },
  {
    titulo: "Nao manda dados para fora",
    texto: "Seus dados ficam entre o SUAP e o seu computador. O codigo e aberto e pode ser auditado.",
    icone: "dados",
  },
];

export const PERGUNTAS = [
  {
    pergunta: "Preciso pagar?",
    resposta:
      "Nao. O Sabichao e gratuito e de codigo aberto (licenca AGPL-3.0). Para conversar com ele, voce usa o assistente de IA que ja tem, como o Claude.",
  },
  {
    pergunta: "E uma ferramenta oficial do IFMA?",
    resposta:
      "Nao. E uma ferramenta independente, sem vinculo com o IFMA ou com o SUAP. Ela usa as mesmas telas que voce usa no navegador, com a sua sessao.",
  },
  {
    pergunta: "O que ele consegue consultar?",
    resposta:
      "Notas, boletim, historico, matriculas, projetos de pesquisa/extensao/ensino, equipe, cronograma, relatorios, Lattes, atividades complementares, estagios e TCC.",
  },
  {
    pergunta: "E se eu nao usar assistente de IA?",
    resposta:
      "O Sabichao e um servidor MCP, feito para funcionar com assistentes de IA. Voce precisa de pelo menos um app como Claude Desktop, Claude Code, Codex ou Gemini CLI.",
  },
  {
    pergunta: "Posso desfazer a instalacao?",
    resposta:
      "Sim. O comando sabichao desinstalar tira o Sabichao dos seus apps. Para remover o programa: uv tool uninstall sabichao.",
  },
];
