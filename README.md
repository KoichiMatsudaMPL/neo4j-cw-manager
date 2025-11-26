# neo4j-cw-manager

Neo4j をバックエンドに使用したタスク管理・ナレッジ管理ツール（MCP サーバー実装）

## 概要

このプロジェクトは [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) サーバーとして実装されており、MCP クライアント（Claude Desktop 等）から利用可能なツールとリソースを提供します。

**現在の状態**: 初期開発段階（サンプルコードベース）

## 必要環境

- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー

## セットアップ

```bash
# 依存パッケージのインストール
uv sync
```

## 使用方法

### Claude Desktop への登録

`~/Library/Application Support/Claude/claude_desktop_config.json` に以下を追加:

```json
{
  "mcpServers": {
    "neo4j-cw-manager": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/neo4j-cw-manager", "python", "main.py"]
    }
  }
}
```

※ `/path/to/neo4j-cw-manager` は実際のプロジェクトパスに置き換えてください。

### 開発時のテスト

```bash
# MCP Inspector でテスト
uv run mcp dev main.py
```

## 現在実装されている機能

### ツール

| ツール名 | 説明 |
|---------|------|
| `add(a, b)` | 2つの数値を加算（サンプル） |
| `multiply(a, b)` | 2つの数値を乗算（サンプル） |

### リソース

| URI パターン | 説明 |
|-------------|------|
| `greeting://{name}` | パーソナライズされた挨拶を取得（サンプル） |
| `info://server` | サーバー情報を取得（サンプル） |

## 技術スタック

- **フレームワーク**: FastMCP (mcp package)
- **トランスポート**: stdio
- **データベース**: Neo4j（予定）

## ライセンス

TBD
