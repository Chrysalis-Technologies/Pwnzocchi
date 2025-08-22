from pathlib import Path
import os, json
from reconx.scheduler import run_scheduler
from reconx.model import Action

def test_scheduler_runs_layer(tmp_path: Path):
    # Create dummy layer1 script
    script = tmp_path / "recon_layer1.sh"
    script.write_text("#!/usr/bin/env bash\nmkdir -p \"$OUT/layer1\"\n" +
                      "echo '{\"layer\":1,\"target\":"'$T'\"}' > \"$OUT/layer1/summary.json\"\n")
    os.chmod(script, 0o755)
    out_dir = tmp_path / "OUT"
    out_dir.mkdir()
    # Make CWD the tmp dir so adapter finds script
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        act = [Action(tool="layer1", args={}, target="1.2.3.4", priority=1)]
        run_scheduler(out_dir, act, time_budget_minutes=1, max_parallel=1, timeout_per_task=10, rate_per_sec=0.0)
        # state db and combined summary should exist
        assert (out_dir / "_state.sqlite").exists()
        comb = list((out_dir / "combined").glob("summary_*.json"))
        assert comb
    finally:
        os.chdir(cwd)
