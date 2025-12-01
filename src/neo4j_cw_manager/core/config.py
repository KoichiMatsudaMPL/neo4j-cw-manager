"""Configuration management for Neo4j connection."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Neo4jConfig:
    """Neo4j connection configuration."""

    uri: str
    user: str
    password: str
    database: str = "neo4j"

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Neo4jConfig":
        """
        Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file. If None, searches in current
                      directory and parent directories.

        Returns:
            Neo4jConfig instance with loaded values.

        Raises:
            ValueError: If required environment variables are not set.
        """
        # Load .env file as fallback, but never override existing environment variables
        # This ensures environment variables passed by MCP clients always take precedence
        if env_file:
            load_dotenv(env_file, override=False)
        else:
            # Find project root by looking for pyproject.toml
            current = Path(__file__).resolve()
            for parent in [current.parent] + list(current.parents):
                env_path = parent / ".env"
                pyproject_path = parent / "pyproject.toml"
                if pyproject_path.exists() and env_path.exists():
                    load_dotenv(env_path, override=False)
                    break
            else:
                # Fallback to default behavior
                load_dotenv(override=False)

        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        database = os.getenv("NEO4J_DATABASE", "neo4j")

        missing = []
        if not uri:
            missing.append("NEO4J_URI")
        if not user:
            missing.append("NEO4J_USER")
        if not password:
            missing.append("NEO4J_PASSWORD")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return cls(uri=uri, user=user, password=password, database=database)
