# ReconX

Production-grade, rule-driven recon orchestrator.
It wraps your existing `recon_layerN.sh` scripts, consumes their `summary.json`, and drives deeper actions via rules.

## CLI
```bash
# Plan (dry-run rules to propose deeper actions)
python -m reconx plan --target 1.2.3.4 --out ./enum_1.2.3.4_$(date -u +%Y%m%dT%H%M%SZ) --layers 1,2,3,4 --plan auto

# Run
python -m reconx run --target 1.2.3.4 --out ./enum_1.2.3.4_$(date -u +%Y%m%dT%H%M%SZ) --layers 1,2,3,4 --max-parallel 2 --timeout 900 --rate 0.2

# Resume
python -m reconx resume --target 1.2.3.4 --out ./enum_1.2.3.4_... --layers 1,2,3,4
```

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
