---
name: sabichao-frequencia
description: Planejar, consultar e registrar frequência/atividade diária em projetos do SUAP IFMA e gerar listas de frequência com o Sabichão. Use quando o usuário pedir distribuição de carga horária de bolsista, frequência mensal, diário de atividades, semanas na virada do mês ou lista de frequência de projeto, especialmente de extensão.
---

# Frequência e atividades de projetos

Separe planejamento de comprovação: um calendário sugerido não prova presença. Registre somente atividades realmente realizadas e confirmadas pelo usuário. Não invente datas, horas ou descrições para completar uma meta.

## Identificar e consultar

1. Use `meu_perfil` para identificar o usuário; faça login se necessário.
2. Confirme projeto, participante, mês/ano e carga semanal exigida pelo edital ou vínculo. Consulte `projeto_detalhes` e a equipe quando necessário.
3. Abra `projeto_aba` com a aba real do projeto. No fluxo de extensão observado, ela é `registro_frequencia` (não presumir que o nome descritivo `registros_frequencia_atividade` seja o identificador real).
4. Descubra URLs por `acoes_disponiveis`; não fabrique IDs. Consulte registros existentes, inclusive dos meses vizinhos na semana compartilhada, antes de propor novos lançamentos. Se a ferramenta não permitir obter esses registros, peça os dados ao usuário e marque a contagem como incompleta.
5. Inclua links do SUAP ao apresentar registros ou formulários. Esta orientação também está disponível pela tool `orientacao_frequencia` e pelo recurso `suap://orientacoes/frequencia`, em qualquer cliente MCP compatível.

## Sugerir distribuição mensal

As orientações abaixo são sugestões do usuário, não regras institucionais verificadas. Preferências explícitas podem alterar a distribuição e a meta, mas não dispensam confirmar compatibilidade com o edital e as atividades realizadas.

- Use como referência **12h por semana**, preferencialmente **3 encontros de 4h** em dias úteis. Confirme a carga real; não atribua 12h automaticamente a todo bolsista.
- Use semanas de segunda a domingo para a proposta; informe essa convenção e ajuste se o usuário ou edital definir outra.
- Exclua finais de semana e feriados nacionais, estaduais e municipais. Confirme localidade, calendário aplicável e eventuais suspensões institucionais. Não declare feriados verificados sem fonte/calendário; explicite lacunas.
- Apresente somente as datas do mês-alvo, agrupadas por semana, com subtotais semanais e total mensal. Não fixe o mês em 48h ou 60h: some os lançamentos reais do mês.
- Uma semana que atravessa dois meses tem **12h no total entre os dois**, não 12h em cada mês. Some horas já registradas e propostas nos dois lados; mostre o saldo compartilhado. Se não houver dados do mês vizinho, não assuma saldo zero.
- Para uma semana compartilhada, pode sugerir **2 encontros de 6h dentro do mês-alvo**, apenas se as 12h estiverem disponíveis na semana inteira e houver dois dias elegíveis. Se o outro mês já consumiu parte da meta, distribua só o saldo. Não force dois encontros quando não houver dias suficientes.
- O usuário pode definir outra distribuição/meta. Mostre qualquer mudança explicitamente, sem chamá-la de regra oficial ou ocultar excesso, falta de dias úteis ou conflito com registros existentes. Não transfira horas entre semanas automaticamente.
- Considere datas de execução e vínculo do participante; não proponha atividades fora desses intervalos.

### Prévia para revisão

Mostre data, dia da semana, horas, descrição confirmada e situação (existente ou proposto). Para cada semana compartilhada, mostre também horas do mês vizinho, total semanal combinado e saldo. Separe proposta futura de atividade realizada; peça ajustes antes de qualquer envio.

## Registrar ou editar

Abra a ação com `projeto_formulario` para obter o contrato atual. No cadastro de extensão observado:

| Campo | Significado |
| --- | --- |
| `data` | Data inicial |
| `data_fim` | Até o dia |
| `carga_horaria` | Carga horária diária, não total do intervalo |
| `descricao` | Atividade efetivamente realizada |

Para atividade em um único dia, preencha **`data_fim` igual a `data`**. Isso é válido segundo orientação do usuário. Para dias não consecutivos, prepare lançamentos individuais com início e fim iguais: não use um intervalo que possa incluir feriados ou finais de semana. O comportamento de expansão de intervalos ainda não foi verificado; não suponha que o SUAP pule dias automaticamente.

Na edição observada, existem `data`, `carga_horaria` e `descricao`, sem `data_fim`. Releia o formulário em vez de copiar o payload do cadastro.

Antes de chamar `projeto_enviar`, mostre todos os lançamentos, totais e projeto/participante; obtenha confirmação explícita. Para lote, a confirmação deve cobrir a lista exata. Verifique a resposta e releia a aba para conferir persistência. Em erro ou timeout, confira se o registro foi salvo antes de reenviar, evitando duplicação. Não exclua registros nem valide frequências sem solicitação e confirmação específicas.

## Gerar lista de frequência

Descubra a ação “Gerar Lista de Frequência” e abra seu formulário. Campos observados: `data_inicio`, `data_termino`, `participante` e `situacao` (Todas, Validadas ou Pendentes). Para o select dinâmico da extensão, use `projeto_participantes_frequencia(projeto_id, consulta, pagina)` e escolha o `valor` retornado. Esse é o ID de vínculo, não necessariamente o ID do membro na equipe. A consulta usa o controle assinado do próprio formulário, sem expô-lo. Se falhar ou não houver correspondência inequívoca, consulte o usuário; não invente o valor. Há paginação: confira `total` e consulte as próximas páginas quando necessário.

Confirme período, participante e situação antes de submeter. Gere a lista com base nos registros do SUAP, não no calendário apenas sugerido. Não trate “Aguardando Validação” como validado. Verifique como a resposta entrega o documento; não prometa PDF ou download sem inspecionar o retorno. `projeto_enviar` salva respostas PDF em arquivo local e retorna o caminho; isso não significa que o agente consegue anexar o arquivo no chat. Para outro formato, informe a limitação e forneça o link oficial, sem inventar arquivo gerado. Retorno HTML sem erros não comprova persistência: releia a aba e confira os campos antes de declarar salvo. A geração real e a expansão de intervalos no SUAP ainda precisam de validação acompanhada.

## Exemplos de conferência (sem enviar ao SUAP)

- Semana comum, meta confirmada 12h: 3 dias úteis de 4h totalizam 12h; um feriado exige redistribuição aprovada, não lançamento naquele dia.
- Semana 28/09–04/10/2026, meta 12h: setembro já tem 4h; outubro pode receber só 8h nessa semana, não dois encontros de 6h. As 4h de setembro não entram no total mensal de outubro.
- Semana compartilhada sem horas em nenhum dos meses: dois dias elegíveis do mês-alvo com 6h cada podem completar 12h; o outro mês fica sem saldo nessa semana. Confirme essa concentração com o usuário.
- Semana compartilhada sem dados do mês vizinho: não fechar total ou lançar 12h presumindo ausência de registros; pedir os dados faltantes.
- Evento em 01/10/2026 com 4h: início 2026-10-01, fim 2026-10-01, carga diária 4h, descrição confirmada.
- Usuário prefere 2 dias de 6h em vez de 3 de 4h: aceitar como proposta ajustável se compatível com o vínculo; nunca inferir que esses encontros ocorreram.
