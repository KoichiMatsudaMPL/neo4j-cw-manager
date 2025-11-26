# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server implementation built with the FastMCP framework. It provides tools and resources that can be accessed by MCP clients.

## Development Setup

### Package Management
This project uses `uv` for Python package management:
- Install dependencies: `uv sync`
- Add new dependencies: `uv add <package-name>`

### Running the Server
Start the MCP server with stdio transport:
```bash
python main.py
```

## Architecture

### MCP Server Structure
- **Entry point**: `main.py` - FastMCP server initialization and tool/resource definitions
- **Transport**: stdio (standard input/output) for client-server communication
- **Framework**: FastMCP from `mcp` package (version >=1.22.0)

### Tool Registration
Tools are registered using the `@mcp.tool()` decorator. Each tool function:
- Must have type hints for parameters and return value
- Should include a docstring describing its purpose
- Is automatically exposed to MCP clients

### Resource Registration
Resources are registered using the `@mcp.resource()` decorator with URI patterns:
- URI pattern format: `scheme://{param}` (e.g., `greeting://{name}`)
- Resource functions receive URI parameters as arguments
- Return string data accessible to MCP clients

### Current Implementation
The codebase currently contains:
- Tools: `add()`, `multiply()` - basic arithmetic operations
- Resources: `get_greeting()`, `get_server_info()` - informational endpoints

## Python Version
Requires Python >=3.11
