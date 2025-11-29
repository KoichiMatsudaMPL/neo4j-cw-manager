"""Related node operations for knowledge base."""

from typing import Optional

from neo4j_cw_manager.core import get_connection, run_query as neo4j_run_query

from .utils import format_result


async def get_related_nodes(
    node_name: str,
    project: Optional[str] = None,
    depth: int = 1,
) -> str:
    """
    Get a node and its related nodes up to specified depth.

    Args:
        node_name: Name of the node to search for
        project: Optional project name to filter the starting node
        depth: Relationship traversal depth (default: 1)

    Returns:
        JSON string with the target node and related nodes with relationships.
    """
    conn = get_connection()
    conn.initialize()

    project_condition = "AND n.project = $project" if project else ""

    query = f"""
    MATCH (n {{name: $node_name}})
    {project_condition}
    WITH n
    LIMIT 1
    CALL {{
        WITH n
        MATCH path = (n)-[*0..{depth}]-(related)
        RETURN collect(DISTINCT {{
            element_id: elementId(related),
            labels: labels(related),
            name: related.name,
            summary: related.summary,
            project: related.project,
            properties: properties(related)
        }}) as nodes,
        collect(DISTINCT {{
            from_id: elementId(startNode(relationships(path)[0])),
            to_id: elementId(endNode(relationships(path)[0])),
            type: type(relationships(path)[0]),
            properties: properties(relationships(path)[0])
        }}) as relationships
    }}
    RETURN {{
        nodes: nodes,
        relationships: relationships
    }} as result
    """

    params = {"node_name": node_name, "depth": depth}
    if project:
        params["project"] = project

    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
