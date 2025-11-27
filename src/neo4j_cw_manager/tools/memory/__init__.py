"""Memory tools using Neo4j for graph database operations."""

import json
from typing import Any, Optional

from neo4j_cw_manager.core import (
    create_node as neo4j_create_node,
    create_relationship as neo4j_create_relationship,
    delete_node as neo4j_delete_node,
    delete_relationship as neo4j_delete_relationship,
    find_node_by_id,
    find_nodes as neo4j_find_nodes,
    find_relationships as neo4j_find_relationships,
    run_query as neo4j_run_query,
    update_node as neo4j_update_node,
    update_relationship as neo4j_update_relationship,
)

# Error messages
ERROR_NODE_NOT_FOUND = "Node not found: {id}"
ERROR_RELATIONSHIP_NOT_FOUND = "Relationship not found: {id}"
ERROR_INVALID_JSON = "Invalid JSON format for properties"


def _format_result(data: Any) -> str:
    """Format result as JSON string."""
    return json.dumps(data, indent=2, default=str)


def _parse_properties(properties_json: Optional[str]) -> dict[str, Any]:
    """Parse JSON string to dictionary."""
    if not properties_json:
        return {}
    try:
        return json.loads(properties_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"{ERROR_INVALID_JSON}: {e}")


async def create_node(
    labels: str,
    properties: str,
) -> str:
    """
    Create a node with given labels and properties.

    Args:
        labels: Comma-separated list of node labels (e.g., "Person,Employee")
        properties: JSON string of node properties (e.g., '{"name": "John", "age": 30}')

    Returns:
        JSON string with created node data including element ID.
    """
    label_list = [label.strip() for label in labels.split(",") if label.strip()]
    props = _parse_properties(properties)
    result = neo4j_create_node(label_list, props)
    return _format_result(result)


async def find_nodes(
    labels: Optional[str] = None,
    properties: Optional[str] = None,
    limit: int = 100,
) -> str:
    """
    Find nodes matching labels and/or properties.

    Args:
        labels: Optional comma-separated list of labels to match.
        properties: Optional JSON string of properties to match.
        limit: Maximum number of results (default: 100).

    Returns:
        JSON string with list of matching nodes.
    """
    label_list = None
    if labels:
        label_list = [label.strip() for label in labels.split(",") if label.strip()]
    props = _parse_properties(properties) if properties else None
    results = neo4j_find_nodes(label_list, props, limit)
    return _format_result(results)


async def get_node(element_id: str) -> str:
    """
    Get a node by its element ID.

    Args:
        element_id: Neo4j element ID.

    Returns:
        JSON string with node data or error message.
    """
    result = find_node_by_id(element_id)
    if not result:
        return ERROR_NODE_NOT_FOUND.format(id=element_id)
    return _format_result(result)


async def update_node(
    element_id: str,
    properties: str,
    merge: bool = True,
) -> str:
    """
    Update node properties.

    Args:
        element_id: Neo4j element ID.
        properties: JSON string of properties to update.
        merge: If True, merge with existing properties. If False, replace all.

    Returns:
        JSON string with updated node data or error message.
    """
    props = _parse_properties(properties)
    result = neo4j_update_node(element_id, props, merge)
    if not result:
        return ERROR_NODE_NOT_FOUND.format(id=element_id)
    return _format_result(result)


async def delete_node(element_id: str, detach: bool = True) -> str:
    """
    Delete a node by its element ID.

    Args:
        element_id: Neo4j element ID.
        detach: If True, delete all relationships first (default: True).

    Returns:
        Success or error message.
    """
    success = neo4j_delete_node(element_id, detach)
    if not success:
        return ERROR_NODE_NOT_FOUND.format(id=element_id)
    return f"Node deleted successfully: {element_id}"


async def create_relationship(
    from_id: str,
    to_id: str,
    rel_type: str,
    properties: Optional[str] = None,
) -> str:
    """
    Create a relationship between two nodes.

    Args:
        from_id: Source node element ID.
        to_id: Target node element ID.
        rel_type: Relationship type (e.g., "KNOWS", "WORKS_AT").
        properties: Optional JSON string of relationship properties.

    Returns:
        JSON string with created relationship data.
    """
    props = _parse_properties(properties) if properties else None
    result = neo4j_create_relationship(from_id, to_id, rel_type, props)
    return _format_result(result)


async def find_relationships(
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
    results = neo4j_find_relationships(from_id, to_id, rel_type, limit)
    return _format_result(results)


async def update_relationship(
    element_id: str,
    properties: str,
    merge: bool = True,
) -> str:
    """
    Update relationship properties.

    Args:
        element_id: Relationship element ID.
        properties: JSON string of properties to update.
        merge: If True, merge with existing properties. If False, replace all.

    Returns:
        JSON string with updated relationship data or error message.
    """
    props = _parse_properties(properties)
    result = neo4j_update_relationship(element_id, props, merge)
    if not result:
        return ERROR_RELATIONSHIP_NOT_FOUND.format(id=element_id)
    return _format_result(result)


async def delete_relationship(element_id: str) -> str:
    """
    Delete a relationship by its element ID.

    Args:
        element_id: Relationship element ID.

    Returns:
        Success or error message.
    """
    success = neo4j_delete_relationship(element_id)
    if not success:
        return ERROR_RELATIONSHIP_NOT_FOUND.format(id=element_id)
    return f"Relationship deleted successfully: {element_id}"


async def run_cypher_query(
    query: str,
    parameters: Optional[str] = None,
    write: bool = False,
) -> str:
    """
    Run a custom Cypher query.

    Args:
        query: Cypher query string.
        parameters: Optional JSON string of query parameters.
        write: If True, execute as write transaction.

    Returns:
        JSON string with query results.
    """
    params = _parse_properties(parameters) if parameters else None
    results = neo4j_run_query(query, params, write)
    return _format_result(results)


__all__ = [
    "create_node",
    "find_nodes",
    "get_node",
    "update_node",
    "delete_node",
    "create_relationship",
    "find_relationships",
    "update_relationship",
    "delete_relationship",
    "run_cypher_query",
]
