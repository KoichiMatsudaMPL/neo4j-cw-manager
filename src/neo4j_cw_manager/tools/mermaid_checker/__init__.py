"""
Mermaid Checker Module

Provides Mermaid syntax validation and block extraction for Markdown files.
"""

from .block_lister import list_mermaid_blocks
from .code_checker import check_mermaid_code
from .file_checker import check_mermaid_file
from .models import (
    BlockValidationResult,
    CheckCodeResult,
    CheckFileResult,
    ListBlocksResult,
    MermaidBlock,
    ValidationResult,
)

__all__ = [
    # Data models
    "MermaidBlock",
    "ValidationResult",
    "BlockValidationResult",
    "CheckFileResult",
    "CheckCodeResult",
    "ListBlocksResult",
    # Public API
    "check_mermaid_code",
    "check_mermaid_file",
    "list_mermaid_blocks",
]
