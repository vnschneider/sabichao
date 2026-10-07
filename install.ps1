# Sabichao: instalador para Windows.
# Uso (PowerShell):
#   powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/vnschneider/sabichao/main/install.ps1 | iex"
#
# O que faz: instala o uv (gerenciador de Python da Astral) se faltar, instala o Sabichao
# com `uv tool install` e abre o assistente `sabichao instalar` (navegador, apps de IA,
# login no SUAP e diagnostico). Nao pede senha de administrador.

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$Origem = if ($env:SUAP_MCP_ORIGEM) { $env:SUAP_MCP_ORIGEM } else {
    'sabichao @ https://github.com/vnschneider/sabichao/archive/refs/heads/main.zip'
}

function Diga([string]$texto) { Write-Host "  $texto" -ForegroundColor DarkYellow }

Write-Host ''
Write-Host '  Sabichao' -ForegroundColor Yellow -NoNewline
Write-Host ' - seu SUAP na ponta da lingua'
Write-Host ''

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Diga 'Instalando o uv (gerenciador de Python)...'
    powershell -NoProfile -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'Nao consegui instalar o uv.' }
}

$sabichaoProcs = Get-Process -Name python* -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -like '*uv*tools*sabichao*' }
if ($sabichaoProcs) {
    Diga "Sabichao esta rodando ($($sabichaoProcs.Count) processo(s)). Fechando para atualizar..."
    $sabichaoProcs | Stop-Process -Force
    Start-Sleep -Seconds 1
}

Diga 'Instalando o Sabichao (pode levar 1 ou 2 minutos)...'
uv tool install --force --reinstall-package sabichao --python 3.12 $Origem
if ($LASTEXITCODE -ne 0) { throw 'Nao consegui instalar o Sabichao.' }
uv tool update-shell *> $null

$bin = (uv tool dir --bin).Trim()
$env:Path = "$bin;$env:Path"
if ($env:SUAP_MCP_SO_INSTALAR) { Diga "Instalado em $bin"; return }
& (Join-Path $bin 'sabichao.exe') instalar
