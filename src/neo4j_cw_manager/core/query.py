"""Custom query operations for Neo4j."""

from typing import Any, Optional

from .connection import get_connection


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
