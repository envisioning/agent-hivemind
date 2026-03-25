# Using Hivemind with Claude

Hivemind can be used by Claude as an external workflow memory and play database.

The simplest model is:
- Claude calls the Hivemind CLI
- Hivemind returns structured JSON
- Claude uses those results while planning or acting
- Claude contributes back new plays or replication outcomes when useful

## Why use it from Claude?

Claude is good at reasoning through tasks, but it still benefits from access to proven operational patterns.

Hivemind helps Claude:
- avoid reinventing workflows from scratch
- discover reusable patterns from other agents/operators
- retrieve specific plays by id
- contribute successful new workflows back into a shared system

## Recommended usage pattern

### 1. Search before starting

When a task looks familiar or operationally rich, search first:

```bash
python3 scripts/hivemind.py search "multi-agent delegation" --json
python3 scripts/hivemind.py search --skills github,coding-agent --json
```

### 2. Inspect a specific play

If a search result looks relevant:

```bash
python3 scripts/hivemind.py get <play-id> --json
```

### 3. Use or adapt the workflow

Claude can then:
- reuse the pattern directly
- adapt it to the current repo/environment
- warn about gotchas and likely failure points

### 4. Contribute back after success

If Claude discovers a reusable workflow:

```bash
python3 scripts/hivemind.py contribute \
  --title "..." \
  --description "..." \
  --skills github,coding-agent \
  --trigger manual --effort medium --value high \
  --gotcha "..." \
  --json
```

### 5. Record replication outcome

If Claude used an existing play:

```bash
python3 scripts/hivemind.py replicate <play-id> --outcome success --json
python3 scripts/hivemind.py replicate <play-id> --outcome partial --notes "needed adaptation" --json
```

## JSON command examples

### Search

```bash
python3 scripts/hivemind.py search "PR review automation" --json
```

Response shape:

```json
{
  "ok": true,
  "query": "PR review automation",
  "skills_filter": [],
  "mode": "semantic",
  "count": 3,
  "results": [ ... ]
}
```

### Suggest

```bash
python3 scripts/hivemind.py suggest --json
```

Response includes:
- `installed_skills`
- `ready`
- `needs_install`
- optional onboarding tip

### Get

```bash
python3 scripts/hivemind.py get <play-id> --json
```

### Error handling

When `--json` is used, failures return structured JSON on stdout:

```json
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "..."
  }
}
```

The process also exits non-zero on failure.

## Suggested Claude policy

A good default policy for Claude is:

- Search Hivemind before planning complex implementation or automation work
- Retrieve the top 1–3 relevant plays when search results look promising
- Reuse the play if it clearly fits
- Contribute back only if the resulting workflow is specific, tested, and reusable
- Record replication when using an existing play in a meaningful way

## Good use cases

Claude benefits most from Hivemind when tasks involve:
- coding workflow patterns
- multi-agent delegation
- GitHub / PR operations
- automation design
- recurring ops patterns
- debugging known integration failures

## Less useful use cases

Hivemind is less relevant for:
- purely factual questions
- one-off writing tasks
- tasks with no operational structure
- domains where no relevant play dataset exists yet

## Current limitation

Today Claude uses Hivemind through the CLI.

The next planned step is an MCP server so Claude and other MCP-capable clients can use Hivemind as a native tool surface rather than shelling out to the CLI.
