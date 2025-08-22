import argparse
import json
import logging
from datetime import datetime
from typing import List, Dict


KNOWN_VULNS = [
    {
        "pattern": "Apache/2.4.49",
        "vulnerability": "CVE-2021-41773",
        "severity": "high",
        "description": "Path traversal in Apache httpd 2.4.49",
    },
    {
        "pattern": "OpenSSH_7.2",
        "vulnerability": "CVE-2016-0777",
        "severity": "medium",
        "description": "OpenSSH roaming issue",
    },
]


def load_services(path: str) -> List[Dict[str, object]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Input file %s not found", path)
    except json.JSONDecodeError as exc:
        logging.error("Invalid JSON in %s: %s", path, exc)
    return []


def scan_vulnerabilities(entries: List[Dict[str, object]]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for e in entries:
        banner = e.get("banner", "")
        host = e.get("host")
        port = e.get("port")
        for vuln in KNOWN_VULNS:
            if vuln["pattern"] in banner:
                results.append(
                    {
                        "host": host,
                        "port": port,
                        "vulnerability": vuln["vulnerability"],
                        "severity": vuln["severity"],
                        "description": vuln["description"],
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }
                )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Layer 4 - Vulnerability Scan")
    parser.add_argument(
        "--input",
        default="layer3_output.json",
        help="Input JSON from layer 3",
    )
    parser.add_argument(
        "--output",
        default="layer4_output.json",
        help="Output JSON file",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Layer 4 reading input from %s", args.input)

    services = load_services(args.input)
    results = scan_vulnerabilities(services)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logging.info("Layer 4 output written to %s", args.output)
    except OSError as exc:  # pragma: no cover
        logging.error("Failed to write output: %s", exc)


if __name__ == "__main__":
    main()
