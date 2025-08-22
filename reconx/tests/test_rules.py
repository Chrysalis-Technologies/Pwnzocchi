from pathlib import Path
from reconx.rules import load_rules, evaluate_rules
from reconx.model import SummaryModel
import json

def test_rule_matches():
    rules = load_rules(Path(__file__).resolve().parents[1] / "examples" / "rules.yaml")
    fx = Path(__file__).resolve().parents[1] / "fixtures"
    s1 = SummaryModel.model_validate(json.loads((fx / "layer1_summary.json").read_text()))
    s2 = SummaryModel.model_validate(json.loads((fx / "layer2_summary.json").read_text()))
    actions = evaluate_rules(rules, [s1, s2])
    tools = [a.tool for a in actions]
    assert "http_enum" in tools
    assert "ssh_banner" in tools
    assert "dns_enum" in tools
    assert "tls_probe" in tools
    assert "dir_enum" in tools
