"""Search operations for knowledge base."""

from typing import Optional

from neo4j_cw_manager.core import get_connection, run_query as neo4j_run_query

from .utils import format_result


async def search_nodes(
    keyword: str,
    project: Optional[str] = None,
    limit: int = 100,
) -> str:
    """
    Search nodes by keyword in name, summary, and properties.

    Args:
        keyword: Search keyword
        project: Optional project name to filter results
        limit: Maximum number of results (default: 100)

    Returns:
        JSON string with list of matching nodes.
    """
    conn = get_connection()
    conn.initialize()

    project_condition = "AND n.project = $project" if project else ""

    query = f"""
    MATCH (n)
    WHERE (
        toLower(n.name) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.summary, '')) CONTAINS toLower($keyword)
        OR any(key IN keys(n) WHERE toLower(toString(n[key])) CONTAINS toLower($keyword))
    )
    {project_condition}
    RETURN elementId(n) as element_id,
           labels(n) as labels,
           n.name as name,
           n.summary as summary,
           n.project as project,
           properties(n) as properties
    ORDER BY n.name
    LIMIT $limit
    """

    params = {"keyword": keyword, "limit": limit}
    if project:
        params["project"] = project

    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
