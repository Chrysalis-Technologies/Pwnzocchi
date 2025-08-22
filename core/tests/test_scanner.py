import subprocess

from core.modules.config import get_settings
from core.modules.scanner import start_scanning


def test_start_scanning(monkeypatch, tmp_path):
    monkeypatch.setenv("ADAPTER_ID", "abcd")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    get_settings.cache_clear()

    called = {}

    def fake_run(cmd, **kwargs):
        called["cmd"] = cmd

        class Result:
            pass

        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)

    outfile = start_scanning("wlan0")
    assert outfile.parent == tmp_path
    assert called["cmd"][0] == "sudo"
    assert called["cmd"][3] == str(outfile.with_suffix(""))
