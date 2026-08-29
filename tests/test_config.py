# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Aaron Byrne
"""`.mathema/symbology.yaml` loading: a well-formed file loads, and a
deliberately bad one is rejected with a clear error."""
import pytest

from mathema_symbology import _config


@pytest.fixture(autouse=True)
def _clean_config_state(monkeypatch, tmp_path):
    monkeypatch.setattr(_config, "_CONFIG_PATH", tmp_path / ".mathema" / "symbology.yaml")
    monkeypatch.delenv("MATHEMA_SYMBOLOGY_DISABLE", raising=False)
    _config.load_config.cache_clear()
    yield
    _config.load_config.cache_clear()


def _write_config(text: str) -> None:
    _config._CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _config._CONFIG_PATH.write_text(text)


def test_missing_config_file_is_empty_dict():
    assert _config.load_config() == {}


def test_well_formed_config_loads_all_sections():
    _write_config("""
params:
  price: P
funcs:
  velocity: v
separator: "; "
show_missing: false
enabled: true
""")
    config = _config.load_config()
    assert config["params"] == {"price": "P"}
    assert config["funcs"] == {"velocity": "v"}
    assert config["separator"] == "; "
    assert config["show_missing"] is False
    assert config["enabled"] is True


def test_backtick_wrapped_symbol_is_stored_unwrapped():
    _write_config("params:\n  odd: \"`%weird%`\"\n")
    assert _config.load_config()["params"]["odd"] == "%weird%"


def test_non_identifier_symbol_without_backticks_is_rejected():
    _write_config("params:\n  odd: \"%weird%\"\n")
    with pytest.raises(_config.SymbologyConfigError, match="backtick"):
        _config.load_config()


def test_invalid_yaml_is_rejected_with_clear_error():
    _write_config("params: [this is not a mapping\n")
    with pytest.raises(_config.SymbologyConfigError, match="invalid YAML"):
        _config.load_config()


def test_non_mapping_top_level_is_rejected():
    _write_config("- just\n- a\n- list\n")
    with pytest.raises(_config.SymbologyConfigError, match="top level must be a mapping"):
        _config.load_config()


def test_params_section_must_be_a_mapping():
    _write_config("params: not_a_mapping\n")
    with pytest.raises(_config.SymbologyConfigError, match="must be a mapping"):
        _config.load_config()


def test_separator_must_be_a_string():
    _write_config("separator: 5\n")
    with pytest.raises(_config.SymbologyConfigError, match="'separator' must be a string"):
        _config.load_config()


def test_env_var_disables_regardless_of_config(monkeypatch):
    _write_config("enabled: true\n")
    monkeypatch.setenv("MATHEMA_SYMBOLOGY_DISABLE", "1")
    assert _config.is_disabled() is True


def test_env_var_forces_enabled_over_config_disable(monkeypatch):
    _write_config("enabled: false\n")
    monkeypatch.setenv("MATHEMA_SYMBOLOGY_DISABLE", "0")
    assert _config.is_disabled() is False


def test_config_enabled_false_disables_without_env_var():
    _write_config("enabled: false\n")
    assert _config.is_disabled() is True


def test_default_is_enabled():
    assert _config.is_disabled() is False
