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
        servidor.lancar_nota("2024005", 2, 11.0)  # via protocolo, o esquema float entrega 11.0
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
