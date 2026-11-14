---
name: relatorio-de-atividade
description: Escreve o relatório técnico de uma atividade prática da disciplina, no formato exigido pela avaliação. Use quando eu pedir relatório, documentação da atividade, ou quando eu disser que vou fechar a entrega.
---

# Relatório de atividade

1. Rode `git log --format="%h %s%n%b"` e leia os commits desta atividade, incluindo o corpo: é nele que ficam os erros e as mensagens exatas.
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
- Em **Ferramentas de IA**, só atribua uma etapa a um agente ou modelo se o histórico ou os arquivos mostrarem isso. Sem evidência, escreva "a confirmar" e inclua a dúvida na pergunta final.
- Máximo de uma página. Relatório longo não é lido.
- Português do Brasil, primeira pessoa do singular.
