import argparse
import json
import logging
import socket
from datetime import datetime
from typing import List, Dict


def load_hosts(path: str) -> List[Dict[str, str]]:
    """Load layer1 output."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Input file %s not found", path)
    except json.JSONDecodeError as exc:
        logging.error("Invalid JSON in %s: %s", path, exc)
    return []


def scan_ports(hosts: List[Dict[str, str]], ports: List[int]) -> List[Dict[str, object]]:
    """Scan ports on hosts that are up."""
    results: List[Dict[str, object]] = []
    for entry in hosts:
        if entry.get("status") != "up":
            continue
        host = entry.get("host")
        for port in ports:
            state = "closed"
            service = "unknown"
            try:
                with socket.create_connection((host, port), timeout=1) as sock:
                    state = "open"
                    try:
                        service = socket.getservbyport(port, "tcp")
                    except Exception:
                        service = "unknown"
            except Exception:  # pragma: no cover - network conditions vary
                pass
            results.append(
                {
                    "host": host,
                    "port": port,
                    "protocol": "tcp",
                    "state": state,
                    "service": service,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
            )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Layer 2 - Port Scanning")
    parser.add_argument(
        "--input",
        default="layer1_output.json",
        help="Input JSON from layer 1",
    )
    parser.add_argument(
        "--ports",
        default="80,443,22",
        help="Comma separated list of ports to scan",
    )
    parser.add_argument(
        "--output",
        default="layer2_output.json",
        help="Output JSON file",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Layer 2 reading input from %s", args.input)

    hosts = load_hosts(args.input)
    ports = [int(p) for p in args.ports.split(",") if p]
    results = scan_ports(hosts, ports)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logging.info("Layer 2 output written to %s", args.output)
    except OSError as exc:  # pragma: no cover
        logging.error("Failed to write output: %s", exc)


if __name__ == "__main__":
    main()
