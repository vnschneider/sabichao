"""Cliente HTTP do SUAP com allowlist de rotas (foco em estudante).

Paginas de consulta e formularios de projeto sao permitidos.
Rotas administrativas e acoes destrutivas sao bloqueadas.
"""

from __future__ import annotations

import re
import json

import httpx

from sabichao.config import BASE_URL

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

_SEMPRE_BLOQUEADAS = [
    r"/admin/",
    r"breadcrumbs_reset",
    r"/accounts/",
    r"excluir",
    r"deletar",
    r"remover",
]

_ROTAS_ESCRITA = [
    r"/pesquisa/projeto/\d+/",
    r"/pesquisa/[a-z_]+/\d+/",
    r"/projetos/projeto/\d+/",
    r"/projetos/[a-z_]+/\d+/",
    r"/projetos_ensino/projeto/\d+/",
    r"/projetos_ensino/[a-z_]+/\d+/",
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

    # -- Escrita (formularios de projeto) --

    def verificar_rota_escrita(self, caminho: str) -> None:
        if any(re.search(p, caminho) for p in _SEMPRE_BLOQUEADAS):
            raise RotaNaoPermitida(caminho)
        if not any(re.search(p, caminho) for p in _ROTAS_ESCRITA):
            raise RotaNaoPermitida(caminho)

    def _csrf(self, html_texto: str = "") -> str:
        m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)', html_texto)
        if m:
            return m[1]
        return self._http.cookies.get("csrftoken", "")

    def formulario(self, caminho: str) -> tuple[str, list]:
        """GET uma pagina de formulario e retorna (html, formularios)."""
        self.verificar_rota_escrita(caminho)
        resp = self._http.get(caminho)
        if "/accounts/login" in str(resp.url):
            raise SessaoExpirada()
        resp.raise_for_status()
        from sabichao.html_utils import documento, extrair_formularios
        doc = documento(resp.text)
        return resp.text, extrair_formularios(doc)

    def postar(self, caminho: str, dados: dict, csrf_token: str = "") -> httpx.Response:
        """POST dados de formulario para uma rota de projeto."""
        self.verificar_rota_escrita(caminho)
        payload = dict(dados)
        if csrf_token:
            payload["csrfmiddlewaretoken"] = csrf_token
        headers = {"Referer": str(self._http.base_url) + caminho}
        resp = self._http.post(caminho, data=payload, headers=headers)
        if "/accounts/login" in str(resp.url):
            raise SessaoExpirada()
        resp.raise_for_status()
        return resp

    def participantes_frequencia(self, projeto_id: str, consulta: str, pagina: int) -> dict:
        """Consulta somente o autocomplete assinado do formulario de lista de extensao."""
        if not re.fullmatch(r"[0-9]+", projeto_id) or not 1 <= pagina <= 100 or len(consulta) > 100:
            raise ValueError("Projeto, pagina ou consulta invalidos.")
        from sabichao.html_utils import documento
        caminho = f"/projetos/gerar_lista_frequencia/{projeto_id}/"
        html, _ = self.formulario(caminho)
        doc = documento(html)
        select = doc.xpath('//select[@name="participante"]/@id')
        if not select:
            raise ValueError("Campo participante nao encontrado no formulario.")
        scripts = [s.text or "" for s in doc.iter("script") if f'"#{select[0]}"' in (s.text or "")]
        if len(scripts) != 1:
            raise ValueError("Autocomplete do participante nao reconhecido; consulte no SUAP.")
        script = scripts[0]
        url = re.search(r'''url\s*:\s*["']([^"']+)["']''', script)
        control = re.search(r"control\s*:\s*'([^']+)'", script)
        if not url or url[1] != "/json/comum/vinculo/" or not control:
            raise ValueError("Endpoint de participantes nao reconhecido; consulte no SUAP.")
        if not isinstance(json.loads(control[1]), dict):
            raise ValueError("Controle do autocomplete invalido.")
        csrf = self._csrf(html)
        if not csrf:
            raise ValueError("Token CSRF nao encontrado.")
        # Consulta assinada, endpoint fixo, sem seguir redirects com dados privados.
        resp = self._http.post("/json/comum/vinculo/", data={
            "q": consulta, "page": pagina, "control": control[1], "csrfmiddlewaretoken": csrf,
        }, headers={"Referer": str(self._http.base_url).rstrip("/") + caminho,
                    "X-Requested-With": "XMLHttpRequest"}, follow_redirects=False)
        if "/accounts/login" in str(resp.url) or "/accounts/login" in resp.headers.get("location", ""):
            raise SessaoExpirada()
        resp.raise_for_status()
        dados = resp.json()
        if not isinstance(dados, dict) or not isinstance(dados.get("items"), list) or not isinstance(dados.get("total"), int):
            raise ValueError("Resposta de participantes nao reconhecida.")
        return {"participantes": [{"valor": str(i["id"]), "texto": str(i["text"])}
                                  for i in dados["items"]], "total": dados["total"], "pagina": pagina,
                "url_suap": str(self._http.base_url).rstrip("/") + caminho}
