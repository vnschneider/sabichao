# SUAP MCP

Servidor MCP para estudantes consultarem o SUAP IFMA. Somente leitura.

## Instalacao rapida

**Windows** (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/vnschneider/suap-mcp/main/install.ps1 | iex"
```

**macOS / Linux**:
```bash
curl -LsSf https://raw.githubusercontent.com/vnschneider/suap-mcp/main/install.sh | sh
```

O instalador configura tudo: Python, navegador, conexao com Claude Desktop/Code/Codex/Gemini e login no SUAP.

## Funcionalidades

- **Dados academicos do aluno**: perfil, matriculas por periodo, boletins, historico, atividades complementares, participacoes em projetos, estagios, TCC, matriz curricular
- **Projetos (pesquisa, extensao, ensino)**: listagem, dados do projeto, dados do edital, dados da selecao, equipe, cronograma, plano de aplicacao, plano de desembolso, calculo da pontuacao, anexos, fotos, registros de frequencia/atividade, relatorios, pendencias, conclusao
- **Curriculo Lattes** vinculado ao SUAP
- **Orientacao para relatorios**: normas completas FAPEMA e IFMA (PRPGI) para elaboracao de relatorios parciais e finais
- **Navegacao generica** em qualquer pagina permitida

## CLI

```bash
suap-mcp              # inicia servidor MCP (stdio)
suap-mcp instalar     # navegador + apps de IA + login + diagnostico
suap-mcp login        # abre janela do SUAP para login
suap-mcp doctor       # diagnostico: o que esta pronto, o que falta
suap-mcp desinstalar  # remove dos apps de IA
```

## Instalacao manual

Se preferir instalar manualmente:

```bash
uv tool install suap-mcp
suap-mcp instalar
```

Ou para desenvolvimento:

```bash
uv sync
playwright install chromium
uv run suap-mcp doctor
```

## Tools disponiveis

| Tool | Descricao |
|------|-----------|
| `login` | Login via browser (CAPTCHA/Gov.br) |
| `meu_perfil` | Identifica o estudante logado |
| `status_sessao` | Verifica se a sessao esta ativa |
| `aluno_dados_gerais` | Dados gerais e abas disponiveis |
| `aluno_aba` | Conteudo de qualquer aba do aluno (25+) |
| `aluno_matriculas_periodos` | Periodos de matricula |
| `meus_projetos` | Lista projetos (pesquisa/extensao/ensino) |
| `projeto_detalhes` | Dados gerais do projeto e abas (14) |
| `projeto_aba` | Conteudo de qualquer aba do projeto |
| `projeto_equipe` | Membros da equipe |
| `curriculo_lattes` | Curriculo Lattes no SUAP |
| `orientacao_relatorio` | Normas para elaboracao de relatorios (FAPEMA/IFMA) |
| `navegar` | Navegacao generica |

## Apps de IA suportados

- Claude Desktop
- Claude Code
- Codex (OpenAI)
- Gemini CLI

O comando `suap-mcp instalar` detecta e configura automaticamente os apps instalados.
