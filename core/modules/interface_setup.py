"""Detects and prepares external WiFi adapter for monitor mode."""

import logging
import subprocess
from subprocess import CalledProcessError, TimeoutExpired

from .config import get_settings

logger = logging.getLogger(__name__)


def _run_cmd(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Execute a subprocess command with error handling."""
    logger.debug("Running command: %s", " ".join(cmd))
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kwargs)


def setup_monitor_interface() -> str | None:
    """Return interface name set to monitor mode or ``None`` on failure."""
    settings = get_settings()
    try:
        result = _run_cmd(["lsusb"], timeout=10)
    except (CalledProcessError, TimeoutExpired) as exc:
        logger.error("lsusb failed: %s", exc)
        return None

    interface_name: str | None = None
    if settings.adapter_id in result.stdout:
        try:
            iw_result = _run_cmd(["iw", "dev"], timeout=10)
        except (CalledProcessError, TimeoutExpired) as exc:
            logger.error("iw dev failed: %s", exc)
            return None
        for line in iw_result.stdout.splitlines():
            if "Interface" in line:
                interface_name = line.strip().split()[-1]
                break
        if interface_name:
            try:
                subprocess.run(["sudo", "ip", "link", "set", interface_name, "down"], check=True)
                subprocess.run(["sudo", "iw", interface_name, "set", "monitor", "control"], check=True)
                subprocess.run(["sudo", "ip", "link", "set", interface_name, "up"], check=True)
            except CalledProcessError as exc:
                logger.error("Failed to set monitor mode: %s", exc)
                return None
            logger.info("Interface %s set to monitor mode.", interface_name)
            return interface_name
    logger.error("External adapter not found.")
    return None
