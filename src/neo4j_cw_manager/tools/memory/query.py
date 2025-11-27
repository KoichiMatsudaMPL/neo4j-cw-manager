"""Query operations for memory tools."""

from typing import Optional

from neo4j_cw_manager.core import run_query as neo4j_run_query

from .utils import format_result, parse_properties


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
    params = parse_properties(parameters) if parameters else None
    results = neo4j_run_query(query, params, write)
    return format_result(results)
