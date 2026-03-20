#!/usr/bin/env python3
"""Enrich plays descriptions using Claude API with source context."""
import json, os, glob, sys
import requests

OR_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OR_URL = "https://openrouter.ai/api/v1/chat/completions"

# Load all plays
with open(os.path.expanduser("~/Projects/agent-hivemind/seed-data/community-plays.jsonl")) as f:
    plays = [json.loads(line) for line in f if line.strip()]

# Load transcripts for context
transcripts = {}
for txt in glob.glob(os.path.expanduser("~/Projects/agent-hivemind/seed-data/transcripts/*.txt")):
    name = os.path.basename(txt)
    with open(txt) as f:
        content = f.read()[:8000]  # First 8K chars
    transcripts[name] = content

def get_source_context(play):
    """Get source context if available."""
    src = play.get("source", "")
    # Check if source is a transcript filename
    for tname, tcontent in transcripts.items():
        if tname in src:
            return f"From YouTube video transcript '{tname}':\n{tcontent[:4000]}"
    return ""

def enrich_batch(batch, batch_num):
    """Enrich a batch of plays."""
    plays_text = ""
    for i, play in enumerate(batch):
        ctx = get_source_context(play)
        ctx_note = f"\n[SOURCE CONTEXT]: {ctx[:2000]}" if ctx else ""
        plays_text += f"""
---PLAY {i+1}---
Title: {play['title']}
Current description: {play['description']}
Current gotcha: {play['gotcha']}
Skills: {', '.join(play.get('skills', []))}
Trigger: {play.get('trigger', '')}
Source: {play.get('source', '')}{ctx_note}
"""

    resp = requests.post(OR_URL, headers={
        "Authorization": f"Bearer {OR_KEY}",
        "Content-Type": "application/json"
    }, json={
        "model": "anthropic/claude-haiku-4-5",
        "max_tokens": 8000,
        "messages": [{
            "role": "user",
            "content": f"""Rewrite the description and gotcha for each play below. Return ONLY a JSON array of objects with "index" (1-based), "description", and "gotcha".

Rules:
- Description: 3-6 rich sentences. Explain the full workflow step by step. Name specific tools, integrations, costs, schedules. What triggers it, what the agent does, what the user gets.
- Gotcha: 2-3 sentences. The specific non-obvious thing that trips people up. Implementation details only insiders know.
- NO generic filler ("delivered via Telegram", "monitor costs carefully", "test thoroughly")
- NO marketing language
- Sound like a developer explaining to another developer
- If limited source context, write 2-3 solid sentences rather than padding with fluff

{plays_text}

Return ONLY valid JSON array. No markdown, no code fences."""
        }]
    })
    response = resp.json()
    
    try:
        text = response["choices"][0]["message"]["content"].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        results = json.loads(text)
        return results
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  JSON parse error in batch {batch_num}: {e}", file=sys.stderr)
        print(f"  Raw: {text[:200]}", file=sys.stderr)
        return None

# Process in batches of 10
BATCH_SIZE = 10
enriched = list(plays)  # copy
total_enriched = 0

for batch_start in range(0, len(plays), BATCH_SIZE):
    batch = plays[batch_start:batch_start + BATCH_SIZE]
    batch_num = batch_start // BATCH_SIZE + 1
    print(f"Batch {batch_num}/{(len(plays) + BATCH_SIZE - 1) // BATCH_SIZE} (plays {batch_start+1}-{batch_start+len(batch)})...")
    
    results = enrich_batch(batch, batch_num)
    if results:
        for r in results:
            idx = r.get("index", 0) - 1
            if 0 <= idx < len(batch):
                global_idx = batch_start + idx
                enriched[global_idx]["description"] = r["description"]
                enriched[global_idx]["gotcha"] = r["gotcha"]
                total_enriched += 1
    else:
        print(f"  Skipping batch {batch_num} (parse error)", file=sys.stderr)

# Write output
outpath = os.path.expanduser("~/Projects/agent-hivemind/seed-data/community-plays-v2.jsonl")
with open(outpath, "w") as f:
    for play in enriched:
        f.write(json.dumps(play) + "\n")

print(f"\nDone! Enriched {total_enriched}/{len(plays)} plays → {outpath}")
