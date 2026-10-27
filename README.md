<p align="center">
  <img src="site/public/mascote-acenando.svg" width="120" alt="Sabichao — coruja com capelo">
</p>

<h1 align="center">Sabichao</h1>
<p align="center"><strong>Seu SUAP na ponta da lingua.</strong></p>
<p align="center">
  Servidor MCP que conecta assistentes de IA ao SUAP IFMA.<br>
  Consulte notas, boletim, projetos, relatorios e Lattes por conversa.<br>
  Gratuito, codigo aberto, consultas e formularios de projetos com confirmacao.
</p>

<p align="center">
  <a href="https://github.com/vnschneider/sabichao/releases"><img alt="Release" src="https://img.shields.io/github/v/release/vnschneider/sabichao?style=flat-square&color=FFB800"></a>
  <a href="https://github.com/vnschneider/sabichao/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-AGPL--3.0-1B2A4A?style=flat-square"></a>
  <a href="https://pypi.org/project/sabichao"><img alt="PyPI" src="https://img.shields.io/pypi/v/sabichao?style=flat-square&color=FFB800"></a>
</p>

---

## Instalacao

**Windows** (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/vnschneider/sabichao/main/install.ps1 | iex"
```

**macOS / Linux**:

```bash
curl -LsSf https://raw.githubusercontent.com/vnschneider/sabichao/main/install.sh | sh
```

O instalador cuida de tudo: Python, navegador, conexao com os apps de IA e login no SUAP.

## O que ele faz

| Funcionalidade | Descricao |
|---|---|
| **Notas e boletim** | Boletim do semestre, historico completo, atividades complementares |
| **Projetos** | Pesquisa, extensao, ensino — equipe, cronograma, relatorios, pendencias |
| **Frequencia de projetos** | Consulta, orientacao mensal, formularios de atividade e geracao de lista |
| **Relatorios** | Normas FAPEMA e IFMA para relatorios parciais e finais |
| **Matricula** | Matriculas por periodo, estagios, TCC, curriculo Lattes |
| **Navegacao** | Acesso generico a qualquer pagina permitida do SUAP |

## Apps de IA suportados

| App | Deteccao automatica |
|---|---|
| Claude Desktop | `claude_desktop_config.json` |
| Claude Code | `claude_code_config.json` |
| Codex (OpenAI) | `codex/config.json` |
| Gemini CLI | `settings.json` |
| OpenCode | `opencode.json` |

O comando `sabichao instalar` detecta os apps instalados e configura cada um automaticamente.

## CLI

```bash
sabichao              # inicia o servidor MCP (stdio)
sabichao instalar     # instala tudo: navegador, apps, login, diagnostico
sabichao login        # abre janela do SUAP para login
sabichao doctor       # diagnostico: o que esta pronto, o que falta
sabichao desinstalar  # remove dos apps de IA
```

## Tools MCP

| Tool | O que faz |
|---|---|
| `login` | Abre janela do SUAP para login (CAPTCHA/Gov.br) |
| `meu_perfil` | Identifica o estudante logado |
| `status_sessao` | Verifica se a sessao esta ativa |
| `aluno_dados_gerais` | Dados gerais e lista de abas disponiveis |
| `aluno_aba` | Conteudo de qualquer aba do aluno (25+ abas) |
| `aluno_matriculas_periodos` | Periodos de matricula |
| `meus_projetos` | Lista projetos de pesquisa/extensao/ensino |
| `projeto_detalhes` | Dados gerais e abas do projeto (14 abas) |
| `projeto_aba` | Conteudo de qualquer aba do projeto |
| `projeto_equipe` | Membros da equipe |
| `curriculo_lattes` | Curriculo Lattes vinculado |
| `orientacao_relatorio` | Normas para relatorios (FAPEMA/IFMA) |
| `orientacao_frequencia` | Skill de frequencia compartilhada com qualquer agente MCP, sem login |
| `projeto_formulario` | Campos, limites HTML e opcoes disponiveis de formularios de projeto |
| `projeto_participantes_frequencia` | Busca paginada de participantes da lista de extensao pelo autocomplete assinado |
| `projeto_enviar` | Envia formulario apos confirmacao; salva respostas PDF localmente |
| `navegar` | Navegacao generica |

### Frequencia em todos os agentes

A fonte unica da skill fica em `src/sabichao/skills/sabichao-frequencia/SKILL.md`
e acompanha o pacote Python (wheel), nao apenas o checkout do Claude. Todo app
conectado ao mesmo MCP atualizado pode carregar `orientacao_frequencia` ou o
recurso `suap://orientacoes/frequencia`. As instrucoes iniciais do servidor
indicam essa tool; nao e preciso copiar skills para configuracoes de cada app.
O atalho em `.claude/skills/` apenas aponta para a mesma orientacao.

Distribuicao sugerida, nao norma institucional: confirmar carga do edital; como
referencia, 12h/semana em 3 dias uteis de 4h, excluindo feriados confirmados da
localidade. Na semana que atravessa meses, sao 12h **entre os dois meses**, sem
duplicacao. Consulte o mes vizinho antes de calcular saldo. Dois encontros de
6h no mes-alvo sao alternativa apenas quando houver saldo e dias elegiveis.
O usuario pode ajustar a proposta; calendario sugerido nao comprova presenca.

Na extensao, use a aba `registro_frequencia`. Descubra acoes na aba antes de
abrir os formularios. Para um dia, `data_fim` pode ser igual a `data`;
`carga_horaria` e diaria. Nao use intervalos para dias nao consecutivos.
Mostre a previa e obtenha confirmacao antes de enviar. Reconsulte a aba para
conferir persistencia; apos timeout, nao repita POST sem verificar duplicatas.

`projeto_enviar` reconhece PDF pela assinatura e salva com nome local unico em
`~/sabichao/documentos/` (ou `SUAP_MCP_HOME/documentos/`). Retorna caminho e
tamanho; disponibilizar esse arquivo no chat depende do agente. Outros formatos
binarios retornam limitacao explicita, nao falso sucesso. Para participante com
select dinamico, use `projeto_participantes_frequencia`: consulta somente o endpoint
assinado do formulario da lista e retorna valor/texto, sem expor tokens. Nao
invente o ID do vinculo nem confunda com o ID do membro da equipe.
Os PDFs podem conter dados pessoais: ficam no computador do MCP e nao sao
apagados automaticamente. Remova-os quando nao forem mais necessarios.

Depois de atualizar o pacote, reinicie a conexao MCP nos apps para recarregar
tools, recursos e instrucoes. Isso nao instala nem conecta agentes novos.

Testes isolados: `python -m pytest` (ambiente de desenvolvimento). Cobrem POST
com CSRF, reconsulta de persistencia em SUAP simulado, erros de validacao,
timeout sem reenvio e PDF local. Cadastro real, expansao de intervalo e formato
real da lista ainda precisam de validacao acompanhada com dados confirmados.
Consulta real (sem gravar frequencias) confirmou os dois formularios e a busca
assinada de participante no projeto 7187. A consulta de autocomplete usa POST
somente para busca, diferente do POST que registra atividades.

## Seguranca

- **Nao ve sua senha** — voce entra no SUAP numa janela do navegador; so a sessao fica guardada no cofre de senhas do sistema
- **Escrita controlada** — consultas e formularios de projeto usam allowlists; exclusao e administracao sao bloqueadas. O assistente deve mostrar os dados e pedir confirmacao antes de enviar.
- **Nao manda dados para fora** — seus dados ficam entre o SUAP e o seu computador

## Instalacao manual

```bash
uv tool install sabichao
sabichao instalar
```

Para desenvolvimento:

```bash
git clone https://github.com/vnschneider/sabichao.git
cd sabichao
uv sync
playwright install chromium
uv run sabichao doctor
```

## Estrutura

```
src/sabichao/
  config.py       URL base, keyring, diretorios
  auth.py         Login via Playwright + sessao no keyring
  client.py       Cliente HTTP com allowlist de rotas
  html_utils.py   Parsers genericos (tabelas, definicoes, datas)
  parsers.py      Parsers especializados por pagina
  normas.py       Normas FAPEMA e IFMA para relatorios
  server.py       Servidor MCP (tools, recursos e instrucoes para todos os apps)
  skills/         Orientacao de frequencia incluida no pacote Python
  hosts.py        Deteccao e configuracao de apps de IA
  instalador.py   Logica de instalacao
  mascote.py      Coruja pixel art (poses e animacoes)
  cli.py          CLI: instalar, login, doctor, desinstalar
install.ps1       Instalador one-liner Windows
install.sh        Instalador one-liner macOS/Linux
site/             Site de apresentacao (React + Vite)
```

## Licenca

[AGPL-3.0](LICENSE)
