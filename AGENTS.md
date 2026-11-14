# AGENTS.md

Servidor MCP stdio em Python (`servidor.py`) que expõe o diário da turma lendo/gravando
`dados/turma.csv`. O OpenCode o registra em `opencode.json`. O repo também entrega uma Skill e
um subagente da Aula 04 (ver `docs/superpowers/`).

## Comandos (Windows, na raiz)

- Testes: `.venv\Scripts\python.exe -m pytest tests -q`
  Use `python -m pytest`, não `pytest`: só assim a raiz entra no `sys.path` e `import servidor` funciona.
- Um teste: `.venv\Scripts\python.exe -m pytest tests/test_servidor.py::test_situacao -q`
- Servidor: `.venv\Scripts\python.exe servidor.py` (stdio; não imprima nada no terminal)
- Protocolo: `npx -y @modelcontextprotocol/inspector --cli .venv\Scripts\python.exe servidor.py --method tools/list`
- Registro MCP: `opencode mcp list` (reinicie a sessão após editar `opencode.json`)
- Dependências (não há `pyproject.toml`/`requirements.txt`): `.venv\Scripts\python.exe -m pip install "mcp[cli]" pytest`

## Estado conhecido dos testes

`python -m pytest tests -q` hoje dá **3 falhas** (`resumo_turma_contagem`, `boletim_aluno_incompleto`,
`lancar_nota_valida_descreve_efeito`). Elas codificam o CSV antes dos lançamentos da seção 3.8,
mas `dados/turma.csv` já tem Pedro N3 = 8.5. Não altere `servidor.py` para "consertar" isso: ajuste
a expectativa ou restaure os dados, de forma intencional. O fixture `csv_temporario` copia o CSV para
`tmp_path`, então rodar testes nunca altera `dados/turma.csv`.

## Convenções do servidor

- SDK: `from mcp.server import MCPServer` e `ToolError` de `mcp.server.mcpserver.exceptions`.
  Nunca `fastmcp` (API diferente).
- Entrada inválida: `raise ToolError(...)`, nunca retornar string de erro.
- Sem `print()`: o transporte é stdio; use `logging`.
- `dados/turma.csv` é a única persistência; `lancar_nota` reescreve o arquivo inteiro.
- Regras duplicadas de propósito: pesos 3/3/4 e cortes 7.0/5.0 existem em `servidor.py`, no recurso
  `diario://regras` e nos testes — mantenha os três em sincronia.
- Saídas e mensagens em pt-BR, sem acentos no código; commits em português.

## Extensões do OpenCode

- `opencode.json` usa caminhos Windows absolutos (`cwd: D:\Dev\agente-aula4`). Se o repo mudar de
  lugar, atualize o `cwd`, senão o MCP `diario` não sobe.
- `.opencode/skills/relatorio-de-atividade/SKILL.md` — acionada quando se pede relatório/entrega;
  gera `relatorio.md`. O `name` do frontmatter deve ser igual ao nome da pasta.
- `.opencode/agents/auditor-de-contexto.md` — subagente sem permissão de edit/bash/webfetch; audita
  este `AGENTS.md` contra seis defeitos de contexto.
- `.opencode/node_modules/` é gerado pelo OpenCode e ignorado.

## Referências (abra quando precisar)

- `docs/superpowers/specs/2026-11-13-aula04-extensoes-design.md` — decisões (Windows nativo, venv, Inspector, commits).
- `docs/superpowers/plans/2026-11-13-aula04-extensoes.md` — passos e comandos originais das tasks.
- `medicao.md` — números medidos da seção 5.5 (com/sem subagente).
- `Aula-04-MCPs-Skills-e-Subagentes-1.pdf` — enunciado do curso, fora do versionamento.
