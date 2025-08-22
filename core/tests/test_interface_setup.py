import subprocess

import pytest

from core.modules.config import get_settings
from core.modules.interface_setup import setup_monitor_interface


def test_no_adapter(monkeypatch):
    monkeypatch.setenv("ADAPTER_ID", "abcd")
    get_settings.cache_clear()

    def fake_run(cmd, **kwargs):
        class Result:
            stdout = ""
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert setup_monitor_interface() is None


def test_adapter_found(monkeypatch):
    monkeypatch.setenv("ADAPTER_ID", "abcd")
    get_settings.cache_clear()

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        class Result:
            stdout = ""
        if cmd[0] == "lsusb":
            Result.stdout = "Bus 001 Device 002: ID abcd"
        elif cmd[:2] == ["iw", "dev"]:
            Result.stdout = "Interface wlan0"
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert setup_monitor_interface() == "wlan0"
    assert ["lsusb"] in calls
