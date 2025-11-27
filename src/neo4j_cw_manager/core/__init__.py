"""Neo4j database module for shared Neo4j operations."""

from .config import Neo4jConfig
from .connection import Neo4jConnection, get_connection
from .nodes import create_node, delete_node, find_node_by_id, find_nodes, update_node
from .query import run_query
from .relationships import (
    create_relationship,
    delete_relationship,
    find_relationships,
    update_relationship,
)

__all__ = [
    # Config
    "Neo4jConfig",
    # Connection
    "Neo4jConnection",
    "get_connection",
    # Node operations
    "create_node",
    "find_nodes",
    "find_node_by_id",
    "update_node",
    "delete_node",
    # Relationship operations
    "create_relationship",
    "find_relationships",
    "update_relationship",
    "delete_relationship",
    # Query
    "run_query",
]
