"""
Data models for Mermaid Checker MCP Tool.

This module defines Pydantic data models for representing Mermaid code blocks,
validation results, and tool outputs.

Implementation: TDD Green Phase - Minimal implementation to pass tests
Test Coverage: 45 test cases in tests/mermaid_checker/test_models.py
"""

from typing import Optional
from pydantic import BaseModel, Field


class MermaidBlock(BaseModel):
    """
    A Mermaid code block extracted from a Markdown file.

    Implementation: Minimal implementation to pass tests
    Test Coverage: 8 test cases
    🟢
    """

    index: int = Field(..., description="1-based index of the block in the file", ge=1)

    start_line: int = Field(
        ..., description="Line number where the block starts (1-based)", ge=1
    )

    end_line: int = Field(
        ..., description="Line number where the block ends (1-based)", ge=1
    )

    code: str = Field(..., description="The Mermaid diagram code content")

    diagram_type: Optional[str] = Field(
        None, description="Detected diagram type (flowchart, sequenceDiagram, etc.)"
    )


class ValidationResult(BaseModel):
    """
    Result of validating a Mermaid code block.

    Implementation: Minimal implementation to pass tests
    Test Coverage: 4 test cases
    🟢
    """

    valid: bool = Field(..., description="Whether the code is syntactically valid")

    diagram_type: Optional[str] = Field(
        None, description="Detected diagram type if parsing succeeded"
    )

    error_line: Optional[int] = Field(
        None, description="Line number within the block where error occurred", ge=1
    )

    error_message: Optional[str] = Field(
        None, description="Error message describing the syntax error"
    )


class BlockValidationResult(BaseModel):
    """
    Validation result for a specific block in a file.

    Implementation: Minimal implementation to pass tests
    Test Coverage: 1 test case
    🟢
    """

    block: MermaidBlock = Field(..., description="The Mermaid block that was validated")

    result: ValidationResult = Field(
        ..., description="Validation result for this block"
    )


class CheckFileResult(BaseModel):
    """
    Result of checking all Mermaid blocks in a file.

    Implementation: Minimal implementation to pass tests
    Test Coverage: 6 test cases
    🟢
    """

    file_path: str = Field(..., description="Path to the checked file")

    total_blocks: int = Field(
        ..., description="Total number of Mermaid blocks found", ge=0
    )

    valid_blocks: int = Field(..., description="Number of valid blocks", ge=0)

    invalid_blocks: int = Field(..., description="Number of invalid blocks", ge=0)

    errors: list[BlockValidationResult] = Field(
        default_factory=list,
        description="List of validation results for invalid blocks only",
    )


class CheckCodeResult(BaseModel):
    """
    Result of checking a single Mermaid code snippet.

    Implementation: Minimal implementation to pass tests
    Test Coverage: 2 test cases
    🟢
    """

    valid: bool = Field(..., description="Whether the code is syntactically valid")

    diagram_type: Optional[str] = Field(None, description="Detected diagram type")

    error_line: Optional[int] = Field(
        None, description="Line number where error occurred (1-based)", ge=1
    )

    error_message: Optional[str] = Field(None, description="Error message if invalid")


class ListBlocksResult(BaseModel):
    """
    Result of listing Mermaid blocks in a file.

    Implementation: Minimal implementation to pass tests
    Test Coverage: 2 test cases
    🟢
    """

    file_path: str = Field(..., description="Path to the scanned file")

    total_blocks: int = Field(
        ..., description="Total number of Mermaid blocks found", ge=0
    )

    blocks: list[MermaidBlock] = Field(
        default_factory=list, description="List of all Mermaid blocks found"
    )
