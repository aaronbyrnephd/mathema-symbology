# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Aaron Byrne
"""Symbol lookups for mathema claim rendering.

Provides symbol_for_param, symbol_for_func, separator and show_missing.
Each returns None when it has no value for a given name, which mathema
treats the same as this package not being installed. separator returns
its stated default instead.

Lookups consult the project's .mathema/symbology.yaml first, then the
built-in table in _default_mapping.py.

A name shaped like delta_<rest> or delta<Rest> resolves
compositionally: <rest> is looked up on its own and the result is
prefixed with the delta sign, so delta_x gives the delta sign followed
by x, and deltaPhi gives the delta sign followed by phi. A name shaped
like pct_change_<rest> composes the same way with %Δ as its prefix, so
pct_change_ebit gives %Δ followed by EBIT.

A name shaped like <base>_<digits> falls back to the spelling without
the underscore, so alpha_1 and alpha1 both resolve through the single
alpha1 entry.
"""
from __future__ import annotations

import re

from ._config import is_disabled, load_config
from ._default_mapping import (
    _DEFAULT_FUNC_SYMBOLS,
    _DEFAULT_PARAM_SYMBOLS,
    greek_symbol_for_name,
)

_TRAILING_UNDERSCORE_DIGIT = re.compile(r"^(.+)_([0-9]+)$")


def _alt_digit_spelling(name: str) -> str | None:
    """Returns the spelling without the underscore, or None if the name
    is not shaped like <base>_<digits>."""
    match = _TRAILING_UNDERSCORE_DIGIT.match(name)
    return None if match is None else match.group(1) + match.group(2)


def _delta_rest(name: str) -> str | None:
    """Returns the remainder with a lowercase first letter, or None if
    the name is not shaped like delta_<rest> or delta<Rest>."""
    prefix = "delta_"
    if name.startswith(prefix) and len(name) > len(prefix):
        return name[len(prefix):]
    prefix = "delta"
    if name.startswith(prefix) and len(name) > len(prefix) and name[len(prefix)].isupper():
        rest = name[len(prefix):]
        return rest[0].lower() + rest[1:]
    return None


def _pct_change_rest(name: str) -> str | None:
    """Returns the remainder, or None if the name is not shaped like
    pct_change_<rest>."""
    prefix = "pct_change_"
    if name.startswith(prefix) and len(name) > len(prefix):
        return name[len(prefix):]
    return None


def _resolve_rest_symbol(rest: str) -> str:
    """Returns the symbol a composed name's remainder resolves to: its
    default mapping entry, else its Greek-word match, else the
    remainder unchanged."""
    symbol = _DEFAULT_PARAM_SYMBOLS.get(rest)
    if symbol is not None:
        return symbol
    greek = greek_symbol_for_name(rest)
    return greek if greek is not None else rest


def symbol_for_param(name: str) -> str | None:
    """Returns the symbol for a real parameter name, or None when
    neither the project config nor the built-in resolution has one."""
    if is_disabled():
        return None
    override: str | None = load_config().get("params", {}).get(name)
    if override is not None:
        return override

    rest = _delta_rest(name)
    if rest is not None:
        return "Δ" + _resolve_rest_symbol(rest)

    rest = _pct_change_rest(name)
    if rest is not None:
        return "%Δ" + _resolve_rest_symbol(rest)

    symbol = _DEFAULT_PARAM_SYMBOLS.get(name)
    if symbol is not None:
        return symbol

    alt = _alt_digit_spelling(name)
    return None if alt is None else _DEFAULT_PARAM_SYMBOLS.get(alt)


def symbol_for_func(name: str) -> str | None:
    """Returns the symbol for a bound function name, or None when
    neither the project config nor the default mapping has one."""
    if is_disabled():
        return None
    override: str | None = load_config().get("funcs", {}).get(name)
    if override is not None:
        return override
    return _DEFAULT_FUNC_SYMBOLS.get(name)


def separator() -> str:
    """Returns the segment separator, ", " unless the project config
    overrides it."""
    if is_disabled():
        return ", "
    sep: str = load_config().get("separator", ", ")
    return sep


def show_missing(cj: object) -> bool | None:
    """Returns the project config's show_missing value for the claim
    cj, or None when the config doesn't set one."""
    if is_disabled():
        return None
    value: bool | None = load_config().get("show_missing")
    return value
