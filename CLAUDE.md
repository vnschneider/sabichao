# SUAP MCP

Servidor MCP para estudantes consultarem o SUAP IFMA. Somente leitura.

## Estrutura

```
src/suap_mcp/
  config.py       - URL base, keyring, diretorios
  auth.py         - Login via Playwright + sessao no keyring
  client.py       - Cliente HTTP com allowlist de rotas (foco estudante)
  html_utils.py   - Parsers genericos (tabelas, definicoes, datas)
  parsers.py      - Parsers especializados por pagina do SUAP
  normas.py       - Normas FAPEMA e IFMA para relatorios de pesquisa
  server.py       - Servidor MCP com 13 tools + 1 resource
  hosts.py        - Deteccao e configuracao de apps de IA (Claude Desktop, Code, Codex, Gemini)
  instalador.py   - Logica de instalacao (navegador, apps, diagnostico)
  cli.py          - CLI: instalar, login, doctor, desinstalar, mcp
install.ps1       - Instalador one-liner Windows
install.sh        - Instalador one-liner macOS/Linux
```

## Tools

- login, meu_perfil, status_sessao - sessao
- aluno_dados_gerais, aluno_aba, aluno_matriculas_periodos - pagina do aluno (25+ abas)
- meus_projetos, projeto_detalhes, projeto_aba, projeto_equipe - projetos (14 abas cada)
- curriculo_lattes - Lattes
- orientacao_relatorio - normas para relatorios (FAPEMA/IFMA)
- navegar - navegacao generica

## CLI

```bash
suap-mcp              # inicia servidor MCP (stdio)
suap-mcp instalar     # navegador + apps de IA + login + diagnostico
suap-mcp login        # abre janela do SUAP para login
suap-mcp doctor       # diagnostico
suap-mcp desinstalar  # remove dos apps de IA
```

## Rodar em desenvolvimento

```bash
uv sync
uv run suap-mcp doctor
```
