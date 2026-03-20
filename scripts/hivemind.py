#!/usr/bin/env python3
"""Agent Hivemind CLI for plays, comments, and notifications."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

CONFIG_FILE = Path.home() / ".openclaw" / "hivemind-config.env"
CONFIG_CACHE = Path.home() / ".openclaw" / "hivemind-config-cache.json"
KEY_PATH = Path.home() / ".openclaw" / "hivemind-key.pem"
ONBOARD_FLAG_PATH = Path.home() / ".openclaw" / "hivemind-onboard-done"
SYNC_STATE_PATH = Path.home() / ".openclaw" / "hivemind-sync-state.json"
CONFIG_ENDPOINT = "https://tjcryyjrjxbcjzybzdow.supabase.co/functions/v1/hivemind-config"

ONBOARD_INTRO = """Agent Hivemind — Onboarding

This will scan your OpenClaw cron jobs and installed skills to detect
automations you're already running. You can review each one and choose
to share it with the hivemind community.

What gets shared: title, description, skills used, trigger type, effort/value estimate.
What stays private: your workspace files, memory, credentials, config, personal data.
Your identity: an anonymous hash (not reversible to you).

Continue? [Y/n] """

ONBOARD_TIP = "Tip: run 'hivemind onboard' to share your plays with the community."


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


def _fetch_remote_config() -> tuple[str, str] | None:
    """Fetch config from remote endpoint, cache locally for 24h."""
    import time

    # Check cache first
    if CONFIG_CACHE.exists():
        try:
            cache = json.loads(CONFIG_CACHE.read_text(encoding="utf-8"))
            if time.time() - cache.get("fetched_at", 0) < 86400:  # 24h
                return cache["supabase_url"], cache["supabase_anon_key"]
        except (json.JSONDecodeError, KeyError):
            pass

    # Fetch from remote
    try:
        from urllib.request import Request, urlopen

        req = Request(CONFIG_ENDPOINT, headers={"Accept": "application/json"})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            url = data["supabase_url"]
            key = data["supabase_anon_key"]
            # Cache it
            CONFIG_CACHE.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_CACHE.write_text(
                json.dumps({"supabase_url": url, "supabase_anon_key": key, "fetched_at": time.time()}),
                encoding="utf-8",
            )
            return url, key
    except Exception:
        return None


def get_config() -> tuple[str, str]:
    file_values = load_env_file(CONFIG_FILE)

    # Priority: env vars > config file > remote endpoint (cached)
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

    # If either is missing, try remote config
    if not supabase_url or not supabase_key:
        remote = _fetch_remote_config()
        if remote:
            supabase_url = supabase_url or remote[0]
            supabase_key = supabase_key or remote[1]

    if not supabase_url or not supabase_key:
        print(
            "Error: missing Supabase config. Set SUPABASE_URL and SUPABASE_KEY "
            "(env or ~/.openclaw/hivemind-config.env), or check your network connection.",
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


@dataclass
class DetectedPlay:
    title: str
    description: str
    skills: list[str]
    trigger: str
    effort: str
    value: str
    schedule: str | None = None


@dataclass
class OnboardScanResult:
    cron_jobs: list[dict[str, Any]]
    installed_skills: list[str]
    cron_failed: bool


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
    """Generate 384-dim embedding locally if sentence-transformers is available.
    Returns None if unavailable — the server generates embeddings automatically
    using Supabase's built-in gte-small model."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(text).tolist()
    except Exception:
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


def command_exists(name: str) -> bool:
    return subprocess.run(["which", name], capture_output=True, text=True).returncode == 0


def run_local_command(cmd: list[str], timeout: int = 20) -> tuple[bool, str, str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as exc:
        return False, "", str(exc)


def sanitize_generic_text(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    # Remove paths, emails, IPs, and collapse whitespace.
    text = re.sub(r"(?:[A-Za-z]:\\|~?/|/)[^\s,;]+", "", text)
    text = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "", text)
    text = re.sub(r"\b[^@\s]+@[^@\s]+\.[^@\s]+\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:120]


def parse_skills_from_text(text: str, installed_skills: list[str]) -> set[str]:
    lowered = text.lower()
    return {skill for skill in installed_skills if skill.lower() in lowered}


def parse_clawhub_list(stdout: str) -> list[str]:
    skills: list[str] = []
    seen: set[str] = set()
    for raw in stdout.splitlines():
        line = raw.strip()
        if not line:
            continue
        if set(line) <= {"-", "=", "|"}:
            continue
        lowered = line.lower()
        if lowered.startswith("installed") or lowered.startswith("available"):
            continue
        # Accept common skill slug characters.
        m = re.match(r"^[-*]?\s*([a-z0-9][a-z0-9._-]{1,63})\b", lowered)
        if not m:
            continue
        skill = m.group(1)
        if skill in {"name", "skill", "skills", "id"}:
            continue
        if skill not in seen:
            seen.add(skill)
            skills.append(skill)
    return skills


def _extract_jobs_from_cron_json(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("jobs", "crons", "items", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _extract_schedule(job: dict[str, Any]) -> str | None:
    for key in ("schedule", "cron", "expression", "spec"):
        value = job.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    trigger = job.get("trigger")
    if isinstance(trigger, dict):
        for key in ("schedule", "cron", "expression"):
            value = trigger.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _extract_name(job: dict[str, Any]) -> str:
    for key in ("name", "title", "id", "job"):
        value = job.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Cron automation"


def _extract_skills_from_obj(value: Any, installed_skills: list[str], out: set[str]) -> None:
    if isinstance(value, str):
        out.update(parse_skills_from_text(value, installed_skills))
        return
    if isinstance(value, list):
        for item in value:
            _extract_skills_from_obj(item, installed_skills, out)
        return
    if not isinstance(value, dict):
        return
    for key, inner in value.items():
        lowered = str(key).lower()
        if lowered in {"skill", "skills", "tool", "tools", "target_skill", "target_skills"}:
            if isinstance(inner, str):
                out.update(parse_skills_from_text(inner, installed_skills))
            elif isinstance(inner, list):
                for item in inner:
                    if isinstance(item, str):
                        out.update(parse_skills_from_text(item, installed_skills))
        _extract_skills_from_obj(inner, installed_skills, out)


def _normalize_title_from_job_name(job_name: str) -> str:
    cleaned = sanitize_generic_text(job_name)
    words = re.findall(r"[A-Za-z0-9]+", cleaned)
    if not words:
        return "Cron automation"
    # Keep generic short title.
    title = " ".join(words[:6]).strip()
    return title.capitalize() if title else "Cron automation"


KNOWN_PATTERNS: list[dict[str, Any]] = [
    {
        "required": {"weather", "calendar"},
        "title": "Morning daily brief",
        "description": (
            "Automated morning summary combining weather and calendar events."
        ),
    },
    {
        "required": {"weather", "calendar", "todoist"},
        "title": "Morning daily brief",
        "description": (
            "Automated morning summary combining weather, calendar events, and todo items."
        ),
    },
    {
        "required": {"gmail", "todoist"},
        "title": "Email to tasks sync",
        "description": (
            "Automates extracting action items from email and creating tasks."
        ),
    },
    {
        "required": {"github", "calendar"},
        "title": "Daily engineering standup",
        "description": (
            "Generates a daily standup summary from code activity and scheduled meetings."
        ),
    },
]


def detect_play_patterns(scan: OnboardScanResult) -> list[DetectedPlay]:
    detected: list[DetectedPlay] = []
    installed_set = set(scan.installed_skills)
    seen_keys: set[tuple[str, str, tuple[str, ...], str | None]] = set()

    for job in scan.cron_jobs:
        name = _extract_name(job)
        schedule = _extract_schedule(job)
        job_skills: set[str] = set()
        _extract_skills_from_obj(job, scan.installed_skills, job_skills)
        job_skills.update(parse_skills_from_text(name, scan.installed_skills))
        if not job_skills:
            text_blob = json.dumps(job, ensure_ascii=True)
            job_skills.update(parse_skills_from_text(text_blob, scan.installed_skills))

        title = _normalize_title_from_job_name(name)
        description = f"Automated '{title}' workflow."
        if schedule:
            description += f" Runs on cron schedule ({schedule})."

        best_pattern: dict[str, Any] | None = None
        for pattern in KNOWN_PATTERNS:
            required = pattern["required"]
            if required.issubset(job_skills):
                if best_pattern is None or len(required) > len(best_pattern["required"]):
                    best_pattern = pattern

        if best_pattern:
            title = best_pattern["title"]
            description = best_pattern["description"]
            if schedule:
                description += f" Triggered by cron ({schedule})."

        ordered_skills = sorted(job_skills)
        key = (title.lower(), "cron", tuple(ordered_skills), schedule)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        detected.append(
            DetectedPlay(
                title=title,
                description=sanitize_generic_text(description),
                skills=ordered_skills,
                trigger="cron",
                effort="low",
                value="medium",
                schedule=schedule,
            )
        )

    if scan.cron_failed or not scan.cron_jobs:
        for pattern in KNOWN_PATTERNS:
            required = pattern["required"]
            if required.issubset(installed_set):
                ordered_skills = sorted(required)
                key = (pattern["title"].lower(), "manual", tuple(ordered_skills), None)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                detected.append(
                    DetectedPlay(
                        title=pattern["title"],
                        description=pattern["description"],
                        skills=ordered_skills,
                        trigger="manual",
                        effort="medium",
                        value="medium",
                        schedule=None,
                    )
                )
    return detected


def scan_openclaw_for_onboarding() -> OnboardScanResult:
    installed_skills: list[str] = []
    cron_jobs: list[dict[str, Any]] = []
    cron_failed = False

    if command_exists("clawhub"):
        ok, stdout, _stderr = run_local_command(["clawhub", "list"])
        if ok and stdout:
            installed_skills = parse_clawhub_list(stdout)
    if not installed_skills:
        installed_skills = list_installed_skills()

    if command_exists("openclaw"):
        ok, stdout, stderr = run_local_command(["openclaw", "cron", "list", "--json"])
        if ok and stdout:
            try:
                payload = json.loads(stdout)
                cron_jobs = _extract_jobs_from_cron_json(payload)
            except json.JSONDecodeError:
                cron_failed = True
                print("Warning: openclaw cron list --json returned invalid JSON; using skills-only matching.")
        else:
            cron_failed = True
            if stderr:
                print(f"Warning: openclaw cron list failed; using skills-only matching. ({stderr})")
            else:
                print("Warning: openclaw cron list failed; using skills-only matching.")
    else:
        cron_failed = True
        print("Warning: openclaw CLI not found; using skills-only matching.")

    return OnboardScanResult(
        cron_jobs=cron_jobs,
        installed_skills=sorted(set(installed_skills)),
        cron_failed=cron_failed,
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso(ts: datetime | None = None) -> str:
    value = ts or _utc_now()
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _cron_job_key(job: dict[str, Any]) -> str:
    for key in ("id", "job_id", "uuid"):
        value = job.get(key)
        if isinstance(value, str) and value.strip():
            return f"id:{value.strip()}"
    name = _extract_name(job)
    schedule = _extract_schedule(job) or ""
    return f"name:{name.lower()}|schedule:{schedule}"


def load_sync_state(path: Path = SYNC_STATE_PATH) -> dict[str, Any]:
    default: dict[str, Any] = {
        "last_sync": None,
        "known_cron_jobs": [],
        "reported_plays": [],
    }
    if not path.exists():
        return default
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default
    if not isinstance(raw, dict):
        return default
    state = dict(default)
    state["last_sync"] = raw.get("last_sync")
    state["known_cron_jobs"] = [str(v) for v in raw.get("known_cron_jobs", []) if isinstance(v, str)]
    state["reported_plays"] = [str(v) for v in raw.get("reported_plays", []) if isinstance(v, str)]
    return state


def save_sync_state(state: dict[str, Any], path: Path = SYNC_STATE_PATH) -> None:
    payload = {
        "last_sync": state.get("last_sync"),
        "known_cron_jobs": sorted(set(str(v) for v in state.get("known_cron_jobs", []) if str(v).strip())),
        "reported_plays": sorted(set(str(v) for v in state.get("reported_plays", []) if str(v).strip())),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


async def fetch_new_community_plays(
    client: httpx.AsyncClient,
    ctx: AppContext,
    last_sync_iso: str,
    installed_skills: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    rows = await api_get_rest(
        client,
        ctx,
        "plays",
        {
            "created_at": f"gte.{last_sync_iso}",
            "order": "created_at.desc",
            "select": "id,title,skills,effort,value,agent_hash,created_at",
            "limit": "200",
        },
    )
    installed_set = set(installed_skills)
    filtered: list[dict[str, Any]] = []
    for row in rows:
        if row.get("agent_hash") == ctx.agent_hash:
            continue
        skills = [s for s in row.get("skills", []) if isinstance(s, str)]
        if not skills:
            continue
        overlap = installed_set.intersection(skills)
        if not overlap:
            continue
        row["skills"] = skills
        filtered.append(row)

    ready: list[dict[str, Any]] = []
    need_one: list[dict[str, Any]] = []
    for row in filtered:
        skills = row["skills"]
        missing = sorted(set(skills) - installed_set)
        if not missing:
            ready.append(row)
        elif len(missing) == 1:
            row["missing_skills"] = missing
            need_one.append(row)
    return ready[:5], need_one[:5], len(filtered)


async def suggest_replications(
    client: httpx.AsyncClient,
    ctx: AppContext,
    installed_skills: list[str],
    reported_plays: list[str],
) -> list[dict[str, Any]]:
    if not installed_skills:
        return []
    rows = await api_get_rest(
        client,
        ctx,
        "plays",
        {
            "skills": f"ov.{{{','.join(installed_skills)}}}",
            "replication_count": "eq.0",
            "order": "created_at.asc",
            "select": "id,title,skills,created_at,agent_hash",
            "limit": "60",
        },
    )
    installed_set = set(installed_skills)
    reported_set = set(reported_plays)
    suggestions: list[dict[str, Any]] = []
    for row in rows:
        play_id = str(row.get("id", ""))
        if not play_id or play_id in reported_set:
            continue
        if row.get("agent_hash") == ctx.agent_hash:
            continue
        skills = [s for s in row.get("skills", []) if isinstance(s, str)]
        if not skills:
            continue
        if not set(skills).issubset(installed_set):
            continue
        row["skills"] = skills
        suggestions.append(row)
        if len(suggestions) >= 3:
            break
    return suggestions


def should_continue_prompt() -> bool:
    answer = input(ONBOARD_INTRO).strip()
    return answer == "" or answer.lower() in {"y", "yes"}


def prompt_detected_play_action(play: DetectedPlay) -> str:
    print(f'Detected play: "{play.title}"')
    print(f"Skills: {', '.join(play.skills) if play.skills else '<none detected>'}")
    if play.trigger == "cron":
        trigger_line = f"cron ({play.schedule})" if play.schedule else "cron"
    else:
        trigger_line = play.trigger
    print(f"Trigger: {trigger_line}")
    print()
    print(f"Draft description: {play.description}")
    print()
    while True:
        action = input("[S]hare  [E]dit description  [s]kip  [q]uit ").strip()
        if action in {"S", "E", "s", "q"}:
            return action
        if action.lower() in {"share", "edit", "skip", "quit"}:
            return {"share": "S", "edit": "E", "skip": "s", "quit": "q"}[action.lower()]
        print("Invalid choice. Choose S, E, s, or q.")


def prompt_sync_share_action() -> str:
    while True:
        action = input("     [S]hare  [E]dit  [s]kip\n> ").strip()
        if action in {"S", "E", "s"}:
            return action
        if action.lower() in {"share", "edit", "skip"}:
            return {"share": "S", "edit": "E", "skip": "s"}[action.lower()]
        print("Invalid choice. Choose S, E, or s.")


def prompt_replication_action() -> str:
    while True:
        action = input("Report it as working? [Y/n/s]kip ").strip()
        if action == "" or action.lower() in {"y", "yes"}:
            return "y"
        if action.lower() in {"n", "no"}:
            return "n"
        if action.lower() in {"s", "skip"}:
            return "s"
        print("Invalid choice. Choose Y, n, or s.")


async def submit_detected_play(
    client: httpx.AsyncClient,
    ctx: AppContext,
    play: DetectedPlay,
    source: str = "onboard",
) -> dict[str, Any]:
    payload = {
        "action": "submit-play",
        "title": play.title,
        "description": play.description,
        "skills": play.skills,
        "trigger": play.trigger,
        "effort": play.effort,
        "value": play.value,
        "source": source,
        "os": sys.platform,
    }
    return await api_post_function(client, ctx, "submit-play", payload)


def mark_onboard_done(path: Path = ONBOARD_FLAG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")


async def cmd_onboard(ctx: AppContext, args: argparse.Namespace) -> None:
    explicit_run = getattr(args, "explicit_onboard", False)
    if ONBOARD_FLAG_PATH.exists() and not args.force and not explicit_run:
        print("Onboarding already completed. Use --force to run again.")
        return

    if not should_continue_prompt():
        print("Cancelled.")
        return

    scan = scan_openclaw_for_onboarding()
    if not scan.cron_jobs and not scan.installed_skills:
        print("Nothing detected.")
        mark_onboard_done()
        return

    plays = detect_play_patterns(scan)
    if not plays:
        print("Nothing detected.")
        mark_onboard_done()
        return

    shared = 0
    skipped = 0
    failed = 0
    quit_early = False

    async with httpx.AsyncClient(timeout=20.0) as client:
        for play in plays:
            action = prompt_detected_play_action(play)
            if action == "q":
                quit_early = True
                break
            if action == "s":
                skipped += 1
                print()
                continue
            if action == "E":
                edited = input("New description: ").strip()
                if edited:
                    play.description = sanitize_generic_text(edited)
                if not play.description:
                    play.description = "Automated workflow shared from onboarding."

            if args.dry_run:
                shared += 1
                print(f"Dry run: would share '{play.title}'.")
                print()
                continue

            try:
                result = await submit_detected_play(client, ctx, play)
                shared += 1
                print(f"Shared: {result.get('title', play.title)} ({str(result.get('id', ''))[:8]})")
            except ApiError as exc:
                failed += 1
                print(f"Submit failed for '{play.title}': {exc}")
            except httpx.RequestError as exc:
                failed += 1
                print(f"Submit failed for '{play.title}': {exc}")
            print()

    mark_onboard_done()
    mode = "dry-run" if args.dry_run else "live"
    tail = " (stopped early)" if quit_early else ""
    print(
        f"Onboarding complete ({mode}){tail}. "
        f"Detected: {len(plays)} | Shared: {shared} | Skipped: {skipped} | Failed: {failed}"
    )


async def cmd_sync(ctx: AppContext, args: argparse.Namespace) -> None:
    state = load_sync_state()
    now = _utc_now()
    last_sync_dt = _parse_utc_iso(state.get("last_sync"))
    first_sync = last_sync_dt is None
    if last_sync_dt is None:
        last_sync_dt = now - timedelta(days=7)

    if not args.force and (now - last_sync_dt) < timedelta(days=7):
        next_sync = last_sync_dt + timedelta(days=7)
        print(
            "Last sync was recent ({last}). Next recommended sync: {next}. "
            "Use --force to run now.".format(
                last=last_sync_dt.strftime("%Y-%m-%d %H:%M UTC"),
                next=next_sync.strftime("%Y-%m-%d %H:%M UTC"),
            )
        )
        return

    print("Agent Hivemind \u2014 Weekly Sync")
    print()
    print("\U0001f4e4 Sharing: checking for new automations since last sync...")
    print()

    scan = scan_openclaw_for_onboarding()
    known_jobs = set(state.get("known_cron_jobs", []))
    current_job_keys = [_cron_job_key(job) for job in scan.cron_jobs]
    new_jobs = [job for job in scan.cron_jobs if _cron_job_key(job) not in known_jobs]
    new_plays = detect_play_patterns(
        OnboardScanResult(
            cron_jobs=new_jobs,
            installed_skills=scan.installed_skills,
            cron_failed=scan.cron_failed,
        )
    )

    if not new_plays:
        print("Found 0 new automations.")
    else:
        print(f"Found {len(new_plays)} new automations:")
        print()
        for i, play in enumerate(new_plays, 1):
            print(f'  {i}. "{play.title}"')
            print(f"     Skills: {', '.join(play.skills) if play.skills else '<none detected>'}")
            trigger_line = f"cron ({play.schedule})" if play.schedule else play.trigger
            print(f"     Trigger: {trigger_line}")
            print(f"     Draft: {play.description}")
            if not args.quiet:
                print()

    shared = 0
    share_failed = 0
    share_skipped = 0
    reported_now: set[str] = set(state.get("reported_plays", []))
    replication_submitted = 0
    replication_skipped = 0

    async with httpx.AsyncClient(timeout=20.0) as client:
        if new_plays and not args.quiet:
            print()
            for play in new_plays:
                action = prompt_sync_share_action()
                if action == "s":
                    share_skipped += 1
                    print()
                    continue
                if action == "E":
                    edited = input("New description: ").strip()
                    if edited:
                        play.description = sanitize_generic_text(edited)
                    if not play.description:
                        play.description = "Automated workflow shared from weekly sync."
                if args.dry_run:
                    shared += 1
                    print(f"Dry run: would share '{play.title}'.")
                    print()
                    continue
                try:
                    await submit_detected_play(client, ctx, play, source="sync")
                    shared += 1
                    print(f"Shared: {play.title}")
                except (ApiError, httpx.RequestError) as exc:
                    share_failed += 1
                    print(f"Share failed for '{play.title}': {exc}")
                print()
        elif new_plays:
            share_skipped += len(new_plays)
            print("Quiet mode: skipped interactive sharing prompts.")
            print()

        last_sync_iso = _utc_iso(last_sync_dt)
        ready, need_one, community_count = await fetch_new_community_plays(
            client,
            ctx,
            last_sync_iso,
            scan.installed_skills,
        )
        print(f"\U0001f4e5 New from the community ({community_count} plays added since last sync):")
        print()
        if ready:
            print("  Ready to try (you have all skills):")
            for row in ready:
                skills = ", ".join(row.get("skills", []))
                print(f'    \u2022 "{row.get("title", "Untitled")}" \u2014 {skills}')
                print(f'      Effort: {row.get("effort", "?")} | Value: {row.get("value", "?")}')
        else:
            print("  Ready to try (you have all skills): none")
        print()
        if need_one:
            print("  Need 1 more skill:")
            for row in need_one:
                skills = ", ".join(row.get("skills", []))
                missing = ", ".join(row.get("missing_skills", []))
                print(f'    \u2022 "{row.get("title", "Untitled")}" \u2014 {skills}')
                print(f"      Missing: {missing}")
        else:
            print("  Need 1 more skill: none")

        print()
        print("\U0001f4ca Plays you might be running:")
        suggestions = await suggest_replications(
            client,
            ctx,
            scan.installed_skills,
            state.get("reported_plays", []),
        )
        if not suggestions:
            print("  No replication suggestions right now.")
        for row in suggestions:
            title = row.get("title", "Untitled")
            skills = ", ".join(row.get("skills", []))
            created_dt = _parse_utc_iso(row.get("created_at"))
            days_old = (now - created_dt).days if created_dt else "?"
            print(f'  "{title}" matches your skills ({skills})')
            print(f"  and has been in the database for {days_old} days.")
            if args.quiet:
                continue
            action = prompt_replication_action()
            play_id = str(row.get("id", ""))
            if action == "s":
                replication_skipped += 1
                if play_id:
                    reported_now.add(play_id)
                continue
            if action == "n":
                continue
            if args.dry_run:
                replication_submitted += 1
                print(f"Dry run: would report success for '{title}'.")
                continue
            if play_id:
                await api_post_function(
                    client,
                    ctx,
                    "submit-play",
                    {
                        "action": "replicate",
                        "play_id": play_id,
                        "outcome": "success",
                    },
                )
                replication_submitted += 1
                reported_now.add(play_id)

    if args.dry_run:
        print()
        print(
            "Sync complete (dry-run). "
            "No submissions made and sync state was not updated."
        )
        return

    if not scan.cron_failed:
        state["known_cron_jobs"] = current_job_keys
    state["reported_plays"] = sorted(reported_now)
    state["last_sync"] = _utc_iso(now)
    save_sync_state(state)

    print()
    print(
        "Sync complete. Shared: {shared} | Share skipped: {share_skipped} | "
        "Share failed: {share_failed} | Replications: {repl} | Deferred: {deferred}".format(
            shared=shared,
            share_skipped=share_skipped,
            share_failed=share_failed,
            repl=replication_submitted,
            deferred=replication_skipped,
        )
    )
    print("Next sync recommended in 7 days.")

    if first_sync:
        print()
        print("Want to run this automatically? Add to your agent's HEARTBEAT.md or cron:")
        print('  openclaw cron add --name "Hivemind weekly sync" --schedule "0 10 * * 0" \\')
        print(
            '    --command "python3 ~/.openclaw/workspace/skills/agent-hivemind/scripts/hivemind.py sync --quiet"'
        )


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
    if not ONBOARD_FLAG_PATH.exists():
        print(ONBOARD_TIP)
        print()

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

    p = sub.add_parser("onboard", help="Detect and share your existing automations")
    p.add_argument("--force", action="store_true", help="Run even if already onboarded")
    p.add_argument("--dry-run", action="store_true", help="Show what would be shared without submitting")
    p.set_defaults(explicit_onboard=True)

    p = sub.add_parser("sync", help="Run weekly hivemind sync")
    p.add_argument("--dry-run", action="store_true", help="Show what would happen without submitting")
    p.add_argument("--force", action="store_true", help="Run even if last sync was recent")
    p.add_argument("--quiet", action="store_true", help="Skip interactive prompts and print summary only")

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
        "onboard": cmd_onboard,
        "sync": cmd_sync,
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
