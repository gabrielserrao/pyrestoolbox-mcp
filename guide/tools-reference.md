# pyResToolbox MCP — Complete Tool Reference

All 108 tools with exact parameter names, types, constraints, defaults, and descriptions.
Generated from source code at https://github.com/gabrielserrao/pyrestoolbox-mcp

---
## Brine Tools

### `calculate_brine_properties`
Calculate properties of CH4 or CO2 saturated brine.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `degf` | float or List[float] | **required** |  | Temperature (degrees Fahrenheit) - scalar or array |
| `wt` | float | **required** | ge=0, le=30 | Brine salinity (weight percent NaCl) |
| `ch4` | float | 0.0 | ge=0 | Dissolved CH4 mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0 | Dissolved CO2 mole fraction (dimensionless) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `co2_brine_mutual_solubility`
Calculate CO2-brine mutual solubilities and properties.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pres` | float | **required** | gt=0 | Pressure (psia if metric=False, bar if metric=True) |
| `temp` | float | **required** | gt=0 | Temperature (degF if metric=False, degC if metric=True) |
| `ppm` | float | **required** | ge=0 | Brine salinity (ppm) |
| `metric` | bool | False |  | Use metric units (True) or field units (False) |
| `cw_sat` | float | 0.0 | ge=0 | Cw at saturation pressure (1/psi or 1/bar) - 0 for auto-calculate |

### `soreide_whitson_vle`
Calculate Soreide-Whitson VLE brine properties with hydrocarbon gas.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pres` | float | **required** | gt=0 | Pressure (psia | barsa) |
| `temp` | float | **required** |  | Temperature (degF | degC) |
| `ppm` | float | 0.0 | ge=0 | Brine salinity (ppm NaCl) |
| `y_CO2` | float | 0.0 | ge=0, le=1 | CO2 mole fraction in gas |
| `y_H2S` | float | 0.0 | ge=0, le=1 | H2S mole fraction in gas |
| `y_N2` | float | 0.0 | ge=0, le=1 | N2 mole fraction in gas |
| `y_H2` | float | 0.0 | ge=0, le=1 | H2 mole fraction in gas |
| `sg` | float | 0.65 | gt=0, le=3 | Gas specific gravity (air=1) |
| `metric` | bool | False |  | Use metric units |
| `cw_sat` | bool | False |  | Calculate saturated compressibility |

---
## Dca Tools

### `fit_decline`
Fit a decline curve model to production rate vs time data.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `time` | float or List[float] | **required** |  | Time array (user-defined units, e.g. months or years) |
| `rates` | float or List[float] | **required** |  | Production rate array (must be > 0) |
| `method` | Literal['exponential', 'harmonic', 'hyperbolic', 'duong', 'best'] | 'best' |  | Decline model to fit.  |
| `t_start` | float | None |  | Start of fitting window (inclusive) |
| `t_end` | float | None |  | End of fitting window (inclusive) |

### `fit_decline_cumulative`
Fit a decline curve model to rate vs cumulative production data.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `cumulative_production` | float or List[float] | **required** |  | Cumulative production array |
| `rates` | float or List[float] | **required** |  | Production rate array (must be > 0) |
| `method` | Literal['exponential', 'harmonic', 'hyperbolic', 'best'] | 'best' |  | Decline model to fit |
| `calendar_time` | float or List[float] | None |  | Optional calendar time array for uptime calculation |
| `np_start` | float | None |  | Start of fitting window (cumulative) |
| `np_end` | float | None |  | End of fitting window (cumulative) |

### `decline_forecast`
Generate a production rate and cumulative forecast from decline parameters.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `qi` | float | **required** | gt=0 | Initial rate (volume/time) |
| `di` | float | 0.0 | ge=0 | Initial decline rate (1/time). Not used for Duong |
| `b` | float | 0.0 | ge=0, le=2 | Arps b-factor (0=exp, 0<b<1=hyp, 1=harmonic) |
| `method` | Literal['exponential', 'harmonic', 'hyperbolic', 'duong'] | 'hyperbolic' |  | Decline model type |
| `t_end` | float | **required** | gt=0 | End time for forecast |
| `dt` | float | 1.0 | gt=0 | Time step (default 1.0) |
| `q_min` | float | 0.0 | ge=0 | Economic limit rate (0 = no cutoff) |
| `uptime` | float | 1.0 | gt=0, le=1 | Uptime fraction (0-1) |
| `a` | float | None |  | Duong  |
| `m` | float | None |  | Duong  |

### `arps_rate`
Calculate Arps decline rate at specified time(s).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `qi` | float | **required** | gt=0 | Initial rate (volume/time) |
| `di` | float | **required** | gt=0 | Initial decline rate (1/time) |
| `b` | float | **required** | ge=0, le=2 | Arps b-factor |
| `t` | float or List[float] | **required** |  | Time value(s) |

### `arps_cumulative`
Calculate Arps cumulative production at specified time(s).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `qi` | float | **required** | gt=0 | Initial rate (volume/time) |
| `di` | float | **required** | gt=0 | Initial decline rate (1/time) |
| `b` | float | **required** | ge=0, le=2 | Arps b-factor |
| `t` | float or List[float] | **required** |  | Time value(s) |

### `estimated_ultimate_recovery`
Calculate Estimated Ultimate Recovery (EUR) for Arps decline.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `qi` | float | **required** | gt=0 | Initial rate |
| `di` | float | **required** | gt=0 | Initial decline rate (1/time) |
| `b` | float | **required** | ge=0, le=2 | Arps b-factor |
| `q_min` | float | **required** | gt=0 | Economic limit rate |

### `duong_rate`
Calculate Duong decline rate for unconventional reservoirs.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `qi` | float | **required** | gt=0 | Rate at t=1 (volume/time) |
| `a` | float | **required** | gt=0 | Duong  |
| `m` | float | **required** | gt=1 | Duong  |
| `t` | float or List[float] | **required** |  | Time value(s) (must be > 0) |

### `fit_ratio`
Fit a ratio model (GOR, WOR, CGR) to production data.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `x` | float or List[float] | **required** |  | Independent variable (cumulative production or time) |
| `ratio` | float or List[float] | **required** |  | Ratio values (e.g. GOR, WOR) |
| `method` | Literal['linear', 'exponential', 'power', 'logistic', 'best'] | 'best' |  | Ratio model to fit |
| `domain` | Literal['cum', 'time'] | 'cum' |  | Domain type:  |

### `ratio_forecast`
Evaluate a fitted ratio model at given values.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `method` | Literal['linear', 'exponential', 'power', 'logistic'] | **required** |  | Ratio model type |
| `a` | float | **required** |  | Primary parameter |
| `b` | float | **required** |  | Secondary parameter |
| `c` | float | 0.0 |  | Tertiary parameter (logistic only) |
| `x` | float or List[float] | **required** |  | Values to evaluate at |
| `domain` | Literal['cum', 'time'] | 'cum' |  | Domain type |

---
## Gas Tools

### `gas_z_factor`
Calculate gas compressibility factor (Z-factor).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |
| `h2` | float | 0.0 | ge=0.0, le=1.0 | H2 mole fraction (dimensionless) |
| `method` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Calculation method (DAK recommended) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_critical_properties`
Calculate gas pseudo-critical properties (Tc and Pc).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |
| `h2` | float | 0.0 | ge=0.0, le=1.0 | H2 mole fraction (dimensionless) |
| `method` | Literal['PMC', 'SUT', 'BUR', 'BNS'] | 'PMC' |  | Calculation method (PMC recommended for HC gases, BUR/BNS for high non-HC content) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_formation_volume_factor`
Calculate gas formation volume factor (Bg).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |
| `h2` | float | 0.0 | ge=0.0, le=1.0 | H2 mole fraction (dimensionless) |
| `zmethod` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor calculation method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_viscosity`
Calculate gas viscosity (μg).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |
| `h2` | float | 0.0 | ge=0.0, le=1.0 | H2 mole fraction (dimensionless) |
| `zmethod` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor calculation method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_density`
Calculate gas density (ρg) at reservoir conditions.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |
| `h2` | float | 0.0 | ge=0.0, le=1.0 | H2 mole fraction (dimensionless) |
| `zmethod` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor calculation method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_compressibility`
Calculate gas compressibility (Cg).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |
| `h2` | float | 0.0 | ge=0.0, le=1.0 | H2 mole fraction (dimensionless) |
| `zmethod` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor calculation method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_pseudopressure`
Calculate gas pseudopressure difference (m(p)).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p1` | float or List[float] | **required** |  | Initial pressure (psia) - scalar or array |
| `p2` | float or List[float] | **required** |  | Final pressure (psia) - scalar or array |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |
| `h2` | float | 0.0 | ge=0.0, le=1.0 | H2 mole fraction (dimensionless) |
| `zmethod` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor calculation method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_pressure_from_pz`
Calculate pressure from P/Z value.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pz` | float or List[float] | **required** |  | P/Z value (psia) - scalar or array |
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |
| `h2` | float | 0.0 | ge=0.0, le=1.0 | H2 mole fraction (dimensionless) |
| `zmethod` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor calculation method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_sg_from_gradient`
Calculate gas specific gravity from pressure gradient.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `grad` | float or List[float] | **required** |  | Pressure gradient (psi/ft) - scalar or array |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float | **required** | gt=0 | Pressure (psia) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_water_content`
Calculate water content of natural gas.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `degf` | float or List[float] | **required** |  | Temperature (degrees Fahrenheit) - scalar or array |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_sg_from_composition`
Calculate gas specific gravity from composition.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `hc_mw` | float | **required** | gt=0 | Hydrocarbon molecular weight (lb/lbmol) |
| `co2` | float | 0.0 | ge=0, le=1 | CO2 mole fraction |
| `h2s` | float | 0.0 | ge=0, le=1 | H2S mole fraction |
| `n2` | float | 0.0 | ge=0, le=1 | N2 mole fraction |
| `h2` | float | 0.0 | ge=0, le=1 | H2 mole fraction |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_hydrate_prediction`
Predict gas hydrate formation conditions, water balance, and inhibitor requirements.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `p` | float | **required** | gt=0 | Operating pressure (psia | barsa) |
| `degf` | float | **required** |  | Operating temperature (deg F | deg C) |
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1) |
| `method` | str | 'TOWLER' |  | Hydrate prediction method |
| `inhibitor_type` | str | None |  | Inhibitor type: MEOH, MEG, DEG, TEG, or None |
| `inhibitor_wt_pct` | float | 0.0 | ge=0, le=100 | Inhibitor weight percent |
| `co2` | float | 0.0 | ge=0, le=1 | CO2 mole fraction |
| `h2s` | float | 0.0 | ge=0, le=1 | H2S mole fraction |
| `n2` | float | 0.0 | ge=0, le=1 | N2 mole fraction |
| `h2` | float | 0.0 | ge=0, le=1 | H2 mole fraction |
| `p_res` | float | None | gt=0 | Reservoir pressure for water balance |
| `degf_res` | float | None |  | Reservoir temperature for water balance |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `gas_fws_sg`
Estimate free-water-saturated gas specific gravity from separator data.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg_g` | float | **required** | gt=0, le=3 | Separator gas SG (relative to air) |
| `cgr` | float | **required** | ge=0 | Condensate-gas ratio (stb/MMscf | sm3/sm3) |
| `api_st` | float | **required** | gt=0, le=100 | Stock tank liquid API gravity |
| `metric` | bool | False |  | Use metric units |

### `gas_delta_pseudopressure`
Calculate delta-pseudopressure between two pressures.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `p1` | float | **required** | gt=0 | Starting (lower) pressure (psia | barsa) |
| `p2` | float | **required** | gt=0 | Ending (upper) pressure (psia | barsa) |
| `degf` | float | **required** |  | Temperature (deg F | deg C) |
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1) |
| `h2s` | float | 0.0 | ge=0, le=1 | H2S mole fraction |
| `co2` | float | 0.0 | ge=0, le=1 | CO2 mole fraction |
| `n2` | float | 0.0 | ge=0, le=1 | N2 mole fraction |
| `h2` | float | 0.0 | ge=0, le=1 | H2 mole fraction |
| `zmethod` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor method |
| `cmethod` | Literal['PMC', 'SUT', 'BUR', 'BNS'] | 'PMC' |  | Critical properties method |
| `metric` | bool | False |  | Use metric units |

### `create_gas_pvt`
Create a gas PVT object and compute properties at specified conditions.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float | 0.75 | ge=0.5, le=2.0 | Gas specific gravity (air=1) |
| `co2` | float | 0.0 | ge=0, le=1 | CO2 mole fraction |
| `h2s` | float | 0.0 | ge=0, le=1 | H2S mole fraction |
| `n2` | float | 0.0 | ge=0, le=1 | N2 mole fraction |
| `h2` | float | 0.0 | ge=0, le=1 | H2 mole fraction |
| `zmethod` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor method |
| `cmethod` | Literal['PMC', 'SUT', 'BUR', 'BNS'] | 'PMC' |  | Critical properties method |
| `pressures` | float or List[float] | **required** |  | Pressures to evaluate (psia | barsa) |
| `temperature` | float | **required** |  | Temperature (deg F | deg C) |
| `metric` | bool | False |  | Use metric units |

---
## Geomech Tools

### `geomech_vertical_stress`
Calculate vertical stress (overburden) from depth and formation properties.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `depth` | float | **required** | gt=0 | True vertical depth below surface (ft) |
| `water_depth` | float | 0.0 | ge=0 | Water depth for offshore wells (ft) |
| `avg_density` | float | 144.0 | gt=0, le=300 | Average bulk density of overburden (lb/ft³) |
| `water_density` | float | 64.0 | gt=0, le=100 | Water density (lb/ft³) - fresh=62.4, seawater=64.0 |

### `geomech_pore_pressure_eaton`
Calculate pore pressure using Eaton's method from sonic or resistivity logs.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `depth` | float | **required** | gt=0 | True vertical depth (ft) |
| `observed_value` | float | **required** | gt=0 | Observed sonic (μs/ft) or resistivity (ohm-m) |
| `normal_value` | float | **required** | gt=0 | Normal compaction trend value at this depth |
| `overburden_psi` | float | **required** | gt=0 | Overburden stress at depth (psi) |
| `eaton_exponent` | float | 3.0 | gt=0, le=5 | Eaton exponent (3.0 for sonic, 1.2 for resistivity) |
| `method` | Literal['sonic', 'resistivity'] | 'sonic' |  | Method type |

### `geomech_effective_stress`
Calculate effective stress from total stress and pore pressure.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `total_stress` | float or List[float] | **required** |  | Total stress (psi) - scalar or array |
| `pore_pressure` | float or List[float] | **required** |  | Formation pore pressure (psi) - scalar or array |
| `biot_coefficient` | float | 1.0 | gt=0, le=1 | Biot |

### `geomech_horizontal_stress`
Calculate horizontal stresses from vertical stress using elastic theory.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `vertical_stress` | float | **required** | gt=0 | Total vertical stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `poisson_ratio` | float | **required** | gt=0, lt=0.5 | Poisson |
| `tectonic_factor` | float | 0.0 | ge=0, le=1 | Tectonic stress multiplier (0=passive, 0.5=strike-slip, 1.0=reverse) |
| `biot_coefficient` | float | 1.0 | gt=0, le=1 | Biot |

### `geomech_elastic_moduli_conversion`
Convert between elastic moduli (Young's, bulk, shear, Poisson's ratio).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `youngs_modulus` | float | None | gt=0 | Young |
| `bulk_modulus` | float | None | gt=0 | Bulk modulus K (psi) |
| `shear_modulus` | float | None | gt=0 | Shear modulus G (psi) |
| `poisson_ratio` | float | None | gt=-1, lt=0.5 | Poisson |
| `lame_parameter` | float | None |  | Lamé |

### `geomech_rock_strength_mohr_coulomb`
Calculate rock strength using Mohr-Coulomb failure criterion.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `cohesion` | float | **required** | ge=0 | Rock cohesion (psi) |
| `friction_angle` | float | **required** | gt=0, lt=90 | Internal friction angle (degrees, 20-40° typical) |
| `effective_stress_min` | float | **required** | ge=0 | Minimum effective principal stress (psi) |

### `geomech_dynamic_to_static_moduli`
Convert dynamic elastic moduli (from logs) to static moduli (from core tests).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `dynamic_youngs` | float | None | gt=0 | Dynamic Young |
| `dynamic_poisson` | float | None | gt=0, lt=0.5 | Dynamic Poisson |
| `correlation` | Literal['eissa_kazi', 'plona_cook', 'linear'] | 'eissa_kazi' |  | Correlation method |
| `lithology` | Literal['sandstone', 'shale', 'carbonate'] | 'sandstone' |  | Rock lithology |

### `geomech_breakout_width`
Calculate borehole breakout width using Kirsch elastic solution.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_h_max` | float | **required** | gt=0 | Maximum horizontal stress (psi) |
| `sigma_h_min` | float | **required** | gt=0 | Minimum horizontal stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `mud_weight` | float | **required** | gt=0 | Drilling fluid density (ppg) |
| `wellbore_azimuth` | float | **required** | ge=0, le=360 | Well azimuth (degrees, 0-360) |
| `ucs` | float | **required** | gt=0 | Unconfined compressive strength (psi) |
| `friction_angle` | float | **required** | gt=0, lt=90 | Internal friction angle (degrees) |

### `geomech_fracture_gradient`
Calculate fracture gradient and maximum allowable mud weight.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `depth` | float | **required** | gt=0 | True vertical depth (ft) |
| `sigma_h_min` | float | None | gt=0 | Minimum horizontal stress (psi) if known |
| `vertical_stress` | float | **required** | gt=0 | Overburden stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `poisson_ratio` | float | 0.25 | gt=0, lt=0.5 | Poisson |
| `method` | Literal['hubbert_willis', 'eaton', 'matthews_kelly'] | 'eaton' |  | Calculation method |

### `geomech_safe_mud_weight_window`
Calculate safe mud weight window from pore pressure and fracture gradient.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `fracture_pressure` | float | **required** | gt=0 | Formation fracture pressure (psi) |
| `depth` | float | **required** | gt=0 | True vertical depth (ft) |
| `collapse_pressure` | float | None | gt=0 | Collapse pressure for stability (psi) |
| `safety_margin_overbalance` | float | 0.5 | ge=0 | Overbalance safety margin (ppg) |
| `safety_margin_fracture` | float | 0.5 | ge=0 | Fracture safety margin (ppg) |

### `geomech_critical_mud_weight_collapse`
Calculate critical mud weight to prevent borehole collapse.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_h_max` | float | **required** | gt=0 | Maximum horizontal stress (psi) |
| `sigma_h_min` | float | **required** | gt=0 | Minimum horizontal stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `cohesion` | float | **required** | ge=0 | Rock cohesion (psi) |
| `friction_angle` | float | **required** | gt=0, lt=90 | Internal friction angle (degrees) |
| `wellbore_azimuth` | float | **required** | ge=0, le=360 | Well azimuth (degrees) |
| `wellbore_inclination` | float | 0.0 | ge=0, le=90 | Well deviation from vertical (degrees) |
| `depth` | float | **required** | gt=0 | True vertical depth (ft) |

### `geomech_reservoir_compaction`
Calculate reservoir compaction from pressure depletion.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pressure_drop` | float | **required** | gt=0 | Reservoir pressure depletion (psi) |
| `reservoir_thickness` | float | **required** | gt=0 | Net pay thickness (ft) |
| `pore_compressibility` | float | None | gt=0 | Pore compressibility (1/psi) if known |
| `bulk_compressibility` | float | None | gt=0 | Bulk compressibility (1/psi) if known |
| `youngs_modulus` | float | **required** | gt=0 | Static Young |
| `poisson_ratio` | float | **required** | gt=0, lt=0.5 | Poisson |
| `biot_coefficient` | float | 1.0 | gt=0, le=1 | Biot coefficient |

### `geomech_pore_compressibility`
Calculate effective pore compressibility from rock and fluid properties.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `bulk_compressibility` | float | None | gt=0 | Rock bulk compressibility (1/psi) |
| `grain_compressibility` | float | 3e-07 | gt=0 | Grain compressibility (1/psi, default 3e-7) |
| `porosity` | float | **required** | gt=0, lt=1 | Formation porosity (fraction 0-1) |
| `youngs_modulus` | float | None | gt=0 | Young |
| `poisson_ratio` | float | None | gt=0, lt=0.5 | Poisson |

### `geomech_leak_off_pressure`
Analyze leak-off test (LOT) or formation integrity test (FIT) data.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `leak_off_pressure` | float | **required** | gt=0 | LOT pressure at surface (psi) |
| `mud_weight` | float | **required** | gt=0 | Mud weight during test (ppg) |
| `test_depth` | float | **required** | gt=0 | True vertical depth of test (ft) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure at test depth (psi) |
| `test_type` | Literal['LOT', 'FIT'] | 'LOT' |  | Test type - LOT (leak-off) or FIT (integrity test) |

### `geomech_hydraulic_fracture_width`
Estimate hydraulic fracture width from treating pressure and geometry.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `net_pressure` | float | **required** | gt=0 | Net treating pressure (psi) = Pfrac - σh_min |
| `fracture_height` | float | **required** | gt=0 | Fracture height (ft), typically ≈ pay thickness |
| `fracture_half_length` | float | **required** | gt=0 | Fracture half-length (ft), one wing |
| `youngs_modulus` | float | **required** | gt=0 | Formation Young |
| `poisson_ratio` | float | **required** | gt=0, lt=0.5 | Poisson |
| `model` | Literal['PKN', 'KGD'] | 'PKN' |  | Fracture model |

### `geomech_stress_polygon`
Calculate stress polygon bounds for frictional equilibrium constraints.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `vertical_stress` | float | **required** | gt=0 | Vertical stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Pore pressure (psi) |
| `friction_coefficient` | float | 0.6 | gt=0, lt=1.5 | Fault friction coefficient (0.6-0.85 typical) |
| `sigma_h_min` | float | None | gt=0 | Actual min horizontal stress to plot (psi) |
| `sigma_h_max` | float | None | gt=0 | Actual max horizontal stress to plot (psi) |

### `geomech_sand_production`
Predict sand production potential and critical drawdown pressure.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_h_max` | float | **required** | gt=0 | Maximum horizontal stress (psi) |
| `sigma_h_min` | float | **required** | gt=0 | Minimum horizontal stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `ucs` | float | **required** | gt=0 | Unconfined compressive strength (psi) |
| `cohesion` | float | **required** | ge=0 | Rock cohesion (psi) |
| `friction_angle` | float | **required** | gt=0, lt=90 | Internal friction angle (degrees) |
| `wellbore_radius` | float | 0.354 | gt=0 | Wellbore radius (ft) - default 8.5 inch hole |
| `perforation_depth` | float | 0.5 | gt=0 | Perforation tunnel depth (ft) |
| `permeability` | float | **required** | gt=0 | Formation permeability (mD) |
| `porosity` | float | **required** | gt=0, lt=1 | Formation porosity (fraction) |

### `geomech_fault_stability`
Analyze fault stability using Coulomb failure stress (CFS) criterion.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_1` | float | **required** | gt=0 | Maximum principal stress (psi) |
| `sigma_3` | float | **required** | gt=0 | Minimum principal stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Pore pressure (psi) |
| `fault_strike` | float | **required** | ge=0, le=360 | Fault strike azimuth (degrees) |
| `fault_dip` | float | **required** | gt=0, le=90 | Fault dip angle (degrees from horizontal) |
| `sigma_1_azimuth` | float | 0.0 | ge=0, le=360 | σ1 azimuth (degrees from North) |
| `friction_coefficient` | float | 0.6 | gt=0, lt=1.5 | Fault friction coefficient |
| `cohesion` | float | 0.0 | ge=0 | Fault cohesion (psi) - typically 0 for reactivation |

### `geomech_deviated_well_stress`
Transform principal stresses to deviated wellbore coordinate system.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_v` | float | **required** | gt=0 | Vertical stress (psi) |
| `sigma_h_max` | float | **required** | gt=0 | Maximum horizontal stress (psi) |
| `sigma_h_min` | float | **required** | gt=0 | Minimum horizontal stress (psi) |
| `sigma_h_max_azimuth` | float | **required** | ge=0, le=360 | σH_max azimuth from North (degrees) |
| `well_azimuth` | float | **required** | ge=0, le=360 | Well azimuth from North (degrees) |
| `well_inclination` | float | **required** | ge=0, le=90 | Well inclination from vertical (degrees) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `mud_weight` | float | **required** | gt=0 | Drilling fluid density (ppg) |
| `depth` | float | **required** | gt=0 | True vertical depth (ft) |

### `geomech_tensile_failure`
Predict tensile failure and fracture initiation at wellbore wall.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_h_max` | float | **required** | gt=0 | Maximum horizontal stress (psi) |
| `sigma_h_min` | float | **required** | gt=0 | Minimum horizontal stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `tensile_strength` | float | 0.0 | ge=0 | Rock tensile strength (psi) - often ~UCS/10 |
| `thermal_stress` | float | 0.0 |  | Thermal stress contribution (psi) - negative for cooling |

### `geomech_shear_failure_criteria`
Evaluate multiple shear failure criteria for rock strength comparison.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_1` | float | **required** |  | Maximum principal stress (psi) |
| `sigma_2` | float | **required** |  | Intermediate principal stress (psi) |
| `sigma_3` | float | **required** | ge=0 | Minimum principal stress (psi) |
| `ucs` | float | **required** | gt=0 | Unconfined compressive strength (psi) |
| `cohesion` | float | **required** | ge=0 | Rock cohesion (psi) |
| `friction_angle` | float | **required** | gt=0, lt=90 | Internal friction angle (degrees) |
| `criteria` | Literal['mohr_coulomb', 'drucker_prager', 'mogi_coulomb', 'modified_lade', 'modified_wiebols'] | ['mohr_coulomb' |  | List of failure criteria to evaluate |

### `geomech_breakout_stress_inversion`
Estimate horizontal stress magnitude from observed breakout width.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `breakout_width` | float | **required** | gt=0, lt=180 | Observed breakout angular width (degrees) |
| `sigma_v` | float | **required** | gt=0 | Vertical stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `mud_weight` | float | **required** | gt=0 | Drilling fluid density during observation (ppg) |
| `ucs` | float | **required** | gt=0 | Unconfined compressive strength (psi) |
| `friction_angle` | float | **required** | gt=0, lt=90 | Internal friction angle (degrees) |
| `depth` | float | **required** | gt=0 | True vertical depth (ft) |

### `geomech_breakdown_pressure`
Calculate formation breakdown pressure for hydraulic fracturing.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_h_max` | float | **required** | gt=0 | Maximum horizontal stress (psi) |
| `sigma_h_min` | float | **required** | gt=0 | Minimum horizontal stress (psi) |
| `pore_pressure` | float | **required** | gt=0 | Formation pore pressure (psi) |
| `tensile_strength` | float | 0.0 | ge=0 | Rock tensile strength (psi) |
| `poroelastic_constant` | float | 0.0 | ge=0, le=1.0 | Poroelastic constant η = α(1-2ν)/(1-ν), typically 0-0.5 |

### `geomech_stress_path`
Calculate stress changes during reservoir depletion or injection.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `initial_pore_pressure` | float | **required** | gt=0 | Initial formation pore pressure (psi) |
| `final_pore_pressure` | float | **required** | gt=0 | Final formation pore pressure (psi) |
| `vertical_stress` | float | **required** | gt=0 | Vertical stress - assumed constant (psi) |
| `initial_sigma_h` | float | **required** | gt=0 | Initial horizontal stress (psi) |
| `poisson_ratio` | float | **required** | gt=0, lt=0.5 | Poisson |
| `biot_coefficient` | float | 1.0 | gt=0, le=1 | Biot coefficient |
| `stress_path_coefficient` | float | None | gt=0, lt=1 | Stress path coefficient γ = Δσh/ΔPp. If not provided, calculated from ν |

### `geomech_thermal_stress`
Calculate thermal stress effects on wellbore and formation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `temperature_change` | float | **required** |  | Temperature change (degF) - negative for cooling, positive for heating |
| `youngs_modulus` | float | **required** | gt=0 | Young |
| `poisson_ratio` | float | **required** | gt=0, lt=0.5 | Poisson |
| `thermal_expansion_coefficient` | float | 6e-06 | gt=0 | Linear thermal expansion coefficient (1/degF) - typical 5-8e-6 |
| `biot_coefficient` | float | 1.0 | gt=0, le=1 | Biot coefficient |

### `geomech_ucs_from_logs`
Estimate Unconfined Compressive Strength (UCS) from well log data.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sonic_dt` | float | None | gt=0 | Sonic transit time (μs/ft) |
| `porosity` | float | None | gt=0, lt=1 | Porosity (fraction) |
| `youngs_modulus` | float | None | gt=0 | Young |
| `lithology` | Literal['sandstone', 'shale', 'carbonate', 'general'] | 'sandstone' |  | Rock lithology for correlation selection |
| `correlation` | Literal['mcnally', 'horsrud', 'chang', 'lal', 'vernik'] | 'mcnally' |  | UCS correlation to use |

### `geomech_critical_drawdown`
Calculate critical drawdown pressure before sand/shear failure at wellbore.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sigma_h_max` | float | **required** | gt=0 | Maximum horizontal stress (psi) |
| `sigma_h_min` | float | **required** | gt=0 | Minimum horizontal stress (psi) |
| `reservoir_pressure` | float | **required** | gt=0 | Initial reservoir pressure (psi) |
| `ucs` | float | **required** | gt=0 | Unconfined compressive strength (psi) |
| `cohesion` | float | **required** | ge=0 | Rock cohesion (psi) |
| `friction_angle` | float | **required** | gt=0, lt=90 | Internal friction angle (degrees) |
| `wellbore_radius` | float | 0.354 | gt=0 | Wellbore radius (ft) |

---
## Inflow Tools

### `oil_rate_radial`
Calculate oil production rate for radial flow (vertical well).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pi` | float | **required** | gt=0 | Initial reservoir pressure (psia) |
| `pb` | float | **required** | ge=0 | Bubble point pressure (psia) |
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `sg_g` | float | **required** | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `psd` | float or List[float] | **required** |  | Sandface pressure (psia) - scalar or array |
| `h` | float | **required** | gt=0 | Net pay thickness (ft) |
| `k` | float | **required** | gt=0 | Permeability (mD) |
| `s` | float | 0.0 |  | Skin factor (dimensionless) |
| `re` | float | **required** | gt=0 | Drainage radius (ft) |
| `rw` | float | **required** | gt=0 | Wellbore radius (ft) |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at bubble point (scf/stb) |
| `vogel` | bool | False |  | Use Vogel IPR for reservoir pressure below bubble point |

### `oil_rate_linear`
Calculate oil production rate for linear flow.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pi` | float | **required** | gt=0 | Initial reservoir pressure (psia) |
| `pb` | float | **required** | ge=0 | Bubble point pressure (psia) |
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `sg_g` | float | **required** | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `psd` | float or List[float] | **required** |  | Sandface pressure (psia) - scalar or array |
| `h` | float | **required** | gt=0 | Net pay thickness (ft) |
| `k` | float | **required** | gt=0 | Permeability (mD) |
| `area` | float | **required** | gt=0 | Drainage area (sq ft) |
| `length` | float | **required** | gt=0 | Well length (ft) |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at bubble point (scf/stb) |

### `gas_rate_radial`
Calculate gas production rate for radial flow (vertical well).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pi` | float | **required** | gt=0 | Initial reservoir pressure (psia) |
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `psd` | float or List[float] | **required** |  | Sandface pressure (psia) - scalar or array |
| `h` | float | **required** | gt=0 | Net pay thickness (ft) |
| `k` | float | **required** | gt=0 | Permeability (mD) |
| `s` | float | 0.0 |  | Skin factor (dimensionless) |
| `re` | float | **required** | gt=0 | Drainage radius (ft) |
| `rw` | float | **required** | gt=0 | Wellbore radius (ft) |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |

### `gas_rate_linear`
Calculate gas production rate for linear flow.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pi` | float | **required** | gt=0 | Initial reservoir pressure (psia) |
| `sg` | float | **required** | ge=0.5, le=2.0 | Gas specific gravity (air=1, dimensionless) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `psd` | float or List[float] | **required** |  | Sandface pressure (psia) - scalar or array |
| `h` | float | **required** | gt=0 | Net pay thickness (ft) |
| `k` | float | **required** | gt=0 | Permeability (mD) |
| `area` | float | **required** | gt=0 | Drainage area (sq ft) |
| `length` | float | **required** | gt=0 | Well length (ft) |
| `h2s` | float | 0.0 | ge=0.0, le=1.0 | H2S mole fraction (dimensionless) |
| `co2` | float | 0.0 | ge=0.0, le=1.0 | CO2 mole fraction (dimensionless) |
| `n2` | float | 0.0 | ge=0.0, le=1.0 | N2 mole fraction (dimensionless) |

---
## Layer Tools

### `lorenz_to_beta`
Convert Lorenz coefficient to Dykstra-Parsons beta parameter.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `value` | float | **required** | ge=0, le=1 | Lorenz or beta value |

### `beta_to_lorenz`
Convert Dykstra-Parsons beta to Lorenz coefficient.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `value` | float | **required** | ge=0, le=1 | Lorenz or beta value |

### `lorenz_from_flow_fractions`
Calculate Lorenz coefficient from flow and permeability fractions.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `flow_frac` | float or List[float] | **required** |  | Flow fractions per layer |
| `perm_frac` | float or List[float] | **required** |  | Permeability-thickness fractions per layer |

### `flow_fractions_from_lorenz`
Generate flow fractions from Lorenz coefficient.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `value` | float | **required** | ge=0, le=1 | Lorenz or beta value |

### `generate_layer_distribution`
Generate layered permeability distribution from Lorenz coefficient.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `lorenz` | float | **required** | ge=0, le=1 | Lorenz coefficient (0=homogeneous, 1=heterogeneous) |
| `nlay` | int | **required** | gt=0, le=100 | Number of layers |
| `h` | float | 1.0 | gt=0, lt=1 | Total thickness (ft, default=1 for normalized) |
| `k_avg` | float | 1.0 | gt=0, lt=1 | Average permeability (mD, default=1 for normalized) |
| `normalize` | bool | True |  | Normalize output (h and k fractions vs absolute) |

---
## Library Tools

### `get_component_properties`
Get critical properties for hydrocarbon components from database.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `component` | str | **required** |  | Component name (e.g.,  |
| `eos` | Literal['PR79', 'PR77', 'SRK', 'RK'] | 'PR79' |  | Equation of State model |

---
## Matbal Tools

### `gas_material_balance`
Perform P/Z gas material balance for OGIP estimation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pressures` | float or List[float] | **required** |  | Reservoir pressures at each survey (psia | barsa). First = initial pressure |
| `cumulative_gas` | float or List[float] | **required** |  | Cumulative gas production at each survey (user units — OGIP in same units) |
| `temperature` | float | **required** |  | Reservoir temperature (deg F | deg C) |
| `gas_sg` | float | 0.65 | ge=0.5, le=2.0 | Gas specific gravity (air=1) |
| `co2` | float | 0.0 | ge=0, le=1 | CO2 mole fraction |
| `h2s` | float | 0.0 | ge=0, le=1 | H2S mole fraction |
| `n2` | float | 0.0 | ge=0, le=1 | N2 mole fraction |
| `h2` | float | 0.0 | ge=0, le=1 | H2 mole fraction |
| `cumulative_water` | float or List[float] | None |  | Cumulative water production (optional) |
| `water_fvf` | float | 1.0 | gt=0 | Water FVF (rb/stb) |
| `water_influx` | float or List[float] | None |  | Cumulative water influx (optional, for Havlena-Odeh) |
| `z_method` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor method |
| `c_method` | Literal['PMC', 'SUT', 'BUR'] | 'PMC' |  | Critical properties method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_material_balance`
Perform Havlena-Odeh oil material balance for OOIP estimation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pressures` | float or List[float] | **required** |  | Reservoir pressures at each survey (psia | barsa). First = initial pressure |
| `cumulative_oil` | float or List[float] | **required** |  | Cumulative oil production (STB | sm3) at each pressure step |
| `temperature` | float | **required** |  | Reservoir temperature (deg F | deg C) |
| `api` | float | 0.0 | ge=0, le=100 | Stock tank oil API gravity |
| `sg_sp` | float | 0.0 | ge=0, le=3 | Separator gas specific gravity |
| `sg_g` | float | 0.0 | ge=0, le=3 | Weighted average surface gas SG |
| `pb` | float | 0.0 | ge=0 | Bubble point pressure (psia | barsa) |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at Pb (scf/stb | sm3/sm3) |
| `producing_gor` | float or List[float] | None |  | Cumulative producing GOR at each step |
| `cumulative_water` | float or List[float] | None |  | Cumulative water production |
| `water_injection` | float or List[float] | None |  | Cumulative water injection |
| `gas_injection` | float or List[float] | None |  | Cumulative gas injection |
| `water_fvf` | float | 1.0 | gt=0 | Water FVF |
| `gas_cap_ratio` | float | 0.0 | ge=0 | Gas cap ratio m = G*Bgi/(N*Boi) |
| `cf` | float | 0.0 | ge=0 | Formation compressibility (1/psi | 1/bar) |
| `sw_i` | float | 0.0 | ge=0, le=1 | Initial water saturation |
| `cw` | float | 0.0 | ge=0 | Water compressibility (1/psi | 1/bar) |
| `rs_method` | Literal['VELAR', 'STAN', 'VALMC'] | 'VELAR' |  | Solution GOR method |
| `bo_method` | Literal['MCAIN', 'STAN'] | 'MCAIN' |  | Oil FVF method |
| `z_method` | Literal['DAK', 'HY', 'WYW', 'BUR'] | 'DAK' |  | Z-factor method |
| `c_method` | Literal['PMC', 'SUT', 'BUR'] | 'PMC' |  | Critical properties method |
| `metric` | bool | False |  | Use metric units |

---
## Nodal Tools

### `flowing_bhp`
Calculate flowing bottom hole pressure using VLP correlations.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `thp` | float | **required** | gt=0 | Tubing head pressure (psia | barsa) |
| `completion` | CompletionModel | **required** |  | Wellbore completion |
| `vlp_method` | Literal['HB', 'WG', 'GRAY', 'BB'] | 'WG' |  | VLP correlation: HB (Hagedorn-Brown), WG (Woldesemayat-Ghajar), GRAY, BB (Beggs & Brill) |
| `well_type` | Literal['gas', 'oil'] | 'gas' |  | Well type |
| `gas_rate_mmscfd` | float | 0.0 | ge=0 | Gas rate (MMscf/d | sm3/d) |
| `cgr` | float | 0.0 | ge=0 | Condensate-gas ratio (STB/MMscf) |
| `water_rate_bwpd` | float | 0.0 | ge=0 | Water rate (STB/d | sm3/d) |
| `oil_viscosity` | float | 1.0 | gt=0 | Condensate/oil viscosity (cP) |
| `api` | float | 45.0 | gt=0, le=100 | Condensate/oil API gravity |
| `reservoir_pressure` | float | 0.0 | ge=0 | Reservoir pressure for condensate dropout |
| `total_liquid_stbpd` | float | 0.0 | ge=0 | Total liquid rate for oil wells (STB/d) |
| `gor` | float | 0.0 | ge=0 | Producing GOR for oil wells (scf/stb) |
| `water_cut` | float | 0.0 | ge=0, le=1 | Water cut fraction (0-1) |
| `water_sg` | float | 1.07 | gt=0 | Water specific gravity |
| `gas_sg` | float | 0.65 | gt=0, le=3 | Gas specific gravity |
| `injection` | bool | False |  | Injection well mode |
| `metric` | bool | False |  | Use metric units |

### `ipr_curve`
Generate an Inflow Performance Relationship (IPR) curve.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `reservoir` | ReservoirModel | **required** |  | Reservoir description |
| `well_type` | Literal['gas', 'oil', 'water'] | 'gas' |  | Well type |
| `n_points` | int | 20 | gt=1, le=100 | Number of pressure points |
| `min_pwf` | float | None |  | Minimum flowing BHP (psia | barsa). Default 14.7 psia |
| `water_cut` | float | 0.0 | ge=0, le=1 | Water cut fraction (oil wells) |
| `water_sg` | float | 1.07 | gt=0 | Water specific gravity |
| `bo` | float | 1.2 | gt=0 | Oil FVF if no OilPVT (rb/stb) |
| `uo` | float | 1.0 | gt=0 | Oil viscosity if no OilPVT (cP) |
| `gas_sg` | float | 0.65 | gt=0, le=3 | Gas SG if no GasPVT |
| `metric` | bool | False |  | Use metric units |

### `outflow_curve`
Generate a VLP outflow (tubing performance) curve.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `thp` | float | **required** | gt=0 | Tubing head pressure (psia | barsa) |
| `completion` | CompletionModel | **required** |  | Wellbore completion |
| `vlp_method` | Literal['HB', 'WG', 'GRAY', 'BB'] | 'WG' |  | VLP correlation |
| `well_type` | Literal['gas', 'oil'] | 'gas' |  | Well type |
| `rates` | float or List[float] | None |  | Rates to evaluate (auto-generated if None) |
| `n_rates` | int | 20 | gt=1, le=100 | Number of rate points if rates is None |
| `max_rate` | float | None |  | Maximum rate for auto-generation |
| `gas_rate_mmscfd` | float | 0.0 | ge=0 | Not used directly; rates override |
| `cgr` | float | 0.0 | ge=0 | Condensate-gas ratio |
| `water_rate_bwpd` | float | 0.0 | ge=0 | Water rate |
| `oil_viscosity` | float | 1.0 | gt=0 | Oil viscosity (cP) |
| `api` | float | 45.0 | gt=0, le=100 | API gravity |
| `gor` | float | 0.0 | ge=0 | Producing GOR for oil wells |
| `water_cut` | float | 0.0 | ge=0, le=1 | Water cut fraction |
| `water_sg` | float | 1.07 | gt=0 | Water SG |
| `gas_sg` | float | 0.65 | gt=0, le=3 | Gas SG |
| `injection` | bool | False |  | Injection mode |
| `metric` | bool | False |  | Use metric units |

### `operating_point`
Find the VLP/IPR operating point (intersection of inflow and outflow curves).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `thp` | float | **required** | gt=0 | Tubing head pressure (psia | barsa) |
| `completion` | CompletionModel | **required** |  | Wellbore completion |
| `reservoir` | ReservoirModel | **required** |  | Reservoir description |
| `vlp_method` | Literal['HB', 'WG', 'GRAY', 'BB'] | 'WG' |  | VLP correlation |
| `well_type` | Literal['gas', 'oil'] | 'gas' |  | Well type |
| `cgr` | float | 0.0 | ge=0 | Condensate-gas ratio |
| `water_rate_bwpd` | float | 0.0 | ge=0 | Water rate |
| `oil_viscosity` | float | 1.0 | gt=0 | Oil viscosity (cP) |
| `api` | float | 45.0 | gt=0, le=100 | API gravity |
| `gor` | float | 0.0 | ge=0 | Producing GOR |
| `water_cut` | float | 0.0 | ge=0, le=1 | Water cut fraction |
| `water_sg` | float | 1.07 | gt=0 | Water SG |
| `gas_sg` | float | 0.65 | gt=0, le=3 | Gas SG |
| `bo` | float | 1.2 | gt=0 | Oil FVF |
| `uo` | float | 1.0 | gt=0 | Oil viscosity |
| `n_points` | int | 25 | gt=1, le=100 | Number of points for curves |
| `metric` | bool | False |  | Use metric units |

### `generate_vfp_prod_table`
Generate VFPPROD table for ECLIPSE/Intersect simulation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `table_num` | int | **required** | ge=1 | VFP table number |
| `completion` | CompletionModel | **required** |  | Wellbore completion |
| `well_type` | Literal['gas', 'oil'] | 'gas' |  | Well type |
| `vlp_method` | Literal['HB', 'WG', 'GRAY', 'BB'] | 'WG' |  | VLP correlation |
| `flo_rates` | float or List[float] | None |  | Flow rates (auto if None) |
| `thp_values` | float or List[float] | None |  | THP values (auto if None) |
| `wfr_values` | float or List[float] | None |  | Water fraction values |
| `gfr_values` | float or List[float] | None |  | Gas fraction values |
| `alq_values` | float or List[float] | None |  | Artificial lift values |
| `gas_sg` | float | 0.65 | gt=0, le=3 | Gas SG |
| `oil_viscosity` | float | 1.0 | gt=0 | Oil viscosity (cP) |
| `api` | float | 45.0 | gt=0, le=100 | API gravity |
| `reservoir_pressure` | float | 0.0 | ge=0 | Reservoir pressure |
| `water_sg` | float | 1.07 | gt=0 | Water SG |
| `datum_depth` | float | 0.0 | ge=0 | Reference depth (ft | m) |
| `metric` | bool | False |  | Use metric units |

### `generate_vfp_inj_table`
Generate VFPINJ table for ECLIPSE/Intersect simulation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `table_num` | int | **required** | ge=1 | VFP table number |
| `completion` | CompletionModel | **required** |  | Wellbore completion |
| `flo_type` | Literal['WAT', 'GAS', 'OIL'] | 'WAT' |  | Flow rate type |
| `vlp_method` | Literal['HB', 'WG', 'GRAY', 'BB'] | 'WG' |  | VLP correlation |
| `flo_rates` | float or List[float] | None |  | Flow rates |
| `thp_values` | float or List[float] | None |  | THP values |
| `gas_sg` | float | 0.65 | gt=0, le=3 | Gas SG |
| `water_sg` | float | 1.07 | gt=0 | Water SG |
| `api` | float | 35.0 | gt=0, le=100 | Oil API gravity |
| `datum_depth` | float | 0.0 | ge=0 | Reference depth (ft | m) |
| `metric` | bool | False |  | Use metric units |

---
## Oil Tools

### `oil_bubble_point`
Calculate oil bubble point pressure (Pb).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `rsb` | float | **required** | ge=0 | Solution GOR at bubble point (scf/stb) |
| `sg_g` | float | 0.0 | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `method` | Literal['STAN', 'VALMC', 'VELAR'] | 'VALMC' |  | Calculation method (VALMC recommended) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_solution_gor`
Calculate solution gas-oil ratio (Rs) at specified pressure.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `sg_g` | float | 0.0 | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `pb` | float | 0.0 | ge=0 | Bubble point pressure (psia) |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at bubble point (scf/stb) |
| `method` | Literal['VELAR', 'STAN', 'VALMC'] | 'VELAR' |  | Calculation method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_formation_volume_factor`
Calculate oil formation volume factor (Bo).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `sg_g` | float | 0.0 | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `pb` | float | 0.0 | ge=0 | Bubble point pressure (psia) |
| `rs` | float or List[float] | 0.0 |  | Solution GOR (scf/stb) - scalar or array |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at bubble point (scf/stb) |
| `method` | Literal['MCAIN', 'STAN'] | 'MCAIN' |  | Calculation method (MCAIN recommended) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_viscosity`
Calculate oil viscosity (μo).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `pb` | float | 0.0 | ge=0 | Bubble point pressure (psia) |
| `rs` | float or List[float] | 0.0 |  | Solution GOR (scf/stb) - scalar or array |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at bubble point (scf/stb) |
| `method` | Literal['BR'] | 'BR' |  | Calculation method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_density`
Calculate oil density (ρo) at reservoir conditions.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `rs` | float or List[float] | **required** |  | Solution GOR (scf/stb) - scalar or array |
| `sg_g` | float | **required** | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `bo` | float or List[float] | **required** |  | Oil FVF (rb/stb) - scalar or array |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_compressibility`
Calculate oil compressibility (Co).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `pb` | float | **required** | ge=0 | Bubble point pressure (psia) |
| `sg_g` | float | **required** | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `rs` | float or List[float] | **required** |  | Solution GOR (scf/stb) - scalar or array |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at bubble point (scf/stb) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_api_from_sg`
Convert oil specific gravity to API gravity.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg` | float or List[float] | **required** |  | Specific gravity - scalar or array |

### `oil_sg_from_api`
Convert API gravity to oil specific gravity.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float or List[float] | **required** |  | API gravity (degrees) - scalar or array |

### `generate_black_oil_table`
Generate comprehensive black oil PVT table.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pi` | float | **required** | gt=0 | Initial reservoir pressure (psia) |
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `sg_g` | float | **required** | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `pmax` | float | 0.0 | ge=0 | Maximum pressure for table (psia, 0=auto) |
| `pb` | float | 0.0 | ge=0 | Bubble point pressure (psia, 0=calculate) |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at bubble point (scf/stb, 0=calculate) |
| `nrows` | int | 50 | gt=0, le=200 | Number of table rows |
| `export` | bool | False |  | Export ECLIPSE-compatible files |
| `pb_method` | Literal['STAN', 'VALMC', 'VELAR'] | 'VALMC' |  | Bubble point calculation method |
| `rs_method` | Literal['VELAR', 'STAN', 'VALMC'] | 'VELAR' |  | Solution GOR method |
| `bo_method` | Literal['MCAIN', 'STAN'] | 'MCAIN' |  | Oil FVF method |
| `uo_method` | Literal['BR'] | 'BR' |  | Oil viscosity method |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_rs_at_bubble_point`
Calculate solution GOR at bubble point using Standing correlation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `rsb` | float | **required** | ge=0 | Solution GOR at bubble point (scf/stb) |
| `sg_g` | float | 0.0 | ge=0, le=3 | Gas specific gravity (air=1, dimensionless) |
| `method` | Literal['STAN', 'VALMC', 'VELAR'] | 'VALMC' |  | Calculation method (VALMC recommended) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `evolved_gas_sg`
Calculate evolved gas specific gravity.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `sg_g` | float | **required** | ge=0, le=3 | Separator gas specific gravity |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `psep` | float | 100.0 | gt=0 | Separator pressure (psia) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `stock_tank_gas_sg`
Calculate stock tank gas specific gravity.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |
| `degf` | float | **required** | gt=-460, lt=1000 | Temperature (degrees Fahrenheit) |
| `sg_g` | float | **required** | ge=0, le=3 | Separator gas specific gravity |
| `p` | float or List[float] | **required** |  | Pressure (psia) - scalar or array |
| `psep` | float | 100.0 | gt=0 | Separator pressure (psia) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `oil_sg_from_jacoby`
Calculate oil specific gravity from molecular weight and Jacoby aromaticity.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `mw` | float or List[float] | **required** | gt=0 | Molecular weight (lb/lbmol) - scalar or array |
| `ja` | float or List[float] | **required** | ge=0, le=1 | Jacoby aromaticity factor (0=paraffinic, 1=aromatic) |

### `oil_twu_critical_properties`
Calculate critical properties using Twu (1984) correlation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `mw` | float or List[float] | **required** | gt=0 | Molecular weight (lb/lbmol) - scalar or array |
| `sg` | float or List[float] | **required** | gt=0 | Specific gravity - scalar or array |
| `tb` | float or List[float] | None |  | Boiling point (degR) - optional |
| `damp` | float | 0.0 | ge=0, le=1 | Damping factor (0-1) |
| `metric` | bool | False |  | Use metric units (barsa, degC) |

### `weighted_average_gas_sg`
Calculate weighted average gas specific gravity from separator stages.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg_sp` | float | **required** | gt=0 | Separator gas specific gravity |
| `rsp` | float | **required** | ge=0 | Separator GOR (scf/stb) |
| `sg_st` | float | **required** | gt=0 | Stock tank gas specific gravity |
| `rst` | float | **required** | ge=0 | Stock tank GOR (scf/stb) |

### `stock_tank_incremental_gor`
Calculate incremental GOR from separator to stock tank.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `psp` | float | **required** | gt=0 | Separator pressure (psia) |
| `degf_sp` | float | **required** | gt=-460, lt=1000 | Separator temperature (degF) |
| `api` | float | **required** | gt=0, le=100 | Oil API gravity (degrees) |

### `validate_gas_gravities`
Validate and impute missing gas gravities.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sg_g` | float | None |  | Weighted average gas SG (optional) |
| `sg_sp` | float | None |  | Separator gas SG (optional) |
| `rst` | float | **required** | ge=0 | Stock tank GOR (scf/stb) |
| `rsp` | float | **required** | ge=0 | Separator GOR (scf/stb) |
| `sg_st` | float | **required** | gt=0 | Stock tank gas SG |

### `oil_harmonize_pvt`
Auto-harmonize oil PVT parameters for internal consistency.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pb` | float | 0.0 | ge=0 | Bubble point pressure (psia | barsa) |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at Pb (scf/stb | sm3/sm3) |
| `degf` | float | 0.0 |  | Reservoir temperature (deg F | deg C) |
| `api` | float | 0.0 | ge=0, le=100 | Stock tank oil API gravity |
| `sg_sp` | float | 0.0 | ge=0, le=3 | Separator gas SG |
| `sg_g` | float | 0.0 | ge=0, le=3 | Weighted average surface gas SG |
| `uo_target` | float | 0.0 | ge=0 | Target viscosity at p_uo (cP) |
| `p_uo` | float | 0.0 | ge=0 | Pressure where viscosity is known (psia) |
| `rs_method` | Literal['VELAR', 'STAN', 'VALMC'] | 'VELAR' |  | Solution GOR method |
| `pb_method` | Literal['STAN', 'VALMC', 'VELAR'] | 'VELAR' |  | Bubble point method |
| `metric` | bool | False |  | Use metric units |

### `create_oil_pvt`
Create an oil PVT object and compute properties at specified pressures.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | **required** | gt=0, le=100 | Stock tank oil API gravity |
| `sg_sp` | float | **required** | gt=0, le=3 | Separator gas SG |
| `pb` | float | **required** | gt=0 | Bubble point pressure (psia | barsa) |
| `temperature` | float | **required** |  | Reservoir temperature (deg F | deg C) |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at Pb. 0 = auto-calculate |
| `sg_g` | float | 0.0 | ge=0, le=3 | Weighted average gas SG |
| `uo_target` | float | 0.0 | ge=0 | Target viscosity (cP) |
| `p_uo` | float | 0.0 | ge=0 | Pressure of target viscosity (psia) |
| `rs_method` | Literal['VELAR', 'STAN', 'VALMC'] | 'VELAR' |  | Solution GOR method |
| `pb_method` | Literal['STAN', 'VALMC', 'VELAR'] | 'VALMC' |  | Bubble point method |
| `bo_method` | Literal['MCAIN', 'STAN'] | 'MCAIN' |  | Oil FVF method |
| `pressures` | float or List[float] | **required** |  | Pressures to evaluate (psia | barsa) |
| `metric` | bool | False |  | Use metric units |

---
## Recommend Tools

### `recommend_methods`
Recommend the best PVT and VLP correlations for given fluid properties.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `gas_sg` | float | 0.65 | ge=0.5, le=2.0 | Gas specific gravity (air=1) |
| `co2` | float | 0.0 | ge=0, le=1 | CO2 mole fraction |
| `h2s` | float | 0.0 | ge=0, le=1 | H2S mole fraction |
| `n2` | float | 0.0 | ge=0, le=1 | N2 mole fraction |
| `h2` | float | 0.0 | ge=0, le=1 | H2 mole fraction |
| `api` | float | None | gt=0, le=100 | Oil API gravity. If provided, includes oil method recommendations |
| `deviation` | float | 0.0 | ge=0, le=90 | Max wellbore deviation from vertical (degrees) |
| `well_type` | Literal['gas', 'oil'] | 'gas' |  | Well type |

### `recommend_gas_methods`
Recommend Z-factor and critical property methods for a gas composition.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `gas_sg` | float | 0.65 | ge=0.5, le=2.0 | Gas specific gravity (air=1) |
| `co2` | float | 0.0 | ge=0, le=1 | CO2 mole fraction |
| `h2s` | float | 0.0 | ge=0, le=1 | H2S mole fraction |
| `n2` | float | 0.0 | ge=0, le=1 | N2 mole fraction |
| `h2` | float | 0.0 | ge=0, le=1 | H2 mole fraction |

### `recommend_oil_methods`
Recommend oil PVT correlation methods based on API gravity.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `api` | float | 35.0 | gt=0, le=100 | Oil API gravity |

### `recommend_vlp_method`
Recommend VLP multiphase flow correlation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `deviation` | float | 0.0 | ge=0, le=90 | Max deviation from vertical (degrees) |
| `well_type` | Literal['gas', 'oil'] | 'gas' |  | Well type |

---
## Sensitivity Tools

### `parameter_sweep`
Sweep a single parameter across a range of values for any pyResToolbox function.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `function_module` | str | **required** |  | Module name (e.g.  |
| `function_name` | str | **required** |  | Function name (e.g.  |
| `base_parameters` | Dict[str, Any | **required** |  | Base keyword arguments for the function |
| `vary_parameter` | str | **required** |  | Name of the parameter to vary |
| `vary_values` | float or List[float] | **required** |  | Values to sweep through |
| `result_key` | str | None |  | Key/attribute to extract from each result |

### `tornado_sensitivity`
Compute tornado-chart sensitivities for multiple parameters.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `function_module` | str | **required** |  | Module name (e.g.  |
| `function_name` | str | **required** |  | Function name (e.g.  |
| `base_parameters` | Dict[str, Any | **required** |  | Base keyword arguments for the function |
| `ranges` | float or List[float] | **required** |  | Parameter ranges as {param_name: [low, high]} |
| `result_key` | str | None |  | Key/attribute to extract scalar from each result |

---
## Simtools Tools

### `generate_rel_perm_table`
Generate relative permeability table for reservoir simulation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `rows` | int | 25 | gt=0, le=100 | Number of table rows |
| `krtable` | Literal['SWOF', 'SGOF', 'SGWFN'] | 'SWOF' |  | Table type (SWOF, SGOF, SGWFN) |
| `krfamily` | Literal['COR', 'LET'] | 'LET' |  | Correlation family (Corey or LET) |
| `kromax` | float | 1.0 | ge=0, le=1 | Max oil rel perm |
| `krwmax` | float | None | ge=0, le=1 | Max water rel perm (SWOF) |
| `krgmax` | float | None | ge=0, le=1 | Max gas rel perm (SGOF/SGWFN) |
| `swc` | float | 0.0 | ge=0, le=1 | Connate water saturation |
| `swcr` | float | None | ge=0, le=1 | Critical water sat (Corey) |
| `sorg` | float | None | ge=0, le=1 | Residual oil to gas |
| `sorw` | float | None | ge=0, le=1 | Residual oil to water |
| `sgc` | float | None | ge=0, le=1 | Critical gas saturation |
| `no` | float | None | gt=0 | Oil Corey exponent |
| `nw` | float | None | gt=0 | Water Corey exponent |
| `ng` | float | None | gt=0 | Gas Corey exponent |
| `Lo` | float | None | gt=0 | Oil L parameter (LET) |
| `Eo` | float | None | gt=0 | Oil E parameter (LET) |
| `To` | float | None | gt=0 | Oil T parameter (LET) |
| `Lw` | float | None | gt=0 | Water L parameter (LET) |
| `Ew` | float | None | gt=0 | Water E parameter (LET) |
| `Tw` | float | None | gt=0 | Water T parameter (LET) |
| `Lg` | float | None | gt=0 | Gas L parameter (LET) |
| `Eg` | float | None | gt=0 | Gas E parameter (LET) |
| `Tg` | float | None | gt=0 | Gas T parameter (LET) |

### `generate_aquifer_influence`
Generate Van Everdingen & Hurst aquifer influence functions.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `start` | float | 0.01 | gt=0 | Starting dimensionless time |
| `end` | float | 1000.0 | gt=0 | Ending dimensionless time |
| `rows` | int | 25 | gt=0, le=200 | Number of table rows |
| `res` | int | 10 | gt=1, le=50 | Resolution for integration |
| `aqunum` | int | 1 | ge=1, le=10 | Aquifer number for ECLIPSE |
| `infl` | Literal['pot', 'press'] | 'pot' |  | Influence function type (pot or press) |
| `ei` | bool | True |  | Use exponential integral |
| `piston` | bool | False |  | Piston-like aquifer |
| `td_scale` | float | None | gt=0 | Time dimension scaling |

### `rachford_rice_flash`
Solve Rachford-Rice equation for vapor-liquid equilibrium.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `zis` | float or List[float] | **required** |  | Overall mole fractions |
| `Kis` | float or List[float] | **required** |  | K-values (yi/xi) |

### `extract_eclipse_problem_cells`
Extract convergence problem cells from ECLIPSE/Intersect PRT file.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `filename` | str | **required** |  | Path to ECLIPSE/Intersect PRT file |
| `silent` | bool | True |  | Suppress console output |

### `validate_simulation_deck`
Validate and process ECLIPSE simulation deck with INCLUDE files.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `files2scrape` | List[str] | **required** |  | List of deck files to process (e.g., [ |
| `tozip` | bool | False |  | Create zip archive of all referenced files |
| `console_summary` | bool | True |  | Print summary to console |

### `generate_black_oil_table_og`
Generate oil-gas black oil PVT tables (PVTO/PVDO + PVDG).

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pi` | float | **required** | gt=0 | Initial pressure (psia | barsa) |
| `api` | float | **required** | gt=0, le=100 | Oil API gravity |
| `degf` | float | **required** |  | Temperature (deg F | deg C) |
| `sg_g` | float | **required** | gt=0, le=3 | Gas specific gravity |
| `pmax` | float | **required** | gt=0 | Maximum pressure (psia | barsa) |
| `pb` | float | 0.0 | ge=0 | Bubble point (0 = calculate) |
| `rsb` | float | 0.0 | ge=0 | Solution GOR at Pb |
| `pmin` | float | 25.0 | gt=0 | Minimum pressure |
| `nrows` | int | 20 | gt=0, le=200 | Number of rows |
| `wt` | float | 0.0 | ge=0, le=30 | Brine salinity (wt%) |
| `ch4_sat` | float | 0.0 | ge=0, le=1 | Methane saturation (0-1) |
| `export` | bool | False |  | Write PVTO/PVDG/PVDO files |
| `pvto` | bool | False |  | Generate PVTO format (vs PVDO) |
| `vis_frac` | float | 1.0 | gt=0 | Viscosity scaling factor |
| `metric` | bool | False |  | Use metric units |

### `generate_pvtw_table`
Generate PVTW water PVT table for reservoir simulation.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `pi` | float | **required** | gt=0 | Reference pressure (psia | barsa) |
| `degf` | float | **required** |  | Temperature (deg F | deg C) |
| `wt` | float | 0.0 | ge=0, le=30 | Salt wt% (0-100) |
| `ch4_sat` | float | 0.0 | ge=0, le=1 | Methane saturation (0-1) |
| `pmin` | float | 500.0 | gt=0 | Minimum pressure |
| `pmax` | float | 10000.0 | gt=0 | Maximum pressure |
| `nrows` | int | 20 | gt=0, le=200 | Number of rows |
| `export` | bool | False |  | Write PVTW.INC file |
| `metric` | bool | False |  | Use metric units |

### `fit_relative_permeability`
Fit relative permeability curve to measured data.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sw` | float or List[float] | **required** |  | Saturation values |
| `kr` | float or List[float] | **required** |  | Measured relative permeability values |
| `krfamily` | Literal['COR', 'LET', 'JER'] | 'COR' |  | Model: COR (Corey), LET, JER (Jerauld) |
| `krmax` | float | 1.0 | gt=0, le=1 | Maximum kr endpoint |
| `sw_min` | float | 0.0 | ge=0, le=1 | Minimum saturation endpoint |
| `sw_max` | float | 1.0 | ge=0, le=1 | Maximum saturation endpoint |

### `fit_relative_permeability_best`
Find best-fit relative permeability model from all available families.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `sw` | float or List[float] | **required** |  | Saturation values |
| `kr` | float or List[float] | **required** |  | Measured relative permeability values |
| `krmax` | float | 1.0 | gt=0, le=1 | Maximum kr endpoint |
| `sw_min` | float | 0.0 | ge=0, le=1 | Minimum saturation endpoint |
| `sw_max` | float | 1.0 | ge=0, le=1 | Maximum saturation endpoint |

### `evaluate_jerauld`
Evaluate Jerauld relative permeability model.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `s` | float or List[float] | **required** |  | Normalized saturation values (0-1) |
| `a` | float | **required** |  | Jerauld  |
| `b` | float | **required** |  | Jerauld  |

### `check_let_physical`
Check if LET parameters produce physically valid relative permeability.

| Parameter | Type | Default | Constraint | Description |
|-----------|------|---------|------------|-------------|
| `s` | float or List[float] | **required** |  | Normalized saturation values (0-1) |
| `L` | float | **required** | gt=0 | LET L parameter |
| `E` | float | **required** | gt=0 | LET E parameter |
| `T` | float | **required** | gt=0 | LET T parameter |
