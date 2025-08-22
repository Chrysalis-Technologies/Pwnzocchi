from pathlib import Path
import json
from reconx.report import build_combined_model, render_reports
from reconx.model import SummaryModel

def test_report_generation(tmp_path: Path):
    fx = Path(__file__).resolve().parents[1] / "fixtures"
    s1 = SummaryModel.model_validate(json.loads((fx / "layer1_summary.json").read_text()))
    s2 = SummaryModel.model_validate(json.loads((fx / "layer2_summary.json").read_text()))
    model = build_combined_model(tmp_path, [s1, s2])
    render_reports(tmp_path, model)
    html = tmp_path / "combined" / "combined_report.html"
    jsn = tmp_path / "combined" / "combined_report.json"
    assert html.exists() and jsn.exists()
