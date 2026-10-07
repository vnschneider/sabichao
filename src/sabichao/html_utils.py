"""Parsers genericos para o HTML do SUAP (tabelas, listas de definicao, datas).

As telas do SUAP sao regulares: tabelas com caption/thead/tbody e blocos
dl > div.list-item > dt/dd. Os coletores localizam tabelas pelos cabecalhos
em vez de seletores frageis de posicao.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from lxml import html as lhtml

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def documento(texto_html: str) -> lhtml.HtmlElement:
    return lhtml.fromstring(texto_html)


def texto(el: lhtml.HtmlElement | None) -> str:
    if el is None:
        return ""
    return re.sub(r"\s+", " ", " ".join(el.itertext())).strip()


@dataclass
class Celula:
    texto: str
    links: list[str] = field(default_factory=list)

    def link(self, contem: str) -> str | None:
        return next((h for h in self.links if contem in h), None)


@dataclass
class Tabela:
    caption: str
    cabecalhos: list[str]
    linhas: list[list[Celula]]

    def registros(self) -> list[dict[str, Celula]]:
        return [dict(zip(self.cabecalhos, linha)) for linha in self.linhas]

    def como_dict(self) -> dict:
        return {
            "caption": self.caption,
            "cabecalhos": self.cabecalhos,
            "linhas": [[c.texto for c in linha] for linha in self.linhas],
        }


def tabelas(doc: lhtml.HtmlElement) -> list[Tabela]:
    resultado = []
    for t in doc.iter("table"):
        caption = texto(t.find("caption"))
        cabecalhos = [texto(th) for th in t.xpath("./thead//th")]
        linhas = []
        for tr in t.xpath("./tbody/tr"):
            celulas = [
                Celula(texto(td), [a.get("href") for a in td.iter("a") if a.get("href")])
                for td in tr.xpath("./td")
            ]
            if celulas:
                linhas.append(celulas)
        resultado.append(Tabela(caption, cabecalhos, linhas))
    return resultado


def tabelas_com(doc: lhtml.HtmlElement, *cabecalhos: str) -> list[Tabela]:
    return [
        t for t in tabelas(doc)
        if all(any(c in h for h in t.cabecalhos) for c in cabecalhos)
    ]


def definicoes(el: lhtml.HtmlElement, somente: set[str] | None = None) -> dict[str, str]:
    pares: dict[str, str] = {}
    for dt in el.iter("dt"):
        rotulo = texto(dt)
        if somente is not None and rotulo not in somente:
            continue
        dd = dt.getnext()
        if dd is not None and dd.tag == "dd":
            pares.setdefault(rotulo, texto(dd))
    return pares


def secoes_accordion(doc: lhtml.HtmlElement) -> dict[str, lhtml.HtmlElement]:
    secoes = {}
    for item in doc.xpath('//div[contains(concat(" ", @class, " "), " accordion-item ")]'):
        titulo = texto(item.find(".//h2"))
        corpo = item.xpath('.//div[contains(@class, "accordion-body")]')
        if titulo and corpo:
            secoes[titulo] = corpo[0]
    return secoes


def parse_data(valor: str | None) -> date | None:
    if not valor:
        return None
    v = valor.strip()
    if m := re.search(r"(\d{4})-(\d{2})-(\d{2})", v):
        return date(int(m[1]), int(m[2]), int(m[3]))
    if m := re.search(r"(\d{1,2})[/.](\d{1,2})[/.](\d{4})", v):
        return date(int(m[3]), int(m[2]), int(m[1]))
    if m := re.search(r"(\d{1,2})º?\s+de\s+([A-Za-zçÇ]+)\s+de\s+(\d{4})", v, re.IGNORECASE):
        mes = MESES.get(m[2].lower())
        if mes:
            return date(int(m[3]), mes, int(m[1]))
    return None


def id_da_url(url: str | None, prefixo: str) -> str | None:
    if not url or prefixo not in url:
        return None
    resto = url.split(prefixo, 1)[1]
    return resto.strip("/").split("/")[0] or None


def extrair_abas(doc: lhtml.HtmlElement) -> list[dict[str, str]]:
    """Extrai as abas disponiveis de uma pagina do SUAP (ul.nav-tabs ou similar)."""
    abas = []
    for li in doc.xpath('//ul[contains(@class, "nav-tabs")]//a | //ul[contains(@class, "nav")]//a[contains(@href, "tab=")]'):
        href = li.get("href") or ""
        nome = texto(li)
        tab = None
        if m := re.search(r"[?&]tab=(\w+)", href):
            tab = m[1]
        elif li.get("data-tab"):
            tab = li.get("data-tab")
        if nome and tab:
            abas.append({"nome": nome, "tab": tab})
    return abas


def extrair_badges(doc: lhtml.HtmlElement) -> list[dict[str, str]]:
    """Extrai badges/status (spans com class 'status' ou 'badge')."""
    badges = []
    for span in doc.xpath('//span[contains(@class, "status")] | //span[contains(@class, "badge")]'):
        badges.append({"texto": texto(span), "classe": span.get("class", "")})
    return badges


_ACOES_KEYWORDS = {
    "registrar", "editar", "adicionar", "gerenciar",
    "enviar", "submeter", "cadastrar", "alterar",
    "salvar", "incluir", "anexar",
}


@dataclass
class CampoFormulario:
    nome: str
    tipo: str
    valor: str = ""
    rotulo: str = ""
    opcoes: list[dict[str, str]] = field(default_factory=list)
    obrigatorio: bool = False

    def como_dict(self) -> dict:
        d: dict = {"nome": self.nome, "tipo": self.tipo}
        if self.rotulo:
            d["rotulo"] = self.rotulo
        if self.valor:
            d["valor"] = self.valor
        if self.opcoes:
            d["opcoes"] = self.opcoes
        if self.obrigatorio:
            d["obrigatorio"] = True
        return d


@dataclass
class Formulario:
    acao: str
    metodo: str
    campos: list[CampoFormulario]
    csrf_token: str = ""

    def como_dict(self) -> dict:
        return {
            "acao": self.acao,
            "metodo": self.metodo,
            "campos": [c.como_dict() for c in self.campos],
        }


def _rotulo_campo(form_el: lhtml.HtmlElement, campo: lhtml.HtmlElement) -> str:
    campo_id = campo.get("id", "")
    if campo_id:
        for label in form_el.iter("label"):
            if label.get("for") == campo_id:
                return texto(label).rstrip(": ")
    parent = campo.getparent()
    while parent is not None and parent != form_el:
        if parent.tag == "label":
            return texto(parent).rstrip(": ")
        parent = parent.getparent()
    return ""


def extrair_formularios(doc: lhtml.HtmlElement) -> list[Formulario]:
    """Extrai formularios HTML com seus campos, tipos e valores atuais."""
    formularios: list[Formulario] = []
    for form_el in doc.iter("form"):
        acao = form_el.get("action", "")
        metodo = (form_el.get("method") or "get").upper()
        csrf = ""
        campos: list[CampoFormulario] = []

        for inp in form_el.iter("input"):
            nome = inp.get("name", "")
            if not nome:
                continue
            tipo = inp.get("type", "text").lower()
            valor = inp.get("value", "")
            if nome == "csrfmiddlewaretoken":
                csrf = valor
                continue
            if tipo in ("submit", "button", "image"):
                continue
            obrigatorio = inp.get("required") is not None
            rotulo = _rotulo_campo(form_el, inp)
            campos.append(CampoFormulario(nome=nome, tipo=tipo, valor=valor, rotulo=rotulo, obrigatorio=obrigatorio))

        for ta in form_el.iter("textarea"):
            nome = ta.get("name", "")
            if not nome:
                continue
            obrigatorio = ta.get("required") is not None
            rotulo = _rotulo_campo(form_el, ta)
            campos.append(CampoFormulario(nome=nome, tipo="textarea", valor=texto(ta), rotulo=rotulo, obrigatorio=obrigatorio))

        for sel in form_el.iter("select"):
            nome = sel.get("name", "")
            if not nome:
                continue
            obrigatorio = sel.get("required") is not None
            rotulo = _rotulo_campo(form_el, sel)
            opcoes = []
            valor_sel = ""
            for opt in sel.iter("option"):
                v = opt.get("value", "")
                t = texto(opt)
                if opt.get("selected") is not None:
                    valor_sel = v
                opcoes.append({"valor": v, "texto": t})
            campos.append(CampoFormulario(nome=nome, tipo="select", valor=valor_sel, rotulo=rotulo, opcoes=opcoes, obrigatorio=obrigatorio))

        if campos or csrf:
            formularios.append(Formulario(acao=acao, metodo=metodo, campos=campos, csrf_token=csrf))
    return formularios


_ACOES_EXCLUIR = {"breadcrumbs_reset", "/admin/", "/accounts/"}


def extrair_links_acoes(doc: lhtml.HtmlElement) -> list[dict[str, str]]:
    """Extrai links de acao (botoes, links com verbos de escrita).

    Filtra links de navegacao/sidebar (breadcrumbs_reset, admin, accounts).
    """
    acoes: list[dict[str, str]] = []
    seen: set[str] = set()
    for a in doc.iter("a"):
        href = a.get("href", "").strip()
        t = texto(a).strip()
        if not href or not t or href.startswith("#") or href.startswith("javascript:"):
            continue
        if any(ex in href for ex in _ACOES_EXCLUIR):
            continue
        cls = a.get("class", "")
        is_btn = "btn" in cls
        is_action = any(kw in t.lower() for kw in _ACOES_KEYWORDS)
        if (is_btn or is_action) and href not in seen:
            seen.add(href)
            acoes.append({"texto": t, "url": href})
    return acoes


def pagina_estruturada(html_texto: str) -> dict:
    """Extrai dados estruturados genericos de uma pagina do SUAP."""
    doc = documento(html_texto)
    titulo = texto(doc.find(".//h2") or doc.find(".//h1"))
    defs = definicoes(doc)
    tabs = tabelas(doc)
    abas = extrair_abas(doc)
    secoes = secoes_accordion(doc)
    resultado: dict = {"titulo": titulo}
    if defs:
        resultado["campos"] = defs
    if tabs:
        resultado["tabelas"] = [t.como_dict() for t in tabs]
    if abas:
        resultado["abas_disponiveis"] = abas
    if secoes:
        resultado["secoes"] = {k: definicoes(v) for k, v in secoes.items()}
    return resultado
