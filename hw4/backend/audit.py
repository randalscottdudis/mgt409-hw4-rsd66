"""Append-only audit of agent runs. The file is a JSON array."""

from __future__ import annotations

import fcntl
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
AUDIT_PATH = BACKEND_DIR.parent / "output" / "audit_trail.json"
LOCK_PATH = AUDIT_PATH.with_suffix(".lock")
SUMMARY_LIMIT = 180

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_HASH = re.compile(r"pbkdf2_sha256\$\S+", re.IGNORECASE)
_SECRET = re.compile(
    r"(?i)(portkey_api_key|api[_-]?key|session_secret|bearer|sk-[A-Za-z0-9_-]{6,})\S*"
)


def sanitize(value: object) -> str:
    """Short text with emails, hashes, and key-like tokens removed."""
    text = " ".join(str(value).split())
    text = _EMAIL.sub("[redacted]", text)
    text = _HASH.sub("[redacted]", text)
    text = _SECRET.sub("[redacted]", text)
    if len(text) > SUMMARY_LIMIT:
        return text[: SUMMARY_LIMIT - 1] + "…"
    return text


def record_event(
    run_id: str,
    event_type: str,
    tool_name: str | None,
    args_summary: str,
    result_summary: str,
    stop_reason: str | None,
) -> None:
    """Append one event. Existing records stay. The write is locked and atomic."""
    event = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_id": run_id,
        "event_type": event_type,
        "tool_name": tool_name,
        "args_summary": sanitize(args_summary),
        "result_summary": sanitize(result_summary),
        "stop_reason": stop_reason,
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            records: list[object] = []
            if AUDIT_PATH.is_file() and AUDIT_PATH.stat().st_size > 0:
                parsed = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
                if not isinstance(parsed, list):
                    raise ValueError("audit_trail.json must stay a JSON array")
                records = parsed
            records.append(event)
            temporary = AUDIT_PATH.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
            os.replace(temporary, AUDIT_PATH)
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
