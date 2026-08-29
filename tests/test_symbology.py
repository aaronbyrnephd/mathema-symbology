# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Aaron Byrne
"""The four protocol functions: delta/pct_change composition, the
YAML-override-over-default-mapping precedence, and the "nothing to
say" `None`/default fallbacks the capability contract depends on."""
import pytest

from mathema_symbology import _config, _default_mapping, _symbology


@pytest.fixture(autouse=True)
def _clean_config_state(monkeypatch, tmp_path):
    monkeypatch.setattr(_config, "_CONFIG_PATH", tmp_path / ".mathema" / "symbology.yaml")
    monkeypatch.delenv("MATHEMA_SYMBOLOGY_DISABLE", raising=False)
    _config.load_config.cache_clear()
    yield
    _config.load_config.cache_clear()


def test_symbol_for_param_hits_the_default_mapping():
    assert _symbology.symbol_for_param("price") == "P"


def test_symbol_for_param_returns_none_for_unknown_name():
    assert _symbology.symbol_for_param("totally_unrecognized_xyz") is None


def test_symbol_for_func_returns_none_for_unknown_name():
    assert _symbology.symbol_for_func("anything") is None


def test_symbol_for_func_hits_the_default_mapping():
    assert _symbology.symbol_for_func("norm_cdf") == "Φ"
    assert _symbology.symbol_for_func("var") == "Var"


def test_symbol_for_param_lets_unrelated_concepts_share_a_bare_symbol():
    # both genuinely bare-R in their own field; mathema resolves any
    # collision per claim at render time
    assert _symbology.symbol_for_param("revenue") == "R"
    assert _symbology.symbol_for_param("resistance") == "R"


def test_symbol_for_param_resolves_option_pricing_vega():
    assert _symbology.symbol_for_param("vega") == "ν"


def test_symbol_for_param_underscore_and_no_underscore_numbered_spellings_match():
    assert _symbology.symbol_for_param("mean1") == _symbology.symbol_for_param("mean_1") == "μ₁"
    assert _symbology.symbol_for_param("beta0") == _symbology.symbol_for_param("beta_0") == "β₀"


def test_symbol_for_param_alt_digit_spelling_returns_none_when_base_is_unknown():
    assert _symbology.symbol_for_param("totally_unrecognized_xyz_1") is None


def test_delta_snake_case_composes_with_default_mapping_lookup():
    assert _symbology.symbol_for_param("delta_revenue") == "ΔR"


def test_delta_snake_case_falls_back_to_greek_word_match():
    assert _symbology.symbol_for_param("delta_phi") == "Δφ"


def test_delta_falls_back_to_the_vendored_greek_table_not_a_lookup_hit():
    # "iota" has no _DEFAULT_PARAM_SYMBOLS entry, so this resolves only
    # through the Greek-word table
    assert "iota" not in _default_mapping._DEFAULT_PARAM_SYMBOLS
    assert _symbology.symbol_for_param("delta_iota") == "Δι"


def test_delta_camel_case_composes_the_same_way():
    assert _symbology.symbol_for_param("deltaPhi") == "Δφ"
    assert _symbology.symbol_for_param("deltaRevenue") == "ΔR"


def test_delta_rest_defaults_to_itself_when_unresolved():
    assert _symbology.symbol_for_param("delta_zzz") == "Δzzz"


def test_bare_delta_with_no_rest_is_not_treated_as_compositional():
    assert _symbology.symbol_for_param("delta") is None


def test_pct_change_composes_with_default_mapping_lookup():
    assert _symbology.symbol_for_param("pct_change_ebit") == "%ΔEBIT"


def test_pct_change_falls_back_to_greek_word_match():
    assert _symbology.symbol_for_param("pct_change_phi") == "%Δφ"


def test_pct_change_rest_defaults_to_itself_when_unresolved():
    assert _symbology.symbol_for_param("pct_change_zzz") == "%Δzzz"


def test_bare_pct_change_with_no_rest_is_not_treated_as_compositional():
    assert _symbology.symbol_for_param("pct_change") is None
    assert _symbology.symbol_for_param("pct_change_") is None


def test_separator_default_matches_mathema_core_default():
    assert _symbology.separator() == ", "


def test_show_missing_defers_by_default():
    assert _symbology.show_missing(cj=None) is None


def test_yaml_override_wins_over_default_mapping():
    _config._CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _config._CONFIG_PATH.write_text("params:\n  price: Pi\n")
    assert _symbology.symbol_for_param("price") == "Pi"


def test_yaml_can_supply_a_symbol_the_default_mapping_has_no_opinion_on():
    _config._CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _config._CONFIG_PATH.write_text("funcs:\n  velocity: v\n")
    assert _symbology.symbol_for_func("velocity") == "v"


def test_yaml_can_override_separator_and_show_missing():
    _config._CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _config._CONFIG_PATH.write_text("separator: \"; \"\nshow_missing: false\n")
    assert _symbology.separator() == "; "
    assert _symbology.show_missing(cj=None) is False


def test_config_enabled_false_silences_every_hook():
    _config._CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _config._CONFIG_PATH.write_text("enabled: false\nparams:\n  price: Pi\n")
    assert _symbology.symbol_for_param("price") is None
    assert _symbology.symbol_for_func("anything") is None
    assert _symbology.separator() == ", "
    assert _symbology.show_missing(cj=None) is None


def test_env_var_disable_silences_every_hook(monkeypatch):
    _config._CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _config._CONFIG_PATH.write_text("params:\n  price: Pi\nseparator: \"; \"\n")
    monkeypatch.setenv("MATHEMA_SYMBOLOGY_DISABLE", "1")
    assert _symbology.symbol_for_param("price") is None
    assert _symbology.symbol_for_func("anything") is None
    assert _symbology.separator() == ", "
    assert _symbology.show_missing(cj=None) is None
