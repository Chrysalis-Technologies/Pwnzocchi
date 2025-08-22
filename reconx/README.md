# ReconX

Production-grade, rule-driven recon orchestrator (authorized use only).
It wraps your existing `recon_layerN.sh` scripts, consumes their `summary.json`, and drives deeper actions via rules.

## Hard Safety Gates
1. Fails unless `AUTH_OK=1` is set in the environment.
2. Requires `--scope scope.json`. Only operates on `targets` with `allowed_tools` within `time_budget_minutes`.
3. No exploits. Recon/enumeration only. Subprocesses run with timeouts and redacted logs.
4. Idempotent: re-runs are safe. `_state.sqlite` dedupes tasks by `(tool, args, target)` hash and skip completed work.

## CLI
```bash
# Plan (dry-run rules to propose deeper actions)
python -m reconx plan --target 1.2.3.4 --scope examples/scope.json --out ./enum_1.2.3.4_$(date -u +%Y%m%dT%H%M%SZ) --layers 1,2,3,4 --plan auto

# Run (executes allowed tools, honors budget)
export AUTH_OK=1
python -m reconx run --target 1.2.3.4 --scope examples/scope.json --out ./enum_1.2.3.4_$(date -u +%Y%m%dT%H%M%SZ) --layers 1,2,3,4 --max-parallel 2 --timeout 900 --rate 0.2

# Resume
python -m reconx resume --target 1.2.3.4 --scope examples/scope.json --out ./enum_1.2.3.4_... --layers 1,2,3,4
```

## Scope File
```json
{
  "targets": ["1.2.3.4","app.example.com"],
  "allowed_tools": ["http_enum","dir_enum","ssh_banner","tls_probe","dns_enum","smb_enum","layer1","layer2","layer3","layer4"],
  "time_budget_minutes": 60
}
```

## Built-in Tools

ReconX ships with several lightweight adapters to kickstart common recon tasks:

- `http_enum` – retrieve basic HTTP headers for a target URL.
- `ssh_banner` – grab SSH server banners to identify versions.
- `dns_enum` – query common DNS record types such as `A`, `AAAA`, `MX`, `TXT` and `NS`.
- `tls_probe` – connect with OpenSSL to collect certificate metadata.

## Summary JSON Schema (emitted by each layer)
```json
{
  "layer": 1,
  "target": "1.2.3.4",
  "evidence": [
    {"type":"service","port":443,"proto":"tcp","service":"https","product":"nginx","version":"1.18"},
    {"type":"vhost","name":"admin.example.com"},
    {"type":"path","url":"https://t:8443/login"}
  ],
  "findings":[
    {"id":"WEB-TLS-OLD","title":"Weak TLS","severity":"medium","evidence_ref": "..."},
    {"id":"EXPOSED-PATH","title":"Interesting path","severity":"info","evidence_ref":"..."}
  ],
  "artifacts":[{"kind":"raw","path":"nmap_full.xml"}]
}
```

## Rules
YAML rule format (see `examples/rules.yaml`):
```yaml
- match: "evidence[type=='service' and service in ['http','https'] and port in [80,443,8080,8443]]"
  then:
    run:
      - tool: "http_enum"
        with:
          url_template: "http{s}://{target}:{port}/"
          wordlists: ["medium"]
          tech_fingerprinting: true
    rationale: "Web service discovered; enumerate endpoints/tech"
    max_parallel: 2
- match: "evidence[type=='service' and service=='dns']"
  then:
    run:
      - tool: "dns_enum"
        with:
          record_types: ["A","AAAA","MX","TXT","NS"]
    rationale: "DNS service present; enumerate basic records"
- match: "evidence[type=='service' and service in ['http','https']]"
  then:
    run:
      - tool: "tls_probe"
        with:
          port: "{port}"
    rationale: "Inspect TLS configuration and certificate details"
```

## Outputs
- `$OUT/_master_log.ndjson` (structured logs)
- `$OUT/_timeline.txt` (human timeline)
- `$OUT/_state.sqlite` (work graph + cache)
- `$OUT/combined/combined_report.html` and `combined_report.json`
- `$OUT/next_steps.md` *(reserved; planned in next iteration)*

## Dev & Tests
```bash
pip install -e .  # or poetry install
pytest -q
```
