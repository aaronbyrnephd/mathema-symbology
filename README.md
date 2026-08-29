# mathema-symbology

Symbol lookups for mathema claim rendering.

[![tests](https://github.com/aaronbyrnephd/mathema-symbology/actions/workflows/tests.yml/badge.svg)](https://github.com/aaronbyrnephd/mathema-symbology/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/mathema-symbology)](https://pypi.org/project/mathema-symbology/)

mathema renders a verified claim back as one readable line of text,
and on its own it can only spell a parameter the way the code spells
it. This package supplies the notation: a curated mapping from common
parameter and function names to the symbols their field's literature
actually uses, so a claim about `price`, `sigma1` or `delta_revenue`
renders as P, σ₁ and ΔR rather than as Python identifiers. mathema
asks it for a symbol on every render, and any name it has no entry
for falls straight back to mathema's own naming.

## Install

```
pip install mathema-symbology
```

mathema discovers it automatically once installed, through the
`mathema.capabilities` entry point; there is no configuration to
write.

## Before and after

```
claim: for price in [0, 100], f(price) >= 0

without:  ∀ price ∈ [0.0, 100.0] ⊂ ℝ ∪ {∅}, f(price) ≥ 0
with:     let P = price, ∀ P ∈ [0.0, 100.0] ⊂ ℝ ∪ {∅}, f(P) ≥ 0

claim: for delta_revenue in [0, 10], f(delta_revenue) >= 0

without:  let x = delta_revenue, ∀ x ∈ [0.0, 10.0] ⊂ ℝ ∪ {∅}, f(x) ≥ 0
with:     let ΔR = delta_revenue, ∀ ΔR ∈ [0.0, 10.0] ⊂ ℝ ∪ {∅}, f(ΔR) ≥ 0

claim: for sigma1 in (0, 5], f(sigma1) >= 0

without:  ∀ sigma1 ∈ (0.0, 5.0] ⊂ ℝ ∪ {∅}, f(sigma1) ≥ 0
with:     let `σ₁` = sigma1, ∀ `σ₁` ∈ (0.0, 5.0] ⊂ ℝ ∪ {∅}, f(`σ₁`) ≥ 0

claim: for variance in [0, 10], f(variance) >= 0

without:  ∀ variance ∈ [0.0, 10.0] ⊂ ℝ ∪ {∅}, f(variance) ≥ 0
with:     let `σ²` = variance, ∀ `σ²` ∈ [0.0, 10.0] ⊂ ℝ ∪ {∅}, f(`σ²`) ≥ 0

claim: for pct_change_ebit in [-50, 50], f(pct_change_ebit) <= 1

without:  let x = pct_change_ebit, ∀ x ∈ [-50.0, 50.0] ⊂ ℝ ∪ {∅}, f(x) ≤ 1
with:     let `%ΔEBIT` = pct_change_ebit, ∀ `%ΔEBIT` ∈ [-50.0, 50.0] ⊂ ℝ ∪ {∅}, f(`%ΔEBIT`) ≤ 1

claim: for half_life in (0, 100], f(half_life) >= 0

without:  let x = half_life, ∀ x ∈ (0.0, 100.0] ⊂ ℝ ∪ {∅}, f(x) ≥ 0
with:     let `t½` = half_life, ∀ `t½` ∈ (0.0, 100.0] ⊂ ℝ ∪ {∅}, f(`t½`) ≥ 0
```

A symbol that isn't a valid identifier arrives backtick-wrapped, and
the rendered text still parses back to an equivalent claim.

## Resolution order

1. The project's own `.mathema/symbology.yaml`, if one exists.
2. Compositional shapes: `delta_<rest>` and `delta<Rest>` resolve
   `<rest>` on its own and prefix Δ, and `pct_change_<rest>` does the
   same with %Δ.
3. The built-in table of standard notation.
4. A `<base>_<digits>` name falls back to the spelling without the
   underscore, so `alpha_1` and `alpha1` resolve identically.

A name none of these recognise renders unchanged.

## Configuration

`.mathema/symbology.yaml` takes four keys, all optional: `params` and
`funcs` map names to symbols, `separator` replaces the ", " between
claim segments, and `show_missing` controls whether an unbounded
domain prints whether missing values are included or excluded. A symbol that isn't a valid Python
identifier goes inside of backticks (handled in mathema):

```yaml
params:
  headcount: N
  runway: "`T_run`"
funcs:
  payback: PB
```

## Adding a symbol

Open a pull request against the table in
[`src/mathema_symbology/_default_mapping.py`](src/mathema_symbology/_default_mapping.py).
An entry has to be real, standard notation in some field, worth making the default for parameter names that match. The missing-symbol issue template asks for details about its inclusion. 

For specific symbols that don't generalise beyond your codebase just use the approach in [Configuration ](#configuration)

## Requirements

Python 3.10 or later. The only runtime dependency is `pyyaml`;
mathema itself is not strictly required, only discovered when present.

## Licence

Apache-2.0, see [LICENSE](LICENSE).

## Version

This is 0.1.0 and the interface may change before 1.0.
