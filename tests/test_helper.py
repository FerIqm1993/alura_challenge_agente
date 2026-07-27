from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import helper  # noqa: E402


def _remove_groq_environment(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GROP_API_KEY", raising=False)


def test_groq_api_key_is_read_directly_from_streamlit_secrets(monkeypatch):
    _remove_groq_environment(monkeypatch)
    monkeypatch.setattr(
        helper.st,
        "secrets",
        {"GROQ_API_KEY": "secret-from-streamlit"},
    )

    assert helper.require_groq_api_key() == "secret-from-streamlit"


def test_environment_is_used_as_local_fallback(monkeypatch):
    monkeypatch.setattr(helper.st, "secrets", {})
    monkeypatch.setenv("GROQ_API_KEY", "secret-from-env")

    assert helper.require_groq_api_key() == "secret-from-env"


def test_legacy_grop_alias_remains_supported(monkeypatch):
    _remove_groq_environment(monkeypatch)
    monkeypatch.setattr(helper.st, "secrets", {"GROP_API_KEY": "legacy-secret"})

    assert helper.require_groq_api_key() == "legacy-secret"


def test_missing_key_mentions_streamlit_secrets(monkeypatch):
    _remove_groq_environment(monkeypatch)
    monkeypatch.setattr(helper.st, "secrets", {})

    with pytest.raises(RuntimeError, match="secreto TOML"):
        helper.require_groq_api_key()
