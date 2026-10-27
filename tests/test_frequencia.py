import json
from importlib.resources import files
from urllib.parse import parse_qs

import httpx
import pytest

from sabichao import server
from sabichao.client import SuapClient


FORM = '''<html><form method="post">
<input name="csrfmiddlewaretoken" value="teste-csrf" type="hidden">
<input name="data" type="date" required min="2026-08-03" max="2026-12-31">
<input name="data_fim" type="date">
<input name="carga_horaria" type="number" min="1" max="12" step="1" required>
<textarea name="descricao" required></textarea>
<select name="participante"><option value="7">Participante teste</option></select>
</form></html>'''


def conectar(monkeypatch, handler):
    monkeypatch.setattr(server, "_cliente", lambda: SuapClient(
        {}, transport=httpx.MockTransport(handler)))


def test_orientacao_disponivel_sem_sessao():
    orientacao = server.orientacao_frequencia()
    assert "12h no total entre os dois" in orientacao["orientacao"]
    assert "data_fim" in orientacao["orientacao"]
    assert server.recurso_frequencia() == orientacao["orientacao"]
    assert files("sabichao").joinpath("skills/sabichao-frequencia/SKILL.md").is_file()


def test_formulario_expoe_limites_e_participante(monkeypatch):
    conectar(monkeypatch, lambda r: httpx.Response(200, text=FORM))
    result = server.projeto_formulario("/projetos/cadastrar_frequencia/7187/")
    campos = {c["nome"]: c for c in result["formularios"][0]["campos"]}
    assert campos["carga_horaria"]["limites"] == {"min": "1", "max": "12", "step": "1"}
    assert campos["data"]["obrigatorio"] is True
    assert campos["participante"]["opcoes"] == [{"valor": "7", "texto": "Participante teste"}]
    assert "teste-csrf" not in json.dumps(result)


def test_cadastro_e_reconsulta_de_persistencia(monkeypatch):
    salvos = []

    def suap(request):
        if request.method == "POST":
            dados = parse_qs(request.content.decode())
            assert dados["csrfmiddlewaretoken"] == ["teste-csrf"]
            assert dados["data"] == dados["data_fim"] == ["2026-10-01"]
            salvos.append(dados)
            return httpx.Response(302, headers={"Location": "/projetos/projeto/7187/?tab=registro_frequencia"})
        if request.url.path == "/projetos/projeto/7187/":
            assert len(salvos) == 1
            return httpx.Response(200, text='''<html><table><thead><tr><th>Descrição</th><th>Carga Horária</th></tr></thead>
            <tbody><tr><td>Atividade confirmada</td><td>4</td></tr></tbody></table></html>''')
        return httpx.Response(200, text=FORM)

    conectar(monkeypatch, suap)
    result = server.projeto_enviar("/projetos/cadastrar_frequencia/7187/", json.dumps({
        "data": "2026-10-01", "data_fim": "2026-10-01",
        "carga_horaria": "4", "descricao": "Atividade confirmada"}))
    assert result["status"] == "enviado"
    assert result["persistencia_verificada"] is False
    aba = server.projeto_aba("7187", "registro_frequencia", "extensao")
    assert "Atividade confirmada" in json.dumps(aba)
    assert len(salvos) == 1


def test_pdf_salvo_sem_usar_nome_remoto(monkeypatch, tmp_path):
    monkeypatch.setenv("SUAP_MCP_HOME", str(tmp_path))
    pdf = b"%PDF-1.4\nconteudo sintetico\n%%EOF"
    conectar(monkeypatch, lambda r: httpx.Response(200, text=FORM) if r.method == "GET" else
             httpx.Response(200, content=pdf, headers={
                 "Content-Type": "application/pdf", "Content-Disposition": 'attachment; filename="../../escape.pdf"'}))
    result = server.projeto_enviar("/projetos/gerar_lista_frequencia/7187/", "{}")
    assert result["status"] == "arquivo_gerado"
    from pathlib import Path
    arquivo = Path(result["arquivo"])
    assert arquivo.parent == tmp_path / "documentos"
    assert arquivo.read_bytes() == pdf
    assert result["tamanho_bytes"] == len(pdf)


@pytest.mark.parametrize("body,headers", [
    (b"nao e PDF", {"Content-Type": "application/pdf"}),
    (b"PK\x03\x04zip", {"Content-Type": "application/octet-stream"}),
])
def test_binario_invalido_nao_vira_sucesso(monkeypatch, tmp_path, body, headers):
    monkeypatch.setenv("SUAP_MCP_HOME", str(tmp_path))
    conectar(monkeypatch, lambda r: httpx.Response(200, text=FORM) if r.method == "GET" else
             httpx.Response(200, content=body, headers=headers))
    result = server.projeto_enviar("/projetos/gerar_lista_frequencia/7187/", "{}")
    assert "erro" in result
    assert not list(tmp_path.rglob("*.pdf"))


def test_validacao_html_preservada(monkeypatch):
    conectar(monkeypatch, lambda r: httpx.Response(200, text=FORM) if r.method == "GET" else
             httpx.Response(200, text='<html><ul class="errorlist"><li>Data inválida</li></ul></html>'))
    result = server.projeto_enviar("/projetos/cadastrar_frequencia/7187/", "{}")
    assert result["status"] == "erro_validacao"
    assert result["erros"] == ["Data inválida"]


def test_timeout_nao_repete_post(monkeypatch):
    posts = []

    def suap(request):
        if request.method == "POST":
            posts.append(request)
            raise httpx.ReadTimeout("tempo esgotado", request=request)
        return httpx.Response(200, text=FORM)

    conectar(monkeypatch, suap)
    result = server.projeto_enviar("/projetos/cadastrar_frequencia/7187/", "{}")
    assert "erro" in result
    assert len(posts) == 1


def test_participante_dinamico_nao_inventa_opcoes(monkeypatch):
    conectar(monkeypatch, lambda r: httpx.Response(200, text=FORM.replace(
        '<option value="7">Participante teste</option>', '')))
    result = server.projeto_formulario("/projetos/gerar_lista_frequencia/7187/")
    campo = next(c for c in result["formularios"][0]["campos"] if c["nome"] == "participante")
    assert "opcoes" not in campo
    assert "dinâmica" in campo["nota"]


def test_formulario_retornado_nao_vira_sucesso(monkeypatch):
    conectar(monkeypatch, lambda r: httpx.Response(200, text=FORM))
    result = server.projeto_enviar("/projetos/gerar_lista_frequencia/7187/", "{}")
    assert result["status"] == "formulario_retornado"
    assert result["formularios"]
    assert "teste-csrf" not in json.dumps(result)


def test_participantes_ajax_assinado(monkeypatch):
    html = FORM.replace('<select name="participante">', '<select id="participante_xyz" name="participante">') + '''
    <script>var input = $("#participante_xyz"); input.select2({ajax:{
    url: "/json/comum/vinculo/", data: function(p){return {
    control: '{"data":"assinatura-privada"}', q:p.term};}}});</script>'''

    def suap(request):
        if request.method == "GET":
            return httpx.Response(200, text=html)
        assert request.url.path == "/json/comum/vinculo/"
        dados = parse_qs(request.content.decode())
        assert dados["control"] == ['{"data":"assinatura-privada"}']
        assert dados["q"] == ["Pessoa"]
        assert dados["csrfmiddlewaretoken"] == ["teste-csrf"]
        return httpx.Response(200, json={"items": [{"id": 7, "text": "Pessoa teste", "html": "<b>Pessoa teste</b>"}], "total": 1})

    conectar(monkeypatch, suap)
    result = server.projeto_participantes_frequencia("7187", "Pessoa")
    assert result["participantes"] == [{"valor": "7", "texto": "Pessoa teste"}]
    assert result["total"] == 1
    assert "assinatura-privada" not in json.dumps(result)


@pytest.mark.parametrize("projeto,pagina", [("../admin", 1), ("7187", 0)])
def test_participantes_rejeita_parametros_antes_de_http(monkeypatch, projeto, pagina):
    def proibido():
        pytest.fail("Nao deve abrir cliente com parametros invalidos")
    monkeypatch.setattr(server, "_cliente", proibido)
    assert "erro" in server.projeto_participantes_frequencia(projeto, pagina=pagina)


def test_participantes_nao_aceita_endpoint_alternativo(monkeypatch):
    html = FORM.replace('<select name="participante">', '<select id="x" name="participante">') + '''
    <script>var input = $("#x"); input.select2({ajax:{url:"https://example.org/roubar", control:'{"data":"x"}'}});</script>'''

    def suap(request):
        assert request.method == "GET"
        return httpx.Response(200, text=html)

    conectar(monkeypatch, suap)
    assert "erro" in server.projeto_participantes_frequencia("7187")


def test_nome_antigo_da_aba_mantem_compatibilidade(monkeypatch):
    def suap(request):
        assert request.url.params["tab"] == "registro_frequencia"
        return httpx.Response(200, text="<html><h1>Frequência</h1></html>")
    conectar(monkeypatch, suap)
    result = server.projeto_aba("7187", "registros_frequencia_atividade", "extensao")
    assert result["url_suap"].endswith("?tab=registro_frequencia")
