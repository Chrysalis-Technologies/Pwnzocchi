"""Warwalker entry point."""

import logging
from pydantic import ValidationError

from core.modules.config import get_settings
from core.modules.interface_setup import setup_monitor_interface
from core.modules.scanner import start_scanning


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        get_settings()
    except ValidationError as exc:
        logging.error("Invalid configuration: %s", exc)
        raise SystemExit(1)

    iface = setup_monitor_interface()
    if iface:
        start_scanning(iface)
    else:
        logging.error("No valid external interface found. Exiting.")
