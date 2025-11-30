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
        JSON string with list of incomplete issues and total count.
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
    # First get total count, then get limited results
    count_query = """
    MATCH (p:Project)-[*1..3]->(n:Issue)
    WHERE ($project IS NULL OR p.name = $project)
      AND (n.status IS NULL OR NOT n.status IN ['completed', 'closed', 'done'])
    RETURN count(n) as total_count
    """

    data_query = f"""
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

    # Get total count
    count_results = neo4j_run_query(count_query, params, write=False)
    total_count = count_results[0]["total_count"] if count_results else 0

    # Get data
    data_results = neo4j_run_query(data_query, params, write=False)

    # Build response with count
    response = {
        "total_count": total_count,
        "returned_count": len(data_results),
        "issues": data_results
    }

    return json.dumps(response, ensure_ascii=False, indent=2)


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


async def upsert_issue(
    number: int,
    title: Optional[str] = None,
    project: Optional[str] = None,
    summary: Optional[str] = None,
    status: Optional[str] = None,
    url: Optional[str] = None,
) -> str:
    """
    Create or update an Issue node.

    Args:
        number: Issue number (required)
        title: Issue title (required for creation, optional for update)
        project: Project name. If None, uses PROJECT environment variable.
        summary: Issue summary (optional)
        status: Issue status (optional, default: "open" for new issues)
        url: GitHub URL (optional)

    Returns:
        JSON string with the created or updated issue data.
    """
    from datetime import datetime, timezone

    conn = get_connection()
    conn.initialize()

    # Use environment variable if project not specified
    if project is None:
        project = get_default_project()

    if project is None:
        return json.dumps({"error": "Project must be specified or set in PROJECT environment variable"})

    # Validate number
    if number <= 0:
        return json.dumps({"error": "Issue number must be a positive integer"})

    # Generate automatic values
    issue_id = f"{project}-issue-{number}"
    issue_name = f"Issue #{number}"
    current_time = datetime.now(timezone.utc).isoformat()

    # Build ON CREATE SET clause (all properties)
    on_create_props = {
        "id": issue_id,
        "name": issue_name,
        "title": title or "",
        "summary": summary,
        "status": status or "open",
        "url": url,
        "created_at": current_time,
        "updated_at": current_time,
    }

    # Build ON MATCH SET clause (only specified properties + updated_at)
    on_match_props = {"updated_at": current_time}
    if title is not None:
        on_match_props["title"] = title
    if summary is not None:
        on_match_props["summary"] = summary
    if status is not None:
        on_match_props["status"] = status
    if url is not None:
        on_match_props["url"] = url

    # Build SET clauses dynamically
    on_create_set = ", ".join([f"i.{key} = $create_{key}" for key in on_create_props.keys()])
    on_match_set = ", ".join([f"i.{key} = $match_{key}" for key in on_match_props.keys()])

    # Build query
    query = f"""
    MATCH (p:Project {{name: $project}})
    MERGE (p)-[:HAS_ISSUE]->(i:Issue {{number: $number, project: $project}})
    ON CREATE SET {on_create_set}
    ON MATCH SET {on_match_set}
    RETURN elementId(i) as element_id,
           i.id as id,
           i.number as number,
           i.title as title,
           i.status as status,
           i.project as project,
           i.summary as summary,
           i.url as url,
           i.created_at as created_at,
           i.updated_at as updated_at
    """

    # Build parameters
    params = {"project": project, "number": number}
    for key, value in on_create_props.items():
        params[f"create_{key}"] = value
    for key, value in on_match_props.items():
        params[f"match_{key}"] = value

    try:
        results = neo4j_run_query(query, params, write=True)
        if not results:
            return json.dumps({"error": f"Project '{project}' not found"})
        return format_result(results)
    except Exception as e:
        return json.dumps({"error": str(e)})
