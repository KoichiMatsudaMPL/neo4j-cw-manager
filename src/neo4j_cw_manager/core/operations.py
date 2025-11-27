"""Generic Neo4j CRUD operations."""

from typing import Any, Optional

from .connection import get_connection


def create_node(
    labels: list[str],
    properties: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a node with given labels and properties.

    Args:
        labels: List of node labels.
        properties: Node properties.

    Returns:
        Created node data including element ID and properties.
    """
    conn = get_connection()
    labels_str = ":".join(labels) if labels else ""
    label_clause = f":{labels_str}" if labels_str else ""

    query = f"""
    CREATE (n{label_clause} $properties)
    RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
    """

    results = conn.execute_write(query, {"properties": properties})
    return results[0] if results else {}


def find_nodes(
    labels: Optional[list[str]] = None,
    properties: Optional[dict[str, Any]] = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Find nodes matching labels and/or properties.

    Args:
        labels: Optional list of labels to match.
        properties: Optional properties to match.
        limit: Maximum number of results.

    Returns:
        List of matching nodes.
    """
    conn = get_connection()
    labels_str = ":".join(labels) if labels else ""
    label_clause = f":{labels_str}" if labels_str else ""

    where_clauses = []
    params: dict[str, Any] = {"limit": limit}

    if properties:
        for key, value in properties.items():
            param_name = f"prop_{key}"
            where_clauses.append(f"n.{key} = ${param_name}")
            params[param_name] = value

    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    query = f"""
    MATCH (n{label_clause})
    {where_clause}
    RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
    LIMIT $limit
    """

    return conn.execute_read(query, params)


def find_node_by_id(element_id: str) -> Optional[dict[str, Any]]:
    """
    Find a node by its element ID.

    Args:
        element_id: Neo4j element ID.

    Returns:
        Node data or None if not found.
    """
    conn = get_connection()
    query = """
    MATCH (n)
    WHERE elementId(n) = $id
    RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
    """

    results = conn.execute_read(query, {"id": element_id})
    return results[0] if results else None


def update_node(
    element_id: str,
    properties: dict[str, Any],
    merge: bool = True,
) -> Optional[dict[str, Any]]:
    """
    Update node properties.

    Args:
        element_id: Neo4j element ID.
        properties: Properties to update.
        merge: If True, merge with existing properties. If False, replace all.

    Returns:
        Updated node data or None if not found.
    """
    conn = get_connection()
    set_clause = "+=" if merge else "="

    query = f"""
    MATCH (n)
    WHERE elementId(n) = $id
    SET n {set_clause} $properties
    RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
    """

    results = conn.execute_write(query, {"id": element_id, "properties": properties})
    return results[0] if results else None


def delete_node(element_id: str, detach: bool = True) -> bool:
    """
    Delete a node by its element ID.

    Args:
        element_id: Neo4j element ID.
        detach: If True, delete all relationships first.

    Returns:
        True if node was deleted, False if not found.
    """
    conn = get_connection()
    detach_clause = "DETACH " if detach else ""

    query = f"""
    MATCH (n)
    WHERE elementId(n) = $id
    {detach_clause}DELETE n
    RETURN count(n) as deleted
    """

    results = conn.execute_write(query, {"id": element_id})
    return results[0]["deleted"] > 0 if results else False


def create_relationship(
    from_id: str,
    to_id: str,
    rel_type: str,
    properties: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Create a relationship between two nodes.

    Args:
        from_id: Source node element ID.
        to_id: Target node element ID.
        rel_type: Relationship type.
        properties: Optional relationship properties.

    Returns:
        Created relationship data.
    """
    conn = get_connection()
    props = properties or {}

    query = f"""
    MATCH (a), (b)
    WHERE elementId(a) = $from_id AND elementId(b) = $to_id
    CREATE (a)-[r:{rel_type} $properties]->(b)
    RETURN elementId(r) as id, type(r) as type, properties(r) as properties,
           elementId(a) as from_id, elementId(b) as to_id
    """

    results = conn.execute_write(
        query, {"from_id": from_id, "to_id": to_id, "properties": props}
    )
    return results[0] if results else {}


def find_relationships(
    from_id: Optional[str] = None,
    to_id: Optional[str] = None,
    rel_type: Optional[str] = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Find relationships matching criteria.

    Args:
        from_id: Optional source node element ID.
        to_id: Optional target node element ID.
        rel_type: Optional relationship type.
        limit: Maximum number of results.

    Returns:
        List of matching relationships.
    """
    conn = get_connection()
    rel_clause = f":{rel_type}" if rel_type else ""

    where_clauses = []
    params: dict[str, Any] = {"limit": limit}

    if from_id:
        where_clauses.append("elementId(a) = $from_id")
        params["from_id"] = from_id
    if to_id:
        where_clauses.append("elementId(b) = $to_id")
        params["to_id"] = to_id

    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    query = f"""
    MATCH (a)-[r{rel_clause}]->(b)
    {where_clause}
    RETURN elementId(r) as id, type(r) as type, properties(r) as properties,
           elementId(a) as from_id, elementId(b) as to_id
    LIMIT $limit
    """

    return conn.execute_read(query, params)


def update_relationship(
    element_id: str,
    properties: dict[str, Any],
    merge: bool = True,
) -> Optional[dict[str, Any]]:
    """
    Update relationship properties.

    Args:
        element_id: Relationship element ID.
        properties: Properties to update.
        merge: If True, merge with existing properties. If False, replace all.

    Returns:
        Updated relationship data or None if not found.
    """
    conn = get_connection()
    set_clause = "+=" if merge else "="

    query = f"""
    MATCH (a)-[r]->(b)
    WHERE elementId(r) = $id
    SET r {set_clause} $properties
    RETURN elementId(r) as id, type(r) as type, properties(r) as properties,
           elementId(a) as from_id, elementId(b) as to_id
    """

    results = conn.execute_write(query, {"id": element_id, "properties": properties})
    return results[0] if results else None


def delete_relationship(element_id: str) -> bool:
    """
    Delete a relationship by its element ID.

    Args:
        element_id: Relationship element ID.

    Returns:
        True if relationship was deleted, False if not found.
    """
    conn = get_connection()

    query = """
    MATCH ()-[r]->()
    WHERE elementId(r) = $id
    DELETE r
    RETURN count(r) as deleted
    """

    results = conn.execute_write(query, {"id": element_id})
    return results[0]["deleted"] > 0 if results else False


def run_query(
    query: str,
    parameters: Optional[dict[str, Any]] = None,
    write: bool = False,
) -> list[dict[str, Any]]:
    """
    Run a custom Cypher query.

    Args:
        query: Cypher query string.
        parameters: Optional query parameters.
        write: If True, execute as write transaction.

    Returns:
        Query results as list of dictionaries.
    """
    conn = get_connection()
    if write:
        return conn.execute_write(query, parameters)
    return conn.execute_read(query, parameters)
