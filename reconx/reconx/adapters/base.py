from __future__ import annotations
from pathlib import Path
import os, shlex
from typing import Dict, Callable
from ..model import Action, Result, SummaryModel, Evidence, Finding, Artifact
from ..utils import safe_run, jload

def _read_or_stub_summary(summary_path: Path, layer: int, target: str) -> SummaryModel:
    if summary_path.exists():
        try:
            data = jload(summary_path)
            return SummaryModel.model_validate(data)
        except Exception:
            pass
    return SummaryModel(layer=layer, target=target, evidence=[], findings=[], artifacts=[])

def run_layer_script(name: str, script_path: Path, out_dir: Path, target: str, layer: int, timeout: int) -> Result:
    layer_dir = out_dir / f"layer{layer}"
    layer_dir.mkdir(parents=True, exist_ok=True)
    log_path = layer_dir / f"{name}.log.txt"
    env = os.environ.copy()
    env["T"] = target
    env["OUT"] = str(out_dir)
    code, out, err = safe_run([script_path.as_posix()], cwd=script_path.parent, timeout=timeout, env=env)
    log_path.write_text((out or "") + "\n" + (err or ""), encoding="utf-8")
    summary_path = layer_dir / "summary.json"
    summary = _read_or_stub_summary(summary_path, layer=layer, target=target)
    return Result(summary=summary, artifacts=[], logs=str(log_path))

def http_enum(action: Action, out_dir: Path, timeout: int) -> Result:
    url_tmpl = action.args.get("url_template", "")
    target = action.target
    port = action.args.get("port", 443)
    url = url_tmpl.replace("{s}", "s" if str(port) in ("443","8443") else "").format(target=target, port=port)
    layer_dir = out_dir / "layer_web"
    layer_dir.mkdir(parents=True, exist_ok=True)
    log_path = layer_dir / "http_enum.log.txt"
    try:
        code, out, err = safe_run(["bash","-lc", f"curl -skI --max-time 10 {shlex.quote(url)}"], timeout=min(timeout, 30))
        log_path.write_text((out or "") + "\n" + (err or ""), encoding="utf-8")
    except Exception as ex:
        log_path.write_text(str(ex), encoding="utf-8")
    ev = []
    if 'out' in locals() and "HTTP/" in (out or ""):
        ev.append(Evidence(type="http-head", url=url))
    summary = SummaryModel(layer=99, target=target, evidence=ev, findings=[], artifacts=[])
    return Result(summary=summary, artifacts=[], logs=str(log_path))

def ssh_banner(action: Action, out_dir: Path, timeout: int) -> Result:
    target = action.target
    port = int(action.args.get("port", 22))
    layer_dir = out_dir / "layer_ssh"
    layer_dir.mkdir(parents=True, exist_ok=True)
    log_path = layer_dir / "ssh_banner.log.txt"
    try:
        cmd = ["bash","-lc", f"echo | timeout 5 nc -v {target} {port}"]
        code, out, err = safe_run(cmd, timeout=min(timeout, 15))
        log_path.write_text((out or "") + "\n" + (err or ""), encoding="utf-8")
    except Exception as ex:
        log_path.write_text(str(ex), encoding="utf-8")
    ev = []
    txt = ((out or "") + (err or ""))
    if "SSH-" in txt:
        ev.append(Evidence(type="service", service="ssh", port=port, proto="tcp"))
    summary = SummaryModel(layer=98, target=target, evidence=ev, findings=[], artifacts=[])
    return Result(summary=summary, artifacts=[], logs=str(log_path))

def dns_enum(action: Action, out_dir: Path, timeout: int) -> Result:
    target = action.target
    record_types = action.args.get("record_types", ["A", "AAAA", "MX", "TXT", "NS"])
    layer_dir = out_dir / "layer_dns"
    layer_dir.mkdir(parents=True, exist_ok=True)
    log_path = layer_dir / "dns_enum.log.txt"
    try:
        cmd = [
            "bash",
            "-lc",
            f"for t in {' '.join(record_types)}; do nslookup -type=$t {shlex.quote(target)}; done",
        ]
        code, out, err = safe_run(cmd, timeout=min(timeout, 60))
        log_path.write_text((out or "") + "\n" + (err or ""), encoding="utf-8")
    except Exception as ex:
        log_path.write_text(str(ex), encoding="utf-8")
    ev = []
    if 'out' in locals() and target in (out or ""):
        ev.append(Evidence(type="dns-record", name=target))
    summary = SummaryModel(layer=96, target=target, evidence=ev, findings=[], artifacts=[])
    return Result(summary=summary, artifacts=[], logs=str(log_path))

def tls_probe(action: Action, out_dir: Path, timeout: int) -> Result:
    target = action.target
    port = int(action.args.get("port", 443))
    layer_dir = out_dir / "layer_tls"
    layer_dir.mkdir(parents=True, exist_ok=True)
    log_path = layer_dir / "tls_probe.log.txt"
    try:
        cmd = [
            "bash",
            "-lc",
            f"echo | timeout 10 openssl s_client -servername {shlex.quote(target)} -connect {shlex.quote(target)}:{port} 2>&1 | head -n 20",
        ]
        code, out, err = safe_run(cmd, timeout=min(timeout, 40))
        log_path.write_text((out or "") + "\n" + (err or ""), encoding="utf-8")
    except Exception as ex:
        log_path.write_text(str(ex), encoding="utf-8")
    ev = []
    subj = None
    issuer = None
    for line in (out or "").splitlines():
        line = line.strip()
        if line.startswith("subject="):
            subj = line.split("subject=")[-1].strip()
        elif line.startswith("issuer="):
            issuer = line.split("issuer=")[-1].strip()
    if subj or issuer:
        ev.append(Evidence(type="tls-cert", service="https", port=port, proto="tcp", name=subj, product=issuer))
    summary = SummaryModel(layer=95, target=target, evidence=ev, findings=[], artifacts=[])
    return Result(summary=summary, artifacts=[], logs=str(log_path))

HANDLERS: Dict[str, Callable[[Action, Path, int], Result]] = {}

def _register_builtin_handlers():
    HANDLERS["http_enum"] = http_enum
    HANDLERS["ssh_banner"] = ssh_banner
    HANDLERS["dns_enum"] = dns_enum
    HANDLERS["tls_probe"] = tls_probe

def run_action(action: Action, out_dir: Path, timeout: int) -> Result:
    if not HANDLERS:
        _register_builtin_handlers()
    tool = action.tool
    if tool.startswith("layer"):
        layer = int(tool.replace("layer",""))
        script_name = f"recon_layer{layer}.sh"
        candidates = [Path.cwd()/script_name, out_dir.parent/script_name, Path(script_name)]
        script = next((p for p in candidates if p.exists()), None)
        if script is None:
            return Result(summary=SummaryModel(layer=layer, target=action.target, evidence=[], findings=[], artifacts=[]),
                          artifacts=[], logs=None)
        return run_layer_script(name=tool, script_path=script, out_dir=out_dir, target=action.target, layer=layer, timeout=timeout)
    handler = HANDLERS.get(tool)
    if handler is None:
        return Result(summary=SummaryModel(layer=97, target=action.target, evidence=[], findings=[], artifacts=[]),
                      artifacts=[], logs=None)
    return handler(action, out_dir, timeout)
