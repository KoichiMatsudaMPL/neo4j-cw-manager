"""
Mermaid Checker Module

This module provides Pydantic data models and public API functions
for the Mermaid syntax checker MCP tool.

Public API:
    Data Models:
    - MermaidBlock: Represents a Mermaid code block
    - ValidationResult: Represents validation outcome
    - BlockValidationResult: Combines block and validation result
    - CheckFileResult: Aggregated file check result
    - CheckCodeResult: Direct code validation result
    - ListBlocksResult: Block listing result

    Functions:
    - check_mermaid_code: Validate a single Mermaid code snippet
    - check_mermaid_file: Validate all Mermaid blocks in a Markdown file
    - list_mermaid_blocks: Extract and list all Mermaid blocks in a file
"""

from typing import List, Optional

from .models import (
    MermaidBlock,
    ValidationResult,
    BlockValidationResult,
    CheckFileResult,
    CheckCodeResult,
    ListBlocksResult,
)
from .checker import validate_code
from .parser import extract_mermaid_blocks

# Error message constants
ERROR_CODE_REQUIRED = "Error: Code is required"
ERROR_FILE_NOT_FOUND = "Error: File not found: {path}"
ERROR_FILE_READ = "Error: Failed to read file: {error}"
MSG_NO_BLOCKS = "No Mermaid blocks found in this file."
MSG_ALL_VALID = "All Mermaid blocks are syntactically correct."


async def check_mermaid_code(code: Optional[str]) -> str:
    """
    Validate a single Mermaid code snippet directly.

    Function Purpose: Public API for Mermaid code validation
    Implementation Strategy: Delegate to checker.validate_code and format output
    Test Correspondence: TC-CODE-N001~N006, TC-CODE-E001~E004, TC-CODE-B001~B003

    Args:
        code: Mermaid diagram code to validate (can be None)

    Returns:
        Formatted string result for MCP response:
        - Valid: "Valid: true\\nDiagram type: {type}"
        - Invalid: "Valid: false\\nError at line {n}: {message}"
                   or "Valid: false\\nError: {message}"
        - Empty: "Error: Code is required"

    Example:
        >>> result = await check_mermaid_code("flowchart TD\\n    A --> B")
        >>> print(result)
        Valid: true
        Diagram type: flowchart
    """
    # Input Validation: Check for empty/whitespace-only/None code
    # Test Correspondence: TC-CODE-E001, TC-CODE-E002, TC-CODE-E003, TC-CODE-B001
    if code is None or not code.strip():
        return ERROR_CODE_REQUIRED

    # Call checker.validate_code for actual validation
    # Test Correspondence: TC-CODE-N001~N006, TC-CODE-E004, TC-CODE-B002, TC-CODE-B003
    try:
        result = await validate_code(code)
    except ValueError:
        # ValueError raised when code is empty (should be caught above, but defensive)
        return ERROR_CODE_REQUIRED

    # Format output based on validation result
    # Test Correspondence: TC-CODE-N001~N006, TC-CODE-E004
    if result.valid:
        # Valid code: "Valid: true\nDiagram type: {type}"
        return f"Valid: true\nDiagram type: {result.diagram_type}"
    else:
        # Invalid code: Format error message
        if result.error_line is not None:
            # With line number: "Valid: false\nError at line {n}: {message}"
            return f"Valid: false\nError at line {result.error_line}: {result.error_message}"
        else:
            # Without line number: "Valid: false\nError: {message}"
            return f"Valid: false\nError: {result.error_message}"


async def check_mermaid_file(file_path: str) -> str:
    """
    Validate all Mermaid code blocks in a Markdown file.

    Function Purpose: Public API for file-level Mermaid validation
    Implementation Strategy: Extract blocks with parser, validate each with checker
    Test Correspondence: TC-FILE-N001~N006, TC-FILE-E001~E004, TC-FILE-B001~B004, TC-FILE-OUT001~OUT003

    Args:
        file_path: Absolute or relative path to the Markdown file

    Returns:
        Formatted string result for MCP response:
        - All valid: "Checked: {path}\\nTotal blocks: {n}\\nValid: {n}\\nInvalid: 0\\n\\nAll Mermaid blocks are syntactically correct."
        - Some invalid: Include error details with block index and line number
        - No blocks: "Checked: {path}\\nTotal blocks: 0\\n\\nNo Mermaid blocks found in this file."
        - File not found: "Error: File not found: {path}"
        - File read error: "Error: Failed to read file: {error}"

    Example:
        >>> result = await check_mermaid_file("docs/architecture.md")
        >>> print(result)
        Checked: docs/architecture.md
        Total blocks: 2
        Valid: 2
        Invalid: 0

        All Mermaid blocks are syntactically correct.
    """
    # Step 1: Extract Mermaid blocks from file
    # Test Correspondence: TC-FILE-E001, TC-FILE-E004, TC-FILE-B001, TC-FILE-B002
    try:
        blocks: List[MermaidBlock] = extract_mermaid_blocks(file_path)
    except FileNotFoundError:
        # File not found error
        # Test Correspondence: TC-FILE-E001
        return ERROR_FILE_NOT_FOUND.format(path=file_path)
    except (IOError, OSError) as e:
        # File read error (permission denied, etc.)
        # Test Correspondence: TC-FILE-E004
        return ERROR_FILE_READ.format(error=str(e))

    # Step 2: Handle no blocks case
    # Test Correspondence: TC-FILE-B001, TC-FILE-B002, TC-FILE-OUT003
    if not blocks:
        return f"Checked: {file_path}\nTotal blocks: 0\n\n{MSG_NO_BLOCKS}"

    # Step 3: Validate each block
    # Test Correspondence: TC-FILE-N001~N006, TC-FILE-E002, TC-FILE-E003
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
                # Format error detail with block index and line number
                # Test Correspondence: TC-FILE-E002, TC-FILE-E003, TC-FILE-OUT002
                error_msg = _format_block_error(block, result)
                error_details.append(error_msg)
        except ValueError:
            # Empty code in block
            # Test Correspondence: TC-FILE-B004
            invalid_count += 1
            error_details.append(
                f"Error in block {block.index} (line {block.start_line}):\n  Empty mermaid block"
            )

    # Step 4: Format output
    # Test Correspondence: TC-FILE-OUT001, TC-FILE-OUT002, TC-FILE-OUT003
    return _format_file_result(
        file_path, len(blocks), valid_count, invalid_count, error_details
    )


def _format_block_error(block: MermaidBlock, result: ValidationResult) -> str:
    """
    Format error message for a single block.

    Function Purpose: Create formatted error string for invalid block
    Implementation Strategy: Include block index, start line, and error message

    Args:
        block: The Mermaid block that failed validation
        result: The validation result with error details

    Returns:
        Formatted error string
    """
    # Format: "Error in block {index} (line {start_line}):\n  {error_message}"
    error_message = result.error_message or "Unknown error"
    return f"Error in block {block.index} (line {block.start_line}):\n  {error_message}"


def _format_file_result(
    file_path: str,
    total_blocks: int,
    valid_count: int,
    invalid_count: int,
    error_details: List[str],
) -> str:
    """
    Format the complete file validation result.

    Function Purpose: Create formatted output string for file validation
    Implementation Strategy: Follow api-endpoints.md output format specification

    Args:
        file_path: Path to the checked file
        total_blocks: Total number of Mermaid blocks found
        valid_count: Number of valid blocks
        invalid_count: Number of invalid blocks
        error_details: List of formatted error messages

    Returns:
        Formatted result string
    """
    # Build output lines
    lines = [
        f"Checked: {file_path}",
        f"Total blocks: {total_blocks}",
        f"Valid: {valid_count}",
        f"Invalid: {invalid_count}",
        "",  # Empty line before details
    ]

    if invalid_count == 0:
        # All valid case
        # Test Correspondence: TC-FILE-N001, TC-FILE-N002, TC-FILE-OUT001
        lines.append(MSG_ALL_VALID)
    else:
        # Some invalid case - add error details
        # Test Correspondence: TC-FILE-E002, TC-FILE-E003, TC-FILE-OUT002
        lines.extend(error_details)

    return "\n".join(lines)


async def list_mermaid_blocks(file_path: str) -> str:
    """
    Extract and list all Mermaid code blocks from a Markdown file.

    Function Purpose: Public API for listing Mermaid blocks in a file
    Implementation Strategy: Extract blocks with parser and format output
    Test Correspondence: TC-LIST-N001~N007, TC-LIST-E001~E002, TC-LIST-B001~B004, TC-LIST-OUT001~OUT002

    Args:
        file_path: Absolute or relative path to the Markdown file

    Returns:
        Formatted string result for MCP response:
        - Blocks found: "File: {path}\\nTotal blocks: {n}\\n\\nBlock 1 (line X-Y):\\n  Type: {type}\\n  Lines: {count}"
        - No blocks: "File: {path}\\nTotal blocks: 0\\n\\nNo Mermaid blocks found in this file."
        - File not found: "Error: File not found: {path}"
        - File read error: "Error: Failed to read file: {error}"

    Example:
        >>> result = await list_mermaid_blocks("docs/architecture.md")
        >>> print(result)
        File: docs/architecture.md
        Total blocks: 2

        Block 1 (line 19-45):
          Type: sequenceDiagram
          Lines: 26

        Block 2 (line 78-95):
          Type: flowchart
          Lines: 17
    """
    # Step 1: Extract Mermaid blocks from file
    # Test Correspondence: TC-LIST-E001, TC-LIST-E002, TC-LIST-B001, TC-LIST-B002
    try:
        blocks: List[MermaidBlock] = extract_mermaid_blocks(file_path)
    except FileNotFoundError:
        # File not found error
        # Test Correspondence: TC-LIST-E001
        return ERROR_FILE_NOT_FOUND.format(path=file_path)
    except (IOError, OSError) as e:
        # File read error (permission denied, etc.)
        # Test Correspondence: TC-LIST-E002
        return ERROR_FILE_READ.format(error=str(e))

    # Step 2: Handle no blocks case
    # Test Correspondence: TC-LIST-B001, TC-LIST-B002, TC-LIST-OUT002
    if not blocks:
        return f"File: {file_path}\nTotal blocks: 0\n\n{MSG_NO_BLOCKS}"

    # Step 3: Format output with block listing
    # Test Correspondence: TC-LIST-N001~N007, TC-LIST-OUT001
    return _format_list_result(file_path, blocks)


def _format_list_result(file_path: str, blocks: List[MermaidBlock]) -> str:
    """
    Format the block listing result.

    Function Purpose: Create formatted output string for block listing
    Implementation Strategy: Follow api-endpoints.md output format specification

    Args:
        file_path: Path to the scanned file
        blocks: List of extracted Mermaid blocks

    Returns:
        Formatted result string
    """
    # Build header
    lines = [
        f"File: {file_path}",
        f"Total blocks: {len(blocks)}",
        "",  # Empty line after header
    ]

    # Format each block
    for block in blocks:
        # Calculate content line count (excludes fence markers)
        # Lines count = number of lines in block.code
        content_lines = len(block.code.split("\n")) if block.code else 0

        # Format diagram type (use "unknown" if None)
        diagram_type = block.diagram_type or "unknown"

        # Add block info
        lines.append(f"Block {block.index} (line {block.start_line}-{block.end_line}):")
        lines.append(f"  Type: {diagram_type}")
        lines.append(f"  Lines: {content_lines}")
        lines.append("")  # Empty line between blocks

    # Remove trailing empty line
    if lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


__all__ = [
    "MermaidBlock",
    "ValidationResult",
    "BlockValidationResult",
    "CheckFileResult",
    "CheckCodeResult",
    "ListBlocksResult",
    "check_mermaid_code",
    "check_mermaid_file",
    "list_mermaid_blocks",
]
