# Aula 04 — Laboratório de extensões (MCP, Skill, Subagente)

Fonte do enunciado: `Aula-04-MCPs-Skills-e-Subagentes-1.pdf` (seções 3 a 6 e "Laboratório e entrega").
O código de referência está na apostila; este spec registra apenas as decisões que ela deixa em aberto.

## Objetivo

Concluir os 10 passos do roteiro e deixar no repositório os 9 itens da Entrega 1, mais um
`relatorio.md` gerado pela Skill (base da Entrega 2, que o aluno revisa).

## Decisões

| Tema | Decisão | Motivo |
|------|---------|--------|
| Caminho | **Wd (Windows nativo)** | No WSL não há `node` nem `opencode` nativo (o `opencode` visível é o binário Windows via `/mnt/c`). No Windows há `opencode` 1.18.26 com modelos gratuitos, `node`/`npx` e Python 3.14. |
| `.venv` | Recriar com `python -m venv --clear .venv` + `pip install "mcp[cli]"` | O `pyvenv.cfg` atual aponta para `/usr/bin` (criado pelo WSL); `.venv\Scripts\python.exe` não executa. |
| `uv` | `winget install --id=astral-sh.uv -e` | Exigido pelo `mcp dev` e pela verificação do passo 1. |
| Inspector | Rodar o Inspector em modo CLI (`npx @modelcontextprotocol/inspector --cli`) com `.venv\Scripts\python.exe servidor.py` | Mesmo procedimento de host (stdio), verificável sem clique. O modo visual (`mcp dev`) fica disponível para o aluno. |
| `opencode.json` | `command: [".venv\\Scripts\\python.exe", "servidor.py"]`, `cwd: "D:\\Dev\\agente-aula4"` | Tradução Wd da seção 3.7. |
| Sessões do agente | `opencode run` não interativo, modelo gratuito padrão | Permite executar 3.8, 4.2, 5.5 e o passo 10 e registrar a saída. |
| Medição (5.5) | Contar chamadas de ferramenta na saída `--format json` de cada rodada + `opencode stats --days 1` antes/depois | Substitui o `/details` visual; se o provedor gratuito reportar 0 tokens, a contagem de chamadas é a medida (como a apostila prevê). |
| PDF da aula | Acrescentar `*.pdf` ao `.gitignore` | Material do curso, não do projeto; mantém `git status --short` limpo. |
| Branch | Commits direto em `master` | O histórico com commits por seção é o próprio entregável. |
| Nome do repositório | Mantém `agente-aula4` | Renomear para `aula04-extensoes` é decisão do aluno no envio. |

## Componentes (arquivos finais)

1. `servidor.py` — implementação da seção 3.5 (4 ferramentas + recurso `diario://regras`).
2. `dados/turma.csv` — estado após os lançamentos da seção 3.8 (Pedro N3 = 8.5; Carla N2 inalterada em 4.0).
3. `opencode.json` — bloco `mcp.diario`, sem credenciais.
4. `.opencode/skills/relatorio-de-atividade/SKILL.md` — texto da seção 4.2.
5. `.opencode/agents/auditor-de-contexto.md` — texto da seção 5.3 com `permission` (edit/bash/webfetch: deny).
6. `AGENTS.md` — gerado pelo `/init` e corrigido conforme o parecer do auditor.
7. `medicao.md` — rodadas A e B, números e conclusão.
8. `.gitignore` — `.venv/`, `.env`, `__pycache__/`, `*.pdf`.
9. `relatorio.md` — gerado pela Skill.

## Commits previstos

`quatro ferramentas e o recurso de regras` ·
`registro do servidor no opencode` · `lancamentos da sessao` · `skill relatorio-de-atividade` ·
`subagente auditor-de-contexto` · `medicao de contexto` · `AGENTS.md auditado e corrigido` · `relatorio da atividade`.

## Verificação (critérios de aceite)

- `uv --version` e `.venv\Scripts\mcp.exe version` respondem.
- Inspector CLI: `tools/list` mostra as 4 ferramentas; `resumo_turma` devolve
  `aprovado: 2 | exame: 1 | reprovado: 1 | incompleto: 1` + histograma; `diario://regras` devolve as 3 linhas.
- `lancar_nota(2024005, 2, 11)` falha com `nota invalida: 11.0. A nota deve estar entre 0 e 10.` e o CSV fica intacto.
- `opencode mcp list` mostra `diario connected`.
- `opencode agent list` lista `auditor-de-contexto (subagent)`.
- Pedido de relatório sem citar o nome da Skill aciona a ferramenta `skill`.
- `git status --short` vazio ao final; histórico com ≥ 4 commits descritivos.

## Fora do escopo / limites conhecidos

- Revisão humana do `relatorio.md` e a segunda versão do `SKILL.md` (Entrega 2, em casa) — a
  primeira versão fica pronta; se o relatório sair fora do formato, o `SKILL.md` é corrigido e as duas versões ficam no histórico do git.
- O comportamento dos modelos gratuitos pode variar; falhas do agente (não do servidor) são registradas, não mascaradas.
