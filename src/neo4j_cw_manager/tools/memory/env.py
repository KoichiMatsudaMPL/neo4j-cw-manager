"""Environment variable utilities for memory tools."""

import os
from pathlib import Path

from dotenv import load_dotenv


def get_default_project() -> str | None:
    """
    Get default project from environment variable.

    Returns:
        Project name from PROJECT environment variable, or None if not set.
    """
    # Find and load .env file from project root
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        env_path = parent / ".env"
        pyproject_path = parent / "pyproject.toml"
        if pyproject_path.exists() and env_path.exists():
            load_dotenv(env_path)
            break

    return os.getenv("PROJECT")
