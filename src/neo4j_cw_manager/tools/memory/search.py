"""Search operations for knowledge base."""

from typing import Optional

from neo4j_cw_manager.core import get_connection, run_query as neo4j_run_query

from .env import get_default_project
from .utils import format_result


async def search_nodes(
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
                 If PROJECT is also None, searches across all projects.
        fields: Optional comma-separated list of property names to return.
                If None or empty, returns all properties.
                Example: "category,file_path"
        limit: Maximum number of results (default: 100)

    Returns:
        JSON string with list of matching nodes.
    """
    conn = get_connection()
    conn.initialize()

    # Use environment variable if project not specified
    if project is None:
        project = get_default_project()

    # Build RETURN and ORDER BY clauses based on fields parameter
    base_fields = {"element_id", "type", "project", "name"}

    if fields:
        field_list = [f.strip() for f in fields.split(",") if f.strip()]
        if field_list:
            # Exclude fields that are already in base fields
            additional_fields = [f for f in field_list if f not in base_fields]
            if additional_fields:
                field_returns = ", ".join([f"n.{field} as {field}" for field in additional_fields])
                return_clause = f"RETURN elementId(n) as element_id, labels(n)[0] as type, p.name as project, n.name as name, {field_returns}"
            else:
                # Only base fields requested
                return_clause = "RETURN elementId(n) as element_id, labels(n)[0] as type, p.name as project, n.name as name"
            order_clause = "ORDER BY project, type, name"
        else:
            # Empty fields list - return all properties
            return_clause = """RETURN elementId(n) as element_id,
                   labels(n)[0] as type,
                   n.name as name,
                   n.summary as summary,
                   p.name as project,
                   properties(n) as properties"""
            order_clause = "ORDER BY project, type, name"
    else:
        # fields not specified - return all properties
        return_clause = """RETURN elementId(n) as element_id,
               labels(n)[0] as type,
               n.name as name,
               n.summary as summary,
               p.name as project,
               properties(n) as properties"""
        order_clause = "ORDER BY project, type, name"

    query = f"""
    MATCH (p:Project)-[r]->(n)
    WHERE type(r) IN ['HAS_KNOWLEDGE', 'HAS_PROCEDURE', 'HAS_RULE', 'HAS_SCREEN', 'HAS_ISSUE']
      AND ($project IS NULL OR p.name = $project)
      AND (
        toLower(coalesce(n.name, '')) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.summary, '')) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.japanese_name, '')) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.alias, '')) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.title, '')) CONTAINS toLower($keyword)
        OR toLower(coalesce(n.id, '')) CONTAINS toLower($keyword)
        OR any(key IN keys(n) WHERE
            NOT key IN ['name', 'summary', 'japanese_name', 'alias', 'title', 'id'] AND
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
    {return_clause}
    {order_clause}
    LIMIT $limit
    """

    params = {"keyword": keyword, "project": project, "limit": limit}

    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
