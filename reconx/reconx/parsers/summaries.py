from __future__ import annotations
from pathlib import Path
from typing import List
from ..utils import jload
from ..model import SummaryModel

def load_summaries_from_layers(out_dir: Path, layers: list[int]) -> List[SummaryModel]:
    results: list[SummaryModel] = []
    for L in layers:
        p = out_dir / f"layer{L}" / "summary.json"
        if p.exists():
            try:
                data = jload(p)
                results.append(SummaryModel.model_validate(data))
            except Exception:
                continue
    return results
