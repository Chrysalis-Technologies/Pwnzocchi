import argparse
import json
import logging
import socket
from datetime import datetime
from typing import List, Dict


def load_ports(path: str) -> List[Dict[str, object]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Input file %s not found", path)
    except json.JSONDecodeError as exc:
        logging.error("Invalid JSON in %s: %s", path, exc)
    return []


def enumerate_services(entries: List[Dict[str, object]]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for e in entries:
        if e.get("state") != "open":
            continue
        host = e.get("host")
        port = e.get("port")
        service = e.get("service", "unknown")
        banner = ""
        try:
            with socket.create_connection((host, port), timeout=2) as sock:
                sock.settimeout(2)
                try:
                    sock.sendall(b"\r\n")
                    data = sock.recv(1024)
                    banner = data.decode(errors="ignore").strip()
                except Exception:
                    banner = ""
        except Exception:  # pragma: no cover - network dependent
            logging.error("Connection failed for %s:%s", host, port)
            continue
        results.append(
            {
                "host": host,
                "port": port,
                "service": service,
                "banner": banner,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Layer 3 - Service Enumeration")
    parser.add_argument(
        "--input",
        default="layer2_output.json",
        help="Input JSON from layer 2",
    )
    parser.add_argument(
        "--output",
        default="layer3_output.json",
        help="Output JSON file",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Layer 3 reading input from %s", args.input)

    entries = load_ports(args.input)
    results = enumerate_services(entries)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logging.info("Layer 3 output written to %s", args.output)
    except OSError as exc:  # pragma: no cover
        logging.error("Failed to write output: %s", exc)


if __name__ == "__main__":
    main()
