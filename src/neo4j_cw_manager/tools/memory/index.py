"""Index operations for knowledge base."""

from typing import Optional

from neo4j_cw_manager.core import get_connection, run_query as neo4j_run_query

from .utils import format_result


async def get_index(
    project: str,
    types: Optional[str] = None,
) -> str:
    """
    Get index of knowledge/procedure nodes for a specific project.

    Args:
        project: Project name (e.g., "bravio-app", "common")
        types: Optional comma-separated list of node types to filter
               (e.g., "KnowledgeNode,Procedure")

    Returns:
        JSON string with list of nodes including name, type, summary.
    """
    conn = get_connection()
    conn.initialize()

    if types:
        type_list = [t.strip() for t in types.split(",")]
        label_condition = " OR ".join([f"n:{label}" for label in type_list])
        query = f"""
        MATCH (n)
        WHERE ({label_condition}) AND n.project = $project
        RETURN elementId(n) as element_id,
               labels(n) as labels,
               n.name as name,
               n.summary as summary,
               n.project as project
        ORDER BY n.name
        """
    else:
        query = """
        MATCH (n)
        WHERE n.project = $project
        RETURN elementId(n) as element_id,
               labels(n) as labels,
               n.name as name,
               n.summary as summary,
               n.project as project
        ORDER BY n.name
        """

    params = {"project": project}
    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
