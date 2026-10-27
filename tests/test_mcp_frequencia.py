"""Contrato MCP real (stdio), sem credenciais nem chamadas ao SUAP."""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_skill_disponivel_por_tool_e_recurso_mcp():
    async def conferir():
        params = StdioServerParameters(command=sys.executable, args=["-m", "sabichao", "mcp"])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                init = await session.initialize()
                assert "orientacao_frequencia" in init.instructions
                tools = await session.list_tools()
                assert "orientacao_frequencia" in {t.name for t in tools.tools}
                assert "projeto_participantes_frequencia" in {t.name for t in tools.tools}
                orientacao = await session.call_tool("orientacao_frequencia", {})
                assert not orientacao.is_error
                assert "12h no total entre os dois" in str(orientacao.content)
                resources = await session.list_resources()
                assert "suap://orientacoes/frequencia" in {str(r.uri) for r in resources.resources}
                recurso = await session.read_resource("suap://orientacoes/frequencia")
                assert "12h no total entre os dois" in recurso.contents[0].text

    asyncio.run(conferir())
