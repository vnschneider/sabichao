import os
import subprocess

import pytest

from sabichao import cli


def test_windows_aguarda_cli_e_abre_instalador_sem_assistente(monkeypatch, capsys):
    chamadas = []
    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(subprocess, "CREATE_NEW_CONSOLE", 0x10, raising=False)
    monkeypatch.setattr(subprocess, "Popen", lambda args, **kw: chamadas.append((args, kw)))
    assert cli.cmd_update() == 0
    args, kw = chamadas[0]
    script = args[-1]
    assert "Wait-Process -Id " + str(os.getpid()) in script
    assert script.index("Wait-Process") < script.index("irm ")
    assert "SUAP_MCP_SO_INSTALAR" in script
    assert "/sabichao/main/install.ps1" in script
    assert "Read-Host" in script
    assert kw["creationflags"] == 0x10
    saida = capsys.readouterr().out
    assert "iniciada" in saida
    assert "concluida" not in saida


def test_falha_ao_abrir_atualizador_retorna_erro(monkeypatch, capsys):
    monkeypatch.setattr(cli.sys, "platform", "win32")
    monkeypatch.setattr(subprocess, "CREATE_NEW_CONSOLE", 0x10, raising=False)
    def falhar(*args, **kwargs):
        raise OSError("PowerShell indisponivel")
    monkeypatch.setattr(subprocess, "Popen", falhar)
    assert cli.cmd_update() == 1
    assert "instalador" in capsys.readouterr().out


def test_unix_substitui_processo_preserva_env_e_falha_de_download(monkeypatch):
    chamadas = []
    class ProcessoSubstituido(Exception):
        pass
    def executar(exe, args, env):
        chamadas.append((exe, args, env))
        raise ProcessoSubstituido()
    monkeypatch.setattr(cli.sys, "platform", "linux")
    monkeypatch.delenv("SUAP_MCP_SO_INSTALAR", raising=False)
    monkeypatch.setenv("SUAP_MCP_ORIGEM", "origem-configurada")
    monkeypatch.setattr(os, "execvpe", executar)
    with pytest.raises(ProcessoSubstituido):
        cli.cmd_update()
    exe, args, env = chamadas[0]
    assert exe == "/bin/sh"
    assert env["SUAP_MCP_SO_INSTALAR"] == "1"
    assert env["SUAP_MCP_ORIGEM"] == "origem-configurada"
    assert "SUAP_MCP_SO_INSTALAR" not in os.environ
    script = args[-1]
    assert "curl -fsSL" in script and "/sabichao/main/install.sh" in script
    assert '&& sh "$script"' in script
    assert 'exit "$code"' in script
    assert "trap" in script


def test_cli_encaminha_update(monkeypatch):
    monkeypatch.setattr(cli.sys, "argv", ["sabichao", "update"])
    monkeypatch.setattr(cli, "cmd_update", lambda: 7, raising=False)
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 7


@pytest.mark.parametrize("atual,esperado", [("0.4.0", "sabichao update"), ("0.3.0", "install.")])
def test_aviso_mcp_usa_update_so_quando_comando_existe(monkeypatch, atual, esperado):
    import importlib.metadata
    import httpx
    from sabichao import server
    monkeypatch.setattr(server, "_atualizacao_cache", None)
    monkeypatch.setattr(importlib.metadata, "version", lambda name: atual)
    monkeypatch.setattr(httpx, "get", lambda *a, **kw: httpx.Response(200, json={"tag_name": "v0.5.0"}))
    aviso = server._verificar_atualizacao()
    assert esperado in aviso["comando_atualizacao"]


@pytest.mark.skipif(os.name == "nt", reason="Shell Unix real; executado na CI Linux")
@pytest.mark.parametrize("codigo", [0, 22])
def test_shell_unix_propaga_resultado_sem_instalar_de_verdade(monkeypatch, tmp_path, codigo):
    chamadas = []
    class ProcessoSubstituido(Exception):
        pass
    def capturar(exe, args, env):
        chamadas.append((exe, args, env))
        raise ProcessoSubstituido()
    monkeypatch.setattr(cli.sys, "platform", "linux")
    monkeypatch.setattr(os, "execvpe", capturar)
    with pytest.raises(ProcessoSubstituido):
        cli.cmd_update()
    exe, args, env = chamadas[0]
    curl = tmp_path / "curl"
    curl.write_text('#!/bin/sh\n' + (f'exit {codigo}\n' if codigo else 'printf "exit 0\\n" > "$4"\n'))
    curl.chmod(0o700)
    env["PATH"] = str(tmp_path) + os.pathsep + env["PATH"]
    resultado = subprocess.run([exe, *args[1:]], env=env, capture_output=True, text=True, timeout=10)
    assert resultado.returncode == codigo
    assert ("concluida" in resultado.stdout) == (codigo == 0)
