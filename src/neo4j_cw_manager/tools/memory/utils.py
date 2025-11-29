"""Utility functions and constants for memory tools."""

import json
from typing import Any, Optional

# Error messages
ERROR_NODE_NOT_FOUND = "Node not found: {id}"
ERROR_RELATIONSHIP_NOT_FOUND = "Relationship not found: {id}"
ERROR_INVALID_JSON = "Invalid JSON format for properties"


def format_result(data: Any) -> str:
    """Format result as JSON string."""
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


def parse_properties(properties_json: Optional[str]) -> dict[str, Any]:
    """Parse JSON string to dictionary."""
    if not properties_json:
        return {}
    try:
        return json.loads(properties_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"{ERROR_INVALID_JSON}: {e}")


def parse_labels(labels: str) -> list[str]:
    """Parse comma-separated labels to list."""
    return [label.strip() for label in labels.split(",") if label.strip()]
