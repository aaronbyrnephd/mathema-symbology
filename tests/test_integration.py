# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Aaron Byrne
"""End-to-end wiring against a real, installed mathema: entry-point
discovery, render_claim_text changing output once this capability is
active, and toggling it never changing a claim's adjudicated verdict.

Everything needing a live mathema install lives in this one file;
`pytest.importorskip` skips it cleanly when mathema isn't installed
(install the `test` extra to run it)."""
import pytest

pytest.importorskip("mathema")

from mathema.conjecture import check_conjectures, claim
from mathema.grammar import domain_contains
from mathema.spec import render_claim_text

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


def test_symbology_capability_is_discoverable_via_entry_points():
    from importlib.metadata import entry_points
    names = {ep.name for ep in entry_points(group="mathema.capabilities")}
    assert "symbology" in names


def test_render_claim_text_changes_visibly_once_active(monkeypatch):
    cj = claim("for price in [0, 100], f(price) >= 0")

    active = render_claim_text(cj, unicode=True)
    monkeypatch.setenv("MATHEMA_SYMBOLOGY_DISABLE", "1")
    disabled = render_claim_text(cj, unicode=True)

    assert active != disabled
    assert "let P = price" in active and "P ∈" in active and "f(P)" in active
    assert active.count("price") == 1  # only in its own "let P = price" clause
    assert "price" in disabled and "let P" not in disabled


def test_intersection_uses_backtick_escaped_unsafe_symbol():
    # ∩ fails .isidentifier(), the case mathema's backtick-wrapping
    # exists to handle
    cj = claim("for intersection in [0, 1], f(intersection) >= 0")
    rendered = render_claim_text(cj, unicode=True)
    assert "let `∩` = intersection" in rendered
    assert "`∩` ∈" in rendered and "f(`∩`)" in rendered

    # render->reparse turns a plain interval into a richer explicit
    # Domain (a general mathema round-trip property, unrelated to
    # symbology), so equivalence is checked via domain_contains, not ==
    reparsed = claim(rendered)
    assert reparsed.lhs == "f((intersection))"
    for value in (0.0, 0.5, 1.0, 1.5, float("nan")):
        assert domain_contains(value, reparsed.domain["intersection"]) == \
            domain_contains(value, cj.domain["intersection"])


def _round_trip(name: str, symbol: str, *, safe: bool):
    """Renders `for <name> in [0, 1], f(<name>) >= 0`, asserts `symbol`
    appears in the let/domain/call positions (backtick-wrapped when
    `safe` is False), then reparses and confirms the domains agree."""
    assert symbol.isidentifier() == safe
    cj = claim(f"for {name} in [0, 1], f({name}) >= 0")
    rendered = render_claim_text(cj, unicode=True)
    shown = symbol if safe else f"`{symbol}`"
    assert f"let {shown} = {name}" in rendered
    assert f"{shown} ∈" in rendered and f"f({shown})" in rendered

    reparsed = claim(rendered)
    assert reparsed.lhs == f"f(({name}))"
    for value in (0.0, 0.5, 1.0, float("nan")):
        assert domain_contains(value, reparsed.domain[name]) == \
            domain_contains(value, cj.domain[name])


def test_true_digit_subscript_symbol_round_trips_through_backticks():
    # a true Unicode subscript digit, so it takes the same backtick
    # escape hatch "intersection" does above
    _round_trip("sigma1", "σ₁", safe=False)


def test_true_superscript_two_symbol_round_trips_through_backticks():
    _round_trip("variance", "σ²", safe=False)


def test_true_superscript_minus_symbol_round_trips_through_backticks():
    _round_trip("a_minus", "a⁻", safe=False)


def test_delta_composed_symbol_round_trips_without_needing_backticks():
    # Δ plus a plain letter is itself .isidentifier()-safe; a delta
    # composition is only unsafe when its resolved parts are
    _round_trip("delta_revenue", "ΔR", safe=True)


def test_pct_change_composed_symbol_round_trips_through_backticks():
    # unsafe unconditionally: "%" is never part of an identifier
    _round_trip("pct_change_ebit", "%ΔEBIT", safe=False)


def test_separator_override_changes_the_top_level_join():
    _write_config('separator: " | "\n')
    cj = claim("for x in [0, 100], f(x) >= 0")
    rendered = render_claim_text(cj, unicode=True)
    assert rendered == "∀ x ∈ [0.0, 100.0] ⊂ ℝ ∪ {∅} | f(x) ≥ 0"


def test_show_missing_override_is_threaded_through_to_render_domain(monkeypatch):
    import mathema.grammar as grammar_module

    _write_config("show_missing: false\n")
    calls = []
    real_render_domain = grammar_module.render_domain

    def spy(bound, **kwargs):
        calls.append(kwargs.get("show_missing"))
        return real_render_domain(bound, **kwargs)

    monkeypatch.setattr(grammar_module, "render_domain", spy)
    cj = claim("for x in [0, 100], f(x) >= 0")
    render_claim_text(cj, unicode=True)
    assert calls and all(call is False for call in calls)


def _by_price(price: float) -> float:
    return price


def _by_sigma1(sigma1: float) -> float:
    return sigma1


def _by_intersection(intersection: float) -> float:
    return intersection


@pytest.mark.parametrize("text, func", [
    ("for price in [0, 100], f(price) >= 0", _by_price),
    ("for sigma1 in [0, 100], f(sigma1) >= 0", _by_sigma1),
    ("for intersection in [0, 1], f(intersection) >= 0", _by_intersection),
])
def test_representative_default_mapping_claims_adjudicate_identically_regardless_of_rendering(
        text, func, monkeypatch):
    # symbology is purely presentation: adjudication must reach the
    # same verdict whether or not this capability is active, since
    # render_claim_text (the only thing it touches) never runs during
    # adjudication
    cj = claim(text)

    monkeypatch.setenv("MATHEMA_SYMBOLOGY_DISABLE", "1")
    result_disabled = check_conjectures(func, [cj])[0]
    monkeypatch.delenv("MATHEMA_SYMBOLOGY_DISABLE", raising=False)
    result_active = check_conjectures(func, [cj])[0]

    assert result_disabled.verdict == result_active.verdict == "holds"
