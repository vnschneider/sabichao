# Sabichao (SUAP MCP)

Servidor MCP para estudantes consultarem o SUAP IFMA. Somente leitura.
Nome: Sabichao. Tagline: "seu SUAP na ponta da lingua". Mascote: coruja com capelo (pixel art).

## Estrutura

```
src/sabichao/
  config.py       - URL base, keyring, diretorios
  auth.py         - Login via Playwright + sessao no keyring
  client.py       - Cliente HTTP com allowlist de rotas (foco estudante)
  html_utils.py   - Parsers genericos (tabelas, definicoes, datas)
  parsers.py      - Parsers especializados por pagina do SUAP
  normas.py       - Normas FAPEMA e IFMA para relatorios de pesquisa
  server.py       - Servidor MCP com 13 tools + 1 resource
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
