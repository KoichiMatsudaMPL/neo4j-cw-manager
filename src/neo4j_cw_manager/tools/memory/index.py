"""Index operations for knowledge base."""

from typing import Optional

from neo4j_cw_manager.core import get_connection, run_query as neo4j_run_query

from .env import get_default_project
from .utils import format_result


async def get_index(
    project: Optional[str] = None,
    types: Optional[str] = None,
) -> str:
    """
    Get index of knowledge/procedure nodes for a specific project.

    Args:
        project: Project name (e.g., "bravio-app", "common").
                 If None, uses PROJECT environment variable.
        types: Optional comma-separated list of node types to filter
               (e.g., "KnowledgeNode,Procedure")

    Returns:
        JSON string with list of nodes including name, type, summary.
    """
    conn = get_connection()
    conn.initialize()

    # Use environment variable if project not specified
    if project is None:
        project = get_default_project()
        if project is None:
            return format_result({"error": "Project not specified and PROJECT environment variable not set"})

    if types:
        type_list = [t.strip() for t in types.split(",")]
        label_condition = " OR ".join([f"labels(n)[0] = '{label}'" for label in type_list])
        query = f"""
        MATCH (p:Project {{name: $project}})-[r]->(n)
        WHERE type(r) IN ['HAS_KNOWLEDGE', 'HAS_PROCEDURE', 'HAS_RULE', 'HAS_SCREEN']
          AND ({label_condition})
        RETURN elementId(n) as element_id,
               labels(n)[0] as type,
               n.name as name,
               n.summary as summary,
               p.name as project
        ORDER BY type, name
        """
    else:
        query = """
        MATCH (p:Project {name: $project})-[r]->(n)
        WHERE type(r) IN ['HAS_KNOWLEDGE', 'HAS_PROCEDURE', 'HAS_RULE', 'HAS_SCREEN']
        RETURN elementId(n) as element_id,
               labels(n)[0] as type,
               n.name as name,
               n.summary as summary,
               p.name as project
        ORDER BY type, name
        """

    params = {"project": project}
    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
