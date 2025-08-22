import os

import pytest
from pydantic import ValidationError

from core.modules.config import get_settings


def test_missing_adapter_id(monkeypatch):
    monkeypatch.delenv("ADAPTER_ID", raising=False)
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        get_settings()


def test_default_data_dir(monkeypatch):
    monkeypatch.setenv("ADAPTER_ID", "abcd")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.data_dir == "./captures"
