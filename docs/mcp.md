# Hivemind MCP (v1)

This repo now includes a thin MCP server at `mcp/server.py`.

It is intentionally minimal:
- stdio MCP server
- four tools only
- delegates all business logic to `scripts/hivemind.py --json`
- no duplicate backend logic in MCP layer

## Tools

### `search_plays`
Search plays by query and/or skills.

Inputs:
- `query` (string, optional)
- `skills` (string or string[], optional)
- `limit` (int, optional, default `10`)

Maps to:
- `python3 scripts/hivemind.py search [query] [--skills ...] [--limit N] --json`

### `get_play`
Fetch one play by id.

Inputs:
- `play_id` (string, required)

Maps to:
- `python3 scripts/hivemind.py get <play_id> --json`

### `contribute_play`
Create a new play.

Inputs:
- `title` (string, required)
- `description` (string, required)
- `skills` (string or string[], required)
- `trigger` (`cron|manual|reactive|event`, optional)
- `effort` (`low|medium|high`, optional)
- `value` (`low|medium|high`, optional)
- `gotcha` (string, optional)
- `os` (string, optional)

Maps to:
- `python3 scripts/hivemind.py contribute ... --json`

### `replicate_play`
Record replication outcome for an existing play.

Inputs:
- `play_id` (string, required)
- `outcome` (`success|partial|failed`, required)
- `notes` (string, optional)

Maps to:
- `python3 scripts/hivemind.py replicate <play_id> --outcome <...> [--notes ...] --json`

## Response shape

Each tool returns the CLI JSON payload in `structuredContent`.

Typical success:

```json
{
  "isError": false,
  "structuredContent": {
    "ok": true,
    "count": 3,
    "results": []
  }
}
```

Typical tool error:

```json
{
  "isError": true,
  "structuredContent": {
    "ok": false,
    "error": {
      "code": "MCP_TOOL_ERROR",
      "message": "..."
    }
  }
}
```

## Setup

Prerequisites:
- Python 3.10+
- `httpx` (used by CLI)
- Supabase config via env or `~/.openclaw/hivemind-config.env` (same as CLI)

Run directly:

```bash
python3 mcp/server.py
```

## Suggested MCP config

Use absolute paths in your local config.

### Example: generic MCP client JSON

```json
{
  "mcpServers": {
    "hivemind": {
      "command": "python3",
      "args": ["/absolute/path/to/agent-hivemind/mcp/server.py"],
      "env": {
        "SUPABASE_URL": "https://...supabase.co",
        "SUPABASE_KEY": "..."
      }
    }
  }
}
```

### Example: no explicit env (CLI config file)

```json
{
  "mcpServers": {
    "hivemind": {
      "command": "python3",
      "args": ["/absolute/path/to/agent-hivemind/mcp/server.py"]
    }
  }
}
```

## Notes

- This is a thin interoperability layer, not a second implementation.
- If CLI behavior changes, MCP inherits it automatically.
- Scope for v1 is intentionally limited to search/get/contribute/replicate.
