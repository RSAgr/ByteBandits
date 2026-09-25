"""MCP stdio server exposing the Algorand PostgreSQL RAG search."""

from mcp.server.fastmcp import FastMCP

from rag.search import search_knowledge

mcp = FastMCP("algorand-knowledge")


@mcp.tool()
def search_algorand_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """Search Algorand examples and documentation in the local knowledge base.

    Returns ranked source records with instruction, code, metadata and lexical/
    semantic scores. Use this context to answer Algorand development questions.
    """
    return search_knowledge(query, top_k)


if __name__ == "__main__":
    mcp.run(transport="stdio")
