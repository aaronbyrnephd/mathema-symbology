# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Aaron Byrne
"""_default_mapping.py's consistency checks, confirmed to fire on a
deliberately bad dictionary, plus its real-notation policies: true
Unicode subscripts and superscripts, and param symbols sharing a bare
letter where function symbols never do."""
import pytest

from mathema_symbology import _default_mapping


def test_shipped_default_mapping_is_internally_consistent():
    # already run once at import time; re-running here just documents
    # the guarantee as a test rather than leaving it as an import-time
    # side effect nothing exercises directly.
    _default_mapping._check_default_mapping_consistency()


def test_duplicate_param_symbols_are_allowed(monkeypatch):
    # mathema resolves param collisions per claim at render time
    monkeypatch.setattr(_default_mapping, "_DEFAULT_PARAM_SYMBOLS", {"price": "P", "profit": "P"})
    _default_mapping._check_default_mapping_consistency()


def test_duplicate_function_symbol_value_is_caught(monkeypatch):
    # distinct bound functions co-occur in one formula (f(x) + g(x))
    monkeypatch.setattr(_default_mapping, "_DEFAULT_FUNC_SYMBOLS", {"cdf": "F", "sf": "F"})
    with pytest.raises(ValueError, match="duplicate symbol"):
        _default_mapping._check_default_mapping_consistency()


def test_reserved_function_letter_collision_is_caught(monkeypatch):
    monkeypatch.setattr(_default_mapping, "_DEFAULT_PARAM_SYMBOLS", {"some_func_like_name": "f"})
    with pytest.raises(ValueError, match="reserved function letter"):
        _default_mapping._check_default_mapping_consistency()


def test_unsafe_param_symbol_is_accepted(monkeypatch):
    # true Unicode subscripts/superscripts are the encouraged case;
    # mathema backtick-wraps them at render time
    monkeypatch.setattr(_default_mapping, "_DEFAULT_PARAM_SYMBOLS", {"weird": "σ₉"})
    _default_mapping._check_default_mapping_consistency()


def test_unsafe_function_symbol_is_always_caught(monkeypatch):
    # a function symbol sits in call position, where backticks are
    # never valid syntax
    monkeypatch.setattr(_default_mapping, "_DEFAULT_FUNC_SYMBOLS", {"weird_func": "∩"})
    with pytest.raises(ValueError, match="backtick-escaped"):
        _default_mapping._check_default_mapping_consistency()


def test_non_identifier_source_names_have_no_default_mapping_entry_at_all():
    # their real notation ("dr/dt", "P/E", "D/E", "P(A∩B)") isn't a
    # single token
    mapping = _default_mapping._DEFAULT_PARAM_SYMBOLS
    for skipped in ("dr_dt", "pe_ratio", "debt_to_equity", "p_a_and_b"):
        assert skipped not in mapping


def test_compositional_names_have_no_literal_default_mapping_entry():
    # composed at lookup time by _symbology.py; a static copy would
    # drift from that logic
    mapping = _default_mapping._DEFAULT_PARAM_SYMBOLS
    for composed in ("delta_x", "delta_revenue", "pct_change_ebit", "pct_change_qty"):
        assert composed not in mapping


def test_digit_subscripts_use_true_unicode_subscript_characters():
    mapping = _default_mapping._DEFAULT_PARAM_SYMBOLS
    assert mapping["purchase_price"] == "P₀"
    assert mapping["sigma1"] == "σ₁"
    assert mapping["c_base"] == "C₀"
    assert mapping["vacuum_permittivity"] == "ε₀"
    assert mapping["vacuum_permeability"] == "μ₀"
    for underscore_form in ("P_0", "σ_1", "C_0", "ε_0", "μ_0"):
        assert underscore_form not in mapping.values()


def test_variance_uses_true_superscript_two():
    assert _default_mapping._DEFAULT_PARAM_SYMBOLS["variance"] == "σ²"


def test_chi_square_uses_true_superscript_two():
    assert _default_mapping._DEFAULT_PARAM_SYMBOLS["chi_square"] == "χ²"


def test_a_minus_uses_true_superscript_minus():
    assert _default_mapping._DEFAULT_PARAM_SYMBOLS["a_minus"] == "a⁻"
    assert not _default_mapping._DEFAULT_PARAM_SYMBOLS["a_minus"].isidentifier()


def test_sample_mean_uses_true_x_bar_notation():
    # a combining macron over x, itself .isidentifier()-safe
    assert _default_mapping._DEFAULT_PARAM_SYMBOLS["sample_mean"] == "x̄"
    assert _default_mapping._DEFAULT_PARAM_SYMBOLS["sample_mean"].isidentifier()


def test_f_reserved_letter_entries_are_renamed():
    mapping = _default_mapping._DEFAULT_PARAM_SYMBOLS
    assert mapping["focal_length"] != "f"
    assert mapping["f_source"] != "f"


def test_unrelated_concepts_genuinely_share_a_bare_symbol():
    # each is standard notation in its own field; no suffix invented
    # just to keep them apart
    mapping = _default_mapping._DEFAULT_PARAM_SYMBOLS
    assert mapping["price"] == mapping["power"] == mapping["pressure"] == "P"
    assert mapping["length"] == mapping["L_ind"] == mapping["total_liabilities"] == "L"
    assert mapping["revenue"] == mapping["resistance"] == mapping["gas_constant"] == "R"
    assert mapping["years"] == mapping["moles"] == mapping["sample_size"] == "n"


def test_letter_subscripts_use_true_unicode_where_the_glyph_exists():
    mapping = _default_mapping._DEFAULT_PARAM_SYMBOLS
    assert mapping["money_supply"] == "Mₛ"
    assert mapping["specific_heat_constant_pressure"] == "cₚ"
    assert mapping["specific_heat_constant_volume"] == "cᵥ"
    assert mapping["pooled_sd"] == "sₚ"
    assert mapping["permittivity"] == "εᵣ"
    assert mapping["p_total"] == "Pₜₒₜ"
    assert mapping["v_max"] == "Vₘₐₓ"
    assert mapping["activation_energy"] == "Eₐ"


def test_ascii_underscore_survives_only_where_unicode_has_no_glyph():
    # no capital subscripts, and no subscript b/c/d/f: these keep their
    # underscore spelling rather than gaining a wrong glyph.
    mapping = _default_mapping._DEFAULT_PARAM_SYMBOLS
    assert mapping["T_hot"] == "T_h" and mapping["T_cold"] == "T_c"
    assert mapping["boltzmann_constant"] == "k_B"
    assert mapping["avogadro_number"] == "N_A"
    assert mapping["risk_free_rate"] == "r_f"
    assert mapping["bonding_e"] == "E_b"


def test_digit_suffixed_keys_are_rejected_by_the_consistency_check(monkeypatch):
    monkeypatch.setattr(_default_mapping, "_DEFAULT_PARAM_SYMBOLS", {"alpha_1": "α₁"})
    with pytest.raises(ValueError, match="no-underscore spelling"):
        _default_mapping._check_default_mapping_consistency()


def test_eulers_number_collision_is_caught(monkeypatch):
    monkeypatch.setattr(_default_mapping, "_DEFAULT_PARAM_SYMBOLS", {"exchange_rate": "e"})
    with pytest.raises(ValueError, match="Euler"):
        _default_mapping._check_default_mapping_consistency()


def test_names_with_no_standard_convention_have_no_entry():
    # a missing entry (mathema falls back to its own naming approach)
    # beats an invented one
    mapping = _default_mapping._DEFAULT_PARAM_SYMBOLS
    for removed in (
        "property_price", "inventory", "universe_size", "loan_amount",
        "path_length", "moles_available", "nominal", "markup",
        "split_ratio", "leverage_ratio", "debt_to_equity", "exchange_rate",
    ):
        assert removed not in mapping


def test_exchange_rate_has_no_entry_because_bare_e_is_eulers_number():
    # exchange rate has no bare-letter convention strong enough to
    # claim a different spelling
    assert "exchange_rate" not in _default_mapping._DEFAULT_PARAM_SYMBOLS
