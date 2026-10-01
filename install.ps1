# SUAP MCP: instalador para Windows.
# Uso (PowerShell):
#   powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/vnschneider/suap-mcp/main/install.ps1 | iex"
#
# O que faz: instala o uv (gerenciador de Python da Astral) se faltar, instala o SUAP MCP
# com `uv tool install` e abre o assistente `suap-mcp instalar` (navegador, apps de IA,
# login no SUAP e diagnostico). Nao pede senha de administrador.

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$Origem = if ($env:SUAP_MCP_ORIGEM) { $env:SUAP_MCP_ORIGEM } else {
    'suap-mcp @ https://github.com/vnschneider/suap-mcp/archive/refs/heads/main.zip'
}

function Diga([string]$texto) { Write-Host "  $texto" -ForegroundColor DarkYellow }

Write-Host ''
Write-Host '  SUAP MCP' -ForegroundColor Yellow -NoNewline
Write-Host ' — consulta o SUAP IFMA para estudantes'
Write-Host ''

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Diga 'Instalando o uv (gerenciador de Python)...'
    powershell -NoProfile -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'Nao consegui instalar o uv.' }
}

Diga 'Instalando o SUAP MCP (pode levar 1 ou 2 minutos)...'
uv tool install --force --reinstall-package suap-mcp --python 3.12 $Origem
if ($LASTEXITCODE -ne 0) { throw 'Nao consegui instalar o SUAP MCP.' }
uv tool update-shell *> $null

$bin = (uv tool dir --bin).Trim()
$env:Path = "$bin;$env:Path"
if ($env:SUAP_MCP_SO_INSTALAR) { Diga "Instalado em $bin"; return }
& (Join-Path $bin 'suap-mcp.exe') instalar
