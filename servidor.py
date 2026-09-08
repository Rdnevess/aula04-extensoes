from mcp.server import MCPServer
mcp = MCPServer("diario")
@mcp.tool()
def boletim(matricula: str) -> str:
    """Boletim de um aluno: as três notas, a média ponderada e a situação."""
    return f"boletim de {matricula}: ainda não implementado"
if __name__ == "__main__":
 mcp.run()