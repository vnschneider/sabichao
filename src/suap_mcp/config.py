"""Configuracao global: URL do SUAP, keyring e diretorios."""

from __future__ import annotations

import os
from pathlib import Path

BASE_URL = os.environ.get("SUAP_MCP_URL", "https://suap.ifma.edu.br")
KEYRING_SERVICE = "suap-mcp"


def home() -> Path:
    definido = os.environ.get("SUAP_MCP_HOME")
    path = Path(definido) if definido else Path.home() / "suap-mcp"
    path.mkdir(parents=True, exist_ok=True)
    return path
