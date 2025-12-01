"""Neo4j connection management."""

from contextlib import contextmanager
from typing import Any, Generator, Optional

from neo4j import Driver, GraphDatabase, ManagedTransaction, Session

from .config import Neo4jConfig


class Neo4jConnection:
    """Manages Neo4j database connection."""

    _instance: Optional["Neo4jConnection"] = None
    _driver: Optional[Driver] = None
    _config: Optional[Neo4jConfig] = None

    def __new__(cls) -> "Neo4jConnection":
        """Singleton pattern to ensure single connection instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, config: Optional[Neo4jConfig] = None, force: bool = False) -> None:
        """
        Initialize the connection with configuration.

        Args:
            config: Neo4j configuration. If None, loads from environment.
            force: If True, reinitialize even if already initialized.
        """
        if self._driver is not None and not force:
            return

        # Close existing connection if reinitializing
        if self._driver is not None:
            self._driver.close()

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

    @property
    def database(self) -> str:
        """Get the database name."""
        if self._config is None:
            raise RuntimeError(
                "Neo4j connection not initialized. Call initialize() first."
            )
        return self._config.database

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Create a session context manager.

        Yields:
            Neo4j session instance.
        """
        import sys
        db = self.database
        print(f"[SESSION] database property: {db}", file=sys.stderr)
        print(f"[SESSION] type: {type(db)}, repr: {repr(db)}", file=sys.stderr)
        session = self.driver.session(database=db)
        print(f"[SESSION] Session created successfully", file=sys.stderr)
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
    Reinitializes if environment variables have changed.

    Returns:
        Neo4jConnection singleton instance.
    """
    import os

    conn = Neo4jConnection()

    # Check if we need to (re)initialize
    if conn._driver is None:
        conn.initialize()
    elif conn._config is not None:
        # Check if environment variables have changed
        current_db = os.getenv("NEO4J_DATABASE", "neo4j")
        if current_db != conn._config.database:
            # Environment changed, reinitialize
            conn.initialize(force=True)

    return conn
