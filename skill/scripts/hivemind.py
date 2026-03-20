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
    )
    supabase_key = (
        os.environ.get("SUPABASE_KEY")
        or file_values.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
        or file_values.get("SUPABASE_ANON_KEY")
        or os.environ.get("HIVEMIND_ANON_KEY")
        or file_values.get("HIVEMIND_ANON_KEY")
    )

    if not supabase_url or not supabase_key:
        print(
            "Error: missing Supabase config. Set SUPABASE_URL and SUPABASE_KEY "
            "(env or ~/.openclaw/hivemind-config.env).",
            file=sys.stderr,
        )
        sys.exit(1)
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
