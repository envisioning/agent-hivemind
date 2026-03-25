#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import requests

SUPABASE_URL = "https://tjcryyjrjxbcjzybzdow.supabase.co"
PROJECT_REF = "tjcryyjrjxbcjzybzdow"
BATCH_SIZE = 25
SLEEP_SECONDS = 0.25


def get_service_role() -> str:
    env_path = Path.home() / ".openclaw" / "credentials" / "hivemind-supabase.env"
    if env_path.exists():
        data = env_path.read_text(encoding="utf-8")
        for line in data.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "SUPABASE_SERVICE_ROLE_KEY":
                return value.strip().strip('"').strip("'")
    value = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("HIVEMIND_SERVICE_ROLE_KEY")
    if value:
        return value
    raise SystemExit("Missing SUPABASE_SERVICE_ROLE_KEY for Hivemind project")


def headers(key: str) -> dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def fetch_missing(base: str, key: str, limit: int) -> list[dict]:
    r = requests.get(
        f"{base}/rest/v1/plays",
        params={
            "select": "id,title,description",
            "embedding": "is.null",
            "order": "created_at.asc",
            "limit": str(limit),
        },
        headers=headers(key),
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


_MODEL = None

def embed_text(base: str, key: str, text: str) -> list[float]:
    global _MODEL
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as exc:
        raise RuntimeError(f"sentence-transformers unavailable: {exc}")
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL.encode(text).tolist()


def update_row(base: str, key: str, play_id: str, embedding: list[float]) -> None:
    r = requests.patch(
        f"{base}/rest/v1/plays",
        params={"id": f"eq.{play_id}"},
        headers={**headers(key), "Prefer": "return=minimal"},
        json={"embedding": embedding},
        timeout=60,
    )
    r.raise_for_status()


def main() -> int:
    key = get_service_role()
    base = SUPABASE_URL
    total_done = 0
    while True:
        rows = fetch_missing(base, key, BATCH_SIZE)
        if not rows:
            print(f"Done. Backfilled {total_done} plays on {PROJECT_REF}.")
            return 0
        print(f"Processing batch of {len(rows)} missing embeddings...")
        for row in rows:
            text = f"{row.get('title','')}. {row.get('description','')}".strip()
            emb = embed_text(base, key, text)
            if len(emb) != 384:
                raise RuntimeError(f"Unexpected embedding dimension for {row['id']}: {len(emb)}")
            update_row(base, key, row["id"], emb)
            total_done += 1
            print(f"  updated {row['id']} :: {row.get('title','')[:80]}")
            time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
