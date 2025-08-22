from __future__ import annotations
from pathlib import Path
from typing import List
from ..model import SummaryModel
from ..utils import jdump
from jinja2 import Template
from datetime import datetime

def build_combined_model(out_dir: Path, summaries: List[SummaryModel]) -> dict:
    model = {
        "targets": sorted(list({s.target for s in summaries})),
        "services": [],
        "findings": [],
        "artifacts": [],
        "evidence": []
    }
    for s in summaries:
        for e in s.evidence:
            d = e.model_dump()
            d["target"] = s.target
            model["evidence"].append(d)
            if d.get("type") == "service":
                model["services"].append(d)
        for f in s.findings:
            d = f.model_dump()
            d["target"] = s.target
            model["findings"].append(d)
        for a in s.artifacts:
            d = a.model_dump()
            d["target"] = s.target
            model["artifacts"].append(d)
    return model

HTML_TEMPLATE = """
<!doctype html>
<html><head><meta charset="utf-8"><title>ReconX Combined Report</title>
<style>
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }
h1 { margin-top: 0; }
table { border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }
th, td { border: 1px solid #ddd; padding: 6px 8px; font-size: 14px; }
th { background: #f2f2f2; text-align: left; }
code { background: #f5f5f5; padding: 2px 4px; }
.small { color: #666; font-size: 12px; }
</style>
</head><body>
<h1>ReconX Combined Report</h1>
<p class="small">Generated: {{ generated }}</p>

<h2>Targets</h2>
<ul>
{% for t in model.targets %}<li>{{ t }}</li>{% endfor %}
</ul>

<h2>Services</h2>
<table><thead><tr><th>Target</th><th>Service</th><th>Port</th><th>Proto</th><th>Product</th><th>Version</th></tr></thead>
<tbody>
{% for s in model.services %}
  <tr><td>{{ s.target }}</td><td>{{ s.service }}</td><td>{{ s.port }}</td><td>{{ s.proto }}</td><td>{{ s.product }}</td><td>{{ s.version }}</td></tr>
{% endfor %}
</tbody></table>

<h2>Findings</h2>
<table><thead><tr><th>Target</th><th>ID</th><th>Title</th><th>Severity</th></tr></thead>
<tbody>
{% for f in model.findings %}
  <tr><td>{{ f.target }}</td><td>{{ f.id }}</td><td>{{ f.title }}</td><td>{{ f.severity }}</td></tr>
{% endfor %}
</tbody></table>

<h2>Evidence</h2>
<table><thead><tr><th>Target</th><th>Type</th><th>Detail</th></tr></thead>
<tbody>
{% for e in model.evidence %}
  <tr><td>{{ e.target }}</td><td>{{ e.type }}</td><td><code>{{ e }}</code></td></tr>
{% endfor %}
</tbody></table>
</body></html>
"""

def render_reports(out_dir: Path, model: dict) -> None:
    combined_dir = out_dir / "combined"
    combined_dir.mkdir(parents=True, exist_ok=True)
    jdump(model, combined_dir / "combined_report.json")
    html = Template(HTML_TEMPLATE).render(model=model, generated=datetime.utcnow().isoformat()+"Z")
    (combined_dir / "combined_report.html").write_text(html, encoding="utf-8")
