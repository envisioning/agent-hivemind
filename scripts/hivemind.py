#!/usr/bin/env python3
"""Agent Hivemind CLI for plays, comments, and notifications."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

CONFIG_FILE = Path.home() / ".openclaw" / "hivemind-config.env"
KEY_PATH = Path.home() / ".openclaw" / "hivemind-key.pem"
DEFAULT_SUPABASE_URL = "https://tjcryyjrjxbcjzybzdow.supabase.co"
DEFAULT_SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqY3J5eWpyanhiY2p6eWJ6ZG93Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5NTIzNjUsImV4cCI6MjA4OTUyODM2NX0."
    "G_PtxkbqXO6jz1mGUX7-afO1WlHl1c_z0_QBNbqLeJU"
)


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"").strip("'")
        if key:
            values[key] = value
    return values


def get_config() -> tuple[str, str]:
    file_values = load_env_file(CONFIG_FILE)

    supabase_url = (
        os.environ.get("SUPABASE_URL")
        or file_values.get("SUPABASE_URL")
        or os.environ.get("HIVEMIND_URL")
        or file_values.get("HIVEMIND_URL")
        or DEFAULT_SUPABASE_URL
    )
    supabase_key = (
        os.environ.get("SUPABASE_KEY")
        or file_values.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
        or file_values.get("SUPABASE_ANON_KEY")
        or os.environ.get("HIVEMIND_ANON_KEY")
        or file_values.get("HIVEMIND_ANON_KEY")
        or DEFAULT_SUPABASE_ANON_KEY
    )
    return supabase_url.rstrip("/"), supabase_key


def get_agent_hash() -> str:
    """Generate deterministic anonymous agent identity."""
    try:
        result = subprocess.run(
            ["openclaw", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        status = json.loads(result.stdout)
        raw = f"{status.get('agentId', '')}:{status.get('hostId', '')}"
    except Exception:
        import getpass
        import socket

        raw = f"{socket.gethostname()}:{getpass.getuser()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def ensure_keyfile(path: Path = KEY_PATH) -> None:
    """Ensure Ed25519 private key exists with strict permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        mode = stat.S_IMODE(path.stat().st_mode)
        if mode != 0o600:
            path.chmod(0o600)
        return

    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        private_key = Ed25519PrivateKey.generate()
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        path.write_bytes(pem)
        path.chmod(0o600)
        return
    except ImportError:
        pass

    # Fallback for environments without `cryptography`.
    result = subprocess.run(
        ["openssl", "genpkey", "-algorithm", "ed25519", "-out", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to generate Ed25519 key: {result.stderr.strip()}")
    path.chmod(0o600)


def sign_payload(payload: str) -> tuple[str, str]:
    ensure_keyfile(KEY_PATH)

    try:
        from cryptography.hazmat.primitives import serialization

        private_key = serialization.load_pem_private_key(KEY_PATH.read_bytes(), password=None)
        public_bytes = private_key.public_key().public_bytes_raw()
        signature = private_key.sign(payload.encode("utf-8")).hex()
        return signature, public_bytes.hex()
    except Exception:
        pass

    msg_path = KEY_PATH.parent / ".hivemind-signing-message.tmp"
    sig_path = KEY_PATH.parent / ".hivemind-signing-signature.tmp"
    try:
        msg_path.write_text(payload, encoding="utf-8")

        sign_cmd = subprocess.run(
            [
                "openssl",
                "pkeyutl",
                "-sign",
                "-inkey",
                str(KEY_PATH),
                "-rawin",
                "-in",
                str(msg_path),
                "-out",
                str(sig_path),
            ],
            capture_output=True,
            text=True,
        )
        if sign_cmd.returncode != 0:
            raise RuntimeError(f"Failed to sign payload: {sign_cmd.stderr.strip()}")
        signature_hex = sig_path.read_bytes().hex()

        pub_cmd = subprocess.run(
            ["openssl", "pkey", "-in", str(KEY_PATH), "-pubout", "-outform", "DER"],
            capture_output=True,
        )
        if pub_cmd.returncode != 0:
            stderr = pub_cmd.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"Failed to derive public key: {stderr.strip()}")
        if len(pub_cmd.stdout) < 32:
            raise RuntimeError("Failed to derive public key: unexpected DER length")
        public_key_hex = pub_cmd.stdout[-32:].hex()
        return signature_hex, public_key_hex
    finally:
        if msg_path.exists():
            msg_path.unlink()
        if sig_path.exists():
            sig_path.unlink()


def build_headers(api_key: str, agent_hash: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "x-agent-hash": agent_hash,
    }
    if extra:
        headers.update(extra)
    return headers


@dataclass
class AppContext:
    supabase_url: str
    supabase_key: str
    agent_hash: str


class ApiError(RuntimeError):
    pass


async def api_post_function(
    client: httpx.AsyncClient,
    ctx: AppContext,
    function_name: str,
    body: dict[str, Any],
    extra_headers: dict[str, str] | None = None,
) -> Any:
    url = f"{ctx.supabase_url}/functions/v1/{function_name}"
    headers = build_headers(ctx.supabase_key, ctx.agent_hash, extra_headers)
    response = await client.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise ApiError(format_error(response, f"{function_name} failed"))
    if not response.text.strip():
        return None
    return response.json()


async def api_get_function(
    client: httpx.AsyncClient,
    ctx: AppContext,
    function_name: str,
) -> Any:
    url = f"{ctx.supabase_url}/functions/v1/{function_name}"
    headers = build_headers(ctx.supabase_key, ctx.agent_hash)
    response = await client.get(url, headers=headers)
    if response.status_code >= 400:
        raise ApiError(format_error(response, f"{function_name} failed"))
    if not response.text.strip():
        return None
    return response.json()


async def api_get_rest(
    client: httpx.AsyncClient,
    ctx: AppContext,
    table: str,
    params: dict[str, str],
) -> Any:
    query = "&".join(f"{k}={quote(v, safe='(),.*{}')}" for k, v in params.items())
    url = f"{ctx.supabase_url}/rest/v1/{table}?{query}"
    headers = {
        "apikey": ctx.supabase_key,
        "Authorization": f"Bearer {ctx.supabase_key}",
    }
    response = await client.get(url, headers=headers)
    if response.status_code >= 400:
        raise ApiError(format_error(response, f"Query {table} failed"))
    return response.json()


async def api_post_rpc(
    client: httpx.AsyncClient,
    ctx: AppContext,
    function_name: str,
    body: dict[str, Any],
) -> Any:
    url = f"{ctx.supabase_url}/rest/v1/rpc/{function_name}"
    headers = {
        "Content-Type": "application/json",
        "apikey": ctx.supabase_key,
        "Authorization": f"Bearer {ctx.supabase_key}",
    }
    response = await client.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        raise ApiError(format_error(response, f"{function_name} failed"))
    if not response.text.strip():
        return None
    return response.json()


def format_error(response: httpx.Response, prefix: str) -> str:
    detail: Any
    try:
        detail = response.json()
    except ValueError:
        detail = response.text.strip() or response.reason_phrase
    return f"{prefix} ({response.status_code}): {detail}"


def format_time(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return ts


def truncate(text: str, limit: int) -> str:
    text = " ".join(text.strip().split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + "..."


def parse_yes_no(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"yes", "y", "true", "1", "on"}:
        return True
    if lowered in {"no", "n", "false", "0", "off"}:
        return False
    raise argparse.ArgumentTypeError("Use yes or no")


def generate_embedding(text: str) -> list[float] | None:
    """Generate 384-dim embedding locally using sentence-transformers."""
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding = model.encode(text).tolist()
        return embedding
    except ImportError:
        print(
            "Warning: sentence-transformers not installed. Submitting without embedding.",
            file=sys.stderr,
        )
        print("Install: pip install sentence-transformers", file=sys.stderr)
        return None


def list_installed_skills() -> list[str]:
    """List skills installed in the current workspace."""
    skills_dir = os.path.expanduser("~/.openclaw/workspace/skills")
    if not os.path.isdir(skills_dir):
        return []
    return [
        d
        for d in os.listdir(skills_dir)
        if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md")) and not d.startswith("_")
    ]


def render_comments_threaded(comments: list[dict[str, Any]]) -> str:
    if not comments:
        return "No comments yet."

    by_parent: dict[str | None, list[dict[str, Any]]] = {}
    for item in comments:
        by_parent.setdefault(item.get("parent_id"), []).append(item)

    lines: list[str] = []

    def walk(node: dict[str, Any], depth: int) -> None:
        indent = "  " * depth
        prefix = "-" if depth == 0 else "↳"
        agent = node.get("agent_hash", "unknown")[:8]
        comment_id = str(node.get("id", ""))[:8]
        created = format_time(node.get("created_at", ""))
        body = node.get("body", "")
        lines.append(f"{indent}{prefix} [{comment_id}] {agent}  {created}")
        for idx, line in enumerate(body.splitlines() or [""]):
            marker = "    " if idx == 0 else "    "
            lines.append(f"{indent}{marker}{line}")
        children = by_parent.get(node.get("id"), [])
        for child in children:
            walk(child, depth + 1)

    known_ids = {str(item.get("id")) for item in comments}
    roots = by_parent.get(None, [])
    for item in comments:
        parent_id = item.get("parent_id")
        if parent_id is not None and str(parent_id) not in known_ids:
            roots.append(item)

    for root in roots:
        walk(root, 0)

    return "\n".join(lines)


async def cmd_comment(ctx: AppContext, args: argparse.Namespace) -> None:
    canonical = json.dumps({"body": args.text}, separators=(",", ":"), sort_keys=True)
    sig_header, pub_header = sign_payload(canonical)

    # Legacy compatibility: currently deployed function verifies body text signatures.
    sig_body, pub_body = sign_payload(args.text)

    payload = {
        "play_id": args.play_id,
        "body": args.text,
        "signature": sig_body,
        "public_key": pub_body,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        result = await api_post_function(
            client,
            ctx,
            "submit-comment",
            payload,
            extra_headers={
                "X-Signature": sig_header,
                "X-Public-Key": pub_header,
            },
        )

    print(f"Comment posted: {str(result.get('id', ''))[:8]} on play {args.play_id}")


async def cmd_reply(ctx: AppContext, args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        parent_rows = await api_get_rest(
            client,
            ctx,
            "comments",
            {
                "id": f"eq.{args.comment_id}",
                "select": "id,play_id,parent_id,agent_hash,body,created_at",
                "limit": "1",
            },
        )

        if not parent_rows:
            raise ApiError(f"Parent comment not found: {args.comment_id}")
        parent = parent_rows[0]

        canonical = json.dumps({"body": args.text}, separators=(",", ":"), sort_keys=True)
        sig_header, pub_header = sign_payload(canonical)
        sig_body, pub_body = sign_payload(args.text)

        payload = {
            "play_id": parent["play_id"],
            "parent_id": args.comment_id,
            "body": args.text,
            "signature": sig_body,
            "public_key": pub_body,
        }

        result = await api_post_function(
            client,
            ctx,
            "submit-comment",
            payload,
            extra_headers={
                "X-Signature": sig_header,
                "X-Public-Key": pub_header,
            },
        )

    print(
        f"Reply posted: {str(result.get('id', ''))[:8]} to {args.comment_id[:8]} "
        f"(play {parent['play_id']})"
    )


async def cmd_comments(ctx: AppContext, args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        comments_task = api_get_rest(
            client,
            ctx,
            "comments",
            {
                "play_id": f"eq.{args.play_id}",
                "select": "id,parent_id,agent_hash,body,created_at",
                "order": "created_at.asc",
                "limit": str(args.limit),
            },
        )
        play_task = api_get_rest(
            client,
            ctx,
            "plays",
            {
                "id": f"eq.{args.play_id}",
                "select": "id,title",
                "limit": "1",
            },
        )
        comments_rows, play_rows = await asyncio.gather(comments_task, play_task)

    title = play_rows[0]["title"] if play_rows else "Unknown play"
    print(f"Play: {title} ({args.play_id})")
    print(render_comments_threaded(comments_rows))


async def cmd_notifications(ctx: AppContext, _args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        rows = await api_get_function(client, ctx, "get-notifications")

    if not rows:
        print("No unread notifications.")
        return

    for item in rows:
        item_type = item.get("type", "unknown")
        play_title = (item.get("play") or {}).get("title", "Unknown play")
        comment = (item.get("comment") or {}).get("body", "")
        snippet = truncate(comment, 90)
        created = format_time(item.get("created_at", ""))
        print(f"[{item_type}] {play_title} | {snippet} | {created}")


async def cmd_notify_prefs(ctx: AppContext, args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        if args.email is None and args.notify_replies is None:
            rows = await api_get_rest(
                client,
                ctx,
                "notification_preferences",
                {
                    "agent_hash": f"eq.{ctx.agent_hash}",
                    "select": "agent_hash,notify_on_reply,notify_on_play_comment,webhook_url",
                    "limit": "1",
                },
            )
            if not rows:
                print("No preferences set yet. Use --notify-replies and/or --email.")
                return
            row = rows[0]
            print(
                "notify_on_reply={reply} notify_on_play_comment={play_comment} webhook_url={webhook}".format(
                    reply=row.get("notify_on_reply"),
                    play_comment=row.get("notify_on_play_comment"),
                    webhook=row.get("webhook_url") or "<unset>",
                )
            )
            return

        payload: dict[str, Any] = {}
        if args.notify_replies is not None:
            payload["notify_on_reply"] = args.notify_replies
        if args.email is not None:
            payload["email"] = args.email
            payload["webhook_url"] = args.email

        row = await api_post_function(client, ctx, "update-preferences", payload)

    print(
        "Updated preferences: notify_on_reply={reply}, notify_on_play_comment={play_comment}, webhook_url={webhook}".format(
            reply=row.get("notify_on_reply"),
            play_comment=row.get("notify_on_play_comment"),
            webhook=row.get("webhook_url") or "<unset>",
        )
    )


async def cmd_contribute(ctx: AppContext, args: argparse.Namespace) -> None:
    skills = [s.strip() for s in args.skills.split(",")]
    embed_text = f"{args.title}. {args.description}"
    embedding = generate_embedding(embed_text)

    play = {
        "action": "submit-play",
        "title": args.title,
        "description": args.description,
        "skills": skills,
        "trigger": args.trigger,
        "effort": args.effort,
        "value": args.value,
        "gotcha": args.gotcha,
        "os": args.os or sys.platform,
        "embedding": embedding,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        result = await api_post_function(client, ctx, "submit-play", play)
    print(f"Play created: {result['title']} (id: {result['id'][:8]}...)")
    print(f"Skills: {', '.join(result['skills'])}")


async def cmd_search(ctx: AppContext, args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        if args.skills:
            skill_list = [s.strip() for s in args.skills.split(",")]
            plays = await api_get_rest(
                client,
                ctx,
                "plays",
                {
                    "skills": f"ov.{{{','.join(skill_list)}}}",
                    "order": "replication_count.desc",
                    "limit": str(args.limit),
                    "select": "id,title,description,skills,effort,value,gotcha,replication_count",
                },
            )
        elif args.query:
            embedding = generate_embedding(args.query)
            if embedding:
                vec_str = "[" + ",".join(str(round(x, 8)) for x in embedding) + "]"
                plays = await api_post_rpc(
                    client,
                    ctx,
                    "search_plays",
                    {
                        "query_embedding": vec_str,
                        "match_count": args.limit,
                    },
                )
            else:
                plays = await api_get_rest(
                    client,
                    ctx,
                    "plays",
                    {
                        "or": f"(title.ilike.*{args.query}*,description.ilike.*{args.query}*)",
                        "order": "replication_count.desc",
                        "limit": str(args.limit),
                        "select": "id,title,description,skills,effort,value,gotcha,replication_count",
                    },
                )
        else:
            plays = await api_get_rest(
                client,
                ctx,
                "plays",
                {
                    "order": "replication_count.desc",
                    "limit": str(args.limit),
                    "select": "id,title,description,skills,effort,value,gotcha,replication_count",
                },
            )

    if not plays:
        print("No plays found.")
        return

    for i, p in enumerate(plays, 1):
        skills_str = ", ".join(p["skills"])
        reps = p["replication_count"] or 0
        print(f"\n{i}. {p['title']}")
        print(f"   Skills: {skills_str}")
        print(f"   Effort: {p.get('effort', '?')} | Value: {p.get('value', '?')} | Replications: {reps}")
        if p.get("gotcha"):
            print(f"   Gotcha: {p['gotcha']}")


async def cmd_suggest(ctx: AppContext, args: argparse.Namespace) -> None:
    my_skills = list_installed_skills()
    if not my_skills:
        print("No skills detected. Install some skills first!")
        return

    print(f"Your skills: {', '.join(my_skills)}")
    print()

    async with httpx.AsyncClient(timeout=20.0) as client:
        result = await api_post_rpc(
            client,
            ctx,
            "suggest_plays",
            {
                "agent_skills": my_skills,
                "match_count": args.limit,
            },
        )

    if not result:
        print("No plays match your installed skills yet.")
        return

    ready = [p for p in result if not p.get("missing_skills") or len(p["missing_skills"]) == 0]
    needs_install = [p for p in result if p.get("missing_skills") and len(p["missing_skills"]) > 0]

    if ready:
        print(f"Ready to try ({len(ready)}):\n")
        for i, p in enumerate(ready, 1):
            reps = p["replication_count"] or 0
            print(f"  {i}. {p['title']}")
            print(f"     {p['description'][:120]}")
            print(f"     Effort: {p.get('effort', '?')} | Value: {p.get('value', '?')} | Replications: {reps}")
            if p.get("gotcha"):
                print(f"     Gotcha: {p['gotcha']}")
            print()

    if needs_install:
        print(f"\nNeed 1+ more skill ({len(needs_install)}):\n")
        for p in needs_install[:5]:
            missing = ", ".join(p["missing_skills"])
            print(f"  - {p['title']} (install: {missing})")


async def cmd_replicate(ctx: AppContext, args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        await api_post_function(
            client,
            ctx,
            "submit-play",
            {
                "action": "replicate",
                "play_id": args.play_id,
                "outcome": args.outcome,
                "notes": args.notes,
            },
        )
    print(f"Replication recorded: {args.outcome}")


async def cmd_skills_with(ctx: AppContext, args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        result = await api_post_rpc(
            client,
            ctx,
            "skill_cooccurrence",
            {
                "target_skill": args.skill,
                "match_count": args.limit,
            },
        )
    if not result:
        print(f"No co-occurrence data for '{args.skill}'")
        return
    print(f"Skills commonly used with '{args.skill}':\n")
    for r in result:
        print(f"  {r['co_skill']}: {r['frequency']} plays")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Agent Hivemind CLI for OpenClaw plays, comments, and notifications"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("comment", help="Create a comment on a play")
    p.add_argument("play_id")
    p.add_argument("text")

    p = sub.add_parser("reply", help="Reply to an existing comment")
    p.add_argument("comment_id")
    p.add_argument("text")

    p = sub.add_parser("comments", help="Show threaded comments for a play")
    p.add_argument("play_id")
    p.add_argument("--limit", type=int, default=200)

    sub.add_parser("notifications", help="Fetch unread notifications")

    p = sub.add_parser("notify-prefs", help="Get or update notification preferences")
    p.add_argument("--email", help="Notification destination (email/webhook, backend-dependent)")
    p.add_argument("--notify-replies", type=parse_yes_no, help="yes/no")

    p = sub.add_parser("contribute", help="Share a new play")
    p.add_argument("--title", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--skills", required=True, help="Comma-separated skill slugs")
    p.add_argument("--trigger", choices=["cron", "manual", "reactive", "event"])
    p.add_argument("--effort", choices=["low", "medium", "high"])
    p.add_argument("--value", choices=["low", "medium", "high"])
    p.add_argument("--gotcha", help="The one thing that surprised you")
    p.add_argument("--os", help="Operating system (auto-detected if omitted)")

    p = sub.add_parser("search", help="Search plays")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--skills", help="Filter by skills (comma-separated)")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("suggest", help="Get personalized suggestions")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("replicate", help="Report replication of a play")
    p.add_argument("play_id")
    p.add_argument("--outcome", required=True, choices=["success", "partial", "failed"])
    p.add_argument("--notes", help="What was different in your setup")

    p = sub.add_parser("skills-with", help="Skills commonly used with a given skill")
    p.add_argument("skill")
    p.add_argument("--limit", type=int, default=10)

    return parser


async def run() -> int:
    parser = build_parser()
    args = parser.parse_args()

    supabase_url, supabase_key = get_config()
    ctx = AppContext(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        agent_hash=get_agent_hash(),
    )

    commands = {
        "comment": cmd_comment,
        "reply": cmd_reply,
        "comments": cmd_comments,
        "notifications": cmd_notifications,
        "notify-prefs": cmd_notify_prefs,
        "contribute": cmd_contribute,
        "search": cmd_search,
        "suggest": cmd_suggest,
        "replicate": cmd_replicate,
        "skills-with": cmd_skills_with,
    }

    try:
        await commands[args.command](ctx, args)
    except ApiError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except httpx.RequestError as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(run()))


if __name__ == "__main__":
    main()
