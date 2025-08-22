from __future__ import annotations
from pathlib import Path
from typing import List
from datetime import datetime, timedelta
from ..model import SummaryModel, Action, Result
from ..rules import evaluate_rules
from ..utils import append_ndjson, append_timeline, utcnow_iso, jdump
from ..state import init_db, upsert_task, get_pending, set_status
from ..adapters import run_action

def plan_actions(out_dir: Path, summaries: List[SummaryModel], rules: List[dict]):
    actions = evaluate_rules(rules, summaries)
    return actions

def run_scheduler(out_dir: Path,
                  planned_actions: List[Action],
                  time_budget_minutes: int,
                  max_parallel: int,
                  timeout_per_task: int,
                  rate_per_sec: float) -> None:
    db = init_db(out_dir / "_state.sqlite")
    for a in planned_actions:
        upsert_task(db, a.tool, a.args, a.target, priority=a.priority)

    end_time = datetime.utcnow() + timedelta(minutes=time_budget_minutes)
    append_timeline(out_dir / "_timeline.txt", f"Scheduler start; budget={time_budget_minutes}m")
    log_path = out_dir / "_master_log.ndjson"

    while datetime.utcnow() < end_time:
        pending = get_pending(db, limit=max_parallel)
        if not pending:
            break
        for t in pending:
            set_status(db, t["id"], "running")
            append_ndjson(log_path, {"ts": utcnow_iso(), "event": "task_start", "task": t})
            try:
                action = Action(tool=t["tool"], args=t["args"], target=t["target"], priority=t["priority"])
                res: Result = run_action(action, out_dir, timeout_per_task)
                idx_path = out_dir / "combined" / f"summary_{t['id']}_{int(datetime.utcnow().timestamp())}.json"
                jdump(res.summary.model_dump(), idx_path)
                set_status(db, t["id"], "done", logs_path=res.logs)
                append_ndjson(log_path, {"ts": utcnow_iso(), "event":"task_done", "task_id": t["id"], "logs": res.logs})
            except Exception as ex:
                set_status(db, t["id"], "error")
                append_ndjson(log_path, {"ts": utcnow_iso(), "event":"task_error", "task_id": t["id"], "error": str(ex)})
            if rate_per_sec and rate_per_sec > 0:
                import time
                time.sleep(1.0 / rate_per_sec)
    append_timeline(out_dir / "_timeline.txt", "Scheduler end")
