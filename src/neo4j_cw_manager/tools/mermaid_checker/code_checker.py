"""Code validation for Mermaid diagrams."""

from typing import Optional

from .checker import validate_code
from .constants import ERROR_CODE_REQUIRED


async def check_mermaid_code(code: Optional[str]) -> str:
    """
    Validate a single Mermaid code snippet directly.

    Args:
        code: Mermaid diagram code to validate (can be None)

    Returns:
        Formatted string result for MCP response:
        - Valid: "Valid: true\\nDiagram type: {type}"
        - Invalid: "Valid: false\\nError at line {n}: {message}"
                   or "Valid: false\\nError: {message}"
        - Empty: "Error: Code is required"
    """
    if code is None or not code.strip():
        return ERROR_CODE_REQUIRED

    try:
        result = await validate_code(code)
    except ValueError:
        return ERROR_CODE_REQUIRED

    if result.valid:
        return f"Valid: true\nDiagram type: {result.diagram_type}"
    else:
        if result.error_line is not None:
            return f"Valid: false\nError at line {result.error_line}: {result.error_message}"
        else:
            return f"Valid: false\nError: {result.error_message}"
