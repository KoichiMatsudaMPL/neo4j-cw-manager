"""
Markdown Parser for Mermaid Code Blocks

This module provides functionality to extract Mermaid code blocks from Markdown files.

TASK-002: Refactor Phase - Improved Implementation

Example usage:
    >>> from .parser import extract_mermaid_blocks
    >>> blocks = extract_mermaid_blocks("docs/architecture.md")
    >>> for block in blocks:
    ...     print(f"Block {block.index}: {block.diagram_type} at line {block.start_line}")
"""

from typing import List, Optional
from pathlib import Path
from .models import MermaidBlock

# Markdown fence markers
MERMAID_FENCE_START = '```mermaid'
CODE_FENCE_END = '```'

# Diagram type keywords (REQ-NF-003)
DIAGRAM_TYPES = {
    'flowchart': 'flowchart',
    'graph': 'flowchart',  # Alias for flowchart
    'sequenceDiagram': 'sequenceDiagram',
    'classDiagram': 'classDiagram',
    'stateDiagram': 'stateDiagram',
    'stateDiagram-v2': 'stateDiagram',  # Version 2
    'erDiagram': 'erDiagram',
    'gantt': 'gantt',
    'pie': 'pie',
    'gitGraph': 'gitGraph',
}


def extract_mermaid_blocks(file_path: str) -> List[MermaidBlock]:
    """
    Extract all Mermaid code blocks from a Markdown file.

    【機能概要】: Markdownファイルから ```mermaid ... ``` ブロックを抽出
    【実装方針】: シンプルな行単位パース、状態管理で開始/終了を追跡
    【テスト対応】: TC-PARSER-N001 ~ TC-PARSER-B009 (全25件)
    🟢

    Args:
        file_path: Absolute or relative path to Markdown file

    Returns:
        List of MermaidBlock objects, ordered by appearance

    Raises:
        FileNotFoundError: If file does not exist
        IOError: If file cannot be read
        UnicodeDecodeError: If file is not valid UTF-8
    """
    # Read file with UTF-8 encoding
    # Handles: TC-PARSER-E001 (file not found), TC-PARSER-N012 (UTF-8)
    # 🟢
    content = _read_file_content(file_path)

    # Parse lines and extract blocks
    # Handles: TC-PARSER-N001, TC-PARSER-N002, TC-PARSER-B001, TC-PARSER-B002
    # 🟢
    lines = content.split('\n')
    return _parse_lines(lines)


def _read_file_content(file_path: str) -> str:
    """
    Read file content with UTF-8 encoding.

    Args:
        file_path: Path to the file

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file does not exist
        IOError: If file cannot be read
    """
    # Check file existence
    # Handles: TC-PARSER-E001
    # 🟢
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read file with UTF-8 encoding
    # Handles: TC-PARSER-N012 (UTF-8/Japanese support)
    # 🟢
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError as e:
        raise IOError(f"Failed to decode file as UTF-8: {e}") from e
    except Exception as e:
        raise IOError(f"Failed to read file: {e}") from e


def _parse_lines(lines: List[str]) -> List[MermaidBlock]:
    """
    Parse lines and extract Mermaid blocks.

    Args:
        lines: List of lines from the file

    Returns:
        List of extracted MermaidBlock objects
    """
    # Initialize state
    blocks: List[MermaidBlock] = []
    in_mermaid_block = False
    block_start_line = 0
    block_code_lines: List[str] = []
    block_index = 1  # 1-based index

    # Parse line by line
    # Handles: TC-PARSER-N001, TC-PARSER-N002
    # 🟢
    for line_num, line in enumerate(lines, start=1):
        stripped_line = line.strip()

        # Check for Mermaid block start
        if stripped_line.startswith(MERMAID_FENCE_START):
            # Start of Mermaid block
            # 🟢
            in_mermaid_block = True
            block_start_line = line_num
            block_code_lines = []

        elif in_mermaid_block:
            # Inside Mermaid block
            if stripped_line.startswith(CODE_FENCE_END):
                # End of Mermaid block - create MermaidBlock object
                # Handles: TC-PARSER-N001 (line numbers), TC-PARSER-N003-N011 (types)
                # 🟢
                code = '\n'.join(block_code_lines)
                diagram_type = _detect_diagram_type(code)

                block = MermaidBlock(
                    index=block_index,
                    start_line=block_start_line,
                    end_line=line_num,
                    code=code,
                    diagram_type=diagram_type
                )
                blocks.append(block)

                # Reset state for next block
                in_mermaid_block = False
                block_index += 1
            else:
                # Accumulate code lines
                # 🟢
                block_code_lines.append(line)

    # Return extracted blocks (may be empty)
    # Handles: TC-PARSER-B001 (empty file), TC-PARSER-B002 (no blocks)
    # 🟢
    return blocks


def _detect_diagram_type(code: str) -> Optional[str]:
    """
    Detect diagram type from Mermaid code.

    Detects the diagram type by examining the first non-empty line of the code.
    Supports 8 diagram types as specified in REQ-NF-003.

    Args:
        code: Mermaid diagram code

    Returns:
        Diagram type string or None if unknown/empty

    Handles:
        TC-PARSER-N003 to TC-PARSER-N011 (type detection)
        TC-PARSER-B003 (empty block)
        TC-PARSER-B007 (unknown type)
    """
    # Get first non-empty line
    # 🟢
    for line in code.split('\n'):
        line = line.strip()
        if line:
            # Check against known diagram types
            # Handles: REQ-NF-003 (8 diagram types)
            # 🟢
            for keyword, diagram_type in DIAGRAM_TYPES.items():
                if line.startswith(keyword):
                    return diagram_type

            # Unknown type - return None
            # Handles: TC-PARSER-B007
            # 🟢
            return None

    # Empty code - return None
    # Handles: TC-PARSER-B003
    # 🟢
    return None
