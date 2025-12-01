"""Neo4j connection management."""

import os
from contextlib import contextmanager
from typing import Any, Generator, Optional

from neo4j import Driver, GraphDatabase, ManagedTransaction, Session

from .config import Neo4jConfig


class Neo4jConnection:
    """Manages Neo4j database connection using Singleton pattern."""

    _instance: Optional["Neo4jConnection"] = None
    _driver: Optional[Driver] = None
    _config: Optional[Neo4jConfig] = None

    def __new__(cls) -> "Neo4jConnection":
        """Singleton pattern to ensure single connection instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, config: Optional[Neo4jConfig] = None) -> None:
        """
        Initialize the connection with configuration.

        Args:
            config: Neo4j configuration. If None, loads from environment.
        """
        if self._driver is not None:
            return

        self._config = config or Neo4jConfig.from_env()
        self._driver = GraphDatabase.driver(
            self._config.uri,
            auth=(self._config.user, self._config.password),
        )

    def close(self) -> None:
        """Close the database connection."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            Neo4jConnection._instance = None

    @property
    def driver(self) -> Driver:
        """Get the Neo4j driver instance."""
        if self._driver is None:
            raise RuntimeError(
                "Neo4j connection not initialized. Call initialize() first."
            )
        return self._driver

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Create a session context manager.

        Database name is read from environment variable on each session creation,
        allowing dynamic database switching without driver reinitialization.

        Yields:
            Neo4j session instance.
        """
        # Read database name from environment variable on each session creation
        import sys
        env_value = os.getenv("NEO4J_DATABASE")
        database = env_value if env_value is not None else "server"
        print(f"[DEBUG] NEO4J_DATABASE env: {env_value}, using: {database}", file=sys.stderr, flush=True)
        session = self.driver.session(database=database)
        try:
            yield session
        finally:
            session.close()

    def execute_read(
        self, query: str, parameters: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        """
        Execute a read query.

        Args:
            query: Cypher query string.
            parameters: Optional query parameters.

        Returns:
            List of records as dictionaries.
        """

        def _run(tx: ManagedTransaction) -> list[dict[str, Any]]:
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]

        with self.session() as session:
            return session.execute_read(_run)

    def execute_write(
        self, query: str, parameters: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        """
        Execute a write query.

        Args:
            query: Cypher query string.
            parameters: Optional query parameters.

        Returns:
            List of records as dictionaries.
        """

        def _run(tx: ManagedTransaction) -> list[dict[str, Any]]:
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]

        with self.session() as session:
            return session.execute_write(_run)

    def verify_connectivity(self) -> bool:
        """
        Verify the database connection.

        Returns:
            True if connection is successful.

        Raises:
            Exception: If connection fails.
        """
        self.driver.verify_connectivity()
        return True


def get_connection() -> Neo4jConnection:
    """
    Get the Neo4j connection instance.

    Automatically initializes the connection if not already initialized.

    Returns:
        Neo4jConnection singleton instance.
    """
    conn = Neo4jConnection()
    if conn._driver is None:
        conn.initialize()
    return conn
