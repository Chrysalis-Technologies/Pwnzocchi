from __future__ import annotations
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import json
from .utils import sha256_of

SCHEMA = """    CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hash TEXT UNIQUE NOT NULL,
    tool TEXT NOT NULL,
    args_json TEXT NOT NULL,
    target TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL,
    logs_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON tasks(status, priority);
"""

def init_db(db_path: Path) -> Engine:
    eng = create_engine(f"sqlite:///{db_path}", future=True)
    with eng.begin() as con:
        con.exec_driver_sql(SCHEMA)
    return eng

def task_hash(tool: str, args: dict, target: str) -> str:
    return sha256_of({"tool": tool, "args": args, "target": target})

def upsert_task(eng: Engine, tool: str, args: dict, target: str, priority: int = 5) -> int | None:
    h = task_hash(tool, args, target)
    now = datetime.utcnow().isoformat() + "Z"
    args_json = json.dumps(args, sort_keys=True)
    with eng.begin() as con:
        con.exec_driver_sql(
            "INSERT OR IGNORE INTO tasks(hash, tool, args_json, target, priority, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)",
            (h, tool, args_json, target, priority, now, now)
        )
        row = con.exec_driver_sql("SELECT id FROM tasks WHERE hash = ?", (h,)).first()
        return int(row[0]) if row else None

def get_pending(eng: Engine, limit: int = 100) -> List[dict]:
    with eng.begin() as con:
        res = con.exec_driver_sql(
            "SELECT id, hash, tool, args_json, target, priority, status FROM tasks "
            "WHERE status IN ('pending') ORDER BY priority ASC, id ASC LIMIT ?", (limit,)
        )
        rows = [dict(r._mapping) for r in res]
        for r in rows:
            r["args"] = json.loads(r["args_json"])
            del r["args_json"]
        return rows

def set_status(eng: Engine, task_id: int, status: str, logs_path: Optional[str] = None) -> None:
    now = datetime.utcnow().isoformat() + "Z"
    with eng.begin() as con:
        con.exec_driver_sql(
            "UPDATE tasks SET status = ?, updated_at = ?, logs_path = COALESCE(?, logs_path) WHERE id = ?",
            (status, now, logs_path, task_id)
        )

def get_all(eng: Engine) -> list[dict]:
    with eng.begin() as con:
        res = con.exec_driver_sql("SELECT id, hash, tool, args_json, target, priority, status, logs_path FROM tasks ORDER BY id ASC")
        rows = [dict(r._mapping) for r in res]
        for r in rows:
            r["args"] = json.loads(r["args_json"])
            del r["args_json"]
        return rows
