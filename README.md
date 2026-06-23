# voikko-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Finnish language verification MCP server powered by [libvoikko](https://voikko.puimula.org/). Provides spell checking, grammar checking, morphological analysis, hyphenation, and tokenization as MCP tools for any MCP-compatible client (OpenWebUI, OpenCode, Claude Desktop, Cursor, etc.).

## Features

- **Spell checking** — verify single words against libvoikko's Finnish dictionary
- **Grammar checking** — detect capitalization, word-order, and agreement errors
- **Morphological analysis** — inspect base form, case, number, possessive suffixes
- **Hyphenation** — syllable-aware word splitting for line-breaking and pronunciation
- **Tokenization** — split Finnish text into words, whitespace, and punctuation tokens
- **SSE transport** — runs as a web server, no local process management needed

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

## Quick start

```bash
docker compose up --build
```

The server starts on `http://localhost:8000` with SSE transport.

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
- **SSE URL**: `http://localhost:8000/sse`

### OpenCode

Add to `opencode.json`:

```json
{
  "mcp": {
    "voikko-mcp": {
      "type": "remote",
      "url": "http://localhost:8000/sse"
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
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### Cursor

Add an MCP server entry with SSE transport pointing to `http://localhost:8000/sse`.

## Architecture

```
Client (OpenWebUI / OpenCode / Claude) ──GET /sse──▶ uvicorn ──▶ FastMCP ──▶ libvoikko
                  ◀──SSE stream (JSON-RPC)──
```

- **Python 3.11** with **FastMCP** from the official MCP Python SDK
- **libvoikko** C++ library via its Python bindings for all linguistic operations
- **SSE transport** over uvicorn, binding `0.0.0.0:8000`
- Docker image based on `python:3.11-slim` with `libvoikko-dev` and `voikko-fi`

## Credits

- [libvoikko](https://voikko.puimula.org/) — Finnish language processing library by the Voikko project
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — Model Context Protocol implementation by Anthropic
- [FastMCP](https://github.com/jlowin/fastmcp) — High-level MCP server framework
- Finnish morphological dictionary ([voikko-fi](https://github.com/voikko/corevoikko)) maintained by the Voikko community

## License

MIT — see [LICENSE](LICENSE) for details.
