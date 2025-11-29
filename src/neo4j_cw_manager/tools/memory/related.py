"""Related node operations for knowledge base."""

from typing import Optional

from neo4j_cw_manager.core import get_connection, run_query as neo4j_run_query

from .env import get_default_project
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
        project: Optional project name to filter the starting node.
                 If None, uses PROJECT environment variable.
                 If PROJECT is also None, searches across all projects.
        depth: Relationship traversal depth (default: 1)

    Returns:
        JSON string with the target node and related nodes with relationships.
    """
    conn = get_connection()
    conn.initialize()

    # Use environment variable if project not specified
    if project is None:
        project = get_default_project()

    # depth=0の場合は起点ノードのみを返す
    if depth == 0:
        query = """
        MATCH (p:Project)-[*1..2]->(n {name: $node_name})
        WHERE $project IS NULL OR p.name = $project
        WITH n
        LIMIT 1
        RETURN {
            target: {
                element_id: elementId(n),
                labels: labels(n),
                name: n.name,
                summary: n.summary,
                properties: properties(n)
            },
            related: []
        } as result
        """
    else:
        query = f"""
        MATCH (p:Project)-[*1..2]->(n {{name: $node_name}})
        WHERE $project IS NULL OR p.name = $project
        WITH n
        LIMIT 1
        OPTIONAL MATCH path = (n)-[r*1..{depth}]-(related)
        WHERE related <> n
        WITH n,
             collect(DISTINCT {{
                 relationship: type(relationships(path)[-1]),
                 node: {{
                     element_id: elementId(related),
                     labels: labels(related),
                     name: related.name,
                     summary: related.summary,
                     properties: properties(related)
                 }}
             }}) as related_items
        RETURN {{
            target: {{
                element_id: elementId(n),
                labels: labels(n),
                name: n.name,
                summary: n.summary,
                properties: properties(n)
            }},
            related: related_items
        }} as result
        """

    params = {"project": project, "node_name": node_name}

    results = neo4j_run_query(query, params, write=False)
    return format_result(results)
