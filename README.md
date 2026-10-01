<p align="center">
  <img src="site/public/mascote-acenando.svg" width="120" alt="Sabichao — coruja com capelo">
</p>

<h1 align="center">Sabichao</h1>
<p align="center"><strong>Seu SUAP na ponta da lingua.</strong></p>
<p align="center">
  Servidor MCP que conecta assistentes de IA ao SUAP IFMA.<br>
  Consulte notas, boletim, projetos, relatorios e Lattes por conversa.<br>
  Gratuito, codigo aberto, somente leitura.
</p>

<p align="center">
  <a href="https://github.com/vnschneider/suap-mcp/releases"><img alt="Release" src="https://img.shields.io/github/v/release/vnschneider/suap-mcp?style=flat-square&color=FFB800"></a>
  <a href="https://github.com/vnschneider/suap-mcp/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-AGPL--3.0-1B2A4A?style=flat-square"></a>
  <a href="https://pypi.org/project/suap-mcp"><img alt="PyPI" src="https://img.shields.io/pypi/v/suap-mcp?style=flat-square&color=FFB800"></a>
</p>

---

## Instalacao

**Windows** (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/vnschneider/suap-mcp/main/install.ps1 | iex"
```

**macOS / Linux**:

```bash
curl -LsSf https://raw.githubusercontent.com/vnschneider/suap-mcp/main/install.sh | sh
```

O instalador cuida de tudo: Python, navegador, conexao com os apps de IA e login no SUAP.

## O que ele faz

| Funcionalidade | Descricao |
|---|---|
| **Notas e boletim** | Boletim do semestre, historico completo, atividades complementares |
| **Projetos** | Pesquisa, extensao, ensino — equipe, cronograma, relatorios, pendencias |
| **Relatorios** | Normas FAPEMA e IFMA para relatorios parciais e finais |
| **Matricula** | Matriculas por periodo, estagios, TCC, curriculo Lattes |
| **Navegacao** | Acesso generico a qualquer pagina permitida do SUAP |

## Apps de IA suportados

| App | Deteccao automatica |
|---|---|
| Claude Desktop | `claude_desktop_config.json` |
| Claude Code | `claude_code_config.json` |
| Codex (OpenAI) | `codex/config.json` |
| Gemini CLI | `settings.json` |
| OpenCode | `opencode.json` |

O comando `suap-mcp instalar` detecta os apps instalados e configura cada um automaticamente.

## CLI

```bash
suap-mcp              # inicia o servidor MCP (stdio)
suap-mcp instalar     # instala tudo: navegador, apps, login, diagnostico
suap-mcp login        # abre janela do SUAP para login
suap-mcp doctor       # diagnostico: o que esta pronto, o que falta
suap-mcp desinstalar  # remove dos apps de IA
```

## Tools MCP

| Tool | O que faz |
|---|---|
| `login` | Abre janela do SUAP para login (CAPTCHA/Gov.br) |
| `meu_perfil` | Identifica o estudante logado |
| `status_sessao` | Verifica se a sessao esta ativa |
| `aluno_dados_gerais` | Dados gerais e lista de abas disponiveis |
| `aluno_aba` | Conteudo de qualquer aba do aluno (25+ abas) |
| `aluno_matriculas_periodos` | Periodos de matricula |
| `meus_projetos` | Lista projetos de pesquisa/extensao/ensino |
| `projeto_detalhes` | Dados gerais e abas do projeto (14 abas) |
| `projeto_aba` | Conteudo de qualquer aba do projeto |
| `projeto_equipe` | Membros da equipe |
| `curriculo_lattes` | Curriculo Lattes vinculado |
| `orientacao_relatorio` | Normas para relatorios (FAPEMA/IFMA) |
| `navegar` | Navegacao generica |

## Seguranca

- **Nao ve sua senha** — voce entra no SUAP numa janela do navegador; so a sessao fica guardada no cofre de senhas do sistema
- **Somente leitura** — as rotas de escrita sao bloqueadas por allowlist
- **Nao manda dados para fora** — seus dados ficam entre o SUAP e o seu computador

## Instalacao manual

```bash
uv tool install suap-mcp
suap-mcp instalar
```

Para desenvolvimento:

```bash
git clone https://github.com/vnschneider/suap-mcp.git
cd suap-mcp
uv sync
playwright install chromium
uv run suap-mcp doctor
```

## Estrutura

```
src/suap_mcp/
  config.py       URL base, keyring, diretorios
  auth.py         Login via Playwright + sessao no keyring
  client.py       Cliente HTTP com allowlist de rotas
  html_utils.py   Parsers genericos (tabelas, definicoes, datas)
  parsers.py      Parsers especializados por pagina
  normas.py       Normas FAPEMA e IFMA para relatorios
  server.py       Servidor MCP (13 tools + 1 resource)
  hosts.py        Deteccao e configuracao de apps de IA
  instalador.py   Logica de instalacao
  mascote.py      Coruja pixel art (poses e animacoes)
  cli.py          CLI: instalar, login, doctor, desinstalar
install.ps1       Instalador one-liner Windows
install.sh        Instalador one-liner macOS/Linux
site/             Site de apresentacao (React + Vite)
```

## Licenca

[AGPL-3.0](LICENSE)
