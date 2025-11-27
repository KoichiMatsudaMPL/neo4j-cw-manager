"""Block listing for Mermaid diagrams."""

from typing import List

from .constants import ERROR_FILE_NOT_FOUND, ERROR_FILE_READ, MSG_NO_BLOCKS
from .models import MermaidBlock
from .parser import extract_mermaid_blocks


async def list_mermaid_blocks(file_path: str) -> str:
    """
    Extract and list all Mermaid code blocks from a Markdown file.

    Args:
        file_path: Absolute or relative path to the Markdown file

    Returns:
        Formatted string result for MCP response.
    """
    try:
        blocks: List[MermaidBlock] = extract_mermaid_blocks(file_path)
    except FileNotFoundError:
        return ERROR_FILE_NOT_FOUND.format(path=file_path)
    except (IOError, OSError) as e:
        return ERROR_FILE_READ.format(error=str(e))

    if not blocks:
        return f"File: {file_path}\nTotal blocks: 0\n\n{MSG_NO_BLOCKS}"

    return _format_list_result(file_path, blocks)


def _format_list_result(file_path: str, blocks: List[MermaidBlock]) -> str:
    """Format the block listing result."""
    lines = [
        f"File: {file_path}",
        f"Total blocks: {len(blocks)}",
        "",
    ]

    for block in blocks:
        content_lines = len(block.code.split("\n")) if block.code else 0
        diagram_type = block.diagram_type or "unknown"

        lines.append(f"Block {block.index} (line {block.start_line}-{block.end_line}):")
        lines.append(f"  Type: {diagram_type}")
        lines.append(f"  Lines: {content_lines}")
        lines.append("")

    if lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)
