import argparse
import json
import logging
import subprocess
from datetime import datetime
from typing import List, Dict


def discover_hosts(hosts: List[str]) -> List[Dict[str, str]]:
    """Ping each host and return discovery results.

    Args:
        hosts: Iterable of hostnames or IP addresses.

    Returns:
        List of dictionaries containing host discovery data.
    """
    results: List[Dict[str, str]] = []
    for host in hosts:
        try:
            proc = subprocess.run(
                ["ping", "-c", "1", "-W", "1", host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            status = "up" if proc.returncode == 0 else "down"
        except Exception as exc:  # pragma: no cover - network errors not deterministic
            logging.error("Ping failed for %s: %s", host, exc)
            status = "down"
        results.append(
            {
                "host": host,
                "status": status,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Layer 1 - Host Discovery")
    parser.add_argument(
        "targets",
        nargs="+",
        help="Hosts to probe",
    )
    parser.add_argument(
        "--output",
        default="layer1_output.json",
        help="Output JSON file",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    data = discover_hosts(args.targets)
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logging.info("Layer 1 output written to %s", args.output)
    except OSError as exc:  # pragma: no cover - filesystem errors are rare
        logging.error("Failed to write output: %s", exc)


if __name__ == "__main__":
    main()
