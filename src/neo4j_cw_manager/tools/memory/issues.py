"""
Issue-specific operations for Neo4j graph database.
"""

import json
from typing import Optional

from neo4j_cw_manager.core import get_connection
from neo4j_cw_manager.tools.memory.env import get_default_project
from neo4j_cw_manager.tools.memory.query import neo4j_run_query
from neo4j_cw_manager.tools.memory.utils import format_result


async def list_incomplete_issues(
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
                 If PROJECT is also None, searches across all projects.
        limit: Maximum number of results (default: 100)
        order_by: Sort field (created_at, updated_at, number). Default: updated_at
        direction: Sort direction (ASC or DESC). Default: DESC

    Returns:
        JSON string with list of incomplete issues.
    """
    conn = get_connection()
    conn.initialize()

    # Use environment variable if project not specified
    if project is None:
        project = get_default_project()

    # Validate order_by parameter
    valid_order_fields = ["created_at", "updated_at", "number"]
    if order_by not in valid_order_fields:
        return json.dumps(
            {
                "error": f"Invalid order_by field: {order_by}. Must be one of: {', '.join(valid_order_fields)}"
            }
        )

    # Validate direction parameter
    valid_directions = ["ASC", "DESC"]
    direction_upper = direction.upper()
    if direction_upper not in valid_directions:
        return json.dumps(
            {
                "error": f"Invalid direction: {direction}. Must be one of: {', '.join(valid_directions)}"
            }
        )

    # Build the query to match Issue through any Project relationship (direct or indirect)
    query = f"""
    MATCH (p:Project)-[*1..3]->(n:Issue)
    WHERE ($project IS NULL OR p.name = $project)
      AND (n.status IS NULL OR NOT n.status IN ['completed', 'closed', 'done'])
    RETURN elementId(n) as element_id,
           n.id as id,
           n.number as number,
           n.title as title,
           n.status as status,
           n.project as project,
           n.summary as summary,
           n.url as url,
           n.created_at as created_at,
           n.updated_at as updated_at
    ORDER BY n.{order_by} {direction_upper}
    LIMIT $limit
    """

    params = {"project": project, "limit": limit}

    results = neo4j_run_query(query, params, write=False)
    return format_result(results)


async def get_issues_by_id(
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
                 If PROJECT is also None, searches across all projects.

    Returns:
        JSON string with list of matching issues (0 or more).
    """
    conn = get_connection()
    conn.initialize()

    # Use environment variable if project not specified
    if project is None:
        project = get_default_project()

    # Parse comma-separated numbers
    try:
        number_list = [int(num.strip()) for num in issue_numbers.split(",") if num.strip()]
    except ValueError:
        return json.dumps({"error": "Invalid issue number format. Must be comma-separated integers."})

    if not number_list:
        return json.dumps({"error": "No valid issue numbers provided"})

    # Build the query to match Issue through any Project relationship (direct or indirect)
    query = """
    MATCH (p:Project)-[*1..3]->(n:Issue)
    WHERE n.number IN $number_list
      AND ($project IS NULL OR p.name = $project)
    RETURN elementId(n) as element_id,
           n.id as id,
           n.number as number,
           n.title as title,
           n.status as status,
           n.project as project,
           n.summary as summary,
           n.url as url,
           n.created_at as created_at,
           n.updated_at as updated_at
    ORDER BY n.number
    """

    params = {"number_list": number_list, "project": project}

    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
