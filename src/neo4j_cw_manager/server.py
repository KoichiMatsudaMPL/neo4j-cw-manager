from typing import Optional

from mcp.server.fastmcp import FastMCP

from neo4j_cw_manager.tools import (
    check_mermaid_code,
    check_mermaid_file,
    list_mermaid_blocks,
)

mcp = FastMCP("neo4j-cw-manager")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


@mcp.tool()
async def mermaid_check_code(code: Optional[str]) -> str:
    """
    Validate a single Mermaid code snippet.

    Args:
        code: Mermaid diagram code to validate

    Returns:
        Validation result with diagram type if valid, or error details if invalid
    """
    return await check_mermaid_code(code)


@mcp.tool()
async def mermaid_check_file(file_path: str) -> str:
    """
    Validate all Mermaid code blocks in a Markdown file.

    Args:
        file_path: Path to the Markdown file to check

    Returns:
        Summary with block count, valid/invalid counts, and error details
    """
    return await check_mermaid_file(file_path)


@mcp.tool()
async def mermaid_list_blocks(file_path: str) -> str:
    """
    Extract and list all Mermaid code blocks from a Markdown file.

    Args:
        file_path: Path to the Markdown file to scan

    Returns:
        List of blocks with their line ranges, diagram types, and line counts
    """
    return await list_mermaid_blocks(file_path)


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.resource("info://server")
def get_server_info() -> str:
    """Get server information"""
    return "This is a sample MCP server for neo4j-cw-manager"


def main():
    """Entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
