"""Search operations for knowledge base."""

from typing import Optional

from neo4j_cw_manager.core import get_connection, run_query as neo4j_run_query

from .env import get_default_project
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
        project: Optional project name to filter results.
                 If None, uses PROJECT environment variable.
                 If PROJECT is also None, searches across all projects.
        limit: Maximum number of results (default: 100)

    Returns:
        JSON string with list of matching nodes.
    """
    conn = get_connection()
    conn.initialize()

    # Use environment variable if project not specified
    if project is None:
        project = get_default_project()

    query = """
    MATCH (p:Project)-[r]->(n)
    WHERE type(r) IN ['HAS_KNOWLEDGE', 'HAS_PROCEDURE', 'HAS_RULE', 'HAS_SCREEN']
      AND ($project IS NULL OR p.name = $project)
      AND (
        toLower(coalesce(n.name, '')) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.summary, '')) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.japanese_name, '')) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.alias, '')) CONTAINS toLower($keyword)
        OR any(key IN keys(n) WHERE
            CASE valueType(n[key])
                WHEN 'STRING' THEN toLower(n[key]) CONTAINS toLower($keyword)
                WHEN 'INTEGER' THEN toString(n[key]) CONTAINS $keyword
                WHEN 'FLOAT' THEN toString(n[key]) CONTAINS $keyword
                WHEN 'BOOLEAN' THEN toString(n[key]) CONTAINS $keyword
                WHEN 'LIST<STRING>' THEN any(item IN n[key] WHERE toLower(item) CONTAINS toLower($keyword))
                WHEN 'LIST<INTEGER>' THEN any(item IN n[key] WHERE toString(item) CONTAINS $keyword)
                ELSE false
            END
        )
      )
    RETURN elementId(n) as element_id,
           labels(n)[0] as type,
           n.name as name,
           n.summary as summary,
           p.name as project,
           properties(n) as properties
    ORDER BY p.name, type, n.name
    LIMIT $limit
    """

    params = {"keyword": keyword, "project": project, "limit": limit}

    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
