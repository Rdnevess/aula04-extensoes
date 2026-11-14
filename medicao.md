# Medição de contexto — com e sem subagente (seção 5.5)

**Pergunta (igual nas duas rodadas):** "Investigue o pacote mcp instalado em .venv e me diga, em um parágrafo,
quais transportes ele suporta e em quais arquivos cada um está implementado."

**Ambiente:** OpenCode 1.18.26, modelo `opencode/big-pickle` (gratuito), Windows, `mcp` 2.3.0 no `.venv`.
Cada rodada em sessão nova (`opencode run`). As chamadas foram contadas nos eventos `--format json` da sessão principal,
e os totais vieram da diferença do `opencode stats --days 1` antes e depois de cada rodada.

## Janela principal

| Rodada | Chamadas de ferramenta na sessão principal | Passos do modelo | Input (tokens) | Cache read (tokens) | Contexto no último passo |
|--------|--------------------------------------------|------------------|----------------|---------------------|--------------------------|
| A — sem subagente | 11 (10 `bash`, 1 `glob`) | 7 | 18.053 | 91.520 | 19.818 |
| B — `@explore` | 1 (`task`) | 2 | 11.542 | 13.568 | 13.606 |

## Consumo total (`opencode stats`, diferença de cada rodada)

| Rodada | Sessões criadas | Input | Cache read | Ferramentas |
|--------|-----------------|-------|------------|-------------|
| A | 1 | +18,0K | +91,5K | 10 `bash`, 1 `glob` |
| B | 2 (principal + explore) | +58,8K | +206,2K | 13 `bash`, 12 `read`, 1 `task` |

As duas respostas chegaram ao mesmo conteúdo: transportes stdio, SSE e Streamable HTTP, em
`mcp/client/{stdio,sse,streamable_http}.py` e nos arquivos correspondentes de `mcp/server/`. Na rodada B
o subagente também citou o transporte em memória, `mcp/shared/memory.py`.

## Conclusão

Com a delegação, a janela principal caiu de 11 chamadas e 19,8K tokens de contexto final para 1 chamada e 13,6K,
porque as leituras ficaram na janela do subagente. Em compensação, o consumo total subiu cerca de 3× no input
(58,8K contra 18,0K): o `explore` leu mais arquivos (25 chamadas) do que a sessão direta. Isso confirma a seção 5.1:
o subagente gasta tokens e preserva a janela. Vale a pena quando o gargalo é a janela, e não o custo.
