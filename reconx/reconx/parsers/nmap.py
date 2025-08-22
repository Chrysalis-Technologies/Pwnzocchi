from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

def parse_nmap_xml(xml_path: Path) -> Dict[str, Any]:
    return {"parsed": False, "path": str(xml_path)}
