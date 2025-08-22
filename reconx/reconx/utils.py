from __future__ import annotations
import os, json, time, subprocess, platform, re, hashlib, shlex, threading, queue
from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone

def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_dirs(out: Path) -> None:
    (out / "combined").mkdir(parents=True, exist_ok=True)
    (out / "tmp").mkdir(parents=True, exist_ok=True)
    (out / "artifacts").mkdir(parents=True, exist_ok=True)

def jload(p: Path) -> Any:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def jdump(obj: Any, p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

SECRET_PATTERNS = [
    re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._-]+"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*[A-Za-z0-9]{16,}"),
    re.compile(r"(?i)password\s*[:=]\s*\S+"),
    re.compile(r"(?i)secret\s*[:=]\s*\S+"),
    re.compile(r"(?i)access[_-]?token\s*[:=]\s*[A-Za-z0-9._-]+"),
    re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}")  # JWT-ish
]

def redact_secrets(text: str) -> str:
    red = text
    for pat in SECRET_PATTERNS:
        red = pat.sub("[REDACTED]", red)
    return red

class CommandError(Exception):
    pass

def safe_run(cmd: List[str] | str,
             cwd: Path | None = None,
             timeout: int = 600,
             env: Dict[str, str] | None = None,
             cpu_seconds: int | None = None,
             mem_bytes: int | None = None) -> Tuple[int, str, str]:
    if isinstance(cmd, str):
        cmd_list = shlex.split(cmd)
    else:
        cmd_list = cmd
    cmd_list = [str(x) for x in cmd_list]

    preexec = None
    if cpu_seconds is not None or mem_bytes is not None:
        if platform.system() != "Windows":
            import resource
            def set_limits():
                if cpu_seconds is not None:
                    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
                if mem_bytes is not None:
                    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            preexec = set_limits

    proc = subprocess.Popen(
        cmd_list,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env or os.environ.copy(),
        text=True,
        preexec_fn=preexec  # type: ignore[arg-type]
    )
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise CommandError(f"Timeout after {timeout}s: {' '.join(cmd_list)}")
    out = redact_secrets(out or "")
    err = redact_secrets(err or "")
    return proc.returncode, out, err

def sha256_of(obj: Any) -> str:
    b = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

def append_ndjson(p: Path, record: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def append_timeline(p: Path, line: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(f"[{utcnow_iso()}] {line}\n")
