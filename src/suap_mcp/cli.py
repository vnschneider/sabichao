"""CLI `sabichao` - instalar, login, diagnostico e servidor MCP.

Sabichao: seu SUAP na ponta da lingua.
"""

from __future__ import annotations

import os
import sys

NOME = "Sabichao"
TAGLINE = "seu SUAP na ponta da lingua"


def _cor(texto: str, cor: str) -> str:
    cores = {"verde": "\033[32m", "amarelo": "\033[33m", "vermelho": "\033[31m",
             "negrito": "\033[1m", "apagado": "\033[2m", "ciano": "\033[36m"}
    return f"{cores.get(cor, '')}{texto}\033[0m"


def _icone(ok: bool | None) -> str:
    if ok is True:
        return _cor("+", "verde")
    if ok is False:
        return _cor("x", "vermelho")
    return _cor("!", "amarelo")


def _passo(n: int, total: int, titulo: str) -> None:
    print(f"\n  [{n}/{total}] {_cor(titulo, 'negrito')}")


def _linha(ok: bool | None, texto: str, detalhe: str = "") -> None:
    det = f"  {_cor(detalhe, 'apagado')}" if detalhe else ""
    print(f"    {_icone(ok)} {texto}{det}")


def _pergunta(texto: str, padrao: bool, automatico: bool) -> bool:
    if automatico:
        return padrao
    resposta = input(f"    {texto} [{'S/n' if padrao else 's/N'}] ").strip().lower()
    if not resposta:
        return padrao
    return resposta in ("s", "sim", "y", "yes")


def _mascote_banner() -> None:
    try:
        from suap_mcp.mascote import render
        print(render("normal", "pequeno"))
    except Exception:
        pass


def cmd_instalar(automatico: bool = False, apps_escolhidos: list[str] | None = None,
                 com_login: bool = True) -> int:
    """Prepara tudo: navegador, pasta de dados, conexao com apps de IA, login e diagnostico."""
    from suap_mcp import auth, config, instalador

    print()
    _mascote_banner()
    print(f"\n  {_cor(NOME, 'negrito')} - {_cor(TAGLINE, 'ciano')}")
    print(f"  {_cor('Consulta o SUAP IFMA para estudantes. Somente leitura.', 'apagado')}\n")

    total = 4

    _passo(1, total, "Navegador para login no SUAP")
    if instalador.navegador_pronto():
        _linha(True, "Google Chrome encontrado")
    elif _pergunta("Nao achei o Chrome. Baixar o Chromium (~150 MB)?", True, automatico):
        print("    Baixando o Chromium...")
        r = instalador.instalar_chromium()
        _linha(r.ok, r.mensagem)
    else:
        _linha(None, "sem navegador — instale o Google Chrome e rode `sabichao instalar` de novo")

    _passo(2, total, "Pasta de dados")
    pasta = config.home()
    _linha(True, str(pasta))

    _passo(3, total, "Conectar aos assistentes de IA")
    detectados = instalador.apps_detectados()
    if not detectados:
        _linha(None, "nenhum app compativel encontrado",
               "instale o Claude Desktop ou Claude Code e rode `sabichao instalar` de novo")
    escolhidos = []
    for app in detectados:
        if apps_escolhidos is not None:
            marcar = app.id in apps_escolhidos
        elif app.configurado():
            _linha(True, app.nome, "ja conectado")
            continue
        else:
            marcar = _pergunta(f"Conectar ao {app.nome}?", True, automatico)
        if marcar:
            escolhidos.append(app)
    for r in instalador.conectar(escolhidos):
        _linha(r.ok, r.alvo, r.mensagem)
    if any(a.id == "claude-desktop" for a in escolhidos):
        _linha(None, "Feche e abra o Claude Desktop para ele carregar o SUAP MCP.")

    _passo(4, total, "Login no SUAP")
    if auth.carregar_sessao():
        _linha(True, "sessao salva encontrada")
    elif com_login and _pergunta("Abrir janela do SUAP para login agora?", True, automatico):
        try:
            from suap_mcp.client import SuapClient
            from suap_mcp import parsers
            print("    Janela aberta — faca o login nela (fecha sozinha)...")
            cookies = auth.login_interativo()
            with SuapClient(cookies) as client:
                info = parsers.detectar_usuario(client.html("/"))
            nome = (info.get("nome") or "").split()[0] if info.get("nome") else "estudante"
            _linha(True, f"Logado como {nome}!", info.get("matricula", ""))
        except Exception as erro:
            _linha(False, "login nao concluido", f"{erro} — tente depois com `sabichao login`")
    else:
        _linha(None, "rode `sabichao login` quando quiser")

    try:
        from suap_mcp.mascote import render
        print(render("comemorando", "pequeno"))
    except Exception:
        pass
    print(f"\n  {_cor('Pronto!', 'negrito')} No Claude (ou outro app), pergunte sobre suas notas, projetos ou relatorios.\n")
    return 0


def cmd_login() -> int:
    from suap_mcp import auth, parsers
    from suap_mcp.client import SuapClient

    print("Faca login na janela que vai abrir (CAPTCHA/Gov.br). Ela fecha sozinha.")
    try:
        cookies = auth.login_interativo()
        with SuapClient(cookies) as client:
            info = parsers.detectar_usuario(client.html("/"))
        print(f"{_cor('Logado!', 'verde')} {info.get('nome', '')} ({info.get('matricula', '')})")
        return 0
    except Exception as e:
        print(f"{_cor('Erro:', 'vermelho')} {e}")
        return 1


def cmd_doctor() -> int:
    from suap_mcp import instalador

    verificacoes = instalador.diagnostico()
    for v in verificacoes:
        _linha(v["ok"], v["item"], v["detalhe"])
    return 0 if all(v["ok"] for v in verificacoes) else 1


def cmd_desinstalar() -> int:
    from suap_mcp import instalador

    print(f"\n  {_cor(f'Desinstalar {NOME}', 'negrito')}\n")
    resultados = instalador.desconectar_todos()
    for r in resultados:
        _linha(r.ok, r.alvo, r.mensagem)
    if not resultados:
        _linha(True, "nenhum app estava conectado")
    print(f"\n  Para remover o programa: {_cor('uv tool uninstall sabichao', 'negrito')}\n")
    return 0


def cmd_mcp() -> None:
    from suap_mcp.server import main
    main()


def main() -> None:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    args = sys.argv[1:]
    if not args or args[0] == "mcp":
        cmd_mcp()
    elif args[0] == "instalar":
        auto = "--sim" in args
        sem_login = "--sem-login" in args
        sys.exit(cmd_instalar(automatico=auto, com_login=not sem_login))
    elif args[0] == "login":
        sys.exit(cmd_login())
    elif args[0] == "doctor":
        sys.exit(cmd_doctor())
    elif args[0] == "desinstalar":
        sys.exit(cmd_desinstalar())
    elif args[0] in ("-h", "--help", "help"):
        print(f"{NOME} - {TAGLINE}\n")
        print("Comandos:")
        print("  (sem comando)  Inicia o servidor MCP (stdio)")
        print("  instalar       Prepara tudo: navegador, apps de IA, login")
        print("  login          Abre janela do SUAP para login")
        print("  doctor         Diagnostico: o que esta pronto, o que falta")
        print("  desinstalar    Remove o Sabichao dos apps de IA")
        print("\nOpcoes de `instalar`:")
        print("  --sim          Aceita tudo sem perguntar")
        print("  --sem-login    Pula o login no SUAP")
    else:
        print(f"Comando desconhecido: {args[0]}. Use `sabichao --help`.")
        sys.exit(1)
