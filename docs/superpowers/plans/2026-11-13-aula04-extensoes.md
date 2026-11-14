# Aula 04 — Laboratório de extensões — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Concluir os passos 1–10 do roteiro da Aula 04 e deixar no repositório os 9 itens da Entrega 1 e o `relatorio.md`.

**Architecture:** Um servidor MCP stdio (`servidor.py`, SDK `mcp` 2.x, classe `MCPServer`) lê/grava `dados/turma.csv`; é registrado no OpenCode via `opencode.json`. Uma Skill (`.opencode/skills/...`) e um subagente (`.opencode/agents/...`) são arquivos Markdown com frontmatter. As sessões do agente rodam com `opencode run` (não interativo).

**Tech Stack:** Python 3.14 (Windows), `mcp[cli]` 2.x, pytest, uv, Node/npx (Inspector), OpenCode 1.18.26 com modelo gratuito.

**Spec:** `docs/superpowers/specs/2026-11-13-aula04-extensoes-design.md`

## Global Constraints

- Caminho Wd: Python do projeto é `.venv\Scripts\python.exe`; comandos em PowerShell ou Git Bash no Windows.
- Import do SDK: `from mcp.server import MCPServer` e `from mcp.server.mcpserver.exceptions import ToolError` (nunca `fastmcp`).
- Em stdio, nada de `print()` no servidor; depuração via `logging`.
- Erros de ferramenta são `raise ToolError(...)`, nunca string de retorno.
- `opencode.json` sem credenciais.
- Usar só o CSV fictício da apostila.
- Mensagens de commit descritivas, em português, sem acento obrigatório.
- `git status --short` deve ficar vazio ao fim de cada task.

---

### Task 1: Ambiente Wd

**Files:** nenhum versionado (`.venv/` é ignorado).

- [ ] **Step 1: Instalar uv**
Run: `winget install --id=astral-sh.uv -e --accept-source-agreements --accept-package-agreements`
Depois, em terminal novo: `uv --version` → `uv 0.x` (≥ 0.12 conforme a apostila; qualquer versão atual serve).

- [ ] **Step 2: Recriar o .venv para Windows**
Run: `python -m venv --clear .venv` e `.venv\Scripts\python.exe -m pip install "mcp[cli]" pytest`

- [ ] **Step 3: Verificar**
Run: `.venv\Scripts\mcp.exe version` → `MCP version 2.x.x`
Run: `.venv\Scripts\python.exe -c "from mcp.server import MCPServer; from mcp.server.mcpserver.exceptions import ToolError"` → sem saída.
Run: `git status --short` → vazio.

---

### Task 2: Servidor completo (seção 3.5) com testes

**Files:**
- Modify: `servidor.py` (substituição integral)
- Create: `tests/test_servidor.py`

**Interfaces:**
- Produces: ferramentas `listar_alunos() -> str`, `boletim(matricula: str) -> str`, `lancar_nota(matricula: str, avaliacao: int, valor: float) -> str`, `resumo_turma() -> str`; recurso `diario://regras`; helpers `_media(linha) -> float | None`, `_situacao(media) -> str`; constante `ARQUIVO: Path`.

- [ ] **Step 1: Escrever os testes**

```python
# tests/test_servidor.py
import shutil
from pathlib import Path

import pytest
from mcp.server.mcpserver.exceptions import ToolError

import servidor

ORIGINAL = Path(__file__).parent.parent / "dados" / "turma.csv"


@pytest.fixture(autouse=True)
def csv_temporario(tmp_path, monkeypatch):
    copia = tmp_path / "turma.csv"
    shutil.copy(ORIGINAL, copia)
    monkeypatch.setattr(servidor, "ARQUIVO", copia)
    return copia


def test_media_ponderada_pesos_3_3_4():
    linha = {"n1": "8.0", "n2": "7.5", "n3": "9.0"}
    assert servidor._media(linha) == 8.25


def test_media_incompleta_quando_falta_nota():
    assert servidor._media({"n1": "6.0", "n2": "7.0", "n3": ""}) is None


@pytest.mark.parametrize("media,esperado", [
    (None, "incompleto"), (7.0, "aprovado"), (6.99, "exame"),
    (5.0, "exame"), (4.99, "reprovado"),
])
def test_situacao(media, esperado):
    assert servidor._situacao(media) == esperado


def test_resumo_turma_contagem():
    assert "aprovado: 2 | exame: 1 | reprovado: 1 | incompleto: 1" in servidor.resumo_turma()


def test_boletim_aluno_incompleto():
    saida = servidor.boletim("2024004")
    assert "N3 (peso 4): nao lancada" in saida
    assert "situacao: incompleto" in saida


def test_boletim_matricula_inexistente():
    with pytest.raises(ToolError, match="nao existe"):
        servidor.boletim("9999999")


def test_lancar_nota_invalida_nao_grava(csv_temporario):
    antes = csv_temporario.read_text(encoding="utf-8")
    with pytest.raises(ToolError, match="nota invalida: 11.0"):
        servidor.lancar_nota("2024005", 2, 11)
    assert csv_temporario.read_text(encoding="utf-8") == antes


def test_lancar_nota_valida_descreve_efeito(csv_temporario):
    saida = servidor.lancar_nota("2024004", 3, 8.5)
    assert saida.startswith("N3 de Pedro de Alcantara: nao lancada -> 8.5.")
    assert "(aprovado)" in saida
    assert "2024004,Pedro de Alcantara,6.0,7.0,8.5" in csv_temporario.read_text(encoding="utf-8")


def test_lancar_nota_avaliacao_invalida():
    with pytest.raises(ToolError, match="avaliacao deve ser"):
        servidor.lancar_nota("2024001", 4, 5.0)


def test_listar_alunos_tem_cinco_linhas_mais_cabecalho():
    assert len(servidor.listar_alunos().splitlines()) == 6


def test_regras():
    assert "N1=3, N2=3, N3=4" in servidor.regras()
```

- [ ] **Step 2: Rodar e ver falhar**
Run: `.venv\Scripts\python.exe -m pytest tests -q`
Expected: FAIL (`AttributeError: module 'servidor' has no attribute '_media'`).

- [ ] **Step 3: Substituir `servidor.py` pelo código da seção 3.5**

```python
"""Servidor MCP do diário da disciplina."""
import csv
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

ARQUIVO = Path(__file__).parent / "dados" / "turma.csv"
COLUNAS = ["matricula", "nome", "n1", "n2", "n3"]
PESOS = (3, 3, 4)

mcp = MCPServer("diario")


def _ler():
    with ARQUIVO.open(encoding="utf-8", newline="") as arq:
        return list(csv.DictReader(arq))


def _gravar(linhas):
    with ARQUIVO.open("w", encoding="utf-8", newline="") as arq:
        escritor = csv.DictWriter(arq, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)


def _media(linha):
    notas = [linha["n1"], linha["n2"], linha["n3"]]
    if any(nota.strip() == "" for nota in notas):
        return None
    soma = sum(float(nota) * peso for nota, peso in zip(notas, PESOS))
    return round(soma / sum(PESOS), 2)


def _situacao(media):
    if media is None:
        return "incompleto"
    if media >= 7.0:
        return "aprovado"
    if media >= 5.0:
        return "exame"
    return "reprovado"


def _buscar(linhas, matricula):
    for linha in linhas:
        if linha["matricula"] == matricula:
            return linha
    raise ToolError(f"matricula {matricula} nao existe na turma")


@mcp.tool()
def listar_alunos() -> str:
    """Lista a turma inteira com matrícula, nome, notas lançadas e situação atual."""
    saida = ["matricula  nome                  n1    n2    n3    media  situacao"]
    for linha in _ler():
        media = _media(linha)
        saida.append(
            f"{linha['matricula']:<10} {linha['nome']:<20} "
            f"{linha['n1'] or '-':<5} {linha['n2'] or '-':<5} {linha['n3'] or '-':<5} "
            f"{media if media is not None else '-':<6} {_situacao(media)}"
        )
    return "\n".join(saida)


@mcp.tool()
def boletim(matricula: str) -> str:
    """Boletim de um aluno: as três notas, a média ponderada e a situação."""
    linha = _buscar(_ler(), matricula)
    media = _media(linha)
    return (
        f"{linha['nome']} ({linha['matricula']})\n"
        f"  N1 (peso 3): {linha['n1'] or 'nao lancada'}\n"
        f"  N2 (peso 3): {linha['n2'] or 'nao lancada'}\n"
        f"  N3 (peso 4): {linha['n3'] or 'nao lancada'}\n"
        f"  media: {media if media is not None else 'incompleta'}\n"
        f"  situacao: {_situacao(media)}"
    )


@mcp.tool()
def lancar_nota(matricula: str, avaliacao: int, valor: float) -> str:
    """Lança a nota de uma avaliação (1, 2 ou 3) de um aluno, sobrescrevendo a anterior."""
    if avaliacao not in (1, 2, 3):
        raise ToolError("avaliacao deve ser 1, 2 ou 3")
    if not 0 <= valor <= 10:
        raise ToolError(f"nota invalida: {valor}. A nota deve estar entre 0 e 10.")
    linhas = _ler()
    linha = _buscar(linhas, matricula)
    anterior = linha[f"n{avaliacao}"] or "nao lancada"
    linha[f"n{avaliacao}"] = f"{valor:.1f}"
    _gravar(linhas)
    media = _media(linha)
    return (
        f"N{avaliacao} de {linha['nome']}: {anterior} -> {valor:.1f}. "
        f"Media agora: {media if media is not None else 'incompleta'} "
        f"({_situacao(media)})."
    )


@mcp.tool()
def resumo_turma() -> str:
    """Resumo da turma: contagem por situação, média geral e histograma das médias."""
    linhas = _ler()
    medias = [m for m in (_media(linha) for linha in linhas) if m is not None]
    contagem = {"aprovado": 0, "exame": 0, "reprovado": 0, "incompleto": 0}
    for linha in linhas:
        contagem[_situacao(_media(linha))] += 1
    faixas = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10.01)]
    histograma = []
    for inicio, fim in faixas:
        quantos = sum(1 for m in medias if inicio <= m < fim)
        histograma.append(f"  {inicio:>2}-{min(fim, 10):<2} | {'#' * quantos} {quantos}")
    geral = round(sum(medias) / len(medias), 2) if medias else "sem media"
    return (
        f"turma: {len(linhas)} alunos | media geral: {geral}\n"
        + " | ".join(f"{k}: {v}" for k, v in contagem.items())
        + "\n"
        + "\n".join(histograma)
    )


@mcp.resource("diario://regras")
def regras() -> str:
    """As regras de cálculo do diário: pesos das avaliações e limites de situação."""
    return (
        "Media ponderada com pesos N1=3, N2=3, N3=4.\n"
        "aprovado: media >= 7.0 | exame: media >= 5.0 | reprovado: media < 5.0\n"
        "Aluno com alguma avaliacao nao lancada fica como incompleto."
    )


if __name__ == "__main__":
    mcp.run()
```

Nota: os testes assumem que `@mcp.tool()` devolve a função original. Confirmar com `.venv\Scripts\python.exe -c "import servidor; print(type(servidor.boletim))"` → `<class 'function'>`. `python -m pytest` (e não `pytest`) é obrigatório para que a raiz entre no `sys.path` e `import servidor` funcione.

- [ ] **Step 4: Rodar e ver passar**
Run: `.venv\Scripts\python.exe -m pytest tests -q` → todos PASS.

- [ ] **Step 5: Verificar pelo protocolo (Inspector CLI, seções 3.4–3.6)**
Run: `npx -y @modelcontextprotocol/inspector --cli .venv\Scripts\python.exe servidor.py --method tools/list` → 4 ferramentas.
Run: `... --method tools/call --tool-name resumo_turma` → contém `aprovado: 2 | exame: 1 | reprovado: 1 | incompleto: 1`.
Run: `... --method resources/read --uri diario://regras` → 3 linhas de regra.
Run: `... --method tools/call --tool-name lancar_nota --tool-arg matricula=2024005 avaliacao=2 valor=11` → erro `nota invalida: 11.0...`; `git diff dados/turma.csv` vazio.

- [ ] **Step 6: Commit**
`git add servidor.py tests && git commit -m "quatro ferramentas e o recurso de regras"`

---

### Task 3: Registro no OpenCode (seção 3.7)

**Files:** Create: `opencode.json`

- [ ] **Step 1: Criar o arquivo**

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "diario": {
      "type": "local",
      "command": [".venv\\Scripts\\python.exe", "servidor.py"],
      "cwd": "D:\\Dev\\agente-aula4",
      "enabled": true
    }
  }
}
```

- [ ] **Step 2: Verificar**
Run: `opencode mcp list` → `✓ diario connected`. Se falhar por chave `cwd` não reconhecida na versão 1.18, testar com `command` absoluto `D:\\Dev\\agente-aula4\\.venv\\Scripts\\python.exe`, `D:\\Dev\\agente-aula4\\servidor.py` e registrar a diferença no relatório.

- [ ] **Step 3: Commit**
`git add opencode.json && git commit -m "registro do servidor no opencode"`

---

### Task 4: Uso em sessão (seção 3.8)

**Files:** Modify (pelo agente): `dados/turma.csv`

- [ ] **Step 1: Análise** — `opencode run "Use o diário para me dizer quem está a menos de meio ponto da aprovação, e o que falta lançar. Não invente número: consulte a ferramenta."` Guardar a saída em `notas-sessao.txt` do scratchpad (não versionar).
- [ ] **Step 2: Lançamento inválido** — `opencode run "Lance 11 na segunda avaliação da Carla Nogueira."` → agente relata recusa. `git diff dados/turma.csv` vazio (Carla N2 = 4.0).
- [ ] **Step 3: Lançamento válido** — `opencode run "Lance 8.5 na terceira avaliação do Pedro de Alcântara e me diga como ficou a situação dele."` → `cat dados/turma.csv` mostra `2024004,Pedro de Alcantara,6.0,7.0,8.5`.
- [ ] **Step 4: Commit** — `git add dados/turma.csv && git commit -m "lancamentos da sessao no diario"`

---

### Task 5: Skill `relatorio-de-atividade` (seção 4.2)

**Files:** Create: `.opencode/skills/relatorio-de-atividade/SKILL.md`

- [ ] **Step 1: Criar o arquivo**

```markdown
---
name: relatorio-de-atividade
description: Escreve o relatório técnico de uma atividade prática da disciplina, no formato exigido pela avaliação. Use quando eu pedir relatório, documentação da atividade, ou quando eu disser que vou fechar a entrega.
---

# Relatório de atividade

1. Rode `git log --oneline` e leia os commits desta atividade.
2. Rode `git diff --stat $(git rev-list --max-parents=0 HEAD)..HEAD` para medir o tamanho do que mudou desde o primeiro commit.
3. Escreva `relatorio.md` com estas seções, nesta ordem:
   - **O que foi pedido** — o enunciado, em duas frases
   - **O que foi feito** — o que existe e funciona ao final
   - **O que falhou** — os erros que apareceram no caminho, com a mensagem exata
   - **Como foi resolvido** — o que corrigiu cada um
   - **Ferramentas de IA** — qual agente, qual modelo, e em que etapa de cada
4. Termine perguntando o que faltou, em vez de preencher lacuna com suposição.

Regras:
- Nunca invente um erro que não aconteceu. Se o histórico não mostra falha, escreva que não houve.
- Máximo de uma página. Relatório longo não é lido.
- Português do Brasil, primeira pessoa do singular.
```

- [ ] **Step 2: Verificar estrutura** — `ls .opencode/skills/*/SKILL.md` e `head -4 .opencode/skills/relatorio-de-atividade/SKILL.md` (name idêntico à pasta).
- [ ] **Step 3: Commit** — `git add .opencode/skills && git commit -m "skill relatorio-de-atividade"`

(O teste de acionamento ocorre na Task 9, quando o histórico está completo.)

---

### Task 6: Subagente `auditor-de-contexto` (seções 5.3–5.4)

**Files:** Create: `.opencode/agents/auditor-de-contexto.md`

- [ ] **Step 1: Criar o arquivo**

```markdown
---
description: Audita o AGENTS.md do projeto contra os seis defeitos de configuração catalogados por Santos et al. Use quando eu pedir para revisar, auditar ou enxugar o arquivo de contexto.
mode: subagent
temperature: 0.1
permission:
  edit: deny
  bash: deny
  webfetch: deny
---

Você audita arquivos de contexto de agente. Leia o `AGENTS.md` do projeto e procure, nesta ordem, os seis defeitos:

1. **Lint Leakage** — regra de estilo que o formatador ou o linter já garantem.
2. **Context Bloat** — conteúdo que não vale para toda sessão.
3. **Skill Leakage** — procedimento raro que deveria estar em uma Skill.
4. **Conflicting Instructions** — instruções que se contradizem.
5. **Init Fossilization** — texto genérico com cara de gerado e nunca revisto.
6. **Blind Reference** — arquivo citado sem dizer para que serve e quando abrir.

Devolva **no máximo 15 linhas**, assim:
- uma linha por defeito encontrado, no formato `DEFEITO — trecho — correção proposta`;
- a última linha diz quantas linhas o arquivo tem hoje e quantas teria depois das correções.

Não reescreva o arquivo. Não use ferramenta de edição. Aponte e proponha.
```

- [ ] **Step 2: Verificar** — `opencode agent list` contém `auditor-de-contexto (subagent)`.
- [ ] **Step 3: Commit** — `git add .opencode/agents && git commit -m "subagente auditor-de-contexto com permissoes restritas"`

---

### Task 7: Medição de contexto (seção 5.5)

**Files:** Create: `medicao.md`

- [ ] **Step 1: Linha de base** — `opencode stats --days 1` (anotar Input).
- [ ] **Step 2: Rodada A** — `opencode run --format json "Investigue o pacote mcp instalado em .venv e me diga, em um parágrafo, quais transportes ele suporta e em quais arquivos cada um está implementado." > A.jsonl` (scratchpad). Contar eventos de ferramenta (read/glob/grep/list) da sessão principal; `opencode stats --days 1` de novo.
- [ ] **Step 3: Rodada B** — mesmo, com o prefixo `@explore ` → `B.jsonl`; contar chamadas na sessão principal (esperado: 1 `task`) e stats.
- [ ] **Step 4: Escrever `medicao.md`** com tabela (rodada · chamadas na janela principal · tokens de input · resposta resumida) e conclusão de 2–3 frases baseada nos números medidos (sem número inventado; se tokens = 0, dizer).
- [ ] **Step 5: Commit** — `git add medicao.md && git commit -m "medicao de contexto com e sem subagente"`

---

### Task 8: AGENTS.md — /init e auditoria (passo 10)

**Files:** Create: `AGENTS.md`

- [ ] **Step 1: Gerar** — `opencode run --command init` (se a flag não existir na versão: `opencode run "/init"`). Confirmar que `AGENTS.md` foi criado.
- [ ] **Step 2: Commit do gerado** — `git add AGENTS.md && git commit -m "AGENTS.md gerado pelo init"` (preserva a versão original para comparação).
- [ ] **Step 3: Auditar** — `opencode run "@auditor-de-contexto audite o AGENTS.md deste projeto"`; guardar o parecer.
- [ ] **Step 4: Corrigir** — aplicar as correções propostas pertinentes no `AGENTS.md` (incluindo `## Comandos` com `.venv\Scripts\python.exe -m pytest tests -q` e `opencode mcp list`).
- [ ] **Step 5: Commit** — `git add AGENTS.md && git commit -m "AGENTS.md corrigido conforme auditoria"`

---

### Task 9: Relatório pela Skill (Entrega 2)

**Files:** Create (pelo agente): `relatorio.md`

- [ ] **Step 1: Acionar sem citar a Skill** — `opencode run --format json "Vou fechar a entrega: escreva o relatório desta atividade." > R.jsonl`; confirmar evento da ferramenta `skill` com `relatorio-de-atividade`.
- [ ] **Step 2: Conferir formato** — 5 seções na ordem, ≤ 1 página, 1ª pessoa, pergunta final. Se fora do formato, corrigir o `SKILL.md`, commitar (`skill relatorio-de-atividade v2`) e rodar de novo.
- [ ] **Step 3: Commit** — `git add relatorio.md && git commit -m "relatorio da atividade gerado pela skill"`
- [ ] **Step 4: Verificação final** — `git status --short` vazio; `git log --oneline` ≥ 4 commits; `pytest` verde; `opencode mcp list` connected.
