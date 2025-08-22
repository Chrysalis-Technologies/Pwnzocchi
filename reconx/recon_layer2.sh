#!/usr/bin/env bash
mkdir -p "$OUT/layer2"
cat > "$OUT/layer2/summary.json" <<'JSON'
{
  "layer": 2,
  "target": "${T}",
  "evidence": [{"type":"service","port":22,"proto":"tcp","service":"ssh"}],
  "findings": [],
  "artifacts": []
}
JSON
