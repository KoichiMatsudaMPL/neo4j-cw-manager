"""Relationship operations for memory tools."""

from typing import Optional

from neo4j_cw_manager.core import (
    create_relationship as neo4j_create_relationship,
    delete_relationship as neo4j_delete_relationship,
    find_relationships as neo4j_find_relationships,
    update_relationship as neo4j_update_relationship,
)

from .utils import (
    ERROR_RELATIONSHIP_NOT_FOUND,
    format_result,
    parse_properties,
)


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
    props = parse_properties(properties) if properties else None
    result = neo4j_create_relationship(from_id, to_id, rel_type, props)
    return format_result(result)


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
    return format_result(results)


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
    props = parse_properties(properties)
    result = neo4j_update_relationship(element_id, props, merge)
    if not result:
        return ERROR_RELATIONSHIP_NOT_FOUND.format(id=element_id)
    return format_result(result)


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
