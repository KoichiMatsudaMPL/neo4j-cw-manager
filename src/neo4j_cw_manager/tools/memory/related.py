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

    where_clause = "WHERE n.name = $node_name"
    if project:
        where_clause += " AND n.project = $project"

    query = f"""
    MATCH (n)
    {where_clause}
    WITH n
    LIMIT 1
    CALL {{
        WITH n
        MATCH path = (n)-[r*0..{depth}]-(related)
        WITH n, path, related, relationships(path) as rels
        RETURN collect(DISTINCT {{
            element_id: elementId(related),
            labels: labels(related),
            name: related.name,
            summary: related.summary,
            project: related.project,
            properties: properties(related)
        }}) as nodes,
        [rel in rels | {{
            from_id: elementId(startNode(rel)),
            to_id: elementId(endNode(rel)),
            type: type(rel),
            properties: properties(rel)
        }}] as relationships
    }}
    RETURN {{
        nodes: nodes,
        relationships: relationships
    }} as result
    """

    params = {"node_name": node_name}
    if project:
        params["project"] = project

    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
