from pathlib import Path
import os
from reconx.adapters import run_action
from reconx.model import Action

def test_layer_adapter(tmp_path: Path):
    # Create a fake layer1 script that writes summary.json
    script = tmp_path / "recon_layer1.sh"
    script.write_text('''#!/usr/bin/env bash
mkdir -p "$OUT/layer1"
echo '{"layer":1,"target":"'$T'","evidence":[{"type":"service","port":80,"service":"http"}]}' > "$OUT/layer1/summary.json"
''')
    os.chmod(script, 0o755)
    out_dir = tmp_path / "OUT"
    out_dir.mkdir()
    # Ensure CWD is tmp_path so the adapter finds the script
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        res = run_action(Action(tool="layer1", args={}, target="1.2.3.4"), out_dir, timeout=10)
        assert res.summary.layer == 1
        assert res.summary.target == "1.2.3.4"
        assert res.summary.evidence and res.summary.evidence[0].service == "http"
    finally:
        os.chdir(cwd)
