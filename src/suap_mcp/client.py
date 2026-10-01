"""Cliente HTTP do SUAP com allowlist de rotas (foco em estudante).

Apenas paginas de consulta do proprio aluno sao permitidas.
Rotas administrativas e acoes de escrita sao bloqueadas.
"""

from __future__ import annotations

import re

import httpx

from suap_mcp.config import BASE_URL

_ROTAS_PERMITIDAS = [
    # -- Pagina do aluno e todas as abas --
    r"/edu/aluno/\w+/(\?.*)?$",

    # -- Pesquisa --
    r"/pesquisa/meus_projetos/(\?.*)?$",
    r"/pesquisa/projeto/\d+/(\?.*)?$",
    r"/pesquisa/meus_recursos/(\?.*)?$",

    # -- Extensao --
    r"/projetos/meus_projetos/(\?.*)?$",
    r"/projetos/projeto/\d+/(\?.*)?$",

    # -- Projetos de Ensino --
    r"/projetos_ensino/meus_projetos/(\?.*)?$",
    r"/projetos_ensino/projeto/\d+/(\?.*)?$",

    # -- Lattes --
    r"/cnpq/curriculo/\d+/$",

    # -- Declaracoes e certificados (somente leitura) --
    r"/edu/declaracao_participacao_projeto_final_pdf/\d+/\w+/(\?.*)?$",
    r"/pesquisa/emitir_(declaracao_participacao|certificado)_pdf/\d+/$",
    r"/projetos/emitir_certificado_extensao_pdf/\d+/$",
    r"/projetos_ensino/emitir_certificado_participacao_pdf/\d+/$",
    r"/arquivo/visualizar_arquivo_pdf/[0-9a-f]+/?$",

    # -- Boletins e historico --
    r"/edu/emitir_boletim_pdf/\d+/\d+/$",
    r"/edu/emitir_historico_pdf/\d+/$",

    # -- Pagina inicial (para detectar tipo de usuario) --
    r"/$",
]

_ROTAS_BLOQUEADAS = [
    r"/admin/",
    r"breadcrumbs_reset",
    r"/accounts/",
    r"submeter",
    r"enviar",
    r"entregar",
    r"cadastrar",
    r"excluir",
    r"deletar",
    r"remover",
]


class SessaoExpirada(Exception):
    pass


class RotaNaoPermitida(Exception):
    pass


class SuapClient:
    def __init__(self, cookies: dict[str, str], base_url: str = BASE_URL,
                 transport: httpx.BaseTransport | None = None):
        self._http = httpx.Client(
            base_url=base_url,
            cookies=cookies,
            follow_redirects=True,
            timeout=60,
            headers={"User-Agent": "sabichao/0.1 (+uso pessoal do estudante)"},
            transport=transport,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> SuapClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def verificar_rota(self, caminho: str) -> None:
        if any(re.search(p, caminho) for p in _ROTAS_BLOQUEADAS):
            raise RotaNaoPermitida(caminho)
        if not any(re.match(p, caminho) for p in _ROTAS_PERMITIDAS):
            raise RotaNaoPermitida(caminho)

    def _get(self, caminho: str, aba: bool = False) -> httpx.Response:
        self.verificar_rota(caminho)
        headers = {"X-Requested-With": "XMLHttpRequest"} if aba else {}
        resp = self._http.get(caminho, headers=headers)
        if "/accounts/login" in str(resp.url):
            raise SessaoExpirada()
        resp.raise_for_status()
        return resp

    def html(self, caminho: str, aba: bool = False) -> str:
        return self._get(caminho, aba=aba).text

    def json(self, caminho: str):
        return self._get(caminho).json()

    def pdf(self, caminho: str) -> bytes:
        conteudo = self._get(caminho).content
        if not conteudo.startswith(b"%PDF"):
            raise ValueError(f"resposta nao e PDF: {caminho}")
        return conteudo
