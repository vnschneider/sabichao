"""Login no SUAP via janela do navegador e gerenciamento de sessao no keyring.

O SUAP exige CAPTCHA ou Gov.br no login. O usuario loga numa janela pequena;
ao detectar sucesso, capturamos os cookies de sessao e fechamos a janela.
A senha nunca passa pela ferramenta.
"""

from __future__ import annotations

import json

import keyring

from sabichao import config
from sabichao.config import BASE_URL, KEYRING_SERVICE

COOKIES_SESSAO = ("__Host-sessionid", "__Host-csrftoken")
_TEMPO_LOGIN_MS = 10 * 60 * 1000


def login_interativo(base_url: str = BASE_URL) -> dict[str, str]:
    from playwright.sync_api import sync_playwright

    perfil = config.home() / "_navegador"
    opcoes = {"headless": False, "args": ["--window-size=520,760"], "viewport": {"width": 500, "height": 680}}
    with sync_playwright() as p:
        try:
            context = p.chromium.launch_persistent_context(str(perfil), channel="chrome", **opcoes)
        except Exception:
            context = p.chromium.launch_persistent_context(str(perfil), **opcoes)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(f"{base_url}/accounts/login/?next=/")
        page.wait_for_url(
            lambda url: url.startswith(base_url) and "/accounts/login" not in url
            and "/login/govbr" not in url,
            timeout=_TEMPO_LOGIN_MS,
        )
        cookies = {c["name"]: c["value"] for c in context.cookies(base_url)
                   if c["name"] in COOKIES_SESSAO}
        context.close()
    if "__Host-sessionid" not in cookies:
        raise RuntimeError("login nao concluido: cookie de sessao ausente")
    salvar_sessao(cookies, base_url)
    return cookies


def salvar_sessao(cookies: dict[str, str], base_url: str = BASE_URL) -> None:
    keyring.set_password(KEYRING_SERVICE, base_url, json.dumps(cookies))


def carregar_sessao(base_url: str = BASE_URL) -> dict[str, str] | None:
    bruto = keyring.get_password(KEYRING_SERVICE, base_url)
    return json.loads(bruto) if bruto else None


def apagar_sessao(base_url: str = BASE_URL) -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, base_url)
    except keyring.errors.PasswordDeleteError:
        pass
