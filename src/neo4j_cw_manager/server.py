import atexit
from typing import Any, Optional, Union

from mcp.server.fastmcp import FastMCP

from neo4j_cw_manager.core import get_connection
from neo4j_cw_manager.tools import (
    check_mermaid_code,
    check_mermaid_file,
    list_mermaid_blocks,
    neo4j_create_node,
    neo4j_create_relationship,
    neo4j_delete_node,
    neo4j_delete_relationship,
    neo4j_find_nodes,
    neo4j_find_relationships,
    neo4j_get_index,
    neo4j_get_issues_by_id,
    neo4j_get_node,
    neo4j_get_related_nodes,
    neo4j_list_incomplete_issues,
    neo4j_run_cypher_query,
    neo4j_search_nodes,
    neo4j_update_node,
    neo4j_update_relationship,
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


# Neo4j Graph Database Tools


@mcp.tool()
async def graph_create_node(labels: str, properties: Union[str, dict[str, Any]]) -> str:
    """
    Create a node with given labels and properties.

    Args:
        labels: Comma-separated list of node labels (e.g., "Person,Employee")
        properties: JSON string or dict of node properties (e.g., '{"name": "John", "age": 30}')

    Returns:
        JSON string with created node data including element ID.
    """
    return await neo4j_create_node(labels, properties)


@mcp.tool()
async def graph_find_nodes(
    labels: Optional[str] = None,
    properties: Optional[Union[str, dict[str, Any]]] = None,
    limit: int = 100,
) -> str:
    """
    Find nodes matching labels and/or properties.

    Args:
        labels: Optional comma-separated list of labels to match.
        properties: Optional JSON string or dict of properties to match.
        limit: Maximum number of results (default: 100).

    Returns:
        JSON string with list of matching nodes.
    """
    return await neo4j_find_nodes(labels, properties, limit)


@mcp.tool()
async def graph_get_node(element_id: str) -> str:
    """
    Get a node by its element ID.

    Args:
        element_id: Neo4j element ID.

    Returns:
        JSON string with node data or error message.
    """
    return await neo4j_get_node(element_id)


@mcp.tool()
async def graph_update_node(
    element_id: str,
    properties: Union[str, dict[str, Any]],
    merge: bool = True,
) -> str:
    """
    Update node properties.

    Args:
        element_id: Neo4j element ID.
        properties: JSON string or dict of properties to update.
        merge: If True, merge with existing properties. If False, replace all.

    Returns:
        JSON string with updated node data or error message.
    """
    return await neo4j_update_node(element_id, properties, merge)


@mcp.tool()
async def graph_delete_node(element_id: str, detach: bool = True) -> str:
    """
    Delete a node by its element ID.

    Args:
        element_id: Neo4j element ID.
        detach: If True, delete all relationships first (default: True).

    Returns:
        Success or error message.
    """
    return await neo4j_delete_node(element_id, detach)


@mcp.tool()
async def graph_create_relationship(
    from_id: str,
    to_id: str,
    rel_type: str,
    properties: Optional[Union[str, dict[str, Any]]] = None,
) -> str:
    """
    Create a relationship between two nodes.

    Args:
        from_id: Source node element ID.
        to_id: Target node element ID.
        rel_type: Relationship type (e.g., "KNOWS", "WORKS_AT").
        properties: Optional JSON string or dict of relationship properties.

    Returns:
        JSON string with created relationship data.
    """
    return await neo4j_create_relationship(from_id, to_id, rel_type, properties)


@mcp.tool()
async def graph_find_relationships(
    from_id: Optional[str] = None,
    to_id: Optional[str] = None,
    rel_type: Optional[str] = None,
    limit: int = 100,
) -> str:
    """
    Find relationships matching criteria.

    Args:
        from_id: Optional source node element ID.
        to_id: Optional target node element ID.
        rel_type: Optional relationship type.
        limit: Maximum number of results (default: 100).

    Returns:
        JSON string with list of matching relationships.
    """
    return await neo4j_find_relationships(from_id, to_id, rel_type, limit)


@mcp.tool()
async def graph_update_relationship(
    element_id: str,
    properties: Union[str, dict[str, Any]],
    merge: bool = True,
) -> str:
    """
    Update relationship properties.

    Args:
        element_id: Relationship element ID.
        properties: JSON string or dict of properties to update.
        merge: If True, merge with existing properties. If False, replace all.

    Returns:
        JSON string with updated relationship data or error message.
    """
    return await neo4j_update_relationship(element_id, properties, merge)


@mcp.tool()
async def graph_delete_relationship(element_id: str) -> str:
    """
    Delete a relationship by its element ID.

    Args:
        element_id: Relationship element ID.

    Returns:
        Success or error message.
    """
    return await neo4j_delete_relationship(element_id)


@mcp.tool()
async def graph_query(
    query: str,
    parameters: Optional[Union[str, dict[str, Any]]] = None,
    write: bool = False,
) -> str:
    """
    Run a custom Cypher query.

    Args:
        query: Cypher query string.
        parameters: Optional JSON string or dict of query parameters.
        write: If True, execute as write transaction.

    Returns:
        JSON string with query results.
    """
    return await neo4j_run_cypher_query(query, parameters, write)


@mcp.tool()
async def graph_get_index(
    project: str,
    types: Optional[str] = None,
) -> str:
    """
    Get index of knowledge/procedure nodes for a specific project.

    Args:
        project: Project name (e.g., "bravio-app", "common")
        types: Optional comma-separated list of node types to filter
               (e.g., "KnowledgeNode,Procedure")

    Returns:
        JSON string with list of nodes including name, type, summary.
    """
    return await neo4j_get_index(project, types)


@mcp.tool()
async def graph_search(
    keyword: str,
    project: Optional[str] = None,
    fields: Optional[str] = None,
    limit: int = 100,
) -> str:
    """
    Search nodes by keyword in name, summary, and properties.

    Args:
        keyword: Search keyword
        project: Optional project name to filter results.
                 If None, uses PROJECT environment variable.
        fields: Optional comma-separated list of property names to return.
                If None or empty, returns all properties.
                Example: "category,file_path"
        limit: Maximum number of results (default: 100)

    Returns:
        JSON string with list of matching nodes.
    """
    return await neo4j_search_nodes(keyword, project, fields, limit)


@mcp.tool()
async def graph_get_related(
    node_name: str,
    project: Optional[str] = None,
    depth: int = 1,
) -> str:
    """
    Get a node and its related nodes up to specified depth.

    Args:
        node_name: Name of the node to search for
        project: Optional project name to filter the starting node
        depth: Relationship traversal depth (default: 1)

    Returns:
        JSON string with the target node and related nodes with relationships.
    """
    return await neo4j_get_related_nodes(node_name, project, depth)


@mcp.tool()
async def graph_list_incomplete_issues(
    project: Optional[str] = None,
    limit: int = 100,
    order_by: str = "updated_at",
    direction: str = "DESC",
) -> str:
    """
    List incomplete (not completed/closed/done) issues.

    Args:
        project: Optional project name to filter results.
                 If None, uses PROJECT environment variable.
        limit: Maximum number of results (default: 100)
        order_by: Sort field (created_at, updated_at, number). Default: updated_at
        direction: Sort direction (ASC or DESC). Default: DESC

    Returns:
        JSON string with list of incomplete issues.
    """
    return await neo4j_list_incomplete_issues(project, limit, order_by, direction)


@mcp.tool()
async def graph_get_issues_by_id(
    issue_numbers: str,
    project: Optional[str] = None,
) -> str:
    """
    Get Issue nodes by their issue numbers.

    Args:
        issue_numbers: Comma-separated list of issue numbers.
                       Example: "705,704" or "705"
                       Can be a single number or multiple numbers.
        project: Optional project name to filter results.
                 If None, uses PROJECT environment variable.

    Returns:
        JSON string with list of matching issues (0 or more).
    """
    return await neo4j_get_issues_by_id(issue_numbers, project)


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.resource("info://server")
def get_server_info() -> str:
    """Get server information"""
    return "This is a sample MCP server for neo4j-cw-manager"


def _cleanup_neo4j() -> None:
    """Close Neo4j connection on exit."""
    try:
        conn = get_connection()
        conn.close()
    except Exception:
        pass


def main():
    """Entry point for the MCP server."""
    conn = get_connection()
    conn.initialize()
    atexit.register(_cleanup_neo4j)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
