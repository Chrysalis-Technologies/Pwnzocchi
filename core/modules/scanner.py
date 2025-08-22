"""Module responsible for capturing Wi-Fi handshakes."""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from subprocess import CalledProcessError

from .config import get_settings

logger = logging.getLogger(__name__)


def start_scanning(interface: str) -> Path:
    """Start packet capture on ``interface`` and return output file path."""
    settings = get_settings()
    data_dir = Path(settings.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = data_dir / f"capture_{timestamp}.pcapng"
    # airodump-ng expects the output prefix without the extension; ``with_suffix``
    # safely strips the ``.pcapng`` suffix regardless of path complexity.
    output_prefix = filename.with_suffix("")
    logger.info("Capturing packets on %s into %s", interface, filename)
    try:
        subprocess.run(
            [
                "sudo",
                "airodump-ng",
                "-w",
                str(output_prefix),
                "--output-format",
                "pcapng",
                interface,
            ],
            check=True,
        )
    except CalledProcessError as exc:
        logger.error("airodump-ng failed: %s", exc)
        raise
    return filename
