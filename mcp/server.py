#!/usr/bin/env python3
"""Thin MCP server for Agent Hivemind.

This v1 server exposes four MCP tools and delegates all business logic to the
existing CLI in scripts/hivemind.py using --json output.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SERVER_NAME = "agent-hivemind"
SERVER_VERSION = "0.1.0"

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "scripts" / "hivemind.py"

TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_plays",
        "description": "Search Hivemind plays by query and/or skill filters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Optional free-text query."},
                "skills": {
                    "description": "Optional skill filters.",
                    "oneOf": [
                        {"type": "array", "items": {"type": "string"}},
                        {"type": "string"},
                    ],
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "get_play",
        "description": "Fetch a single play by id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "play_id": {"type": "string", "description": "Play UUID."},
            },
            "required": ["play_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "contribute_play",
        "description": "Contribute a new play to Hivemind.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "skills": {
                    "description": "Skill slugs as list or comma-separated string.",
                    "oneOf": [
                        {"type": "array", "items": {"type": "string"}},
                        {"type": "string"},
                    ],
                },
                "trigger": {"type": "string", "enum": ["cron", "manual", "reactive", "event"]},
                "effort": {"type": "string", "enum": ["low", "medium", "high"]},
                "value": {"type": "string", "enum": ["low", "medium", "high"]},
                "gotcha": {"type": "string"},
                "os": {"type": "string"},
            },
            "required": ["title", "description", "skills"],
            "additionalProperties": False,
        },
    },
    {
        "name": "replicate_play",
        "description": "Record a replication outcome for a play.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "play_id": {"type": "string"},
                "outcome": {"type": "string", "enum": ["success", "partial", "failed"]},
                "notes": {"type": "string"},
            },
            "required": ["play_id", "outcome"],
            "additionalProperties": False,
        },
    },
]

TOOL_NAMES = {tool["name"] for tool in TOOLS}


class ToolError(RuntimeError):
    pass


def _read_message() -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        text = line.decode("utf-8", errors="replace").strip()
        if not text or ":" not in text:
            continue
        key, value = text.split(":", 1)
        headers[key.strip().lower()] = value.strip()

    length_raw = headers.get("content-length")
    if length_raw is None:
        raise RuntimeError("Missing Content-Length header")
    try:
        length = int(length_raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid Content-Length: {length_raw}") from exc

    payload = sys.stdin.buffer.read(length)
    if not payload:
        return None
    return json.loads(payload.decode("utf-8"))


def _write_message(payload: dict[str, Any]) -> None:
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    header = f"Content-Length: {len(data)}\r\n\r\n".encode("ascii")
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()


def _send_result(msg_id: Any, result: dict[str, Any]) -> None:
    _write_message({"jsonrpc": "2.0", "id": msg_id, "result": result})


def _send_error(msg_id: Any, code: int, message: str, data: Any | None = None) -> None:
    payload: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if data is not None:
        payload["error"]["data"] = data
    _write_message(payload)


def _extract_cli_json(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        candidate = line.strip()
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ToolError("CLI did not return JSON output")


def _normalize_skills(skills: Any) -> str | None:
    if skills is None:
        return None
    if isinstance(skills, str):
        value = skills.strip()
        return value or None
    if isinstance(skills, list):
        normalized = [str(s).strip() for s in skills if str(s).strip()]
        return ",".join(normalized) if normalized else None
    raise ToolError("skills must be a string or array of strings")


def _run_cli_json(args: list[str]) -> dict[str, Any]:
    if not CLI_PATH.exists():
        raise ToolError(f"Missing CLI entrypoint: {CLI_PATH}")

    cmd = [sys.executable, str(CLI_PATH), *args, "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), check=False)

    try:
        payload = _extract_cli_json(result.stdout)
    except ToolError:
        details = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        raise ToolError(f"CLI call failed: {details}") from None

    if result.returncode != 0:
        message = payload.get("error", {}).get("message") if isinstance(payload, dict) else None
        raise ToolError(message or f"CLI call failed with exit code {result.returncode}")

    return payload


def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "search_plays":
        query = str(arguments.get("query", "") or "").strip()
        skills = _normalize_skills(arguments.get("skills"))
        limit = int(arguments.get("limit", 10))
        cmd = ["search"]
        if query:
            cmd.append(query)
        if skills:
            cmd.extend(["--skills", skills])
        cmd.extend(["--limit", str(limit)])
        return _run_cli_json(cmd)

    if name == "get_play":
        play_id = str(arguments.get("play_id", "")).strip()
        if not play_id:
            raise ToolError("play_id is required")
        return _run_cli_json(["get", play_id])

    if name == "contribute_play":
        title = str(arguments.get("title", "")).strip()
        description = str(arguments.get("description", "")).strip()
        skills = _normalize_skills(arguments.get("skills"))
        if not title:
            raise ToolError("title is required")
        if not description:
            raise ToolError("description is required")
        if not skills:
            raise ToolError("skills is required")

        cmd = [
            "contribute",
            "--title",
            title,
            "--description",
            description,
            "--skills",
            skills,
        ]
        for key in ("trigger", "effort", "value", "gotcha", "os"):
            value = arguments.get(key)
            if value is None:
                continue
            value_text = str(value).strip()
            if value_text:
                cmd.extend([f"--{key}", value_text])
        return _run_cli_json(cmd)

    if name == "replicate_play":
        play_id = str(arguments.get("play_id", "")).strip()
        outcome = str(arguments.get("outcome", "")).strip()
        notes = arguments.get("notes")
        if not play_id:
            raise ToolError("play_id is required")
        if outcome not in {"success", "partial", "failed"}:
            raise ToolError("outcome must be one of: success, partial, failed")

        cmd = ["replicate", play_id, "--outcome", outcome]
        if notes is not None and str(notes).strip():
            cmd.extend(["--notes", str(notes).strip()])
        return _run_cli_json(cmd)

    raise ToolError(f"Unknown tool: {name}")


def _tool_success(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
        "structuredContent": payload,
        "isError": False,
    }


def _tool_error(message: str) -> dict[str, Any]:
    payload = {"ok": False, "error": {"code": "MCP_TOOL_ERROR", "message": message}}
    return {
        "content": [{"type": "text", "text": message}],
        "structuredContent": payload,
        "isError": True,
    }


def _handle_request(message: dict[str, Any]) -> None:
    msg_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if method == "initialize":
        _send_result(
            msg_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )
        return

    if method == "ping":
        _send_result(msg_id, {})
        return

    if method == "tools/list":
        _send_result(msg_id, {"tools": TOOLS})
        return

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name not in TOOL_NAMES:
            _send_result(msg_id, _tool_error(f"Unknown tool: {name}"))
            return
        try:
            payload = _call_tool(str(name), arguments)
            _send_result(msg_id, _tool_success(payload))
        except Exception as exc:
            _send_result(msg_id, _tool_error(str(exc)))
        return

    if method == "notifications/initialized":
        return

    if isinstance(method, str) and method.startswith("notifications/"):
        return

    if msg_id is None:
        return

    _send_error(msg_id, -32601, f"Method not found: {method}")


def main() -> None:
    while True:
        try:
            message = _read_message()
            if message is None:
                return
            _handle_request(message)
        except KeyboardInterrupt:
            return
        except json.JSONDecodeError as exc:
            _send_error(None, -32700, f"Parse error: {exc}")
        except Exception as exc:
            _send_error(None, -32000, f"Server error: {exc}")


if __name__ == "__main__":
    main()
