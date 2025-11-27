"""File validation for Mermaid diagrams."""

from typing import List

from .checker import validate_code
from .constants import (
    ERROR_FILE_NOT_FOUND,
    ERROR_FILE_READ,
    MSG_ALL_VALID,
    MSG_NO_BLOCKS,
)
from .models import MermaidBlock, ValidationResult
from .parser import extract_mermaid_blocks


async def check_mermaid_file(file_path: str) -> str:
    """
    Validate all Mermaid code blocks in a Markdown file.

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
        return f"Checked: {file_path}\nTotal blocks: 0\n\n{MSG_NO_BLOCKS}"

    valid_count = 0
    invalid_count = 0
    error_details: List[str] = []

    for block in blocks:
        try:
            result = await validate_code(block.code)
            if result.valid:
                valid_count += 1
            else:
                invalid_count += 1
                error_msg = _format_block_error(block, result)
                error_details.append(error_msg)
        except ValueError:
            invalid_count += 1
            error_details.append(
                f"Error in block {block.index} (line {block.start_line}):\n"
                "  Empty mermaid block"
            )

    return _format_file_result(
        file_path, len(blocks), valid_count, invalid_count, error_details
    )


def _format_block_error(block: MermaidBlock, result: ValidationResult) -> str:
    """Format error message for a single block."""
    error_message = result.error_message or "Unknown error"
    return f"Error in block {block.index} (line {block.start_line}):\n  {error_message}"


def _format_file_result(
    file_path: str,
    total_blocks: int,
    valid_count: int,
    invalid_count: int,
    error_details: List[str],
) -> str:
    """Format the complete file validation result."""
    lines = [
        f"Checked: {file_path}",
        f"Total blocks: {total_blocks}",
        f"Valid: {valid_count}",
        f"Invalid: {invalid_count}",
        "",
    ]

    if invalid_count == 0:
        lines.append(MSG_ALL_VALID)
    else:
        lines.extend(error_details)

    return "\n".join(lines)
