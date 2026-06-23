# voikko-mcp

Finnish language verification MCP server powered by libvoikko. Exposes spell checking, grammar checking, and morphological analysis as MCP tools for any MCP-compatible client.

## Tools

| Tool | Description |
|------|-------------|
| `check_spelling` | Check if a single Finnish word is spelled correctly. Returns correctness and suggestions. |
| `suggest_spelling` | Get spelling suggestions for a misspelled Finnish word. |
| `check_grammar` | Grammar check of full Finnish text. Returns detailed error information with positions and suggestions. |
| `verify_text` | Full verification (spelling + grammar) in a single call. |
| `analyze_word` | Morphological analysis of a Finnish word (basename, case, number, etc.). |
| `hyphenate_word` | Hyphenate a Finnish word into syllables. |
| `tokenize_text` | Tokenize Finnish text into words, whitespace, and punctuation. |

## Build and run

```bash
docker compose up --build
```

The server listens on `http://localhost:8000` using SSE transport.

## Connecting from clients

### OpenWebUI

Go to **Settings > MCP Servers > Add**, then enter:

- **Name**: voikko-mcp
- **SSE URL**: `http://localhost:8000`

### OpenCode

Add to your `opencode.json`:

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

### Claude Desktop / Cursor

Add an MCP server entry with SSE transport pointing to `http://localhost:8000`.
