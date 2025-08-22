from __future__ import annotations
import argparse, os, json
from pathlib import Path
from typing import Set
from .utils import ensure_dirs, append_timeline, jload
from .parsers import load_summaries_from_layers
from .rules import load_rules
from .scheduler import plan_actions, run_scheduler
from .report import build_combined_model, render_reports
from .model import Action, SummaryModel

def _require_auth(scope_path: Path):
    if os.environ.get("AUTH_OK","0") != "1":
        raise SystemExit("AUTH_OK=1 is required in the environment")
    if not scope_path.exists():
        raise SystemExit("--scope must point to a valid scope.json")

def _load_scope(scope_path: Path):
    scope = jload(scope_path)
    if not isinstance(scope, dict):
        raise SystemExit("scope.json must be an object")
    targets = set(scope.get("targets") or [])
    allowed_tools = set(scope.get("allowed_tools") or [])
    budget = int(scope.get("time_budget_minutes") or 0)
    if not targets or not allowed_tools or budget <= 0:
        raise SystemExit("scope.json must include targets[], allowed_tools[], and time_budget_minutes>0")
    return targets, allowed_tools, budget

def _validate_target_in_scope(target: str, targets: Set[str]):
    if target not in targets:
        raise SystemExit(f"Target {target} is not listed in scope.json targets")

def cmd_plan(args):
    scope_path = Path(args.scope)
    _require_auth(scope_path)
    targets, allowed_tools, budget = _load_scope(scope_path)
    _validate_target_in_scope(args.target, targets)
    out = Path(args.out)
    ensure_dirs(out)
    layers = [int(x) for x in (args.layers.split(",") if args.layers else []) if x.strip()]
    summaries = load_summaries_from_layers(out, layers)
    rules_path = Path(args.rules) if args.rules else Path(__file__).resolve().parents[1] / "examples" / "rules.yaml"
    rules = load_rules(rules_path)
    planned = plan_actions(out, summaries, rules, allowed_tools)
    for a in planned:
        print(json.dumps(a.model_dump(), indent=2))
    print(f"Planned actions: {len(planned)}")

def _seed_layer_actions(allowed_tools: Set[str], layers, target: str):
    actions = []
    for L in layers:
        t = f"layer{L}"
        if t in allowed_tools:
            actions.append(Action(tool=t, args={}, target=target, priority=1))
    return actions

def cmd_run(args):
    scope_path = Path(args.scope)
    _require_auth(scope_path)
    targets, allowed_tools, budget = _load_scope(scope_path)
    _validate_target_in_scope(args.target, targets)
    out = Path(args.out)
    ensure_dirs(out)
    append_timeline(out / "_timeline.txt", "Run start")
    layers = [int(x) for x in (args.layers.split(",") if args.layers else []) if x.strip()]
    summaries = load_summaries_from_layers(out, layers)
    seed = _seed_layer_actions(allowed_tools, layers, args.target)
    rules_path = Path(args.rules) if args.rules else Path(__file__).resolve().parents[1] / "examples" / "rules.yaml"
    rules = load_rules(rules_path)
    planned = seed + plan_actions(out, summaries, rules, allowed_tools)
    # Dedup
    ded = {}
    for a in planned:
        key = (a.tool, json.dumps(a.args, sort_keys=True), a.target)
        ded[key] = a
    planned = list(ded.values())
    with (out / 'next_steps.md').open('w', encoding='utf-8') as f:
        f.write('# Next Steps\n\n')
        for a in planned:
            f.write(f"- [{a.priority}] {a.tool} on {a.target} with {a.args}\n")

    run_scheduler(out, planned, time_budget_minutes=int(args.time_budget or 0) or budget,
                  max_parallel=int(args.max_parallel or 1),
                  timeout_per_task=int(args.timeout or 600),
                  rate_per_sec=float(args.rate or 0.0))
    # Build report
    summaries = load_summaries_from_layers(out, layers)
    comb_dir = out / "combined"
    if comb_dir.exists():
        for p in sorted(comb_dir.glob("summary_*.json")):
            try:
                from .utils import jload
                summaries.append(SummaryModel.model_validate(jload(p)))
            except Exception:
                continue
    model = build_combined_model(out, summaries)
    render_reports(out, model)
    append_timeline(out / "_timeline.txt", "Run end")

def cmd_resume(args):
    return cmd_run(args)

def main():
    parser = argparse.ArgumentParser(prog="reconx", description="Rule-driven recon orchestrator (authorized use only)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--target", required=True)
    common.add_argument("--scope", required=True)
    common.add_argument("--out", required=True)
    common.add_argument("--layers", default="1,2,3,4")
    common.add_argument("--plan", default="auto", choices=["auto","manual"])
    common.add_argument("--rules")
    common.add_argument("--max-parallel", type=int, default=1)
    common.add_argument("--timeout", type=int, default=600)
    common.add_argument("--rate", type=float, default=0.0)
    common.add_argument("--time-budget", type=int)
    p1 = sub.add_parser("plan", parents=[common])
    p1.set_defaults(func=cmd_plan)
    p2 = sub.add_parser("run", parents=[common])
    p2.set_defaults(func=cmd_run)
    p3 = sub.add_parser("resume", parents=[common])
    p3.set_defaults(func=cmd_resume)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
