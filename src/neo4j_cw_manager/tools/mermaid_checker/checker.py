"""
Mermaid CLI Checker

This module provides functionality to validate Mermaid diagram code syntax
using the official Mermaid CLI (mmdc command).

TASK-003: Refactor Phase - Improved Implementation

Example usage:
    >>> from .checker import validate_code
    >>> result = await validate_code("flowchart TD\\n    A --> B")
    >>> print(f"Valid: {result.valid}, Type: {result.diagram_type}")
"""

import asyncio
import re
import tempfile
from pathlib import Path
from typing import Optional

from .models import ValidationResult
from .parser import DIAGRAM_TYPES

# Constants
DEFAULT_TIMEOUT = 30
TEMP_FILE_SUFFIX = '.mmd'
OUTPUT_FILE_SUFFIX = '.svg'
TEMP_FILE_ENCODING = 'utf-8'

# Error messages
ERROR_CODE_REQUIRED = "Code is required"
ERROR_CLI_NOT_FOUND = "Mermaid CLI not found. Please install @mermaid-js/mermaid-cli"
ERROR_VALIDATION_FAILED = "Validation failed"
ERROR_TIMEOUT_TEMPLATE = "Validation timed out after {timeout}s"

# Regex patterns for error parsing
LINE_NUMBER_PATTERN = re.compile(r'line\s+(\d+)', re.IGNORECASE)


async def validate_code(code: str, timeout: int = DEFAULT_TIMEOUT) -> ValidationResult:
    """
    Validate Mermaid diagram code syntax using Mermaid CLI.

    Function Purpose: Validate Mermaid code and return detailed results
    Implementation Strategy: Use mmdc CLI subprocess with timeout
    Test Correspondence: TC-CHECKER-N001-N012, E001-E006, B001-B006
    🟢

    Args:
        code: Mermaid diagram code to validate
        timeout: Maximum validation time in seconds (default: 30)

    Returns:
        ValidationResult with validation status and error details

    Raises:
        ValueError: If code is empty or whitespace-only

    Example:
        >>> result = await validate_code("flowchart TD\\n    A --> B")
        >>> assert result.valid is True
        >>> assert result.diagram_type == "flowchart"
    """
    # Input Validation: Check for empty code
    # Test Correspondence: TC-CHECKER-E001, TC-CHECKER-E002
    # 🟢
    if not code or not code.strip():
        raise ValueError(ERROR_CODE_REQUIRED)

    # Detect Diagram Type: Extract from first non-empty line
    # Test Correspondence: TC-CHECKER-N001-N011, TC-CHECKER-B003
    # 🟢
    diagram_type = _detect_diagram_type(code)

    # Create Temporary File: Write code to temp file for CLI
    # Implementation: UTF-8 encoding for Japanese support
    # 🟢
    temp_file = None
    try:
        temp_file = _create_temp_file(code)

        # Execute Mermaid CLI: Run mmdc with timeout
        # Test Correspondence: TC-CHECKER-N001-N012
        # 🟢
        exit_code, stdout, stderr = await _run_mmdc(temp_file, timeout)

        # Success Case: Valid syntax
        # 🟢
        if exit_code == 0:
            return ValidationResult(
                valid=True,
                diagram_type=diagram_type,
                error_line=None,
                error_message=None
            )

        # Error Case: Parse CLI output for error details
        # Test Correspondence: TC-CHECKER-E003, TC-CHECKER-E006
        # 🟢
        error_line, error_message = _parse_cli_error(stderr)
        return ValidationResult(
            valid=False,
            diagram_type=diagram_type,
            error_line=error_line,
            error_message=error_message
        )

    except FileNotFoundError:
        # CLI Not Found: mmdc command not available
        # Test Correspondence: TC-CHECKER-E004
        # 🟢
        return ValidationResult(
            valid=False,
            diagram_type=None,
            error_line=None,
            error_message=ERROR_CLI_NOT_FOUND
        )

    except asyncio.TimeoutError:
        # Timeout: Validation exceeded time limit
        # Test Correspondence: TC-CHECKER-E005, TC-CHECKER-B005
        # 🟢
        return ValidationResult(
            valid=False,
            diagram_type=None,
            error_line=None,
            error_message=ERROR_TIMEOUT_TEMPLATE.format(timeout=timeout)
        )

    finally:
        # Cleanup: Delete temporary file
        # 🟢
        if temp_file and temp_file.exists():
            temp_file.unlink(missing_ok=True)


def _detect_diagram_type(code: str) -> Optional[str]:
    """
    Detect diagram type from Mermaid code.

    Function Purpose: Identify diagram type from first line
    Implementation Strategy: Reuse DIAGRAM_TYPES from parser.py
    🟢

    Args:
        code: Mermaid diagram code

    Returns:
        Diagram type string or None if unknown

    Example:
        >>> _detect_diagram_type("flowchart TD\\n    A --> B")
        'flowchart'
        >>> _detect_diagram_type("sequenceDiagram\\n    Alice->>Bob: Hello")
        'sequenceDiagram'
        >>> _detect_diagram_type("unknownType\\n    foo")
        None
    """
    # Implementation: Check first non-empty line against known types
    # Test Correspondence: TC-CHECKER-N001-N011
    # 🟢
    for line in code.split('\n'):
        line = line.strip()
        if line:
            for keyword, diagram_type in DIAGRAM_TYPES.items():
                if line.startswith(keyword):
                    return diagram_type
            # Unknown type - first non-empty line doesn't match any known type
            return None
    # Empty code - no non-empty lines found
    return None


def _create_temp_file(code: str) -> Path:
    """
    Create temporary file with Mermaid code.

    Function Purpose: Write code to temporary .mmd file
    Implementation Strategy: Use NamedTemporaryFile with UTF-8
    🟢

    Args:
        code: Mermaid diagram code

    Returns:
        Path to temporary file

    Note:
        The file is created with delete=False, so caller is responsible
        for cleanup using unlink().
    """
    # Implementation: Create temp file with .mmd extension
    # UTF-8 encoding for Japanese character support
    # 🟢
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix=TEMP_FILE_SUFFIX,
        encoding=TEMP_FILE_ENCODING,
        delete=False
    ) as f:
        f.write(code)
        return Path(f.name)


async def _run_mmdc(temp_file: Path, timeout: int) -> tuple[int, str, str]:
    """
    Run Mermaid CLI (mmdc) command.

    Function Purpose: Execute mmdc subprocess with timeout
    Implementation Strategy: asyncio.create_subprocess_exec with wait_for
    🟢

    Args:
        temp_file: Path to temporary file with Mermaid code
        timeout: Maximum execution time in seconds

    Returns:
        Tuple of (exit_code, stdout, stderr)

    Raises:
        FileNotFoundError: If mmdc command not found
        asyncio.TimeoutError: If execution exceeds timeout

    Note:
        Creates temporary output file which is automatically cleaned up
        in the finally block.
    """
    # Create temporary output file (required by mmdc)
    # 🟢
    output_file = temp_file.with_suffix(OUTPUT_FILE_SUFFIX)

    try:
        # Implementation: Create subprocess for mmdc CLI
        # Command: mmdc --input <file> --output <temp_output>
        # 🟢
        process = await asyncio.create_subprocess_exec(
            'mmdc',
            '--input', str(temp_file),
            '--output', str(output_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            # Execute with timeout
            # Test Correspondence: TC-CHECKER-N012, TC-CHECKER-B004, TC-CHECKER-B005
            # 🟢
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            # returncode should always be set after communicate()
            return_code = process.returncode if process.returncode is not None else 1
            return return_code, stdout.decode('utf-8'), stderr.decode('utf-8')

        except asyncio.TimeoutError:
            # Timeout: Kill process and re-raise
            # 🟢
            process.kill()
            await process.wait()
            raise

    finally:
        # Cleanup: Delete temporary output file
        # 🟢
        if output_file.exists():
            output_file.unlink(missing_ok=True)


def _parse_cli_error(stderr: str) -> tuple[Optional[int], str]:
    """
    Parse Mermaid CLI error output.

    Function Purpose: Extract error line number and message from stderr
    Implementation Strategy: Regex-based flexible parsing
    🟡 (Error format may vary by Mermaid version)

    Args:
        stderr: Standard error output from mmdc

    Returns:
        Tuple of (error_line, error_message)

    Example:
        >>> _parse_cli_error("Parse error on line 3: Unexpected token")
        (3, 'Parse error on line 3: Unexpected token')
        >>> _parse_cli_error("Syntax error")
        (None, 'Syntax error')
    """
    # Implementation: Flexible error parsing
    # Try to extract line number with regex
    # 🟡
    error_line = None
    error_message = stderr.strip()

    # Try to extract line number: "line 3", "on line 3", etc.
    # 🟡
    line_match = LINE_NUMBER_PATTERN.search(stderr)
    if line_match:
        error_line = int(line_match.group(1))

    # Clean up error message (remove extra whitespace, newlines)
    # 🟢
    if error_message:
        # Take first meaningful line
        lines = [line.strip() for line in error_message.split('\n') if line.strip()]
        if lines:
            error_message = lines[0]
        # Fallback to generic message if empty
        if not error_message:
            error_message = ERROR_VALIDATION_FAILED
    else:
        error_message = ERROR_VALIDATION_FAILED

    return error_line, error_message
