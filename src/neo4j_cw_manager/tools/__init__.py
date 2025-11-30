"""
Tools package for neo4j-cw-manager MCP server.
"""

from .mermaid_checker import (
    check_mermaid_code,
    check_mermaid_file,
    list_mermaid_blocks,
)
from .memory import (
    create_node as neo4j_create_node,
    create_relationship as neo4j_create_relationship,
    delete_node as neo4j_delete_node,
    delete_relationship as neo4j_delete_relationship,
    find_nodes as neo4j_find_nodes,
    find_relationships as neo4j_find_relationships,
    get_index as neo4j_get_index,
    get_issues_by_id as neo4j_get_issues_by_id,
    get_node as neo4j_get_node,
    get_related_nodes as neo4j_get_related_nodes,
    list_incomplete_issues as neo4j_list_incomplete_issues,
    run_cypher_query as neo4j_run_cypher_query,
    search_nodes as neo4j_search_nodes,
    update_node as neo4j_update_node,
    update_relationship as neo4j_update_relationship,
    upsert_issue as neo4j_upsert_issue,
)

__all__ = [
    # Mermaid tools
    "check_mermaid_code",
    "check_mermaid_file",
    "list_mermaid_blocks",
    # Neo4j tools
    "neo4j_create_node",
    "neo4j_find_nodes",
    "neo4j_get_node",
    "neo4j_update_node",
    "neo4j_delete_node",
    "neo4j_create_relationship",
    "neo4j_find_relationships",
    "neo4j_update_relationship",
    "neo4j_delete_relationship",
    "neo4j_run_cypher_query",
    # Knowledge base tools
    "neo4j_get_index",
    "neo4j_search_nodes",
    "neo4j_get_related_nodes",
    # Issue tools
    "neo4j_get_issues_by_id",
    "neo4j_list_incomplete_issues",
    "neo4j_upsert_issue",
]
