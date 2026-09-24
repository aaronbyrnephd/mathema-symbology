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

# An explicit override of where the config file lives; None means it is
# found from the working directory on every read (see `config_path`).
_CONFIG_PATH: Path | None = None


def config_path() -> Path:
    """The project's `.mathema/symbology.yaml`: under the nearest
    ancestor of the working directory that holds a `.mathema/`
    directory, searching no higher than the enclosing git repository and
    never at the home directory, whose `.mathema/` is per-user
    configuration. Without one, the working directory's own
    `.mathema/symbology.yaml`, which may not exist."""
    if _CONFIG_PATH is not None:
        return _CONFIG_PATH
    here = Path.cwd().resolve()
    home = Path.home().resolve()
    for directory in (here, *here.parents):
        if directory == home:
            break
        if (directory / ".mathema").is_dir():
            return directory / ".mathema" / "symbology.yaml"
        if (directory / ".git").exists():
            break
    return here / ".mathema" / "symbology.yaml"


class SymbologyConfigError(ValueError):
    """Raised for a structurally invalid `.mathema/symbology.yaml`,
    with the offending key named in the message."""


def _validate_symbol(symbol: object, section: str, name: str, path: Path) -> str:
    if not isinstance(symbol, str):
        raise SymbologyConfigError(
            f"{path}: {section}.{name!r} -> {symbol!r} must be a string")
    if symbol.isidentifier():
        return symbol
    if len(symbol) >= 2 and symbol.startswith("`") and symbol.endswith("`"):
        return symbol[1:-1]
    raise SymbologyConfigError(
        f"{path}: {section}.{name!r} -> {symbol!r} is not a valid "
        f"identifier; wrap it in backticks (e.g. \"`{symbol}`\") to use it "
        f"verbatim")


def _validate_mapping(raw: dict[str, Any], section: str, path: Path) -> dict[str, str]:
    section_value = raw.get(section, {})
    if not isinstance(section_value, dict):
        raise SymbologyConfigError(
            f"{path}: {section!r} must be a mapping of name -> symbol, "
            f"got {type(section_value).__name__}")
    validated = {}
    for name, symbol in section_value.items():
        if not isinstance(name, str):
            raise SymbologyConfigError(
                f"{path}: {section!r} keys must be strings, got {name!r}")
        validated[name] = _validate_symbol(symbol, section, name, path)
    return validated


def load_config() -> dict[str, Any]:
    """The parsed, validated project config at `config_path()`, or `{}`
    when the file doesn't exist. Cached per file; call
    `load_config.cache_clear()` to force a re-read within one process.

    Raises:
        SymbologyConfigError: the file exists but is malformed
            (invalid YAML, a non-mapping top level or section, a
            non-string name or symbol, or a symbol that's neither
            `.isidentifier()`-safe nor backtick-wrapped).
    """
    return _load(config_path())


@functools.lru_cache(maxsize=8)
def _load(path: Path) -> dict[str, Any]:
    """`load_config` for one file, cached per path, so a process that
    works in several projects reads each project's own file."""
    if not path.is_file():
        return {}

    import yaml

    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        raise SymbologyConfigError(f"{path}: invalid YAML ({e})") from e

    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise SymbologyConfigError(
            f"{path}: top level must be a mapping, got {type(raw).__name__}")

    config: dict[str, Any] = {
        "params": _validate_mapping(raw, "params", path),
        "funcs": _validate_mapping(raw, "funcs", path),
    }
    if "show_missing" in raw:
        if not isinstance(raw["show_missing"], bool):
            raise SymbologyConfigError(f"{path}: 'show_missing' must be a boolean")
        config["show_missing"] = raw["show_missing"]
    if "enabled" in raw:
        if not isinstance(raw["enabled"], bool):
            raise SymbologyConfigError(f"{path}: 'enabled' must be a boolean")
        config["enabled"] = raw["enabled"]
    return config


load_config.cache_clear = _load.cache_clear  # type: ignore[attr-defined]


def is_disabled() -> bool:
    env = os.environ.get("MATHEMA_SYMBOLOGY_DISABLE")
    if env is not None and env not in ("", "0", "false", "False"):
        return True
    if env in ("0", "false", "False"):
        return False
    return load_config().get("enabled", True) is False
