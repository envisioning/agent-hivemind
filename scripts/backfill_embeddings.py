#!/usr/bin/env python3
"""Backfill embeddings for existing plays using local sentence-transformers."""

import json
import os
from urllib.request import Request, urlopen

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://tjcryyjrjxbcjzybzdow.supabase.co")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def main():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Fetch plays without embeddings
    req = Request(
        f"{SUPABASE_URL}/rest/v1/plays?embedding=is.null&select=id,title,description",
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
        }
    )
    with urlopen(req) as resp:
        plays = json.loads(resp.read())
    
    print(f"Found {len(plays)} plays without embeddings")
    
    for p in plays:
        text = f"{p['title']}. {p['description']}"
        embedding = model.encode(text).tolist()
        
        # Update via REST
        data = json.dumps({"embedding": embedding}).encode()
        req = Request(
            f"{SUPABASE_URL}/rest/v1/plays?id=eq.{p['id']}",
            data=data, method="PATCH",
            headers={
                "apikey": SERVICE_KEY,
                "Authorization": f"Bearer {SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            }
        )
        with urlopen(req) as resp:
            pass
        print(f"  ✓ {p['title']}")
    
    print(f"\nDone. {len(plays)} embeddings generated.")


if __name__ == "__main__":
    main()
