---
name: pyrestoolbox-mcp
description: >
  Skill for using the pyResToolbox MCP Server — a 108-tool reservoir engineering
  calculation suite exposed via the Model Context Protocol. Use this skill whenever
  the user asks about petroleum engineering calculations, PVT analysis, well
  performance, inflow performance relationships (IPR), reservoir simulation input
  generation, decline curve analysis (DCA), material balance, geomechanics,
  wellbore stability, brine/CO2 properties, relative permeability, nodal analysis,
  or any reservoir engineering workflow. Also trigger when the user mentions
  pyResToolbox, pyrestoolbox-mcp, bubble point, Z-factor, GOR, formation volume
  factor, oil viscosity, gas properties, SWOF/SGOF tables, aquifer influence,
  black oil tables, Corey/LET curves, Arps decline, P/Z plots, Havlena-Odeh,
  fracture gradient, mud weight window, or ECLIPSE simulation keywords. This skill
  covers both individual calculations and multi-step reservoir engineering workflows.
---

# pyResToolbox MCP Server — Agent Usage Guide

This skill teaches you how to effectively use the **pyResToolbox MCP Server**, which
provides 108 production-ready reservoir engineering tools via the Model Context Protocol.

The server wraps the [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox) Python
library by Mark Burgoyne and is served through
[FastMCP](https://github.com/jlowin/fastmcp).

**Repository:** https://github.com/gabrielserrao/pyrestoolbox-mcp

---

## CRITICAL: Parameter Naming Conventions

Different tool families use different parameter names for similar concepts. Getting
these wrong will cause validation errors. Pay close attention:

### Pressure parameter names
- Oil PVT tools: `p` (pressure array/scalar)
- Gas PVT tools: `p` (pressure array/scalar)
- Inflow tools: `psd` (sandface pressure) — **NOT `pwf` or `p`**
- Nodal tools: `pr` (reservoir pressure inside ReservoirModel), `thp` (tubing head)
- Geomech tools: `pore_pressure`, `vertical_stress`, etc.

### Gas specific gravity parameter names
- Oil tools: `sg_g` (gas specific gravity)
- Gas tools: `sg` (gas specific gravity) — **NOT `sg_g` or `sg_gas`**
- Inflow gas tools: `sg` — same as gas tools
- Nodal tools: `gas_sg`

### Method parameter names
- `gas_z_factor`: parameter is `method` → "DAK", "HY", "WYW", "BUR"
- `gas_formation_volume_factor`, `gas_viscosity`, `gas_density`, `gas_compressibility`:
  parameter is `zmethod` → "DAK", "HY", "WYW", "BUR" — **NOT `method`**
- `gas_critical_properties`: parameter is `method` → "PMC", "SUT", "BUR", "BNS"
- `gas_delta_pseudopressure`, `create_gas_pvt`: uses BOTH `zmethod` AND `cmethod`
- Oil tools: parameter is `method`
- Nodal tools: parameter is `vlp_method` → "HB", "WG", "GRAY", "BB"
- Fracture gradient: parameter is `method` → "hubbert_willis", "eaton", "matthews_kelly"

### Temperature parameter name
- Most tools: `degf` (degrees Fahrenheit in field units)
- Nodal ReservoirModel: `degf`
- Nodal CompletionModel: `wellhead_temp` and `bht`
- Matbal tools: `temperature`

---

## Unit Systems

Every tool accepts a `metric` boolean parameter. Default is `False` (field units).

| System   | Pressure | Temperature | Length | Rate (oil)   | Rate (gas)     | GOR        |
|----------|----------|-------------|--------|--------------|----------------|------------|
| Field    | psia     | °F          | ft     | STB/day      | MSCF/day       | scf/stb    |
| Metric   | barsa    | °C          | m      | sm³/day      | sm³/day        | sm³/sm³    |

Set `metric: true` when the user provides metric values. Always state units in output.

---

## Valid Method Codes — Complete Reference

These are the EXACT string values accepted by each Literal type. Using any other
value will cause a Pydantic validation error.

### Bubble Point / Solution GOR methods
| Code     | Method                        | Used in                              |
|----------|-------------------------------|--------------------------------------|
| `"STAN"` | Standing (1947)               | oil_bubble_point, oil_solution_gor   |
| `"VALMC"`| Valko & McCain (2003)         | oil_bubble_point, oil_solution_gor   |
| `"VELAR"`| Velarde (1997)                | oil_bubble_point, oil_solution_gor   |

Default for bubble point: `"VALMC"`. Default for solution GOR: `"VELAR"`.

### Oil FVF methods
| Code      | Method                       | Used in                    |
|-----------|------------------------------|----------------------------|
| `"MCAIN"` | McCain et al. (1988)         | oil_formation_volume_factor|
| `"STAN"`  | Standing (1947)              | oil_formation_volume_factor|

Default: `"MCAIN"`. Note the spelling is `MCAIN` not `MCCAIN`.

### Oil Viscosity methods
| Code   | Method                        | Used in       |
|--------|-------------------------------|---------------|
| `"BR"` | Beggs & Robinson (1975)       | oil_viscosity |

Only `"BR"` is available. No alternatives.

### Z-factor methods (parameter name varies — see above)
| Code    | Method                                     | Used in              |
|---------|--------------------------------------------|----------------------|
| `"DAK"` | Dranchuk & Abou-Kassem (1975)              | All gas tools        |
| `"HY"`  | Hall & Yarborough (1973)                   | All gas tools        |
| `"WYW"` | Wang, Ye & Wu (2021)                       | All gas tools        |
| `"BUR"` | Burgoyne/Nielsen/Stanko EOS (2025, SPE-229932) | All gas tools   |

Default: `"DAK"`. Use `"BUR"` for hydrogen-containing or unusual gas mixtures.

### Critical Properties methods
| Code    | Method                                     | Used in                     |
|---------|--------------------------------------------|-----------------------------|
| `"PMC"` | Piper, McCain & Corredor (1993)            | gas_critical_properties     |
| `"SUT"` | Sutton (1985)                              | gas_critical_properties     |
| `"BUR"` | Burgoyne/Nielsen/Stanko (2025)             | gas_critical_properties     |
| `"BNS"` | Same as BUR (alternate name)               | gas_critical_properties     |

Default: `"PMC"`. Note: matbal tools accept `"PMC"`, `"SUT"`, `"BUR"` only (no `"BNS"`).

### VLP correlations (parameter: `vlp_method`)
| Code     | Method                        | Best for                    |
|----------|-------------------------------|-----------------------------|
| `"WG"`   | Woldesemayat-Ghajar           | General (recommended)       |
| `"HB"`   | Hagedorn-Brown (1965)         | Vertical oil wells          |
| `"GRAY"` | Gray (1978)                   | Gas wells with condensate   |
| `"BB"`   | Beggs & Brill (1973)          | General purpose, deviated   |

Default: `"WG"`.

### Relative Permeability families
| Code    | Method                        | Table Generation | Curve Fitting |
|---------|-------------------------------|------------------|---------------|
| `"COR"` | Corey (1954)                  | YES              | YES           |
| `"LET"` | Lomeland, Ebeltoft & Thomas   | YES              | YES           |
| `"JER"` | Jerauld (2006)                | **NO**           | YES           |

**IMPORTANT**: `"JER"` is only valid for `fit_relative_permeability`, NOT for
`generate_rel_perm_table`. Using `"JER"` for table generation will fail.

### Rel perm table types (parameter: `krtable`)
| Code      | Description              |
|-----------|--------------------------|
| `"SWOF"`  | Water-oil table          |
| `"SGOF"`  | Gas-oil table            |
| `"SGWFN"` | Gas-water function table |

### Decline Curve methods
| Code             | Method                        | When to use                    |
|------------------|-------------------------------|--------------------------------|
| `"exponential"`  | Exponential decline           | Boundary-dominated flow        |
| `"harmonic"`     | Harmonic decline              | b=1 case                       |
| `"hyperbolic"`   | Hyperbolic decline            | General Arps (0<b<2)           |
| `"duong"`        | Duong (2011)                  | Tight/shale/unconventional     |
| `"best"`         | Auto-select (highest R²)     | Let the tool pick              |

**Note**: For `fit_decline_cumulative`, `"duong"` is NOT available.

### Ratio analysis methods
| Code            | Method                         |
|-----------------|--------------------------------|
| `"linear"`      | Linear model                   |
| `"exponential"` | Exponential model              |
| `"power"`       | Power model                    |
| `"logistic"`    | Logistic model                 |
| `"best"`        | Auto-select (fitting only)     |

### Geomech-specific Literal values

**Fracture gradient method**: `"hubbert_willis"`, `"eaton"`, `"matthews_kelly"`
**Fracture width model**: `"PKN"`, `"KGD"`
**Pore pressure method**: `"sonic"`, `"resistivity"`
**Dynamic-to-static correlation**: `"eissa_kazi"`, `"plona_cook"`, `"linear"`
**Lithology**: `"sandstone"`, `"shale"`, `"carbonate"` (some tools add `"general"`)
**UCS correlation**: `"mcnally"`, `"horsrud"`, `"chang"`, `"lal"`, `"vernik"`
**Shear failure criteria**: `"mohr_coulomb"`, `"drucker_prager"`, `"mogi_coulomb"`,
  `"modified_lade"`, `"modified_wiebols"`
**Leak-off test type**: `"LOT"`, `"FIT"`

### Component library EOS
| Code     | Method              |
|----------|---------------------|
| `"PR79"` | Peng-Robinson 1979  |
| `"PR77"` | Peng-Robinson 1977  |
| `"SRK"`  | Soave-Redlich-Kwong |
| `"RK"`   | Redlich-Kwong       |

Default: `"PR79"`.

### Sensitivity analysis valid modules
`"gas"`, `"oil"`, `"brine"`, `"simtools"`, `"layer"`, `"library"`, `"nodal"`,
`"matbal"`, `"dca"`

---

## Parameter Validation Constraints

These are enforced by Pydantic and will cause errors if violated.

### Oil parameters
| Parameter | Constraint             |
|-----------|------------------------|
| `api`     | gt=0, le=100           |
| `degf`    | gt=-460, lt=1000       |
| `sg_g`    | ge=0, le=3             |
| `rsb`     | ge=0                   |
| `p`       | must be > 0 (validated)|
| `rs`      | must be >= 0           |
| `bo`      | must be > 0            |
| `nrows`   | gt=0, le=200           |

### Gas parameters
| Parameter | Constraint             |
|-----------|------------------------|
| `sg`      | ge=0.5, le=2.0         |
| `degf`    | gt=-460, lt=1000       |
| `p`       | must be > 0            |
| `h2s`     | ge=0.0, le=1.0         |
| `co2`     | ge=0.0, le=1.0         |
| `n2`      | ge=0.0, le=1.0         |
| `h2`      | ge=0.0, le=1.0         |

### Inflow parameters
| Parameter | Constraint                   |
|-----------|------------------------------|
| `pi`      | gt=0                         |
| `pb`      | ge=0                         |
| `psd`     | must be > 0                  |
| `h`       | gt=0                         |
| `k`       | gt=0                         |
| `re`      | gt=0                         |
| `rw`      | gt=0, must be < re           |
| `s`       | any float (default 0.0)      |

### Geomech parameters
| Parameter            | Constraint                    |
|----------------------|-------------------------------|
| `poisson_ratio`      | gt=0, lt=0.5                  |
| `friction_angle`     | gt=0, lt=90                   |
| `biot_coefficient`   | gt=0, le=1                    |
| `porosity`           | gt=0, lt=1                    |
| `wellbore_azimuth`   | ge=0, le=360                  |
| `wellbore_inclination`| ge=0, le=90                  |
| `tectonic_factor`    | ge=0, le=1                    |

### Rel perm parameters
| Parameter    | Constraint     |
|--------------|----------------|
| `kromax`     | ge=0, le=1     |
| `krwmax`     | ge=0, le=1     |
| `krgmax`     | ge=0, le=1     |
| `swc`        | ge=0, le=1     |
| `sorw`       | ge=0, le=1     |
| `no`, `nw`   | gt=0           |
| `Lo`,`Eo`,`To`| gt=0          |

### Rachford-Rice
| Parameter | Constraint                              |
|-----------|-----------------------------------------|
| `zis`     | min 2 elements, all >= 0, sum ≈ 1.0    |
| `Kis`     | min 2 elements, all >= 0                |

### DCA parameters
| Parameter | Constraint     |
|-----------|----------------|
| `qi`      | gt=0           |
| `di`      | gt=0 (Arps), ge=0 (forecast) |
| `b`       | ge=0, le=2     |
| `m`       | gt=1 (Duong)   |
| `a`       | gt=0 (Duong)   |

---

## Nodal Analysis — Nested Object Structure

Nodal tools require nested Pydantic objects. You MUST pass them as nested dicts:

### CompletionModel (required by most nodal tools)
```json
{
  "tubing_id": 2.992,
  "tubing_length": 10000.0,
  "wellhead_temp": 80.0,
  "bht": 200.0,
  "roughness": 0.0006,
  "casing_id": 0.0,
  "metric": false
}
```

### ReservoirModel (required by ipr_curve, operating_point)
```json
{
  "pr": 4000.0,
  "degf": 180.0,
  "k": 100.0,
  "h": 50.0,
  "re": 1500.0,
  "rw": 0.354,
  "S": 0.0,
  "D": 0.0,
  "metric": false
}
```

### Multi-segment completion (optional, overrides tubing_id/length)
```json
{
  "segments": [
    {"md": 5000.0, "id": 4.5, "deviation": 0.0},
    {"md": 10000.0, "id": 2.992, "deviation": 30.0}
  ],
  "wellhead_temp": 80.0,
  "bht": 200.0
}
```

---

## Tool Categories & Exact Call Signatures

### 1. Oil PVT Properties

| Tool | Required Parameters | Optional (with defaults) |
|------|-------------------|--------------------------|
| `oil_bubble_point` | api, degf, rsb | sg_g=0.0, method="VALMC", metric=false |
| `oil_solution_gor` | api, degf, p | sg_g=0.0, pb=0.0, rsb=0.0, method="VELAR", metric=false |
| `oil_formation_volume_factor` | api, degf, p | sg_g=0.0, pb=0.0, rs=0.0, rsb=0.0, method="MCAIN", metric=false |
| `oil_viscosity` | api, degf, p | pb=0.0, rs=0.0, rsb=0.0, method="BR", metric=false |
| `oil_density` | p, api, degf, rs, sg_g, bo | metric=false |
| `oil_compressibility` | p, api, degf, pb, sg_g, rs | rsb=0.0, metric=false |
| `oil_api_from_sg` | sg (oil specific gravity) | — |
| `oil_sg_from_api` | api | — |
| `generate_black_oil_table` | pi, api, degf, sg_g | pmax=0.0, pb=0.0, rsb=0.0, nrows=50, export=false, pb_method="VALMC", rs_method="VELAR", bo_method="MCAIN", uo_method="BR", metric=false |
| `create_oil_pvt` | api, sg_sp, pb, temperature, pressures[] | rsb=0.0, sg_g=0.0, uo_target=0.0, p_uo=0.0, rs_method="VELAR", pb_method="VALMC", bo_method="MCAIN", metric=false |

**Additional oil tools**: `oil_rs_at_bubble_point`, `evolved_gas_sg`, `stock_tank_gas_sg`,
`oil_sg_from_jacoby`, `oil_twu_critical_properties`, `weighted_average_gas_sg`,
`stock_tank_incremental_gor`, `validate_gas_gravities`, `oil_harmonize_pvt`

### 2. Gas PVT Properties

| Tool | Required Parameters | Optional (with defaults) |
|------|-------------------|--------------------------|
| `gas_z_factor` | sg, degf, p | h2s=0.0, co2=0.0, n2=0.0, h2=0.0, **method**="DAK", metric=false |
| `gas_critical_properties` | sg | h2s=0.0, co2=0.0, n2=0.0, h2=0.0, **method**="PMC", metric=false |
| `gas_formation_volume_factor` | sg, degf, p | h2s/co2/n2/h2=0.0, **zmethod**="DAK", metric=false |
| `gas_viscosity` | sg, degf, p | h2s/co2/n2/h2=0.0, **zmethod**="DAK", metric=false |
| `gas_density` | sg, degf, p | h2s/co2/n2/h2=0.0, **zmethod**="DAK", metric=false |
| `gas_compressibility` | sg, degf, p | h2s/co2/n2/h2=0.0, **zmethod**="DAK", metric=false |
| `gas_pseudopressure` | sg, degf, p1, p2 | h2s/co2/n2/h2=0.0, **zmethod**="DAK", metric=false |
| `gas_pressure_from_pz` | pz, sg, degf | h2s/co2/n2/h2=0.0, **zmethod**="DAK", metric=false |
| `gas_water_content` | p, degf | metric=false |
| `gas_sg_from_composition` | hc_mw | co2=0.0, h2s=0.0, n2=0.0, h2=0.0, metric=false |
| `gas_hydrate_prediction` | p, degf, sg | method="TOWLER", inhibitor_type=null, inhibitor_wt_pct=0.0, co2/h2s/n2/h2=0.0, p_res=null, degf_res=null, metric=false |
| `gas_sg_from_gradient` | grad, degf, p | metric=false |
| `gas_fws_sg` | sg_g, cgr, api_st | metric=false |
| `gas_delta_pseudopressure` | p1, p2, degf, sg | h2s/co2/n2/h2=0.0, **zmethod**="DAK", **cmethod**="PMC", metric=false |
| `create_gas_pvt` | pressures[], temperature | sg=0.75, co2/h2s/n2/h2=0.0, **zmethod**="DAK", **cmethod**="PMC", metric=false |

**WARNING**: `gas_z_factor` uses `method` but other gas tools use `zmethod`. This is a
common source of errors!

### 3. Well Performance & Inflow (uses `psd` for sandface pressure)

| Tool | Required Parameters | Optional (with defaults) |
|------|-------------------|--------------------------|
| `oil_rate_radial` | pi, pb, api, degf, sg_g, **psd**, h, k, re, rw | s=0.0, rsb=0.0, vogel=false |
| `oil_rate_linear` | pi, pb, api, degf, sg_g, **psd**, h, k, area, length | rsb=0.0 |
| `gas_rate_radial` | pi, **sg**, degf, **psd**, h, k, re, rw | s=0.0, h2s=0.0, co2=0.0, n2=0.0 |
| `gas_rate_linear` | pi, **sg**, degf, **psd**, h, k, area, length | h2s=0.0, co2=0.0, n2=0.0 |

**CRITICAL**: Parameter is `psd` (sandface pressure), NOT `pwf`. Using `pwf` will fail.
The `rw` (wellbore radius) must be less than `re` (drainage radius) or validation fails.

### 4. Nodal Analysis (requires nested objects)

| Tool | Required Parameters |
|------|-------------------|
| `flowing_bhp` | thp, completion:{...}, vlp_method, well_type, + rate params |
| `ipr_curve` | reservoir:{...}, well_type | 
| `outflow_curve` | thp, completion:{...}, vlp_method, well_type |
| `operating_point` | thp, completion:{...}, reservoir:{...}, vlp_method, well_type |
| `generate_vfp_prod_table` | table_num, completion:{...}, well_type, vlp_method |
| `generate_vfp_inj_table` | table_num, completion:{...}, flo_type |

**`well_type`**: `"gas"`, `"oil"` (for most), or `"gas"`, `"oil"`, `"water"` (for ipr_curve)
**`flo_type`** (VFP injection only): `"WAT"`, `"GAS"`, `"OIL"`

### 5. Simulation Support

| Tool | Required Parameters | Key Options |
|------|-------------------|-------------|
| `generate_rel_perm_table` | (all optional with defaults) | krtable="SWOF"/"SGOF"/"SGWFN", krfamily="COR"/"LET" only |
| `fit_relative_permeability` | sw[], kr[] | krfamily="COR"/"LET"/"JER" |
| `fit_relative_permeability_best` | sw[], kr[] | Auto-selects best model |
| `generate_aquifer_influence` | (all optional) | start=0.01, end=1000, rows=25, res=10, infl="pot"/"press" |
| `rachford_rice_flash` | zis[], Kis[] | zis must sum to ~1.0 |
| `generate_black_oil_table_og` | pi, api, degf, sg_g, pmax | Various optional params |
| `generate_pvtw_table` | pi, degf | wt=0.0, ch4_sat=0.0, pmin=500, pmax=10000, nrows=20 |
| `extract_eclipse_problem_cells` | filename | silent=true |
| `validate_simulation_deck` | files2scrape[] | tozip=false, console_summary=true |
| `evaluate_jerauld` | s[], a, b | — |
| `check_let_physical` | s[], L, E, T | All L,E,T must be > 0 |

### 6. Decline Curve Analysis

| Tool | Required Parameters | Key Options |
|------|-------------------|-------------|
| `fit_decline` | time[], rates[] | method="best" (default), t_start, t_end |
| `fit_decline_cumulative` | cumulative_production[], rates[] | method="best", NO duong option |
| `decline_forecast` | qi, t_end | di=0.0, b=0.0, method="hyperbolic", dt=1.0, q_min=0.0, uptime=1.0, a/m for Duong |
| `arps_rate` | qi, di, b, t | — |
| `arps_cumulative` | qi, di, b, t | — |
| `estimated_ultimate_recovery` | qi, di, b, q_min | — |
| `duong_rate` | qi, a, m, t | m must be > 1 |
| `fit_ratio` | x[], ratio[] | method="best", domain="cum"/"time" |
| `ratio_forecast` | method, a, b, x | c=0.0 (logistic), domain="cum"/"time" |

### 7. Material Balance

| Tool | Required Parameters | Key Options |
|------|-------------------|-------------|
| `gas_material_balance` | pressures[], cumulative_gas[], temperature | gas_sg=0.65, z_method="DAK", c_method="PMC" (NO "BNS") |
| `oil_material_balance` | pressures[], cumulative_oil[], temperature | api, sg_sp, pb, rsb, rs_method="VELAR", bo_method="MCAIN", z_method="DAK", c_method="PMC" |

**NOTE**: Matbal uses `z_method` and `c_method` (with underscore), NOT `zmethod`/`cmethod`.

### 8. Brine & CO₂ Properties

| Tool | Required Parameters | Key Options |
|------|-------------------|-------------|
| `calculate_brine_properties` | p, degf, wt (wt% NaCl, 0-30) | ch4=0.0, co2=0.0, metric=false |
| `co2_brine_mutual_solubility` | pres, temp, ppm | metric=false, cw_sat=0.0 |
| `soreide_whitson_vle` | pres, temp | ppm=0.0, y_CO2/y_H2S/y_N2/y_H2=0.0, sg=0.65, metric=false |

**Note**: Brine salinity uses `wt` (weight percent) in `calculate_brine_properties` but
`ppm` in the other two tools. Don't mix them up.

### 9. Reservoir Heterogeneity

| Tool | Required Parameters |
|------|-------------------|
| `lorenz_to_beta` | value (float, 0-1) |
| `beta_to_lorenz` | value (float, 0-1) |
| `lorenz_from_flow_fractions` | flow_frac[], perm_frac[] (must sum to ~1.0) |
| `flow_fractions_from_lorenz` | flow_frac[], perm_frac[] (must sum to ~1.0) |
| `generate_layer_distribution` | lorenz (0-1), nlay (int) | h=1.0, k_avg=1.0, normalize=true |

### 10. Geomechanics (27 tools)

Read **references/tools-reference.md** for complete parameter details. Key tools:

| Tool | Key Required Params | Key Literal Values |
|------|--------------------|--------------------|
| `geomech_vertical_stress` | depth | avg_density=144.0 |
| `geomech_pore_pressure_eaton` | depth, observed_value, normal_value, overburden_psi | method="sonic"/"resistivity" |
| `geomech_horizontal_stress` | vertical_stress, pore_pressure, poisson_ratio | tectonic_factor=0.0 |
| `geomech_fracture_gradient` | depth, vertical_stress, pore_pressure | method="hubbert_willis"/"eaton"/"matthews_kelly" |
| `geomech_safe_mud_weight_window` | pore_pressure, fracture_pressure, depth | safety margins |
| `geomech_breakdown_pressure` | sigma_h_max, sigma_h_min, pore_pressure | tensile_strength=0.0 |
| `geomech_hydraulic_fracture_width` | net_pressure, fracture_height, fracture_half_length, youngs_modulus, poisson_ratio | model="PKN"/"KGD" |
| `geomech_ucs_from_logs` | (one of: sonic_dt, porosity, youngs_modulus) | lithology="sandstone"/"shale"/"carbonate"/"general", correlation="mcnally"/"horsrud"/"chang"/"lal"/"vernik" |
| `geomech_shear_failure_criteria` | sigma_1, sigma_2, sigma_3, ucs, cohesion, friction_angle | criteria=["mohr_coulomb","drucker_prager","mogi_coulomb","modified_lade","modified_wiebols"] |
| `geomech_dynamic_to_static_moduli` | dynamic_youngs or dynamic_poisson | correlation="eissa_kazi"/"plona_cook"/"linear", lithology="sandstone"/"shale"/"carbonate" |

### 11. Utility Tools

| Tool | Required Parameters |
|------|-------------------|
| `get_component_properties` | component (string, e.g. "Methane", "C1", "CO2") | eos="PR79"/"PR77"/"SRK"/"RK" |
| `recommend_methods` | (all optional) | gas_sg, co2, h2s, n2, h2, api, deviation, well_type="gas"/"oil" |
| `recommend_gas_methods` | (all optional) | gas_sg=0.65, co2, h2s, n2, h2 |
| `recommend_oil_methods` | (all optional) | api=35.0 |
| `recommend_vlp_method` | (all optional) | deviation=0.0, well_type="gas"/"oil" |
| `parameter_sweep` | function_module, function_name, base_parameters, vary_parameter, vary_values[] |
| `tornado_sensitivity` | function_module, function_name, base_parameters, ranges:{param: [low, high]} |

---

## Common Workflows

### Workflow 1: Complete Oil PVT Analysis

1. `oil_bubble_point` → get Pb (pass api, degf, rsb, sg_g)
2. `oil_solution_gor` at multiple pressures → Rs profile
3. `oil_formation_volume_factor` → Bo
4. `oil_viscosity` → μo
5. `oil_density` → ρo (requires rs, sg_g, bo as inputs)
6. Or use `generate_black_oil_table` with pi, api, degf, sg_g to get everything at once

### Workflow 2: Well Performance Study

1. `oil_bubble_point` → determine Pb
2. `oil_rate_radial` at several `psd` values → build IPR
3. Or use `ipr_curve` from nodal module (requires nested reservoir object)
4. `outflow_curve` → VLP curve (requires nested completion object)
5. `operating_point` → intersection of IPR and VLP

### Workflow 3: Simulation Input Generation

1. `generate_rel_perm_table` with COR or LET → SWOF/SGOF tables
2. `generate_black_oil_table` or `generate_black_oil_table_og` → PVTO/PVDG
3. `generate_pvtw_table` → PVTW keyword
4. `generate_aquifer_influence` → AQUTAB
5. `generate_vfp_prod_table` / `generate_vfp_inj_table` → VFP tables

### Workflow 4: Gas Reservoir Evaluation

1. `gas_critical_properties` → Tc, Pc (with contaminants h2s, co2, n2, h2)
2. `gas_z_factor` at multiple pressures → Z-factor profile (param: `method`)
3. `gas_rate_radial` → deliverability (param: `psd` for sandface pressure, `sg` for gas gravity)
4. `gas_material_balance` → OGIP from P/Z data (param: `z_method`, `c_method`)

### Workflow 5: Geomechanics / Drilling

1. `geomech_vertical_stress` → overburden
2. `geomech_pore_pressure_eaton` → pore pressure
3. `geomech_horizontal_stress` → min/max horizontal stress
4. `geomech_safe_mud_weight_window` → safe drilling window
5. `geomech_fracture_gradient` → fracture initiation pressure

### Workflow 6: CO₂ Sequestration Screening

1. `calculate_brine_properties` → formation brine baseline (salinity in wt%)
2. `co2_brine_mutual_solubility` → CO₂ solubility (salinity in ppm)
3. `soreide_whitson_vle` → multi-gas phase equilibrium

---

## Best Practices for Error-Free Calls

1. **Check parameter names against this document.** The #1 source of errors is using
   wrong parameter names (`pwf` vs `psd`, `method` vs `zmethod`, `sg` vs `sg_g`).

2. **Check enum values are exact strings.** Must be EXACT: `"VALMC"` not `"ValMC"`,
   `"DAK"` not `"dak"`, `"SWOF"` not `"swof"`.

3. **Verify numeric constraints.** API must be 0-100, gas SG must be 0.5-2.0,
   Poisson's ratio must be 0-0.5 (exclusive), friction angle 0-90 (exclusive).

4. **Arrays must be valid.** Pressures > 0, compositions sum to ~1.0 for Rachford-Rice,
   flow/perm fractions sum to ~1.0 for layer tools.

5. **Use arrays for sweeps.** Many tools accept arrays for pressure. Use this instead
   of calling the tool multiple times.

6. **Compare correlations.** Call the same tool with different method values and present
   the comparison as a table.

7. **Chain tools for workflows.** Use output of one tool as input to the next.

8. **Use recommend tools first.** Call `recommend_oil_methods`, `recommend_gas_methods`,
   or `recommend_vlp_method` if unsure which correlation to use.

9. **Present results clearly.** Format as tables with units in headers. Round pressure
   to 1 decimal, Bo to 4 decimals, viscosity to 2 decimals, Z-factor to 4 decimals.

---

## Error Handling

Common errors and fixes:

| Error | Cause | Fix |
|-------|-------|-----|
| `Unknown parameter 'pwf'` | Wrong parameter name | Use `psd` for inflow tools |
| `Unknown parameter 'method'` | Wrong method param name | Use `zmethod` for gas Bg/μg/ρg/cg |
| `Input should be 'DAK', 'HY', 'WYW' or 'BUR'` | Wrong Literal value | Check exact string in method table above |
| `Gas specific gravity must be >= 0.5` | sg out of range | Ensure 0.5 ≤ sg ≤ 2.0 |
| `Wellbore radius must be < drainage radius` | rw >= re | Make rw < re |
| `Mole fractions must sum to 1.0` | Composition doesn't sum | Ensure zis sums to ~1.0 |
| `All pressure values must be positive` | Negative/zero pressure | Ensure all pressures > 0 |
| `krfamily 'JER' not valid` | JER used for table generation | Only use COR or LET for generate_rel_perm_table |

---

## References

For the complete parameter reference of all 108 tools, read:
- `references/tools-reference.md` — Full tool signatures with every parameter, type, constraint, and default
