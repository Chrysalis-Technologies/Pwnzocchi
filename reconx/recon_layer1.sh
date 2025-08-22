#!/usr/bin/env bash
mkdir -p "$OUT/layer1"
cat > "$OUT/layer1/summary.json" <<'JSON'
{
  "layer": 1,
  "target": "${T}",
  "evidence": [{"type":"service","port":80,"proto":"tcp","service":"http"}],
  "findings": [],
  "artifacts": []
}
JSON
