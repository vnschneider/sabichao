"""Parsers especializados para paginas do SUAP (foco em estudante).

Cada funcao recebe HTML bruto e devolve dados estruturados (dicts/listas).
"""

from __future__ import annotations

import re

from suap_mcp.html_utils import (
    Celula,
    definicoes,
    documento,
    extrair_abas,
    id_da_url,
    parse_data,
    secoes_accordion,
    tabelas,
    tabelas_com,
    texto,
)


# ---------------------------------------------------------------------------
# Deteccao do estudante logado
# ---------------------------------------------------------------------------

def detectar_usuario(pagina_html: str) -> dict:
    """Detecta o estudante logado a partir da pagina inicial do SUAP."""
    doc = documento(pagina_html)
    links = [a.get("href", "") for a in doc.iter("a")]
    matricula = None
    for href in links:
        if m := re.search(r"/edu/aluno/(\w+)/", href):
            matricula = m[1]
            break
    nome_el = doc.find('.//span[@class="nome-usuario"]') or doc.find('.//strong')
    nome = texto(nome_el) if nome_el is not None else None
    return {
        "matricula": matricula,
        "nome": nome,
    }


# ---------------------------------------------------------------------------
# Pagina do Aluno (/edu/aluno/{matricula}/)
# ---------------------------------------------------------------------------

_CAMPOS_DADOS_GERAIS_ALUNO = {
    "Nome:", "Matrícula:", "Ingresso:", "E-mail Acadêmico:", "E-mail Google Sala de Aula:",
    "CPF:", "Período de Referência:", "I.R.A.:", "Curso:", "Matriz:", "Qtd. Períodos:",
    "Situação Sistêmica:", "Data da Migração:", "Impressão Digital:", "Emitiu Diploma:",
}


def parse_aluno_dados_gerais(pagina: str) -> dict:
    """Dados gerais e cabecalho da pagina do aluno."""
    doc = documento(pagina)
    titulo = texto(doc.find(".//h2") or doc.find(".//h1"))
    m = re.search(r"(.+?)\s*\((\w+)\)", titulo) if titulo else None
    nome = m[1].strip() if m else titulo
    matricula = m[2] if m else None

    campos = definicoes(doc)
    abas = extrair_abas(doc)
    return {
        "nome": nome,
        "matricula": matricula,
        "campos": campos,
        "abas_disponiveis": abas,
    }


def parse_aluno_dados_academicos(pagina: str) -> dict:
    """Aba 'Dados academicos' do aluno."""
    doc = documento(pagina)
    campos = definicoes(doc)
    secoes = secoes_accordion(doc)
    resultado: dict = {"campos": campos}
    for titulo, corpo in secoes.items():
        resultado[titulo] = definicoes(corpo)
    tabs = tabelas(doc)
    if tabs:
        resultado["tabelas"] = [t.como_dict() for t in tabs]
    return resultado


def parse_aluno_matriculas_periodos(pagina: str) -> list[dict]:
    """Tabela 'Matriculas em periodos' da aba dados academicos."""
    doc = documento(pagina)
    resultado = []
    for t in tabelas_com(doc, "Ano/Período Letivo"):
        for reg in t.registros():
            periodo = reg.get("Ano/Período Letivo", Celula(""))
            turma = reg.get("Turma", Celula(""))
            situacao = reg.get("Situação no Período", Celula(""))
            resultado.append({
                "periodo": periodo.texto,
                "turma": turma.texto,
                "situacao": situacao.texto,
            })
    return resultado


def parse_boletim(pagina: str) -> list[dict]:
    """Boletim de notas de um periodo."""
    doc = documento(pagina)
    resultado = []
    for t in tabelas(doc):
        if not any("Disciplina" in h or "Componente" in h for h in t.cabecalhos):
            continue
        for reg in t.registros():
            item = {h: c.texto for h, c in reg.items()}
            resultado.append(item)
    return resultado


def parse_historico(pagina: str) -> dict:
    """Historico academico."""
    doc = documento(pagina)
    tabs = tabelas(doc)
    campos = definicoes(doc)
    return {
        "campos": campos,
        "tabelas": [t.como_dict() for t in tabs],
    }


def parse_atividades_complementares(pagina: str) -> list[dict]:
    """Atividades complementares do aluno."""
    doc = documento(pagina)
    resultado = []
    for t in tabelas(doc):
        for reg in t.registros():
            resultado.append({h: c.texto for h, c in reg.items()})
    return resultado


def parse_participacoes_projetos(pagina: str) -> list[dict]:
    """Participacoes em projetos (aba do aluno)."""
    doc = documento(pagina)
    resultado = []
    for t in tabelas(doc):
        for reg in t.registros():
            item = {h: c.texto for h, c in reg.items()}
            links = [l for c in reg.values() for l in c.links]
            projeto_link = next((l for l in links if "/projeto/" in l), None)
            if projeto_link:
                item["link_projeto"] = projeto_link
                item["projeto_id"] = id_da_url(projeto_link, "/projeto/")
            resultado.append(item)
    return resultado


def parse_estagios(pagina: str) -> list[dict]:
    """Estagios e afins do aluno."""
    doc = documento(pagina)
    resultado = []
    for t in tabelas(doc):
        for reg in t.registros():
            resultado.append({h: c.texto for h, c in reg.items()})
    return resultado


# ---------------------------------------------------------------------------
# Projetos de Pesquisa/Extensao/Ensino
# ---------------------------------------------------------------------------

def parse_meus_projetos(pagina: str) -> dict:
    """Lista de projetos do usuario (pesquisa, extensao ou ensino)."""
    doc = documento(pagina)
    titulo = texto(doc.find(".//h2") or doc.find(".//h1"))
    total_m = re.search(r"Total de (\d+)", texto(doc))
    total = int(total_m[1]) if total_m else None

    projetos = []
    for t in tabelas(doc):
        for reg in t.registros():
            item = {h: c.texto for h, c in reg.items()}
            links = [l for c in reg.values() for l in c.links]
            projeto_link = next((l for l in links if "/projeto/" in l), None)
            if projeto_link:
                item["link"] = projeto_link
                item["projeto_id"] = id_da_url(projeto_link, "/projeto/")
            projetos.append(item)
    return {"titulo": titulo, "total": total, "projetos": projetos}


def parse_projeto_dados_gerais(pagina: str) -> dict:
    """Dados gerais de um projeto (cabecalho + abas disponiveis)."""
    doc = documento(pagina)
    titulo_pagina = texto(doc.find(".//h2") or doc.find(".//h1"))

    titulo_el = doc.xpath('//*[contains(text(), "Título do Projeto")]')
    titulo_projeto = None
    if titulo_el:
        vizinho = titulo_el[0].getnext()
        if vizinho is not None:
            titulo_projeto = texto(vizinho)

    campos = definicoes(doc)
    abas = extrair_abas(doc)
    secoes = secoes_accordion(doc)

    resultado: dict = {
        "tipo": titulo_pagina,
        "titulo_projeto": titulo_projeto or campos.get("Título do Projeto:", titulo_pagina),
        "campos": campos,
        "abas_disponiveis": abas,
    }
    if secoes:
        for titulo, corpo in secoes.items():
            resultado.setdefault("secoes", {})[titulo] = definicoes(corpo)
    return resultado


def parse_projeto_aba(pagina: str, nome_aba: str) -> dict:
    """Conteudo generico de uma aba de projeto."""
    doc = documento(pagina)
    campos = definicoes(doc)
    tabs = tabelas(doc)
    secoes = secoes_accordion(doc)

    resultado: dict = {"aba": nome_aba}
    if campos:
        resultado["campos"] = campos
    if tabs:
        resultado["tabelas"] = [t.como_dict() for t in tabs]
    if secoes:
        resultado["secoes"] = {k: definicoes(v) for k, v in secoes.items()}

    textos_longos = []
    for el in doc.xpath("//p | //div[contains(@class, 'box-body')]"):
        t = texto(el)
        if len(t) > 100:
            textos_longos.append(t[:2000])
    if textos_longos:
        resultado["conteudo_texto"] = textos_longos[:10]

    return resultado


def parse_projeto_equipe(pagina: str) -> list[dict]:
    """Equipe de um projeto."""
    doc = documento(pagina)
    membros = []

    for t in tabelas(doc):
        for reg in t.registros():
            membro = {h: c.texto for h, c in reg.items()}
            links = [l for c in reg.values() for l in c.links]
            if links:
                membro["links"] = links
            membros.append(membro)

    for box in doc.xpath('//div[contains(@class, "general-box")]'):
        nome_el = box.find(".//a")
        if nome_el is None:
            continue
        dados = definicoes(box)
        status = [texto(s) for s in box.xpath('.//span[contains(@class, "status")]')]
        membros.append({
            "nome": texto(nome_el),
            "link": nome_el.get("href", ""),
            "status": status,
            **dados,
        })

    return membros


def parse_projeto_cronograma(pagina: str) -> dict:
    """Cronograma de um projeto."""
    doc = documento(pagina)
    tabs = tabelas(doc)
    return {"tabelas": [t.como_dict() for t in tabs]}


def parse_projeto_anexos(pagina: str) -> list[dict]:
    """Anexos de um projeto."""
    doc = documento(pagina)
    anexos = []
    for t in tabelas(doc):
        for reg in t.registros():
            item = {h: c.texto for h, c in reg.items()}
            links = [l for c in reg.values() for l in c.links]
            if links:
                item["links"] = links
            anexos.append(item)
    return anexos


def parse_projeto_relatorios(pagina: str) -> list[dict]:
    """Relatorios de um projeto."""
    doc = documento(pagina)
    relatorios = []
    for t in tabelas(doc):
        for reg in t.registros():
            item = {h: c.texto for h, c in reg.items()}
            links = [l for c in reg.values() for l in c.links]
            if links:
                item["links"] = links
            relatorios.append(item)
    return relatorios


# ---------------------------------------------------------------------------
# Lattes
# ---------------------------------------------------------------------------

def parse_lattes(pagina: str) -> dict:
    """Dados do curriculo Lattes no SUAP (/cnpq/curriculo/{id}/)."""
    doc = documento(pagina)
    titulo = texto(doc.find(".//h2") or doc.find(".//h1"))
    campos = definicoes(doc)
    secoes = secoes_accordion(doc)

    resultado: dict = {
        "titulo": titulo,
        "campos": campos,
    }
    if secoes:
        for sec_titulo, corpo in secoes.items():
            tabs = tabelas(corpo)
            defs = definicoes(corpo)
            sec_data: dict = {}
            if defs:
                sec_data["campos"] = defs
            if tabs:
                sec_data["tabelas"] = [t.como_dict() for t in tabs]
            if not sec_data:
                sec_data["texto"] = texto(corpo)[:2000]
            resultado.setdefault("secoes", {})[sec_titulo] = sec_data

    atualizado = re.search(r"Atualizado em\s*(\d{2}/\d{2}/\d{4})", texto(doc))
    if atualizado:
        resultado["atualizado_em"] = atualizado[1]

    return resultado


# ---------------------------------------------------------------------------
# Pagina generica
# ---------------------------------------------------------------------------

def parse_pagina_generica(pagina: str) -> dict:
    """Extrai dados estruturados de qualquer pagina do SUAP."""
    doc = documento(pagina)
    titulo = texto(doc.find(".//h2") or doc.find(".//h1"))
    campos = definicoes(doc)
    tabs = tabelas(doc)
    abas = extrair_abas(doc)
    secoes = secoes_accordion(doc)

    resultado: dict = {"titulo": titulo}
    if campos:
        resultado["campos"] = campos
    if tabs:
        resultado["tabelas"] = [t.como_dict() for t in tabs]
    if abas:
        resultado["abas_disponiveis"] = abas
    if secoes:
        resultado["secoes"] = {}
        for sec_titulo, corpo in secoes.items():
            sec_campos = definicoes(corpo)
            sec_tabs = tabelas(corpo)
            sec: dict = {}
            if sec_campos:
                sec["campos"] = sec_campos
            if sec_tabs:
                sec["tabelas"] = [t.como_dict() for t in sec_tabs]
            resultado["secoes"][sec_titulo] = sec
    return resultado
