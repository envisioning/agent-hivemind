#!/usr/bin/env python3
"""Daily play count tracker for agent-hivemind.

Queries Supabase for current play count, compares to previous,
and reports growth to Michell via Telegram."""

import json
import os
from datetime import datetime
from pathlib import Path

import requests

# Config
SUPABASE_URL = "https://tjcryyjrjxbcjzybzdow.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqY3J5eWpyanhiY2p6eWJ6ZG93Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5NTIzNjUsImV4cCI6MjA4OTUyODM2NX0.G_PtxkbqXO6jz1mGUX7-afO1WlHl1c_z0_QBNbqLeJU"
STATE_FILE = Path(__file__).parent.parent / "state" / "play-count-state.json"

def get_play_count():
    """Query Supabase for total play count."""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
    }
    
    # Get count using supabase REST API
    url = f"{SUPABASE_URL}/rest/v1/plays?select=id&limit=100000"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    plays = resp.json()
    return len(plays)

def load_state():
    """Load previous count state."""
    if STATE_FILE.exists():
        return json.load(open(STATE_FILE))
    return {"last_count": 223, "last_reported": None}  # Baseline from seed

def save_state(state):
    """Save current count state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    json.dump(state, open(STATE_FILE, 'w'), indent=2)

def format_report(current, previous, timestamp):
    """Format the report message."""
    delta = current - previous
    
    lines = [
        f"Hivemind Daily Update",
        f"",
        f"Current plays: {current}",
        f"Previous: {previous}",
    ]
    
    if delta > 0:
        lines.append(f"New today: +{delta}")
        lines.append(f"")
        lines.append(f"Growth: {delta} plays since last check")
    elif delta == 0:
        lines.append(f"No new plays since last check")
    else:
        lines.append(f"Note: count decreased by {abs(delta)} (possible deduplication)")
    
    lines.append(f"")
    lines.append(f"Baseline was 223 at launch")
    lines.append(f"Net growth: +{current - 223} since launch")
    
    return "\n".join(lines)

def main():
    # Get current count
    current = get_play_count()
    
    # Load previous state
    state = load_state()
    previous = state.get("last_count", 223)
    
    # Format report
    timestamp = datetime.now().isoformat()
    report = format_report(current, previous, timestamp)
    
    # Print to stdout (will be captured by OpenClaw)
    print(report)
    
    # Update state
    state["last_count"] = current
    state["last_reported"] = timestamp
    save_state(state)
    
    return current, current - previous

if __name__ == "__main__":
    main()
