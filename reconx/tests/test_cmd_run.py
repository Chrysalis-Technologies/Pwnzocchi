from argparse import Namespace
import json
from pathlib import Path

from reconx.__main__ import cmd_run


def test_cmd_run_creates_next_steps(tmp_path: Path, monkeypatch):
    scope = {
        "targets": ["1.2.3.4"],
        "allowed_tools": ["layer1"],
        "time_budget_minutes": 5,
    }
    scope_path = tmp_path / "scope.json"
    scope_path.write_text(json.dumps(scope))
    out_dir = tmp_path / "out"

    called = {}

    def fake_run_scheduler(out, planned, time_budget_minutes, max_parallel, timeout_per_task, rate_per_sec):
        assert (out / "next_steps.md").exists()
        called["called"] = True

    monkeypatch.setenv("AUTH_OK", "1")
    monkeypatch.setattr("reconx.__main__.run_scheduler", fake_run_scheduler)
    monkeypatch.setattr("reconx.__main__.plan_actions", lambda *args, **kwargs: [])

    args = Namespace(
        target="1.2.3.4",
        scope=str(scope_path),
        out=str(out_dir),
        layers="1",
        plan="auto",
        rules=None,
        max_parallel=1,
        timeout=10,
        rate=0.0,
        time_budget=1,
    )

    cmd_run(args)

    assert (out_dir / "next_steps.md").exists()
    assert called.get("called")

