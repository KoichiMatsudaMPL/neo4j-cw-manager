"""Node operations for memory tools."""

from typing import Optional

from neo4j_cw_manager.core import (
    create_node as neo4j_create_node,
    delete_node as neo4j_delete_node,
    find_node_by_id,
    find_nodes as neo4j_find_nodes,
    update_node as neo4j_update_node,
)

from .utils import (
    ERROR_NODE_NOT_FOUND,
    format_result,
    parse_labels,
    parse_properties,
)


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
    label_list = parse_labels(labels)
    props = parse_properties(properties)
    result = neo4j_create_node(label_list, props)
    return format_result(result)


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
    label_list = parse_labels(labels) if labels else None
    props = parse_properties(properties) if properties else None
    results = neo4j_find_nodes(label_list, props, limit)
    return format_result(results)


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
    return format_result(result)


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
    props = parse_properties(properties)
    result = neo4j_update_node(element_id, props, merge)
    if not result:
        return ERROR_NODE_NOT_FOUND.format(id=element_id)
    return format_result(result)


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
