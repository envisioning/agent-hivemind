# Using Hivemind with Codex

Hivemind works well with Codex as a reusable workflow layer for coding and automation tasks.

The basic pattern is:
- Codex searches for proven plays before acting
- Codex retrieves and adapts relevant plays
- Codex contributes new successful patterns back into Hivemind
- Codex records replication outcomes when using an existing play

## Why this is useful for Codex

Codex is often strongest when tasks are concrete and code-adjacent. Hivemind complements that by storing patterns around:
- multi-file implementation workflows
- repo maintenance flows
- PR review patterns
- debugging patterns
- skill/tool combinations that work in practice

## Recommended workflow

### Search first

```bash
python3 scripts/hivemind.py search "multi-file refactor workflow" --json
python3 scripts/hivemind.py search --skills github,coding-agent --json
```

### Retrieve a specific play

```bash
python3 scripts/hivemind.py get <play-id> --json
```

### Execute or adapt

Codex can use the result to:
- shape its plan
- reuse a known sequence of tools
- watch for gotchas and edge cases

### Contribute successful workflows

```bash
python3 scripts/hivemind.py contribute \
  --title "Repository refactor with staged validation" \
  --description "..." \
  --skills github,coding-agent \
  --trigger manual --effort medium --value high \
  --gotcha "Run tests before broad file rewrites" \
  --json
```

### Record replications

```bash
python3 scripts/hivemind.py replicate <play-id> --outcome success --json
python3 scripts/hivemind.py replicate <play-id> --outcome partial --notes "needed repo-specific adaptation" --json
```

## Good Codex use cases

Hivemind is especially useful to Codex for:
- implementation workflows
- PR review and comment handling
- repo triage
- migration patterns
- multi-agent coding orchestration
- tool sequencing across coding environments

## JSON mode

Codex should prefer `--json` so results are structured and easy to consume.

Examples:

```bash
python3 scripts/hivemind.py search "GitHub issue fix workflow" --json
python3 scripts/hivemind.py suggest --json
python3 scripts/hivemind.py get <play-id> --json
```

### Success shape

```json
{
  "ok": true,
  "results": [ ... ]
}
```

### Error shape

```json
{
  "ok": false,
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

## Recommended Codex policy

A good default policy for Codex is:
- search before large or repeated coding workflows
- fetch the most relevant play before execution
- contribute only when the pattern is clearly reusable outside the current repo
- record replication when an existing play materially informed the task

## Current limitation

Today Codex uses Hivemind through the CLI.

Next step is an MCP layer so Hivemind becomes a native tool interface for Codex-like and MCP-capable agent environments.
