#!/bin/sh
# Sabichao: instalador para macOS e Linux.
# Uso:
#   curl -LsSf https://raw.githubusercontent.com/vnschneider/suap-mcp/main/install.sh | sh
#
# O que faz: instala o uv (gerenciador de Python da Astral) se faltar, instala o Sabichao
# com `uv tool install` e abre o assistente `suap-mcp instalar` (navegador, apps de IA,
# login no SUAP e diagnostico). Nao usa sudo.
set -eu

ORIGEM="${SUAP_MCP_ORIGEM:-suap-mcp @ https://github.com/vnschneider/suap-mcp/archive/refs/heads/main.zip}"

diga() { printf '  \033[33m%s\033[0m\n' "$1"; }

printf '\n  \033[1;33mSabichao\033[0m - seu SUAP na ponta da lingua\n\n'

if ! command -v uv >/dev/null 2>&1; then
    diga "Instalando o uv (gerenciador de Python)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    PATH="$HOME/.local/bin:$PATH"
    export PATH
fi

diga "Instalando o Sabichao (pode levar 1 ou 2 minutos)..."
uv tool install --force --reinstall-package suap-mcp --python 3.12 "$ORIGEM"
uv tool update-shell >/dev/null 2>&1 || true

BIN="$(uv tool dir --bin)"
PATH="$BIN:$PATH"
export PATH
if [ -n "${SUAP_MCP_SO_INSTALAR:-}" ]; then diga "Instalado em $BIN"; exit 0; fi
if [ -t 1 ] && [ -r /dev/tty ]; then
    "$BIN/suap-mcp" instalar </dev/tty
else
    "$BIN/suap-mcp" instalar --sim --sem-login
fi
