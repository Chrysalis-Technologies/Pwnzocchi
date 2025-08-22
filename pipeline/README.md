# Reconnaissance Pipeline

This directory contains a modular four-layer reconnaissance pipeline. Each layer reads JSON output from the previous layer and writes its own standardized JSON results. Logging and error handling ensure the pipeline is auditable and resilient.

## Layers

1. **Layer 1 – Host Discovery**
   - Input: target hosts supplied via CLI.
   - Output: `layer1_output.json`
   - Fields: `host`, `status`, `timestamp`.

2. **Layer 2 – Port Scanning**
   - Input: `layer1_output.json`
   - Output: `layer2_output.json`
   - Fields: `host`, `port`, `protocol`, `state`, `service`, `timestamp`.

3. **Layer 3 – Service Enumeration**
   - Input: `layer2_output.json`
   - Output: `layer3_output.json`
   - Fields: `host`, `port`, `service`, `banner`, `timestamp`.

4. **Layer 4 – Vulnerability Scan**
   - Input: `layer3_output.json`
   - Output: `layer4_output.json`
   - Fields: `host`, `port`, `vulnerability`, `severity`, `description`, `timestamp`.

## Running the Pipeline

```bash
# Layer 1
python layer1.py 192.168.1.1 192.168.1.2

# Layer 2
python layer2.py --input layer1_output.json --ports 22,80,443

# Layer 3
python layer3.py --input layer2_output.json

# Layer 4
python layer4.py --input layer3_output.json
```

Each script logs its progress and errors to the console with timestamps.
