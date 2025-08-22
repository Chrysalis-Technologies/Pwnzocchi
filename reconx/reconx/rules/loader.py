from __future__ import annotations
from pathlib import Path
from typing import Any, List, Dict
from ruamel.yaml import YAML

def load_rules(path: Path) -> List[Dict[str, Any]]:
    yaml = YAML(typ="safe")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.load(f) or []
    if not isinstance(data, list):
        raise ValueError("rules.yaml must be a list of rule objects")
    return data
