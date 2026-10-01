"""Logica de instalacao: navegador, apps de IA, login e diagnostico.

Chamado por `sabichao instalar` apos o script de uma linha (install.ps1/install.sh).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from suap_mcp import auth, config, hosts


@dataclass
class Resultado:
    alvo: str
    ok: bool
    mensagem: str


def navegador_pronto() -> bool:
    return shutil.which("chrome") is not None or shutil.which("google-chrome") is not None or _chrome_windows()


def _chrome_windows() -> bool:
    import platform
    if platform.system() != "Windows":
        return False
    candidatos = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    return any(c.exists() for c in candidatos)


def instalar_chromium() -> Resultado:
    r = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        return Resultado("navegador", False, (r.stderr or r.stdout).strip()[-300:])
    return Resultado("navegador", True, "Chromium baixado")


def apps_detectados() -> list[hosts.Host]:
    return [h for h in hosts.todos() if h.instalado()]


def conectar(apps: list[hosts.Host]) -> list[Resultado]:
    resultados = []
    for app in apps:
        try:
            resultados.append(Resultado(app.nome, True, app.configurar()))
        except Exception as erro:
            resultados.append(Resultado(app.nome, False, str(erro)))
    return resultados


def desconectar_todos() -> list[Resultado]:
    resultados = []
    for app in hosts.todos():
        if not (app.instalado() and app.configurado()):
            continue
        try:
            resultados.append(Resultado(app.nome, True, app.remover()))
        except Exception as erro:
            resultados.append(Resultado(app.nome, False, str(erro)))
    return resultados


def diagnostico() -> list[dict]:
    verificacoes = []
    cookies = auth.carregar_sessao()
    verificacoes.append({
        "item": "Sessao SUAP",
        "ok": cookies is not None,
        "detalhe": "sessao salva no keyring" if cookies else "sem sessao - use `sabichao login`",
    })
    verificacoes.append({
        "item": "Navegador",
        "ok": navegador_pronto(),
        "detalhe": "Google Chrome encontrado" if navegador_pronto() else "instale o Chrome ou rode `playwright install chromium`",
    })
    verificacoes.append({
        "item": "Pasta de dados",
        "ok": config.home().exists(),
        "detalhe": str(config.home()),
    })
    apps = apps_detectados()
    for app in apps:
        verificacoes.append({
            "item": app.nome,
            "ok": app.configurado(),
            "detalhe": "conectado" if app.configurado() else "detectado, nao conectado",
        })
    if not apps:
        verificacoes.append({
            "item": "Apps de IA",
            "ok": False,
            "detalhe": "nenhum app compativel encontrado (Claude Desktop, Claude Code, Codex, Gemini CLI, OpenCode)",
        })
    return verificacoes
