"""Servidor MCP do SUAP — consultas para estudantes.

Experiencia no chat: o assistente consulta dados academicos, projetos, equipes,
cronogramas e informacoes do aluno logado no SUAP IFMA.
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from sabichao import auth, normas, parsers
from sabichao.client import SessaoExpirada, SuapClient
from sabichao.config import BASE_URL

INSTRUCOES = """\
SUAP MCP: consulta dados academicos do SUAP IFMA para o estudante logado. Somente leitura.

QUANDO USAR: sempre que o estudante perguntar sobre notas, boletim, historico, matricula, projetos \
de pesquisa/extensao/ensino, equipe do projeto, cronograma, relatorios, Lattes, atividades \
complementares, estagios, TCC, documentos, ou pedir ajuda para elaborar relatorio de pesquisa.

COMO CONDUZIR:
1. Se o resultado trouxer erro de sessao, chame `login` e avise o estudante para entrar na janela.
2. Comece por `meu_perfil` para descobrir a matricula (guarde-a para as chamadas seguintes).
3. Para dados academicos: `aluno_dados_gerais` mostra as abas; `aluno_aba` abre qualquer uma delas.
4. Para projetos: `meus_projetos` lista; `projeto_detalhes` mostra as abas; `projeto_aba` abre uma.
5. Para relatorios: `orientacao_relatorio` traz as normas (FAPEMA ou IFMA); combine com dados do \
projeto (cronograma, equipe, resultados) e guie o estudante secao por secao.
6. `navegar` e o fallback para qualquer pagina permitida nao coberta pelas ferramentas acima.

IMPORTANTE: Todas as ferramentas sao de leitura. Nenhuma altera dados no SUAP.
"""

servidor = MCPServer(name="sabichao", title="Sabichao - seu SUAP na ponta da lingua", instructions=INSTRUCOES, version="0.1.0")

LEITURA = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
LEITURA_SUAP = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
COLETA = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=True)

_perfil_cache: dict | None = None


def _erro_amigavel(erro: Exception) -> str:
    if isinstance(erro, SessaoExpirada):
        return "A sessao do SUAP expirou. Chame `login` para entrar de novo."
    return f"{type(erro).__name__}: {erro}"


def _cliente() -> SuapClient:
    cookies = auth.carregar_sessao()
    if not cookies:
        raise SessaoExpirada()
    return SuapClient(cookies)


# ============================================================================
# Sessao e Identificacao
# ============================================================================

@servidor.tool(annotations=COLETA)
def login() -> dict:
    """Abre uma janela do SUAP no computador do estudante para login (CAPTCHA/Gov.br). A janela fecha
    sozinha apos o login. Avise o estudante para olhar a janela. Devolve nome e matricula."""
    try:
        cookies = auth.login_interativo()
        with SuapClient(cookies) as client:
            pagina = client.html("/")
            info = parsers.detectar_usuario(pagina)
        return {"logado": True, **info}
    except Exception as e:
        return {"logado": False, "erro": _erro_amigavel(e)}


@servidor.tool(annotations=LEITURA_SUAP)
def meu_perfil() -> dict:
    """PONTO DE PARTIDA: identifica o estudante logado e retorna nome, matricula, curso, situacao e
    abas disponiveis. Chame primeiro para descobrir a matricula (necessaria nas outras ferramentas)."""
    global _perfil_cache
    try:
        with _cliente() as client:
            pagina = client.html("/")
            info = parsers.detectar_usuario(pagina)
            if info.get("matricula"):
                aluno_html = client.html(f"/edu/aluno/{info['matricula']}/")
                info["aluno"] = parsers.parse_aluno_dados_gerais(aluno_html)
            _perfil_cache = info
            return info
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


@servidor.tool(annotations=LEITURA_SUAP)
def status_sessao() -> dict:
    """Verifica se a sessao do SUAP esta ativa. Use antes de uma sequencia de consultas para evitar
    erros repetidos. Se inativa, chame `login`."""
    cookies = auth.carregar_sessao()
    if not cookies:
        return {"ativa": False, "motivo": "Nenhuma sessao salva. Use `login`."}
    try:
        with SuapClient(cookies) as client:
            client.html("/")
        return {"ativa": True}
    except SessaoExpirada:
        return {"ativa": False, "motivo": "Sessao expirada. Use `login`."}
    except Exception as e:
        return {"ativa": False, "motivo": str(e)}


# ============================================================================
# Ensino — Pagina do Aluno
# ============================================================================

@servidor.tool(annotations=LEITURA_SUAP)
def aluno_dados_gerais(matricula: str) -> dict:
    """Dados gerais do aluno: nome, curso, situacao e lista de abas disponiveis.
    A matricula e o codigo como '20181BCC0022'. Use `meu_perfil` para descobri-la."""
    try:
        with _cliente() as client:
            html = client.html(f"/edu/aluno/{matricula}/")
            return parsers.parse_aluno_dados_gerais(html)
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


@servidor.tool(annotations=LEITURA_SUAP)
def aluno_aba(matricula: str, aba: str) -> dict:
    """Le o conteudo de uma aba da pagina do aluno.

    Abas disponiveis (use `aluno_dados_gerais` para ver a lista completa):
    dados_academicos, dados_pessoais, pasta_documental, requisitos_conclusao,
    pedidos_renovacao_matricula, procedimentos_matricula, atividades_complementares,
    tcc_relatorios, medidas_disciplinares_premiacoes, boletins, historico,
    caracterizacao_socioeconomica, atividades_estudantis, dados_bancarios,
    ivs, participacoes_projetos, estagios_afins, locais_horarios,
    requerimentos, nada_consta, documentos_processos, matriz_curricular,
    competicoes_esportivas, atendimentos_saude"""
    try:
        with _cliente() as client:
            html = client.html(f"/edu/aluno/{matricula}/?tab={aba}", aba=True)
            if aba == "dados_academicos":
                return parsers.parse_aluno_dados_academicos(html)
            elif aba == "participacoes_projetos":
                return {"participacoes": parsers.parse_participacoes_projetos(html)}
            elif aba == "estagios_afins":
                return {"estagios": parsers.parse_estagios(html)}
            elif aba == "atividades_complementares":
                return {"atividades": parsers.parse_atividades_complementares(html)}
            elif aba == "boletins":
                return {"boletim": parsers.parse_boletim(html)}
            elif aba == "historico":
                return parsers.parse_historico(html)
            else:
                return parsers.parse_pagina_generica(html)
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


@servidor.tool(annotations=LEITURA_SUAP)
def aluno_matriculas_periodos(matricula: str) -> dict:
    """Lista os periodos de matricula do aluno com situacao de cada um."""
    try:
        with _cliente() as client:
            html = client.html(f"/edu/aluno/{matricula}/")
            periodos = parsers.parse_aluno_matriculas_periodos(html)
            return {"matricula": matricula, "periodos": periodos}
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


# ============================================================================
# Projetos (Pesquisa, Extensao, Ensino)
# ============================================================================

@servidor.tool(annotations=LEITURA_SUAP)
def meus_projetos(tipo: str = "pesquisa") -> dict:
    """Lista os projetos do estudante. tipo: 'pesquisa', 'extensao' ou 'ensino'.
    Retorna titulo, edital, vinculo, situacao e link de cada projeto."""
    prefixo = {"pesquisa": "/pesquisa", "extensao": "/projetos", "ensino": "/projetos_ensino"}.get(tipo)
    if not prefixo:
        return {"erro": f"Tipo invalido: {tipo}. Use: pesquisa, extensao ou ensino."}
    try:
        with _cliente() as client:
            html = client.html(f"{prefixo}/meus_projetos/")
            dados = parsers.parse_meus_projetos(html)
            dados["tipo"] = tipo
            dados["base_url"] = BASE_URL
            return dados
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


@servidor.tool(annotations=LEITURA_SUAP)
def projeto_detalhes(projeto_id: str, tipo: str = "pesquisa") -> dict:
    """Dados gerais de um projeto e lista de abas disponiveis.
    tipo: 'pesquisa', 'extensao' ou 'ensino'.
    projeto_id: o numero do projeto (ex: '11344').

    Abas tipicas de um projeto:
    dados_do_projeto, dados_do_edital, dados_da_selecao, equipe, cronograma,
    plano_de_aplicacao, plano_de_desembolso, calculo_da_pontuacao,
    anexos, fotos, registros_frequencia_atividade, relatorios, pendencias, conclusao"""
    prefixo = {"pesquisa": "/pesquisa", "extensao": "/projetos", "ensino": "/projetos_ensino"}.get(tipo)
    if not prefixo:
        return {"erro": f"Tipo invalido: {tipo}. Use: pesquisa, extensao ou ensino."}
    try:
        with _cliente() as client:
            html = client.html(f"{prefixo}/projeto/{projeto_id}/")
            return parsers.parse_projeto_dados_gerais(html)
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


@servidor.tool(annotations=LEITURA_SUAP)
def projeto_aba(projeto_id: str, aba: str, tipo: str = "pesquisa") -> dict:
    """Le uma aba especifica de um projeto.

    Abas disponiveis (use `projeto_detalhes` para ver a lista real do projeto):
    - dados_do_projeto: datas de execucao, area de conhecimento, grupo de pesquisa, flags
    - dados_do_edital: informacoes do edital vinculado
    - dados_da_selecao: pre-selecao, selecao, pontuacao do curriculo, datas
    - equipe: membros, vinculos, carga horaria, bolsas
    - cronograma: atividades previstas com meses de execucao
    - plano_de_aplicacao: itens orcamentarios previstos
    - plano_de_desembolso: desembolso mensal por rubrica
    - calculo_da_pontuacao: pontuacao do curriculo para selecao
    - anexos: documentos anexados ao projeto
    - fotos: fotos registradas no projeto
    - registros_frequencia_atividade: registros de presenca e atividades
    - relatorios: relatorios parciais e finais
    - pendencias: itens pendentes do projeto
    - conclusao: dados de conclusao/encerramento

    tipo: 'pesquisa', 'extensao' ou 'ensino'."""
    prefixo = {"pesquisa": "/pesquisa", "extensao": "/projetos", "ensino": "/projetos_ensino"}.get(tipo)
    if not prefixo:
        return {"erro": f"Tipo invalido: {tipo}. Use: pesquisa, extensao ou ensino."}
    try:
        with _cliente() as client:
            html = client.html(f"{prefixo}/projeto/{projeto_id}/?tab={aba}", aba=True)
            if aba == "equipe":
                return {"equipe": parsers.parse_projeto_equipe(html)}
            elif aba == "cronograma":
                return parsers.parse_projeto_cronograma(html)
            elif aba == "anexos":
                return {"anexos": parsers.parse_projeto_anexos(html)}
            elif aba == "relatorios":
                return {"relatorios": parsers.parse_projeto_relatorios(html)}
            elif aba == "plano_de_desembolso":
                return parsers.parse_projeto_aba(html, aba)
            elif aba == "plano_de_aplicacao":
                return parsers.parse_projeto_aba(html, aba)
            else:
                return parsers.parse_projeto_aba(html, aba)
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


@servidor.tool(annotations=LEITURA_SUAP)
def projeto_equipe(projeto_id: str, tipo: str = "pesquisa") -> dict:
    """Lista os membros da equipe de um projeto com seus papeis e vinculos."""
    prefixo = {"pesquisa": "/pesquisa", "extensao": "/projetos", "ensino": "/projetos_ensino"}.get(tipo)
    if not prefixo:
        return {"erro": f"Tipo invalido: {tipo}. Use: pesquisa, extensao ou ensino."}
    try:
        with _cliente() as client:
            html = client.html(f"{prefixo}/projeto/{projeto_id}/?tab=equipe", aba=True)
            return {"projeto_id": projeto_id, "equipe": parsers.parse_projeto_equipe(html)}
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


# ============================================================================
# Lattes
# ============================================================================

@servidor.tool(annotations=LEITURA_SUAP)
def curriculo_lattes(lattes_id: str) -> dict:
    """Dados do curriculo Lattes cadastrado no SUAP.
    lattes_id: o numero do curriculo (aparece nos dados do aluno ou na pagina do SUAP).
    Ex: curriculo_lattes('123')"""
    try:
        with _cliente() as client:
            html = client.html(f"/cnpq/curriculo/{lattes_id}/")
            return parsers.parse_lattes(html)
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


# ============================================================================
# Navegacao Generica
# ============================================================================

@servidor.tool(annotations=LEITURA_SUAP)
def navegar(caminho: str, aba: bool = False) -> dict:
    """Navega para qualquer pagina permitida do SUAP e retorna dados estruturados.
    caminho: o path da URL (ex: '/pesquisa/meus_projetos/').
    aba: true se for uma requisicao de aba (AJAX).

    Use para acessar paginas nao cobertas pelas ferramentas especificas.
    Rotas de escrita e administrativas sao bloqueadas por seguranca."""
    try:
        with _cliente() as client:
            html = client.html(caminho, aba=aba)
            return parsers.parse_pagina_generica(html)
    except Exception as e:
        return {"erro": _erro_amigavel(e)}


# ============================================================================
# Elaboracao de Relatorios
# ============================================================================

@servidor.resource("suap://normas/relatorio/{modalidade}")
def recurso_normas_relatorio(modalidade: str) -> str:
    """Normas completas para elaboracao de relatorio de pesquisa.
    modalidade: 'fapema' ou 'ifma'."""
    if modalidade == "fapema":
        return normas.FAPEMA
    elif modalidade == "ifma":
        return normas.IFMA
    return f"Modalidade invalida: {modalidade}. Use: fapema ou ifma."


@servidor.tool(annotations=LEITURA)
def orientacao_relatorio(modalidade: str = "", tipo_relatorio: str = "parcial") -> dict:
    """Retorna as normas e orientacoes completas para elaboracao de relatorio de pesquisa.

    modalidade: 'fapema' (projetos financiados pela FAPEMA/PIBIC Jr) ou
                'ifma' (projetos dos programas de pesquisa PRPGI/IFMA).
                Se vazio, retorna um resumo das duas modalidades para o estudante escolher.

    tipo_relatorio: 'parcial' ou 'final' (afeta quais secoes sao obrigatorias no IFMA).

    COMO USAR COM O ESTUDANTE:
    1. Pergunte qual modalidade do projeto (FAPEMA ou IFMA interno).
    2. Chame esta ferramenta com a modalidade.
    3. Use as ferramentas de projeto (projeto_detalhes, projeto_aba) para buscar dados reais.
    4. Guie o estudante secao por secao, usando os dados do projeto e as normas."""
    if not modalidade:
        return {
            "instrucao": "Pergunte ao estudante qual a modalidade do projeto para obter as normas corretas.",
            "modalidades_disponiveis": normas.RESUMO_MODALIDADES,
        }

    if modalidade not in normas.MODALIDADES:
        return {"erro": f"Modalidade invalida: {modalidade}. Use: fapema ou ifma."}

    resumo = normas.RESUMO_MODALIDADES[modalidade]
    texto = normas.FAPEMA if modalidade == "fapema" else normas.IFMA

    resultado: dict = {
        "modalidade": resumo["nome"],
        "descricao": resumo["descricao"],
        "tipo_relatorio": tipo_relatorio,
        "secoes": resumo["secoes"],
    }

    if modalidade == "ifma":
        resultado["formatacao"] = resumo["formatacao"]
        if tipo_relatorio == "parcial":
            resultado["nota"] = "Relatorio parcial: inclua secao 09 (Etapas a Serem Realizadas) e secao 13 (Cronograma atualizado, se em atraso). NAO inclua secao 12 (Conclusoes)."
        else:
            resultado["nota"] = "Relatorio final: inclua secao 12 (Conclusoes). NAO inclua secao 09 (Etapas a Serem Realizadas)."

    resultado["observacoes"] = resumo["observacoes"]
    resultado["normas_completas"] = texto
    resultado["dica_assistente"] = (
        "Use as ferramentas do MCP para buscar dados do projeto: "
        "projeto_detalhes (titulo, equipe, datas), projeto_aba('cronograma'), "
        "projeto_aba('relatorios'), projeto_aba('anexos'). "
        "Guie o estudante secao por secao conforme as normas acima."
    )

    return resultado


def main() -> None:
    import logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    servidor.run("stdio")


if __name__ == "__main__":
    main()
