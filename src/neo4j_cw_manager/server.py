from mcp.server.fastmcp import FastMCP

mcp = FastMCP("neo4j-cw-manager")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


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
