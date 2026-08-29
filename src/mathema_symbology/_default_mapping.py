# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Aaron Byrne
"""The built-in name to symbol mapping: a curated table from common
parameter and function names to the notation that relevant field's
literature and code tend to use for that exact quantity.

Every entry has to be defensible as real, standard notation, and a
missing entry is fine as mathema falls back to its own naming approach
whenever this table has nothing to say. That's also why names whose
real notation isn't a single token get no entry at all,
namely `dr_dt` -> ("dr/dt"), `pe_ratio` -> ("P/E"),
`debt_to_equity` -> ("D/E") and `p_a_and_b` ("P(A∩B)").

Unrelated parameter concepts are allowed to share one bare symbol,
because names like "price", "power" and "pressure" (all genuinely bare
P) essentially never meet inside a single claim, and mathema resolves
any collision that does happen per claim at render time. The same goes
for the bare I, L, M, n and R families below, and a case distinction
is always the concept's own natural one, as with population size N
against sample size n. Function symbols are held to the opposite
standard, namely globally distinct and `.isidentifier()`-safe, since
distinct bound functions readily co-occur in one formula (f(x) + g(x))
and a function symbol sits in call position, where backtick escaping
is impossible.

True Unicode subscripts and superscripts are used wherever the glyph
exists (`σ₁` not `σ_1`, `cₚ` not `c_p`, `σ²` not `Var`). An ASCII
underscore spelling survives only where Unicode has no subscript for
the letter: there are no capital subscripts and no subscript
b/c/d/f/g/q/w/y/z, which is why `k_B`, `N_A`, `T_c` and `r_f` stay as
they are. A param symbol is free to be `.isidentifier()`-unsafe
(mathema backtick-wraps it at render time); a function symbol never
is.

`_check_default_mapping_consistency()` re-checks the structural rules
at import time: no symbol is ever bare `f` (mathema's reserved primary
function letter) or bare `e` (Euler's number), a numbered-subscript
name is stored only in its no-underscore spelling (`alpha1`, never
`alpha_1`, since `_symbology.py` retries an unmatched
`<base>_<digits>` name without the underscore), and the function table
keeps its values distinct and identifier-safe. `delta_<rest>` and
`pct_change_<rest>` names are likewise never stored here;
`_symbology.py` composes them at lookup time.
"""

_DEFAULT_PARAM_SYMBOLS: dict[str, str] = {
    "price": "P",
    "power": "P",
    "pressure": "P",
    "price_level": "P",
    "p_total": "Pₜₒₜ",
    "purchase_price": "P₀",
    "price_domestic": "P_d",
    "price_foreign": "P_f",
    # vapor pressure of a pure substance: the degree sign is the real
    # glyph, P°
    "p_pure": "P°",
    "p_value": "p",
    "momentum": "p",
    "probability": "Pr",
    "current": "I",
    "moment_of_inertia": "I",
    "intensity": "I",
    "investment": "I",
    "intersection": "∩",
    "nominal_gdp": "Y",
    "real_gdp": "Yᵣₑₐₗ",
    "length": "L",
    "L_ind": "L",
    "total_liabilities": "L",
    "labor_force": "L",
    "angular_momentum": "L",
    "likelihood": "L",
    "total_mass": "M",
    "molar_mass": "M",
    "m_total": "M",
    "molarity": "M",
    "money_supply": "Mₛ",
    "years": "n",
    "moles": "n",
    "refractive_index": "n",
    "number_density": "n",
    "ncarrier": "n",
    "sample_size": "n",
    "n_samples": "n",
    "face_value": "F",
    "fixed_costs": "FC",
    "helmholtz_free_energy": "F",
    "force": "F",
    "equity": "E",
    "total_equity": "E",
    "electric_field": "E",
    "energy": "E",
    "youngs_modulus": "E",
    "shares_outstanding": "N",
    "population_size": "N",
    "slope": "m",
    "mass": "m",
    "molality": "m",
    # bare m already belongs to molality in stoichiometry, so mass of
    # solute keeps its qualified spelling
    "mass_solute": "mₛₒₗ",
    "total_assets": "A",
    "A_amp": "A",
    "area": "A",
    "amplitude": "A",
    "revenue": "R",
    "annual_rent": "R",
    "resistance": "R",
    "gas_constant": "R",
    "ratio": "r",
    "radius": "r",
    "interest_rate_pct": "r",
    "discount_rate": "r_d",
    "risk_free_rate": "r_f",
    "r_nominal": "rₙₒₘ",
    # focal length and source frequency each have a genuine bare-f
    # convention, blocked by mathema's reserved function letter
    "focal_length": "fₗₑₙ",
    "f_source": "f₀",
    "strike_price": "K",
    "capital": "K",

    # ============================================================
    # Physics and chemistry
    # ============================================================
    "time": "t",
    "distance": "D", # d would be rejected by mathema as it means derivative
    "height": "h",
    "width": "w",
    "velocity": "v",
    "speed": "v",
    "initial_velocity": "v₀",
    "acceleration": "a",
    "angular_velocity": "ω",
    # angular frequency shares angular velocity's own symbol
    "angular_frequency": "ω",
    "angular_acceleration": "α",
    "gravity": "g",
    "gravitational_acceleration": "g",
    "volume": "V",
    "work": "W",
    "weight": "W",
    "kinetic_energy": "KE",
    "potential_energy": "PE",
    "impulse": "J",
    "torque": "τ",
    "torque_val": "τ",
    "spring_constant": "k",
    "coefficient_of_friction": "μ",
    "efficiency": "η",
    # no respelling of frequency avoids reserved f and still reads as
    # frequency, so it keeps a plain-word abbreviation
    "frequency": "freq",
    "wavenumber": "k",
    "wavelength": "λ",
    "temperature": "T",
    "period": "T",
    "T_hot": "T_h",
    "T_cold": "T_c",
    "heat": "Q",
    "heat_capacity": "C",
    "specific_heat_capacity": "c",
    "specific_heat_constant_pressure": "cₚ",
    "specific_heat_constant_volume": "cᵥ",
    "thermal_conductivity": "κ",
    "thermal_expansion_coefficient": "α",
    "diffusion_coefficient": "D",
    "surface_tension": "γ",
    "viscosity": "η",
    "density": "ρ",
    "rho_fluid": "ρ",
    "charge": "q",
    "voltage": "V",
    "magnetic_field": "B",
    "magnetic_flux": "Φ",
    "resistivity": "ρ",
    "conductance": "G",
    "capacitance": "C",
    "permittivity": "εᵣ",
    "vacuum_permittivity": "ε₀",
    "permeability": "μ",
    "vacuum_permeability": "μ₀",
    "speed_of_light": "c",
    "gravitational_constant": "G",
    "planck_constant": "h",
    "reduced_planck_constant": "ħ",
    "boltzmann_constant": "k_B",
    "avogadro_number": "N_A",
    "entropy": "S",
    "enthalpy": "H",
    "internal_energy": "U",
    "gibbs_free_energy": "G",
    "bonding_e": "E_b",
    "atomic_number": "Z",
    "decay_constant": "λ",
    # halflife of pharmacology and nuclear
    # physics, rather than a three-token t_1/2
    "half_life": "t½",
    "concentration": "c",
    "rate_constant": "k",
    "activation_energy": "Eₐ",
    "ph": "pH",
    "v_max": "Vₘₐₓ",

    # ============================================================
    # Statistics and probability
    # ============================================================
    "mean": "μ",
    # a combining macron over x, itself .isidentifier()-safe
    "sample_mean": "x̄",
    "x_bar": "x̄",
    "median": "Med",
    "mode": "Mo",
    "std": "σ",
    "pooled_sd": "sₚ",
    "variance": "σ²",
    "standard_error": "SE",
    # Fisher's g-family skewness and excess kurtosis
    "skew": "γ₁",
    "kurt": "γ₂",
    "covariance": "Cov",
    "correlation": "Corr",
    "degrees_of_freedom": "df",
    "z_score": "z",
    "t_statistic": "t",
    "chi_square": "χ²",
    "effect_size": "ⅆ",
    "confidence_level": "Conf",
    "significance_level": "α",
    "log_likelihood": "ℓ",
    "r_squared": "R²",
    "error_term": "ε",
    "odds_ratio": "OR",
    "iqr": "IQR",
    # estimator hats: a combining circumflex, the same mechanism as
    # x-bar above
    "y_hat": "ŷ",
    "p_hat": "p̂",
    "yhat": "ŷ",
    "phat": "p̂",
    "sensitivity": "Se",
    "specificity": "Sp",
    "sigmax": "σₓ",
    "sigmay": "σᵧ",
    "tauxy": "τₓᵧ",
    "a_minus": "a⁻",
    "sigma1": "σ₁",
    "sigma2": "σ₂",
    "theta1": "θ₁",
    "theta2": "θ₂",
    "mean1": "μ₁",
    "mean2": "μ₂",
    "alpha1": "α₁",
    "alpha2": "α₂",
    "beta0": "β₀",
    "beta1": "β₁",
    "beta2": "β₂",
    "q1": "Q₁",
    "q2": "Q₂",
    "q3": "Q₃",
    "c_base": "C₀",

    # ============================================================
    # Machine learning / data science
    # ============================================================
    "learning_rate": "η",
    "weights": "w",
    "bias": "b",
    "regularization": "λ",
    # how real code spells λ around Python's lambda keyword
    "lambda_": "λ",
    # the n×p design-matrix convention: p features
    "n_features": "p",
    "n_rows": "n",
    "mse": "MSE",
    "rmse": "RMSE",
    # reinforcement learning's discount factor
    "discount_factor": "γ",

    # ============================================================
    # Finance, accounting, and economics
    # ============================================================
    "spread": "s",
    "net_income": "NI",
    "current_liabilities": "CL",
    "current_assets": "CA",
    "tax_rate": "t",
    "inflation": "i",
    "coupon": "C",
    "nopat": "NOPAT",
    "invested_capital": "IC",
    "days_to_maturity": "T",
    "time_to_maturity": "T",
    "net_operating_income": "NOI",
    "interest_expense": "IE",
    "capex": "CapEx",
    "marginal_cost": "MC",
    "quantity": "Q",
    "total_debt": "D",
    "variable_cost": "VC",
    "cogs": "COGS",
    "gross_profit": "GP",
    "operating_income": "OI",
    "ebit": "EBIT",
    "ebitda": "EBITDA",
    "earnings_per_share": "EPS",
    "cash_flow": "CF",
    "free_cash_flow": "FCF",
    "wacc": "WACC",
    "npv": "NPV",
    "irr": "IRR",
    "present_value": "PV",
    "future_value": "FV",
    "duration": "Dur",
    "convexity": "Cvx",
    "dividend_yield": "DY",
    "market_cap": "MCap",
    "book_value": "BV",
    "roe": "ROE",
    "roa": "ROA",
    "roi": "ROI",
    "return_on_tangible_equity": "ROTE",
    "gross_margin": "GM",
    "working_capital": "WC",
    "sharpe_ratio": "SR",
    "yield_to_maturity": "YTM",
    "yield_to_worst": "YTW",
    "cagr": "CAGR",
    "volatility": "σ",
    "spot_price": "S",
    "unemployment_rate": "u",
    "elasticity": "ε",
    "marginal_utility": "MU",
    "marginal_revenue": "MR",
    "consumer_surplus": "CS",
    "producer_surplus": "PS",
    "consumption": "C",
    "government_spending": "G",
    "net_exports": "NX",
    # quant literature writes the option Greek "vega" as nu's glyph;
    "vega": "ν",
}

# Everyday operator-style math functions (sqrt, exp, log, sin, abs,
# floor, det, ...) aren't modified, their actual operator notation reshapes the
# function call which a renaming cannot do anything with.
_DEFAULT_FUNC_SYMBOLS: dict[str, str] = {
    # Φ/φ specifically mean the standard normal CDF/PDF; a bare
    # cdf/pdf binding could be any distribution's, so those keep the
    # distribution-agnostic acronym
    "norm_cdf": "Φ",
    "norm_pdf": "φ",
    "cdf": "CDF",
    "pdf": "PDF",
    "gamma_func": "Γ",
    "beta_func": "B",
    "digamma": "ψ",
    "zeta_func": "ζ",
    # Shannon entropy as a function, H(X); param and func symbols are
    # looked up separately, so this is independent of entropy -> S
    "entropy": "H",
    "var": "Var",
    "cov": "Cov",
    "corr": "Corr",
    "expectation": "E",

    # finance functions callable in their own right, as opposed to the
    # already-computed values of the same name in the param table
    "npv": "NPV",
    "irr": "IRR",
    "pv": "PV",
    "fv": "FV",
}


# The English-word spellings of the Greek letters, consulted by
# _symbology.py's delta and pct_change rules
# Case-sensitive: "phi" and "Phi" are different letters. "omicron" has
# no entry at all (its glyph is indistinguishable from Latin "o"), and
# "vega" resolves to ν.
_GREEK_WORD_TO_SYMBOL: dict[str, str] = {
    "alpha": "α", "beta": "β", "gamma": "γ", "Gamma": "Γ",
    "delta": "δ", "Delta": "Δ", "epsilon": "ε", "zeta": "ζ",
    "eta": "η", "theta": "θ", "Theta": "Θ", "iota": "ι",
    "kappa": "κ", "lambda": "λ", "Lambda": "Λ", "mu": "μ",
    "nu": "ν", "xi": "ξ", "Xi": "Ξ", "rho": "ρ", "sigma": "σ",
    "tau": "τ", "upsilon": "υ", "Upsilon": "Υ",
    "phi": "φ", "Phi": "Φ", "chi": "χ", "psi": "ψ", "Psi": "Ψ",
    "omega": "ω", "Omega": "Ω",
    "vega": "ν",
}


def greek_symbol_for_name(name: str) -> str | None:
    """The Greek symbol `name` spells out in English (`"theta"` -> `θ`),
    case-sensitive, or `None` for any other name."""
    return _GREEK_WORD_TO_SYMBOL.get(name)


def _check_default_mapping_consistency() -> None:
    """Re-checks the mapping's structural rules at import time, so a
    bad entry fails at import rather than at first render.

    Param symbols are free to collide with each other and to be
    `.isidentifier()`-unsafe (see the module docstring), so neither is
    checked. What is checked: a param symbol must not be bare `f`
    (mathema's reserved function letter) or bare `e` (Euler's number),
    a param name must not be a `<base>_<digits>` spelling (only the
    no-underscore form is stored), and function symbols must be
    globally distinct and `.isidentifier()`-safe.

    Raises:
        ValueError: any of the rules above is violated, with the
            offending entry named in the message.
    """
    for name, symbol in _DEFAULT_PARAM_SYMBOLS.items():
        if symbol == "f":
            raise ValueError(
                f"mathema_symbology: {name!r} -> \"f\" collides with mathema's "
                f"own reserved function letter")
        if symbol == "e":
            raise ValueError(
                f"mathema_symbology: {name!r} -> \"e\" collides with Euler's "
                f"number")
        base, sep, tail = name.rpartition("_")
        if sep and base and tail.isdigit():
            raise ValueError(
                f"mathema_symbology: {name!r} must be stored in its "
                f"no-underscore spelling ({base + tail!r}); the underscore "
                f"form is resolved at lookup time")

    seen_func: dict[str, str] = {}
    for name, symbol in _DEFAULT_FUNC_SYMBOLS.items():
        if symbol in seen_func:
            raise ValueError(
                f"mathema_symbology: duplicate symbol {symbol!r} for both "
                f"{seen_func[symbol]!r} and {name!r} in _DEFAULT_FUNC_SYMBOLS")
        seen_func[symbol] = name
        if not symbol.isidentifier():
            # a function symbol sits in a call's name position, where
            # backticks are never valid syntax even post-render
            raise ValueError(
                f"mathema_symbology: function symbol {name!r} -> {symbol!r} "
                f"must be .isidentifier()-safe (function symbols are never "
                f"backtick-escaped)")


_check_default_mapping_consistency()
