# voikko-mcp

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Finnish language verification MCP server powered by [libvoikko](https://voikko.puimula.org/). Provides spell checking, grammar checking, morphological analysis, hyphenation, and tokenization as MCP tools for any MCP-compatible client (OpenWebUI, OpenCode, Claude Desktop, Cursor, etc.).

## Features

- **Spell checking** — verify single words against libvoikko's Finnish dictionary
- **Grammar checking** — detect capitalization, word-order, and agreement errors
- **Morphological analysis** — inspect base form, case, number, possessive suffixes
- **Hyphenation** — syllable-aware word splitting for line-breaking and pronunciation
- **Tokenization** — split Finnish text into words, whitespace, and punctuation tokens
- **Streamable HTTP transport** — runs as a web server, no local process management needed

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

## Quick start

```bash
docker compose up --build
```

The server starts on `http://localhost:8000` with Streamable HTTP transport (endpoint at `/mcp`).

## Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `check_spelling` | `word: str` | `{word, correct, suggestions}` |
| `suggest_spelling` | `word: str` | `list[str]` — suggested corrections |
| `check_grammar` | `text: str` | `list[{start, length, snippet, description, suggestions}]` |
| `verify_text` | `text: str` | `{text, is_correct, spelling_errors, grammar_errors}` |
| `analyze_word` | `word: str` | `list[{BASEFORM, CLASS, SIJAMUOTO, ...}]` |
| `hyphenate_word` | `word: str` | `{word, hyphenated}` |
| `tokenize_text` | `text: str` | `list[{token_type, token_text, position}]` |

All tools include error handling and return empty/fallback values on failure.

## Client configuration

### OpenWebUI

**Settings > MCP Servers > Add**:

- **Name**: `voikko-mcp`
- **Transport**: Streamable HTTP
- **URL**: `http://localhost:8000/mcp`

### OpenCode

Add to `opencode.json`:

```json
{
  "mcp": {
    "voikko-mcp": {
      "type": "remote",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "voikko-mcp": {
      "type": "streamableHttp",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Cursor

Add an MCP server entry with Streamable HTTP transport pointing to `http://localhost:8000/mcp`.

## Architecture

```
Client (OpenWebUI / OpenCode / Claude) ──POST /mcp──▶ uvicorn ──▶ FastMCP ──▶ libvoikko
                  ◀──Streamable HTTP (JSON-RPC)──
```

- **Python 3.11** with **FastMCP** from the official MCP Python SDK
- **libvoikko** C++ library via its Python bindings for all linguistic operations
- **Streamable HTTP transport** over uvicorn, binding `0.0.0.0:8000`
- Docker image based on `python:3.11-slim` with `libvoikko-dev` and `voikko-fi`

## Credits

- [libvoikko](https://voikko.puimula.org/) — Finnish language processing library by the Voikko project
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — Model Context Protocol implementation by Anthropic
- [FastMCP](https://github.com/jlowin/fastmcp) — High-level MCP server framework
- Finnish morphological dictionary ([voikko-fi](https://github.com/voikko/corevoikko)) maintained by the Voikko community

## License

GNU General Public License v3.0 or later — see [LICENSE](LICENSE) for details.
