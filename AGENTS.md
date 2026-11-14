# AGENTS.md

Servidor MCP stdio em Python (`servidor.py`) que expõe o diário da turma lendo/gravando
`dados/turma.csv`. O OpenCode o registra em `opencode.json`. O repo também entrega uma Skill e
um subagente da Aula 04 (seção "Extensões do OpenCode").

## Comandos (Windows, na raiz)

- Testes: `.venv\Scripts\python.exe -m pytest tests -q`
  Use `python -m pytest`, não `pytest`: só assim a raiz entra no `sys.path` e `import servidor` funciona.
- Servidor: `.venv\Scripts\python.exe servidor.py` (stdio; fica aguardando, sem saída)
- Protocolo: `npx -y @modelcontextprotocol/inspector --cli .venv\Scripts\python.exe servidor.py --method tools/list`
- Registro MCP: `opencode mcp list` (reinicie a sessão após editar `opencode.json`)
- Dependências (não há `pyproject.toml`/`requirements.txt`): `.venv\Scripts\python.exe -m pip install "mcp[cli]" pytest`

Os testes usam uma turma fixa (`TURMA_INICIAL` em `tests/test_servidor.py`) e não dependem do estado de `dados/turma.csv`.

## Convenções do servidor

- SDK: `from mcp.server import MCPServer` e `ToolError` de `mcp.server.mcpserver.exceptions`.
  Nunca `fastmcp` (API diferente).
- Entrada inválida: `raise ToolError(...)`, nunca retornar string de erro.
- Sem `print()`: o transporte é stdio; use `logging`.
- `dados/turma.csv` é a única persistência; `lancar_nota` reescreve o arquivo inteiro.
- Pesos 3/3/4 e cortes 7.0/5.0 aparecem em `servidor.py` (`PESOS`, `_situacao`) e no recurso
  `diario://regras` — ao mudar um, mude o outro e os testes.
- Mensagens devolvidas ao modelo em pt-BR sem acento; docstrings podem ter acento. Commits em português.

## Extensões do OpenCode

- `opencode.json` usa `cwd` absoluto (`D:\Dev\agente-aula4`). Se o repo mudar de lugar, atualize o `cwd`, senão o MCP `diario` não sobe.
- `.opencode/skills/relatorio-de-atividade/SKILL.md` — gera `relatorio.md`; o `name` do frontmatter deve ser igual ao nome da pasta.
- `.opencode/agents/auditor-de-contexto.md` — subagente sem edit/bash/webfetch que audita este arquivo.

## Referências

- `docs/superpowers/specs/2026-11-13-aula04-extensoes-design.md` — abra antes de mudar ambiente, caminhos ou o fluxo de commits.
- `medicao.md` — abra só se for refazer a medição da seção 5.5.
- `Aula-04-MCPs-Skills-e-Subagentes-1.pdf` (não versionado) — abra para conferir o enunciado de uma etapa.
