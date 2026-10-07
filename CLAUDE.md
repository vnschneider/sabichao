# Sabichao (SUAP MCP)

Servidor MCP para estudantes consultarem e gerenciarem projetos no SUAP IFMA.
Nome: Sabichao. Tagline: "seu SUAP na ponta da lingua". Mascote: coruja com capelo (pixel art).

## Estrutura

```
src/sabichao/
  config.py       - URL base, keyring, diretorios
  auth.py         - Login via Playwright + sessao no keyring
  client.py       - Cliente HTTP com allowlist de rotas (leitura + escrita em projetos)
  html_utils.py   - Parsers genericos (tabelas, definicoes, datas, formularios)
  parsers.py      - Parsers especializados por pagina do SUAP
  normas.py       - Normas FAPEMA e IFMA para relatorios de pesquisa
  server.py       - Servidor MCP com 15 tools + 1 resource
  hosts.py        - Deteccao e configuracao de apps de IA (Claude Desktop, Code, Codex, Gemini, OpenCode)
  instalador.py   - Logica de instalacao (navegador, apps, diagnostico)
  mascote.py      - Coruja pixel art com meios-blocos e cores ANSI (poses, animacoes)
  cli.py          - CLI: instalar, login, doctor, desinstalar, mcp
install.ps1       - Instalador one-liner Windows
install.sh        - Instalador one-liner macOS/Linux
```

## Tools

- login, meu_perfil, status_sessao - sessao
- aluno_dados_gerais, aluno_aba, aluno_matriculas_periodos - pagina do aluno (25+ abas)
- meus_projetos, projeto_detalhes, projeto_aba, projeto_equipe - projetos (14 abas cada)
- projeto_formulario, projeto_enviar - escrita em projetos (formularios do SUAP)
- curriculo_lattes - Lattes
- orientacao_relatorio - normas para relatorios (FAPEMA/IFMA)
- navegar - navegacao generica

## CLI

```bash
sabichao              # inicia servidor MCP (stdio)
sabichao instalar     # navegador + apps de IA + login + diagnostico
sabichao login        # abre janela do SUAP para login
sabichao doctor       # diagnostico
sabichao desinstalar  # remove dos apps de IA
```

## Site

```
site/
  package.json     - React 19 + Vite 8 + Framer Motion + Phosphor Icons
  index.html       - SPA entry
  vite.config.js   - Build config (outDir: dist)
  Dockerfile       - Multi-stage: node build -> nginx
  nginx.conf       - Coolify-ready (serve install scripts como text/plain)
  gerar_mascote.py - Converte pixel art do mascote.py para SVG
  src/conteudo.js   - Textos e dados da pagina separados dos componentes
  src/componentes/  - Topo, Heroi, Mascote, Instalar, Recursos, Passos, Apps, Garantias, Perguntas, Rodape
```

Deploy: Coolify com Dockerfile, Base Directory `/site`. Dominio via Traefik.

## Rodar em desenvolvimento

```bash
uv sync
uv run sabichao doctor

# Site:
cd site && npm install && npm run dev
# Regenerar SVGs do mascote:
uv run python site/gerar_mascote.py
```

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**This project has a knowledge graph. Start with the code-review-graph
MCP tools to narrow scope, then read the source.** The graph is cheaper than scanning files and
gives you structural context (callers, dependents, test coverage) that file search cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes_tool` or `query_graph_tool` instead of Grep
- **Understanding impact**: `get_impact_radius_tool` instead of manually tracing imports
- **Code review**: `detect_changes_tool` + `get_review_context_tool` instead of reading entire files
- **Finding relationships**: `query_graph_tool` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview_tool` + `list_communities_tool`

### Verify in the source

- Narrow scope with the graph, then read the source. Do not change code from graph output alone.
- For any non-trivial change, read the implementation and the relevant tests before concluding.
- Verify the exact source when touching behavior, database logic, migrations, retries, fallbacks,
  recovery, or compatibility code.
- When the graph and the source disagree, the source wins. The graph may be stale or may not
  model that relationship.
- An empty graph result can mean "not indexed" or "not statically visible", not "does not exist".

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes_tool` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context_tool` | Need source snippets for review — token-efficient |
| `get_impact_radius_tool` | Understanding blast radius of a change |
| `get_affected_flows_tool` | Finding which execution paths are impacted |
| `query_graph_tool` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes_tool` | Finding functions/classes by name or keyword |
| `get_architecture_overview_tool` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes_tool` for code review.
3. Use `get_affected_flows_tool` to understand impact.
4. Use `query_graph_tool` pattern="tests_for" to check coverage.
<!-- /code-review-graph MCP tools -->
