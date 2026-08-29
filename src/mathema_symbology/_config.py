# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Aaron Byrne
"""Loads the project's optional `.mathema/symbology.yaml`, the file a
project uses to override or extend this package's default symbols.
mathema already keeps its own records under `.mathema/`, so that
directory is the natural home for it.

Schema (every key optional):

    params:
      <real parameter name>: <symbol>
    funcs:
      <function alias name>: <symbol>
    separator: <string>
    show_missing: <bool>
    enabled: <bool>

A `<symbol>` either satisfies `.isidentifier()` or is wrapped in
backticks (`` `<symbol>` ``). mathema applies the backtick escaping
itself at render time, so the backticks are stripped back off here.

`MATHEMA_SYMBOLOGY_DISABLE` (any value other than unset/""/"0"/"false")
takes priority over the file's own `enabled: false`, so a CI run can
force this capability off without editing the file."""
from __future__ import annotations

import functools
import os
from pathlib import Path
from typing import Any

_CONFIG_PATH = Path.cwd() / ".mathema" / "symbology.yaml"


class SymbologyConfigError(ValueError):
    """Raised for a structurally invalid `.mathema/symbology.yaml`,
    with the offending key named in the message."""


def _validate_symbol(symbol: object, section: str, name: str) -> str:
    if not isinstance(symbol, str):
        raise SymbologyConfigError(
            f"{_CONFIG_PATH}: {section}.{name!r} -> {symbol!r} must be a string")
    if symbol.isidentifier():
        return symbol
    if len(symbol) >= 2 and symbol.startswith("`") and symbol.endswith("`"):
        return symbol[1:-1]
    raise SymbologyConfigError(
        f"{_CONFIG_PATH}: {section}.{name!r} -> {symbol!r} is not a valid "
        f"identifier; wrap it in backticks (e.g. \"`{symbol}`\") to use it "
        f"verbatim")


def _validate_mapping(raw: dict[str, Any], section: str) -> dict[str, str]:
    section_value = raw.get(section, {})
    if not isinstance(section_value, dict):
        raise SymbologyConfigError(
            f"{_CONFIG_PATH}: {section!r} must be a mapping of name -> symbol, "
            f"got {type(section_value).__name__}")
    validated = {}
    for name, symbol in section_value.items():
        if not isinstance(name, str):
            raise SymbologyConfigError(
                f"{_CONFIG_PATH}: {section!r} keys must be strings, got {name!r}")
        validated[name] = _validate_symbol(symbol, section, name)
    return validated


@functools.lru_cache(maxsize=1)
def load_config() -> dict[str, Any]:
    """The parsed, validated `.mathema/symbology.yaml`, or `{}` when
    the file doesn't exist. Cached; call `load_config.cache_clear()`
    to force a re-read within one process.

    Raises:
        SymbologyConfigError: the file exists but is malformed
            (invalid YAML, a non-mapping top level or section, a
            non-string name or symbol, or a symbol that's neither
            `.isidentifier()`-safe nor backtick-wrapped).
    """
    if not _CONFIG_PATH.is_file():
        return {}

    import yaml

    try:
        raw = yaml.safe_load(_CONFIG_PATH.read_text())
    except yaml.YAMLError as e:
        raise SymbologyConfigError(f"{_CONFIG_PATH}: invalid YAML ({e})") from e

    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise SymbologyConfigError(
            f"{_CONFIG_PATH}: top level must be a mapping, got {type(raw).__name__}")

    config: dict[str, Any] = {
        "params": _validate_mapping(raw, "params"),
        "funcs": _validate_mapping(raw, "funcs"),
    }
    if "separator" in raw:
        if not isinstance(raw["separator"], str):
            raise SymbologyConfigError(f"{_CONFIG_PATH}: 'separator' must be a string")
        config["separator"] = raw["separator"]
    if "show_missing" in raw:
        if not isinstance(raw["show_missing"], bool):
            raise SymbologyConfigError(f"{_CONFIG_PATH}: 'show_missing' must be a boolean")
        config["show_missing"] = raw["show_missing"]
    if "enabled" in raw:
        if not isinstance(raw["enabled"], bool):
            raise SymbologyConfigError(f"{_CONFIG_PATH}: 'enabled' must be a boolean")
        config["enabled"] = raw["enabled"]
    return config


def is_disabled() -> bool:
    env = os.environ.get("MATHEMA_SYMBOLOGY_DISABLE")
    if env is not None and env not in ("", "0", "false", "False"):
        return True
    if env in ("0", "false", "False"):
        return False
    return load_config().get("enabled", True) is False
