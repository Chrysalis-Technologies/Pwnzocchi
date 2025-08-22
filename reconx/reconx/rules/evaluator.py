from __future__ import annotations
from typing import Any, Dict, List, Iterable
from ..model import SummaryModel, Action
import ast

ALLOWED_NODES = {
    ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not,
    ast.Compare, ast.In, ast.Eq, ast.NotEq, ast.Constant, ast.List, ast.Tuple,
    ast.Load, ast.Name
}

def _safe_eval_expr(expr: str, context: dict) -> bool:
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, tuple(ALLOWED_NODES)):
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")
        if isinstance(node, ast.Name):
            if node.id not in context:
                return False
    code = compile(tree, "<match>", "eval")
    return bool(eval(code, {"__builtins__": {}}, context))

def _match_list(expr: str, items: Iterable[dict]) -> List[dict]:
    matched = []
    for it in items:
        ctx = {k: v for k, v in it.items() if isinstance(k, str)}
        try:
            if _safe_eval_expr(expr, ctx):
                matched.append(it)
        except Exception:
            continue
    return matched

def evaluate_rules(rules: List[dict], summaries: List[SummaryModel]) -> List[Action]:
    actions: List[Action] = []
    all_evidence: List[dict] = []
    all_findings: List[dict] = []
    targets = set()
    for s in summaries:
        targets.add(s.target)
        all_evidence.extend([e.model_dump() for e in s.evidence])
        all_findings.extend([f.model_dump() for f in s.findings])

    for rule in rules:
        match = (rule or {}).get("match", "")
        then = (rule or {}).get("then", {}) or {}
        run_list = then.get("run", []) or []
        if not match or not run_list:
            continue

        matched_items: List[dict] = []
        if match.startswith("evidence[") and match.endswith("]"):
            inner = match[len("evidence["):-1]
            matched_items = _match_list(inner, all_evidence)
        elif match.startswith("findings[") and match.endswith("]"):
            inner = match[len("findings["):-1]
            matched_items = _match_list(inner, all_findings)
        else:
            continue

        if not matched_items:
            continue

        for tgt in targets:
            for run in run_list:
                tool = run.get("tool")
                w = run.get("with", {}) or {}
                if not tool:
                    continue
                it = matched_items[0]
                templated_args = {}
                for k, v in w.items():
                    if isinstance(v, str):
                        try:
                            templated_args[k] = v.format(target=tgt, **it)
                        except Exception:
                            templated_args[k] = v
                    else:
                        templated_args[k] = v
                actions.append(Action(tool=tool, args=templated_args, target=tgt, priority=5))
    return actions
