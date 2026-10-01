"""Apps de IA que rodam o servidor MCP do SUAP MCP: deteccao, configuracao e remocao.

Cada app guarda a configuracao de MCP num lugar diferente. Antes de alterar um arquivo
de configuracao, fazemos backup, e a remocao restaura o original.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

NOME_SERVIDOR = "suap-mcp"


def comando_mcp() -> list[str]:
    return [sys.executable, "-m", "suap_mcp", "mcp"]


def _home() -> Path:
    return Path.home()


def _config_claude_desktop() -> Path:
    sistema = platform.system()
    if sistema == "Windows":
        base = Path(os.environ.get("APPDATA", _home() / "AppData" / "Roaming"))
        return base / "Claude" / "claude_desktop_config.json"
    if sistema == "Darwin":
        return _home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    return _home() / ".config" / "Claude" / "claude_desktop_config.json"


@dataclass
class Host:
    id: str
    nome: str

    def instalado(self) -> bool:
        raise NotImplementedError

    def configurado(self) -> bool:
        raise NotImplementedError

    def configurar(self) -> str:
        raise NotImplementedError

    def remover(self) -> str:
        raise NotImplementedError


def _backup(arquivo: Path) -> None:
    copia = arquivo.with_name(arquivo.name + ".suap-mcp-bak")
    if arquivo.exists() and not copia.exists():
        shutil.copy2(arquivo, copia)


def _ler_json(arquivo: Path) -> dict:
    if not arquivo.exists():
        return {}
    texto = arquivo.read_text(encoding="utf-8-sig").strip()
    if not texto:
        return {}
    return json.loads(texto)


def _gravar_json(arquivo: Path, dados: dict) -> None:
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


class HostJson(Host):
    """Apps configurados por um JSON com a chave `mcpServers` (Claude Desktop, Gemini)."""

    def __init__(self, id: str, nome: str, arquivo: Path, pasta_app: Path,
                 executavel: str | None = None, extras: dict | None = None):
        super().__init__(id, nome)
        self.arquivo = arquivo
        self.pasta_app = pasta_app
        self.executavel = executavel
        self.extras = extras or {}

    def instalado(self) -> bool:
        return self.pasta_app.exists() or bool(self.executavel and shutil.which(self.executavel))

    def configurado(self) -> bool:
        return NOME_SERVIDOR in _ler_json(self.arquivo).get("mcpServers", {})

    def configurar(self) -> str:
        _backup(self.arquivo)
        dados = _ler_json(self.arquivo)
        comando, *args = comando_mcp()
        dados.setdefault("mcpServers", {})[NOME_SERVIDOR] = {"command": comando, "args": args, **self.extras}
        _gravar_json(self.arquivo, dados)
        return f"adicionado em {self.arquivo}"

    def remover(self) -> str:
        dados = _ler_json(self.arquivo)
        if dados.get("mcpServers", {}).pop(NOME_SERVIDOR, None) is None:
            return "nao estava configurado"
        _gravar_json(self.arquivo, dados)
        return f"removido de {self.arquivo}"


class HostCli(Host):
    """Apps configurados pela linha de comando (Claude Code, Codex)."""

    def __init__(self, id: str, nome: str, executavel: str, adicionar: list[str],
                 remover_cmd: list[str], arquivo: Path, marcador: str,
                 permissoes: Path | None = None):
        super().__init__(id, nome)
        self.executavel = executavel
        self._adicionar = adicionar
        self._remover = remover_cmd
        self.arquivo = arquivo
        self.marcador = marcador
        self.permissoes = permissoes

    def instalado(self) -> bool:
        return shutil.which(self.executavel) is not None

    def configurado(self) -> bool:
        return self.arquivo.exists() and re.search(self.marcador, self.arquivo.read_text(encoding="utf-8")) is not None

    def _rodar(self, args: list[str]) -> str:
        exe = shutil.which(self.executavel)
        r = subprocess.run([exe, *args], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout).strip()[:300])
        return (r.stdout or "ok").strip().splitlines()[-1] if (r.stdout or "").strip() else "ok"

    def configurar(self) -> str:
        resultado = self._rodar([*self._adicionar, "--", *comando_mcp()])
        if self.permissoes:
            permitir_no_claude_code(self.permissoes)
        return resultado

    def remover(self) -> str:
        if self.permissoes:
            permitir_no_claude_code(self.permissoes, remover=True)
        return self._rodar(self._remover)


PERMITIR = [f"mcp__{NOME_SERVIDOR}"]


def permitir_no_claude_code(arquivo: Path, remover: bool = False) -> None:
    _backup(arquivo)
    dados = _ler_json(arquivo)
    permissoes = dados.setdefault("permissions", {})
    atuais = [r for r in permissoes.get("allow", []) if r not in PERMITIR]
    permissoes["allow"] = atuais if remover else atuais + PERMITIR
    if not permissoes["allow"]:
        del permissoes["allow"]
    _gravar_json(arquivo, dados)


class HostOpenCode(Host):
    """OpenCode: ~/.config/opencode/opencode.json com mcp.servers."""

    def __init__(self) -> None:
        super().__init__("opencode", "OpenCode")
        self.arquivo = _home() / ".config" / "opencode" / "opencode.json"

    def instalado(self) -> bool:
        return shutil.which("opencode") is not None or self.arquivo.parent.exists()

    def configurado(self) -> bool:
        return NOME_SERVIDOR in _ler_json(self.arquivo).get("mcp", {}).get("servers", {})

    def configurar(self) -> str:
        _backup(self.arquivo)
        dados = _ler_json(self.arquivo)
        dados.setdefault("mcp", {}).setdefault("servers", {})[NOME_SERVIDOR] = {
            "type": "local",
            "command": comando_mcp(),
        }
        _gravar_json(self.arquivo, dados)
        return f"adicionado em {self.arquivo}"

    def remover(self) -> str:
        dados = _ler_json(self.arquivo)
        if dados.get("mcp", {}).get("servers", {}).pop(NOME_SERVIDOR, None) is None:
            return "nao estava configurado"
        _gravar_json(self.arquivo, dados)
        return f"removido de {self.arquivo}"


def todos() -> list[Host]:
    home = _home()
    return [
        HostJson("claude-desktop", "Claude Desktop",
                 _config_claude_desktop(), _config_claude_desktop().parent),
        HostCli("claude-code", "Claude Code", "claude",
                ["mcp", "add", NOME_SERVIDOR, "-s", "user"],
                ["mcp", "remove", NOME_SERVIDOR, "-s", "user"],
                home / ".claude.json", rf'"{NOME_SERVIDOR}"\s*:',
                permissoes=home / ".claude" / "settings.json"),
        HostCli("codex", "Codex (OpenAI)", "codex",
                ["mcp", "add", NOME_SERVIDOR],
                ["mcp", "remove", NOME_SERVIDOR],
                home / ".codex" / "config.toml", rf"\[mcp_servers\.{NOME_SERVIDOR}\]"),
        HostJson("gemini", "Gemini CLI",
                 home / ".gemini" / "settings.json", home / ".gemini", "gemini",
                 extras={"timeout": 600000, "trust": True}),
        HostOpenCode(),
    ]
