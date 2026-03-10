# pyResToolbox MCP — Required Updates

**Current MCP version:** Built on `pyrestoolbox>=2.1.4` (72 tools)
**Latest upstream release:** `pyrestoolbox==3.0.4` (March 9, 2026)

This document details every change needed to bring the MCP server to parity with pyResToolbox v3.0.4.

---

## Table of Contents

1. [Dependency Update](#1-dependency-update)
2. [New Module: `dca` — Decline Curve Analysis](#2-new-module-dca--decline-curve-analysis)
3. [New Module: `matbal` — Material Balance](#3-new-module-matbal--material-balance)
4. [New Module: `nodal` — Nodal Analysis / VLP / IPR](#4-new-module-nodal--nodal-analysis--vlp--ipr)
5. [New Module: `recommend` — Method Selection Engine](#5-new-module-recommend--method-selection-engine)
6. [New Module: `sensitivity` — Sensitivity Analysis](#6-new-module-sensitivity--sensitivity-analysis)
7. [New Gas Functions](#7-new-gas-functions)
8. [New Oil Functions](#8-new-oil-functions)
9. [New Simtools Functions](#9-new-simtools-functions)
10. [New Brine Functions](#10-new-brine-functions)
11. [Metric Unit Support](#11-metric-unit-support)
12. [Summary](#12-summary)

---

## 1. Dependency Update

**File:** `pyproject.toml`

```python
# BEFORE
dependencies = [
    "pyrestoolbox>=2.1.4",
    ...
]

# AFTER
dependencies = [
    "pyrestoolbox>=3.0.4",
    ...
]
```

---

## 2. New Module: `dca` — Decline Curve Analysis

**Priority:** HIGH
**New files needed:**
- `src/pyrestoolbox_mcp/tools/dca_tools.py`
- `src/pyrestoolbox_mcp/models/dca_models.py`
- `tests/test_dca_tools.py`

### 2.1 `fit_decline` — Fit decline model to production rate vs time

```python
import pyrestoolbox as rtb

# Signature
rtb.dca.fit_decline(
    t,                    # array-like: Time array
    q,                    # array-like: Rate array (must be > 0)
    method='best',        # str: 'exponential', 'harmonic', 'hyperbolic', 'duong', or 'best'
    t_start=None,         # float: Start of fitting window (inclusive)
    t_end=None            # float: End of fitting window (inclusive)
) -> DeclineResult

# Returns DeclineResult with attributes:
#   .method (str): 'exponential', 'harmonic', 'hyperbolic', or 'duong'
#   .qi (float): Initial rate
#   .di (float): Initial decline rate (1/time) — not used for Duong
#   .b (float): Arps b-factor (0=exp, 0<b<1=hyp, 1=harmonic)
#   .a (float): Duong 'a' parameter (Duong only)
#   .m (float): Duong 'm' parameter (Duong only)
#   .r_squared (float): Goodness of fit
#   .uptime_history (array): Historical uptime fractions
#   .uptime_mean (float): Mean uptime fraction

# Example usage
import numpy as np
t = np.array([1, 2, 3, 6, 12, 18, 24, 36])
q = np.array([1000, 800, 650, 400, 200, 130, 90, 50])

result = rtb.dca.fit_decline(t, q, method='best')
print(f"Best model: {result.method}, qi={result.qi:.0f}, R²={result.r_squared:.4f}")
```

**MCP tool design:**
```python
@mcp.tool()
async def fit_decline(
    time: list[float],
    rates: list[float],
    method: str = "best",
    t_start: float | None = None,
    t_end: float | None = None,
) -> dict:
    """Fit a decline curve model to production rate vs time data.

    Supports Arps (exponential, harmonic, hyperbolic) and Duong models.
    'best' tries all four and returns the highest R-squared fit.

    Args:
        time: Time values (months or years — user-defined units)
        rates: Production rate values (must be > 0)
        method: 'exponential', 'harmonic', 'hyperbolic', 'duong', or 'best'
        t_start: Optional start of fitting window
        t_end: Optional end of fitting window

    Returns:
        Dictionary with model type, fitted parameters (qi, di, b or a, m),
        R-squared, and uptime statistics.
    """
    result = rtb.dca.fit_decline(time, rates, method=method, t_start=t_start, t_end=t_end)
    return {
        "method": result.method,
        "qi": result.qi,
        "di": result.di,
        "b": result.b,
        "a": result.a,
        "m": result.m,
        "r_squared": result.r_squared,
    }
```

### 2.2 `fit_decline_cum` — Fit decline model to rate vs cumulative production

```python
rtb.dca.fit_decline_cum(
    Np,                   # array-like: Cumulative production array
    q,                    # array-like: Rate array (must be > 0)
    method='best',        # str: 'exponential', 'harmonic', 'hyperbolic', or 'best'
    t_calendar=None,      # array-like: Optional calendar time for uptime calc
    Np_start=None,        # float: Start of fitting window (cumulative)
    Np_end=None           # float: End of fitting window (cumulative)
) -> DeclineResult

# Example
Np = np.array([0, 500, 1200, 3000, 5500, 7200, 8500, 10000])
q = np.array([1000, 800, 650, 400, 200, 130, 90, 50])
result = rtb.dca.fit_decline_cum(Np, q, method='hyperbolic')
```

**MCP tool design:**
```python
@mcp.tool()
async def fit_decline_cumulative(
    cumulative_production: list[float],
    rates: list[float],
    method: str = "best",
    calendar_time: list[float] | None = None,
    np_start: float | None = None,
    np_end: float | None = None,
) -> dict:
    """Fit a decline curve model to rate vs cumulative production data.

    Eliminates time from the Arps equations. The returned parameters are
    compatible with time-domain forecasting functions.
    """
    result = rtb.dca.fit_decline_cum(
        cumulative_production, rates, method=method,
        t_calendar=calendar_time, Np_start=np_start, Np_end=np_end
    )
    return {
        "method": result.method,
        "qi": result.qi,
        "di": result.di,
        "b": result.b,
        "r_squared": result.r_squared,
    }
```

### 2.3 `forecast` — Generate rate and cumulative production forecast

```python
rtb.dca.forecast(
    result,               # DeclineResult: From fit_decline() or fit_decline_cum()
    t_end,                # float: End time for forecast
    dt=1.0,               # float: Time step
    q_min=0.0,            # float: Economic limit rate (0 = no cutoff)
    uptime=1.0,           # float: Uptime fraction (0-1)
    ratios=None           # list[RatioResult]: Optional secondary phase ratios
) -> ForecastResult

# Returns ForecastResult with:
#   .t (array): Time array
#   .q (array): Rate array
#   .Qcum (array): Cumulative production array
#   .eur (float): EUR at end of forecast
#   .secondary (dict): Secondary phase forecasts (if ratios provided)

# Example
result = rtb.dca.fit_decline(t, q, method='hyperbolic')
fc = rtb.dca.forecast(result, t_end=360, dt=1, q_min=5, uptime=0.95)
print(f"EUR: {fc.eur:.0f}, final rate: {fc.q[-1]:.1f}")
```

**MCP tool design:**
```python
@mcp.tool()
async def decline_forecast(
    qi: float,
    di: float,
    b: float,
    method: str = "hyperbolic",
    t_end: float = 360,
    dt: float = 1.0,
    q_min: float = 0.0,
    uptime: float = 1.0,
    a: float | None = None,
    m: float | None = None,
) -> dict:
    """Generate a production forecast from decline curve parameters.

    Args:
        qi: Initial rate
        di: Initial decline rate (1/time). Not used for Duong.
        b: Arps b-factor (0=exponential, 0<b<1=hyperbolic, 1=harmonic)
        method: 'exponential', 'harmonic', 'hyperbolic', or 'duong'
        t_end: End time for forecast
        dt: Time step (default 1.0)
        q_min: Economic limit rate (default 0 = no cutoff)
        uptime: Uptime fraction 0-1 (default 1.0)
        a: Duong 'a' parameter (required for Duong method)
        m: Duong 'm' parameter (required for Duong method)

    Returns:
        Dictionary with time, rate, cumulative arrays, and EUR.
    """
    # Build a DeclineResult-like object or call arps_rate/duong_rate directly
    ...
```

### 2.4 `eur` — Estimated Ultimate Recovery

```python
rtb.dca.eur(
    qi,                   # float: Initial rate
    di,                   # float: Initial decline rate (1/time)
    b,                    # float: Arps b-factor (0-1)
    q_min                 # float: Economic limit rate
) -> float               # EUR value

# Example
eur_val = rtb.dca.eur(qi=1000, di=0.05, b=0.5, q_min=10)
print(f"EUR: {eur_val:.0f}")
```

### 2.5 `arps_rate` / `arps_cum` — Direct Arps calculations

```python
rtb.dca.arps_rate(qi, di, b, t) -> float | np.ndarray
rtb.dca.arps_cum(qi, di, b, t) -> float | np.ndarray

# qi: Initial rate
# di: Initial decline rate (1/time), must be > 0
# b: b-factor (0=exp, 0<b<1=hyp, 1=harmonic)
# t: Time (float or array)

# Example
rate_at_12 = rtb.dca.arps_rate(qi=1000, di=0.05, b=0.5, t=12)
cum_at_12 = rtb.dca.arps_cum(qi=1000, di=0.05, b=0.5, t=12)
```

### 2.6 `duong_rate` / `duong_cum` — Duong unconventional decline

```python
rtb.dca.duong_rate(qi, a, m, t) -> float | np.ndarray
rtb.dca.duong_cum(qi, a, m, t) -> float | np.ndarray

# qi: Rate at t=1
# a: Duong 'a' parameter (must be > 0)
# m: Duong 'm' parameter (must be > 1)
# t: Time (must be > 0)

# q(t) = qi * t^(-m) * exp(a/(1-m) * (t^(1-m) - 1))

# Example
rate = rtb.dca.duong_rate(qi=500, a=1.5, m=1.2, t=np.arange(1, 61))
```

### 2.7 `fit_ratio` / `ratio_forecast` — GOR/WOR ratio modeling

```python
rtb.dca.fit_ratio(
    x,                    # array-like: Independent variable (cum production or time)
    ratio,                # array-like: Ratio values (GOR, WOR, etc.)
    method='best',        # str: 'linear', 'exponential', 'power', 'logistic', or 'best'
    domain='cum'          # str: 'cum' or 'time'
) -> RatioResult

# Returns RatioResult with:
#   .method (str): Model type
#   .a, .b, .c (float): Model parameters
#   .r_squared (float): Fit quality
#   .domain (str): 'cum' or 'time'

rtb.dca.ratio_forecast(
    result,               # RatioResult: From fit_ratio()
    x                     # float or array-like: Values to evaluate at
) -> float | np.ndarray

# Example: Fit GOR trend
Np = np.array([1000, 5000, 10000, 20000, 30000])
gor = np.array([800, 1200, 1800, 3000, 5000])
gor_fit = rtb.dca.fit_ratio(Np, gor, method='best', domain='cum')
gor_pred = rtb.dca.ratio_forecast(gor_fit, x=np.linspace(0, 50000, 100))
```

---

## 3. New Module: `matbal` — Material Balance

**Priority:** HIGH
**New files needed:**
- `src/pyrestoolbox_mcp/tools/matbal_tools.py`
- `src/pyrestoolbox_mcp/models/matbal_models.py`
- `tests/test_matbal_tools.py`

### 3.1 `gas_matbal` — P/Z Gas Material Balance

```python
rtb.matbal.gas_matbal(
    p,                    # array-like: Reservoir pressures (psia | barsa). First = initial pressure
    Gp,                   # array-like: Cumulative gas production (same units as desired OGIP)
    degf,                 # float: Reservoir temperature (deg F | deg C)
    sg=0.65,              # float: Gas specific gravity
    co2=0,                # float: CO2 mole fraction
    h2s=0,                # float: H2S mole fraction
    n2=0,                 # float: N2 mole fraction
    h2=0,                 # float: H2 mole fraction
    Wp=None,              # array-like: Cumulative water production (optional)
    Bw=1.0,               # float: Water FVF (rb/stb)
    We=None,              # array-like: Cumulative water influx (optional, for Havlena-Odeh)
    zmethod='DAK',        # str: Z-factor method
    cmethod='PMC',        # str: Critical properties method
    metric=False,         # bool: Use metric units
    pvt_table=None        # DataFrame: Tabulated PVT (optional)
) -> GasMatbalResult

# Returns GasMatbalResult with:
#   .ogip (float): Original gas in place
#   .pz (array): P/Z values
#   .gp (array): Cumulative gas production
#   .slope (float): Slope of P/Z vs Gp regression
#   .intercept (float): Intercept of P/Z vs Gp
#   .method (str): 'pz' or 'havlena_odeh'

# Example
p = [5000, 4500, 4000, 3500, 3000]
Gp = [0, 5, 12, 21, 32]  # Bscf
result = rtb.matbal.gas_matbal(p=p, Gp=Gp, degf=220, sg=0.7)
print(f"OGIP: {result.ogip:.1f} Bscf")
print(f"P/Z values: {result.pz}")
```

**MCP tool design:**
```python
@mcp.tool()
async def gas_material_balance(
    pressures: list[float],
    cumulative_gas: list[float],
    temperature: float,
    gas_sg: float = 0.65,
    co2: float = 0,
    h2s: float = 0,
    n2: float = 0,
    h2: float = 0,
    cumulative_water: list[float] | None = None,
    water_fvf: float = 1.0,
    water_influx: list[float] | None = None,
    z_method: str = "DAK",
    c_method: str = "PMC",
    metric: bool = False,
) -> dict:
    """Perform P/Z gas material balance for OGIP estimation.

    Performs linear regression of P/Z vs cumulative gas production.
    Optionally computes Cole plot and Havlena-Odeh regression when
    water influx data is provided.

    Args:
        pressures: Reservoir pressures at each survey (psia). First = initial pressure.
        cumulative_gas: Cumulative gas production at each survey (user units — OGIP in same units).
        temperature: Reservoir temperature (deg F).
        ...
    """
    result = rtb.matbal.gas_matbal(
        p=pressures, Gp=cumulative_gas, degf=temperature,
        sg=gas_sg, co2=co2, h2s=h2s, n2=n2, h2=h2,
        Wp=cumulative_water, Bw=water_fvf, We=water_influx,
        zmethod=z_method, cmethod=c_method, metric=metric
    )
    return {
        "ogip": result.ogip,
        "pz_values": result.pz.tolist(),
        "cumulative_gas": result.gp.tolist(),
        "slope": result.slope,
        "intercept": result.intercept,
        "method": result.method,
    }
```

### 3.2 `oil_matbal` — Havlena-Odeh Oil Material Balance

```python
rtb.matbal.oil_matbal(
    p,                    # array-like: Reservoir pressures (psia | barsa)
    Np,                   # array-like: Cumulative oil production (STB | sm3)
    degf,                 # float: Reservoir temperature (deg F | deg C)
    api=0,                # float: Stock tank oil API gravity
    sg_sp=0,              # float: Separator gas specific gravity
    sg_g=0,               # float: Weighted average surface gas SG
    pb=0,                 # float: Bubble point pressure (psia | barsa)
    rsb=0,                # float: Solution GOR at Pb (scf/stb | sm3/sm3)
    Rp=None,              # array-like: Cumulative producing GOR
    Wp=None,              # array-like: Cumulative water production
    Wi=None,              # array-like: Cumulative water injection
    Gi=None,              # array-like: Cumulative gas injection
    Bw=1.0,               # float: Water FVF
    m=0,                  # float: Gas cap ratio (m = G*Bgi / N*Boi)
    cf=0,                 # float: Formation compressibility (1/psi)
    sw_i=0,               # float: Initial water saturation
    cw=0,                 # float: Water compressibility (1/psi)
    rsmethod='VELAR',     # str: Solution GOR method
    bomethod='MCAIN',     # str: Oil FVF method
    zmethod='DAK',        # str: Z-factor method
    cmethod='PMC',        # str: Critical properties method
    metric=False,         # bool: Use metric units
    pvt_table=None,       # DataFrame: Tabulated PVT (optional)
    regress=None          # dict: Parameter regression bounds
) -> OilMatbalResult

# Returns OilMatbalResult with:
#   .ooip (float): Original oil in place (STB | sm3)
#   .F (array): Underground withdrawal
#   .Eo (array): Oil expansion term
#   .Eg (array): Gas cap expansion term
#   .Efw (array): Formation/water compressibility term
#   .regressed (dict): Regressed parameters (if regress provided)

# Example
p = [4500, 4000, 3500, 3000, 2500]
Np = [0, 1e6, 3e6, 6e6, 10e6]  # STB
result = rtb.matbal.oil_matbal(
    p=p, Np=Np, degf=200, api=35, sg_sp=0.75,
    pb=3500, rsb=800
)
print(f"OOIP: {result.ooip/1e6:.1f} MMSTB")
```

---

## 4. New Module: `nodal` — Nodal Analysis / VLP / IPR

**Priority:** HIGH
**New files needed:**
- `src/pyrestoolbox_mcp/tools/nodal_tools.py`
- `src/pyrestoolbox_mcp/models/nodal_models.py`
- `tests/test_nodal_tools.py`

This module requires supporting classes (`Completion`, `WellSegment`, `Reservoir`) that must be constructed from user input.

### 4.1 Supporting Classes

```python
# WellSegment — Single wellbore segment
rtb.nodal.WellSegment(
    md,                   # float: Measured depth (ft | m)
    id,                   # float: Internal diameter (inches | mm)
    deviation=0,          # float: Deviation from vertical (degrees). 0=vertical, 90=horizontal
    roughness=None,       # float: Pipe roughness (inches | mm). Default 0.0006 in
    metric=False          # bool: Use metric units
)
# .theta (float): Deviation angle in radians
# .tvd (float): True vertical depth of this segment

# Completion — Wellbore completion (two construction modes)
# Legacy mode (single straight tube):
rtb.nodal.Completion(
    tid=2.441,            # float: Tubing ID (inches | mm)
    length=10000,         # float: Tubing length (ft | m) — wellhead to shoe
    tht=100,              # float: Tubing head temperature (deg F | deg C)
    bht=250,              # float: Bottom hole temperature (deg F | deg C)
    rough=0.0006,         # float: Tubing roughness (inches | mm)
    cid=0,                # float: Casing ID (inches | mm). 0 = no casing section
    crough=None,          # float: Casing roughness. Default = tubing roughness
    mpd=0,                # float: MPD back-pressure (psia | barsa)
    metric=False          # bool: Metric units
)

# Multi-segment mode:
seg1 = rtb.nodal.WellSegment(md=5000, id=4.0, deviation=0)
seg2 = rtb.nodal.WellSegment(md=8000, id=2.441, deviation=45)
seg3 = rtb.nodal.WellSegment(md=10000, id=2.441, deviation=90)
comp = rtb.nodal.Completion(segments=[seg1, seg2, seg3], tht=100, bht=250)

# Properties:
# .segments (list): WellSegment objects
# .total_md (float): Total measured depth
# .total_tvd (float): Total true vertical depth
# .geometry_at_md(md): Returns (id, deviation, roughness) at any MD
# .profile(): Returns MD vs TVD profile table

# Reservoir — Reservoir description for IPR
rtb.nodal.Reservoir(
    pr,                   # float: Reservoir pressure (psia | barsa)
    degf,                 # float: Reservoir temperature (deg F | deg C)
    k,                    # float: Permeability (mD)
    h,                    # float: Net pay thickness (ft | m)
    re,                   # float: Drainage radius (ft | m)
    rw,                   # float: Wellbore radius (ft | m)
    S=0,                  # float: Skin factor
    D=0,                  # float: Non-Darcy coefficient (day/Mscf)
    metric=False          # bool: Metric units
)
```

### 4.2 `fbhp` — Flowing Bottom Hole Pressure from VLP

```python
rtb.nodal.fbhp(
    thp,                  # float: Tubing head pressure (psia | barsa)
    completion,           # Completion: Wellbore completion object
    vlpmethod='WG',       # str: 'HB' (Hagedorn-Brown), 'WG' (Woldesemayat-Ghajar),
                          #       'GRAY', or 'BB' (Beggs & Brill)
    well_type='gas',      # str: 'gas' or 'oil'
    # Gas well parameters:
    gas_pvt=None,         # GasPVT: Optional PVT object
    qg_mmscfd=0,          # float: Gas rate (MMscf/d)
    cgr=0,                # float: Condensate-gas ratio (STB/MMscf)
    qw_bwpd=0,            # float: Water rate (STB/d)
    oil_vis=1.0,          # float: Condensate viscosity (cP)
    api=45,               # float: Condensate API
    pr=0,                 # float: Reservoir pressure for condensate dropout
    # Oil well parameters:
    qt_stbpd=0,           # float: Total liquid rate (STB/d)
    gor=0,                # float: Producing GOR (scf/stb)
    wc=0,                 # float: Water cut (fraction)
    wsg=1.07,             # float: Water specific gravity
    injection=False,      # bool: Injection well mode
    gsg=0.65,             # float: Gas SG (if no gas_pvt)
    metric=False          # bool: Metric units
) -> float               # Flowing BHP (psia | barsa)

# Example — Gas well FBHP
comp = rtb.nodal.Completion(tid=2.441, length=10000, tht=80, bht=250, rough=0.0006)
bhp = rtb.nodal.fbhp(
    thp=500, completion=comp, vlpmethod='WG', well_type='gas',
    qg_mmscfd=5.0, cgr=10, qw_bwpd=50, gsg=0.65
)
print(f"FBHP: {bhp:.0f} psia")
```

**MCP tool design:**
```python
@mcp.tool()
async def flowing_bhp(
    thp: float,
    tubing_id: float,
    tubing_length: float,
    wellhead_temp: float,
    bht: float,
    roughness: float = 0.0006,
    vlp_method: str = "WG",
    well_type: str = "gas",
    gas_rate_mmscfd: float = 0,
    cgr: float = 0,
    water_rate_bwpd: float = 0,
    total_liquid_stbpd: float = 0,
    gor: float = 0,
    water_cut: float = 0,
    gas_sg: float = 0.65,
    api: float = 45,
    metric: bool = False,
    segments: list[dict] | None = None,
) -> dict:
    """Calculate flowing bottom hole pressure using VLP correlations.

    Supports Hagedorn-Brown, Woldesemayat-Ghajar, Gray, and Beggs & Brill
    multiphase flow correlations for gas and oil wells.
    """
    if segments:
        segs = [rtb.nodal.WellSegment(**s, metric=metric) for s in segments]
        comp = rtb.nodal.Completion(segments=segs, tht=wellhead_temp, bht=bht, metric=metric)
    else:
        comp = rtb.nodal.Completion(
            tid=tubing_id, length=tubing_length, tht=wellhead_temp,
            bht=bht, rough=roughness, metric=metric
        )

    bhp = rtb.nodal.fbhp(
        thp=thp, completion=comp, vlpmethod=vlp_method,
        well_type=well_type, qg_mmscfd=gas_rate_mmscfd, cgr=cgr,
        qw_bwpd=water_rate_bwpd, qt_stbpd=total_liquid_stbpd,
        gor=gor, wc=water_cut, gsg=gas_sg, api=api, metric=metric
    )
    return {"fbhp_psia": bhp}
```

### 4.3 `ipr_curve` — Inflow Performance Relationship Curve

```python
rtb.nodal.ipr_curve(
    reservoir,            # Reservoir: Reservoir object
    well_type='gas',      # str: 'gas', 'oil', or 'water'
    gas_pvt=None,         # GasPVT: Optional
    oil_pvt=None,         # OilPVT: Optional
    n_points=20,          # int: Number of pressure points
    min_pwf=None,         # float: Minimum flowing BHP
    wc=0,                 # float: Water cut fraction
    wsg=1.07,             # float: Water SG
    bo=1.2,               # float: Oil FVF (if no oil_pvt)
    uo=1.0,               # float: Oil viscosity (if no oil_pvt)
    gsg=0.65,             # float: Gas SG (if no gas_pvt)
    metric=False          # bool: Metric units
) -> NodalResult         # dict-like with 'pwf' and 'rate' arrays

# Example
res = rtb.nodal.Reservoir(pr=5000, degf=250, k=10, h=50, re=1490, rw=0.354, S=2)
ipr = rtb.nodal.ipr_curve(res, well_type='gas', gsg=0.7)
# ipr['pwf'] -> list of pressures
# ipr['rate'] -> list of rates (MMscf/d for gas)
```

### 4.4 `outflow_curve` — VLP Outflow Curve

```python
rtb.nodal.outflow_curve(
    thp,                  # float: Tubing head pressure (psia | barsa)
    completion,           # Completion: Wellbore
    vlpmethod='WG',       # str: VLP method
    well_type='gas',      # str: 'gas' or 'oil'
    rates=None,           # list: Rates to evaluate (None = auto-generate)
    n_rates=20,           # int: Number of rate points if rates is None
    max_rate=None,        # float: Max rate for auto-generation
    # ... same well parameters as fbhp ...
    metric=False
) -> NodalResult         # dict with 'rates' and 'bhp' arrays

# Example
comp = rtb.nodal.Completion(tid=2.441, length=10000, tht=80, bht=250, rough=0.0006)
vlp = rtb.nodal.outflow_curve(thp=500, completion=comp, well_type='gas', gsg=0.7)
```

### 4.5 `operating_point` — Find VLP/IPR Intersection

```python
rtb.nodal.operating_point(
    thp,                  # float: Tubing head pressure
    completion,           # Completion: Wellbore
    reservoir,            # Reservoir: Reservoir description
    vlpmethod='WG',       # str: VLP method
    well_type='gas',      # str: 'gas' or 'oil'
    # ... same parameters as fbhp + ipr_curve ...
    n_points=25,
    metric=False
) -> NodalResult         # dict with 'rate', 'bhp', 'vlp', 'ipr'

# Example
comp = rtb.nodal.Completion(tid=2.441, length=10000, tht=80, bht=250, rough=0.0006)
res = rtb.nodal.Reservoir(pr=5000, degf=250, k=10, h=50, re=1490, rw=0.354, S=2)
op = rtb.nodal.operating_point(thp=500, completion=comp, reservoir=res, well_type='gas', gsg=0.7)
print(f"Operating rate: {op['rate']:.1f} MMscf/d at BHP: {op['bhp']:.0f} psia")
```

---

## 5. New Module: `recommend` — Method Selection Engine

**Priority:** MEDIUM
**New files needed:**
- `src/pyrestoolbox_mcp/tools/recommend_tools.py`
- `src/pyrestoolbox_mcp/models/recommend_models.py`
- `tests/test_recommend_tools.py`

### 5.1 `recommend_methods` — Master recommendation function

```python
rtb.recommend.recommend_methods(
    sg=0.65,              # float: Gas specific gravity
    co2=0,                # float: CO2 mole fraction
    h2s=0,                # float: H2S mole fraction
    n2=0,                 # float: N2 mole fraction
    h2=0,                 # float: H2 mole fraction
    api=None,             # float: Oil API gravity (include for oil recommendations)
    deviation=0,          # float: Max wellbore deviation (degrees)
    well_type='gas'       # str: 'gas' or 'oil'
) -> dict[str, MethodRecommendation]

# MethodRecommendation attributes:
#   .category (str): e.g. 'zmethod', 'vlp_method'
#   .recommended (str): Recommended method name
#   .rationale (str): Explanation for the recommendation
#   .alternatives (list[str]): Other valid methods
#   .mandatory (bool): Whether recommendation is mandatory

# Example
recs = rtb.recommend.recommend_methods(sg=0.75, co2=0.1, h2s=0.05, api=35, deviation=45)
for key, rec in recs.items():
    print(f"{key}: {rec.recommended} — {rec.rationale}")
```

**MCP tool design:**
```python
@mcp.tool()
async def recommend_methods(
    gas_sg: float = 0.65,
    co2: float = 0,
    h2s: float = 0,
    n2: float = 0,
    h2: float = 0,
    api: float | None = None,
    deviation: float = 0,
    well_type: str = "gas",
) -> dict:
    """Recommend the best PVT and VLP correlations for given fluid properties.

    Analyzes gas composition, oil gravity, and well configuration to suggest
    optimal Z-factor, critical properties, bubble point, GOR, FVF, and VLP methods.
    """
    recs = rtb.recommend.recommend_methods(
        sg=gas_sg, co2=co2, h2s=h2s, n2=n2, h2=h2,
        api=api, deviation=deviation, well_type=well_type
    )
    return {
        key: {
            "recommended": rec.recommended,
            "rationale": rec.rationale,
            "alternatives": rec.alternatives,
            "mandatory": rec.mandatory,
        }
        for key, rec in recs.items()
    }
```

### 5.2 `recommend_gas_methods`

```python
rtb.recommend.recommend_gas_methods(
    sg=0.65, co2=0, h2s=0, n2=0, h2=0
) -> dict[str, MethodRecommendation]
# Returns recommendations for: 'zmethod', 'cmethod'
```

### 5.3 `recommend_oil_methods`

```python
rtb.recommend.recommend_oil_methods(
    api=35.0
) -> dict[str, MethodRecommendation]
# Returns recommendations for: 'pbmethod', 'rsmethod', 'bomethod'
```

### 5.4 `recommend_vlp_method`

```python
rtb.recommend.recommend_vlp_method(
    deviation=0, well_type='gas'
) -> dict[str, MethodRecommendation]
# Returns recommendation for: 'vlp_method'
```

---

## 6. New Module: `sensitivity` — Sensitivity Analysis

**Priority:** MEDIUM
**New files needed:**
- `src/pyrestoolbox_mcp/tools/sensitivity_tools.py`
- `src/pyrestoolbox_mcp/models/sensitivity_models.py`
- `tests/test_sensitivity_tools.py`

### 6.1 `sweep` — Single-parameter sweep

```python
rtb.sensitivity.sweep(
    func,                 # callable: Function to evaluate
    base_kwargs,          # dict: Base keyword arguments
    vary_param,           # str: Parameter name to vary
    vary_values,          # list: Values to sweep
    result_key=None       # str: Key/attribute to extract from each result
) -> SweepResult

# SweepResult attributes:
#   .param (str): Varied parameter name
#   .values (list): Parameter values used
#   .results (list): Function results at each value

# Example — Sweep gas SG effect on Z-factor
result = rtb.sensitivity.sweep(
    func=rtb.gas.gas_z,
    base_kwargs={'p': 3000, 'degf': 200, 'sg': 0.7},
    vary_param='sg',
    vary_values=[0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
)
for val, res in zip(result.values, result.results):
    print(f"SG={val:.2f} -> Z={res:.4f}")
```

**MCP tool design:**
```python
@mcp.tool()
async def parameter_sweep(
    function_name: str,
    base_parameters: dict,
    vary_parameter: str,
    vary_values: list[float],
    result_key: str | None = None,
) -> dict:
    """Sweep a single parameter across a range of values for any pyResToolbox function.

    Evaluates the specified function at each value of the varied parameter
    while keeping all other parameters at their base values.

    Args:
        function_name: Fully qualified function name (e.g. 'gas.gas_z', 'oil.oil_pbub')
        base_parameters: Base keyword arguments for the function
        vary_parameter: Name of the parameter to vary
        vary_values: Values to sweep through
        result_key: Optional key to extract from each result
    """
    # Resolve function from name
    module_name, func_name = function_name.split('.')
    module = getattr(rtb, module_name)
    func = getattr(module, func_name)

    result = rtb.sensitivity.sweep(
        func=func, base_kwargs=base_parameters,
        vary_param=vary_parameter, vary_values=vary_values,
        result_key=result_key
    )
    return {
        "parameter": result.param,
        "values": result.values,
        "results": [float(r) if isinstance(r, (int, float, np.floating)) else str(r) for r in result.results],
    }
```

### 6.2 `tornado` — Multi-parameter tornado sensitivity

```python
rtb.sensitivity.tornado(
    func,                 # callable: Function to evaluate
    base_kwargs,          # dict: Base keyword arguments
    ranges,              # dict: {param: (low, high)} tuples
    result_key=None       # str: Key/attribute to extract
) -> TornadoResult

# TornadoResult attributes:
#   .base_result (float): Result at base values
#   .entries (list[TornadoEntry]): Sorted by decreasing sensitivity

# TornadoEntry attributes:
#   .param (str): Parameter name
#   .low_value (float): Low value used
#   .high_value (float): High value used
#   .low_result (float): Result at low value
#   .high_result (float): Result at high value

# Example — What affects bubble point most?
tornado = rtb.sensitivity.tornado(
    func=rtb.oil.oil_pbub,
    base_kwargs={'api': 35, 'degf': 200, 'rsb': 800, 'sg_sp': 0.75},
    ranges={
        'api': (25, 45),
        'degf': (150, 250),
        'rsb': (400, 1200),
        'sg_sp': (0.65, 0.85),
    }
)
print(f"Base Pb: {tornado.base_result:.0f} psia")
for entry in tornado.entries:
    print(f"  {entry.param}: {entry.low_result:.0f} to {entry.high_result:.0f}")
```

---

## 7. New Gas Functions

**Priority:** MEDIUM
**Files to update:**
- `src/pyrestoolbox_mcp/tools/gas_tools.py`
- `src/pyrestoolbox_mcp/models/gas_models.py`
- `tests/test_gas_tools.py`

### 7.1 `gas_hydrate` — Gas Hydrate Prediction

```python
rtb.gas.gas_hydrate(
    p,                    # float: Operating pressure (psia | barsa)
    degf,                 # float: Operating temperature (deg F | deg C)
    sg,                   # float: Gas specific gravity
    hydmethod='TOWLER',   # str: Hydrate prediction method
    inhibitor_type=None,  # str: Inhibitor type (e.g. 'MEOH', 'MEG', 'DEG', 'TEG')
    inhibitor_wt_pct=0,   # float: Inhibitor weight percent
    co2=0,                # float: CO2 mole fraction
    h2s=0,                # float: H2S mole fraction
    n2=0,                 # float: N2 mole fraction
    h2=0,                 # float: H2 mole fraction
    p_res=None,           # float: Reservoir pressure (for water balance)
    degf_res=None,        # float: Reservoir temperature (for water balance)
    additional_water=0,   # float: Additional free water (bbl/MMscf)
    metric=False          # bool: Metric units
) -> HydrateResult

# HydrateResult attributes (Hydrate Assessment):
#   .hft (float): Hydrate formation temperature at operating pressure
#   .hfp (float): Hydrate formation pressure at operating temperature
#   .subcooling (float): HFT - T_operating (positive = in hydrate zone)
#   .in_hydrate_zone (bool): Whether operating point is in hydrate zone

# Example
result = rtb.gas.gas_hydrate(
    p=2000, degf=60, sg=0.7,
    inhibitor_type='MEOH', inhibitor_wt_pct=25,
    co2=0.02, h2s=0.01
)
print(f"HFT: {result.hft:.1f}°F, In hydrate zone: {result.in_hydrate_zone}")
```

**MCP tool design:**
```python
@mcp.tool()
async def gas_hydrate_prediction(
    pressure: float,
    temperature: float,
    gas_sg: float,
    method: str = "TOWLER",
    inhibitor_type: str | None = None,
    inhibitor_wt_pct: float = 0,
    co2: float = 0,
    h2s: float = 0,
    n2: float = 0,
    h2: float = 0,
    reservoir_pressure: float | None = None,
    reservoir_temperature: float | None = None,
    additional_water: float = 0,
    metric: bool = False,
) -> dict:
    """Predict gas hydrate formation conditions, water balance, and inhibitor requirements.

    Returns hydrate formation temperature/pressure, subcooling margin,
    and whether the operating point is in the hydrate zone.
    """
    result = rtb.gas.gas_hydrate(
        p=pressure, degf=temperature, sg=gas_sg,
        hydmethod=method, inhibitor_type=inhibitor_type,
        inhibitor_wt_pct=inhibitor_wt_pct,
        co2=co2, h2s=h2s, n2=n2, h2=h2,
        p_res=reservoir_pressure, degf_res=reservoir_temperature,
        additional_water=additional_water, metric=metric
    )
    return {
        "hft": result.hft,
        "hfp": result.hfp,
        "subcooling": result.subcooling,
        "in_hydrate_zone": result.in_hydrate_zone,
    }
```

### 7.2 `gas_sg` — Gas SG from MW and contaminants

```python
rtb.gas.gas_sg(
    hc_mw,                # float: Hydrocarbon molecular weight
    co2,                  # float: CO2 mole fraction
    h2s,                  # float: H2S mole fraction
    n2,                   # float: N2 mole fraction
    h2                    # float: H2 mole fraction
) -> float               # Gas SG relative to air

# Example
sg = rtb.gas.gas_sg(hc_mw=20.5, co2=0.05, h2s=0.02, n2=0.01, h2=0)
```

### 7.3 `gas_fws_sg` — Free-Water-Saturated gas SG

```python
rtb.gas.gas_fws_sg(
    sg_g,                 # float: Separator gas SG (relative to air)
    cgr,                  # float: Condensate-gas ratio (stb/MMscf | sm3/sm3)
    api_st,               # float: Stock tank liquid API
    metric=False          # bool: Metric units
) -> float               # FWS gas SG

# Example
fws_sg = rtb.gas.gas_fws_sg(sg_g=0.72, cgr=25, api_st=55)
```

### 7.4 `gas_ponz2p` — Convert P/Z to Pressure

```python
rtb.gas.gas_ponz2p(
    poverz,               # float or array: P/Z value(s) (psia)
    sg,                   # float: Gas SG
    degf,                 # float: Temperature (deg F)
    zmethod='DAK',        # z_method enum
    cmethod='PMC',        # c_method enum
    co2=0, h2s=0, n2=0, h2=0,
    tc=0, pc=0,           # float: Override critical properties
    rtol=1e-7,            # float: Convergence tolerance
    metric=False          # bool: Metric units
) -> np.ndarray          # Pressure(s) (psia)

# Example — useful for material balance work
p = rtb.gas.gas_ponz2p(poverz=4500, sg=0.7, degf=220)
```

### 7.5 `gas_dmp` — Delta Pseudopressure Between Two Pressures

```python
rtb.gas.gas_dmp(
    p1,                   # float: Starting (lower) pressure (psia)
    p2,                   # float: Ending (upper) pressure (psia)
    degf,                 # float: Temperature (deg F)
    sg,                   # float: Gas SG
    zmethod='DAK', cmethod='PMC',
    co2=0, h2s=0, n2=0, h2=0,
    tc=0, pc=0,
    metric=False
) -> float               # Delta m(p) (psi²/cP)

# Example
dmp = rtb.gas.gas_dmp(p1=1000, p2=3000, degf=200, sg=0.7)
```

### 7.6 `darcy_gas` — Darcy Gas Flow from Delta-m(p)

```python
rtb.gas.darcy_gas(
    delta_mp,             # float or array: Delta pseudopressure (psi²/cP)
    k,                    # float or array: Permeability (mD)
    h,                    # float or array: Net pay (ft)
    degf,                 # float: Temperature (deg F)
    l1,                   # float: Inner boundary (rw for radial, 0 for linear) (ft)
    l2,                   # float: Outer boundary (re for radial, L for linear) (ft)
    S,                    # float: Skin factor
    D,                    # float: Non-Darcy coefficient
    radial                # bool: True = radial flow, False = linear flow
) -> np.ndarray          # Gas rate (Mscf/d)
```

### 7.7 `GasPVT` Class — Reusable Gas PVT Object

```python
gas_pvt = rtb.gas.GasPVT(
    sg=0.75,              # float: Gas SG
    co2=0, h2s=0, n2=0, h2=0,  # Contaminant fractions
    zmethod='DAK',        # str: Z-factor method
    cmethod='PMC',        # str: Critical properties method
    metric=False          # bool: Metric units
)

# Methods:
gas_pvt.z(p, degf)       # Z-factor at p and T
gas_pvt.bg(p, degf)      # Gas FVF (rcf/scf)
gas_pvt.density(p, degf) # Gas density (lb/cuft)
gas_pvt.viscosity(p, degf) # Gas viscosity (cP)

# Example
gpvt = rtb.gas.GasPVT(sg=0.7, co2=0.03, zmethod='DAK')
z = gpvt.z(p=3000, degf=200)
bg = gpvt.bg(p=3000, degf=200)
```

**MCP tool design:**
```python
@mcp.tool()
async def create_gas_pvt(
    gas_sg: float = 0.75,
    co2: float = 0,
    h2s: float = 0,
    n2: float = 0,
    h2: float = 0,
    z_method: str = "DAK",
    c_method: str = "PMC",
    pressures: list[float] = [],
    temperature: float = 200,
    metric: bool = False,
) -> dict:
    """Create a gas PVT object and compute properties at specified conditions.

    Computes Z-factor, FVF, density, and viscosity at each pressure/temperature point.
    """
    gpvt = rtb.gas.GasPVT(sg=gas_sg, co2=co2, h2s=h2s, n2=n2, h2=h2,
                           zmethod=z_method, cmethod=c_method, metric=metric)
    results = []
    for p in pressures:
        results.append({
            "pressure": p,
            "z_factor": float(gpvt.z(p, temperature)),
            "bg": float(gpvt.bg(p, temperature)),
            "density": float(gpvt.density(p, temperature)),
            "viscosity": float(gpvt.viscosity(p, temperature)),
        })
    return {"gas_pvt_properties": results}
```

---

## 8. New Oil Functions

**Priority:** MEDIUM
**Files to update:**
- `src/pyrestoolbox_mcp/tools/oil_tools.py`
- `src/pyrestoolbox_mcp/models/oil_models.py`
- `tests/test_oil_tools.py`

### 8.1 `oil_harmonize` — PVT Auto-Harmonization

```python
rtb.oil.oil_harmonize(
    pb=0,                 # float: Bubble point pressure (psia | barsa)
    rsb=0,                # float: Solution GOR at Pb (scf/stb | sm3/sm3)
    degf=0,               # float: Reservoir temperature (deg F | deg C)
    api=0,                # float: Stock tank oil API gravity
    sg_sp=0,              # float: Separator gas SG
    sg_g=0,               # float: Weighted average surface gas SG
    uo_target=0,          # float: Target viscosity at p_uo (cP)
    p_uo=0,               # float: Pressure where viscosity is known (psia)
    rsmethod='VELAR',     # str: Solution GOR method
    pbmethod='VELAR',     # str: Bubble point method
    metric=False          # bool: Metric units
) -> tuple               # (pb, rsb, rsb_frac, vis_frac)

# Behavior:
# - If only pb: calculates rsb from pb
# - If only rsb: calculates pb from rsb
# - If both: finds rsb_frac scaling factor to honor both
# - If uo_target + p_uo: computes vis_frac = uo_target / uo_corr

# Example
pb, rsb, rsb_frac, vis_frac = rtb.oil.oil_harmonize(
    pb=3500, degf=200, api=35, sg_sp=0.75,
    uo_target=1.2, p_uo=5000
)
print(f"Harmonized: Pb={pb:.0f}, Rsb={rsb:.0f}, vis_frac={vis_frac:.3f}")
```

**MCP tool design:**
```python
@mcp.tool()
async def oil_harmonize_pvt(
    bubble_point: float = 0,
    rsb: float = 0,
    temperature: float = 0,
    api: float = 0,
    sg_sp: float = 0,
    sg_g: float = 0,
    target_viscosity: float = 0,
    viscosity_pressure: float = 0,
    rs_method: str = "VELAR",
    pb_method: str = "VELAR",
    metric: bool = False,
) -> dict:
    """Auto-harmonize oil PVT parameters for internal consistency.

    Given one or both of Pb and Rsb, returns mutually consistent values.
    Optionally computes a viscosity scaling factor to match a measurement.
    """
    pb, rsb_out, rsb_frac, vis_frac = rtb.oil.oil_harmonize(
        pb=bubble_point, rsb=rsb, degf=temperature,
        api=api, sg_sp=sg_sp, sg_g=sg_g,
        uo_target=target_viscosity, p_uo=viscosity_pressure,
        rsmethod=rs_method, pbmethod=pb_method, metric=metric
    )
    return {
        "bubble_point_psia": pb,
        "rsb_scf_per_stb": rsb_out,
        "rsb_fraction": rsb_frac,
        "viscosity_fraction": vis_frac,
    }
```

### 8.2 `oil_viso` — Oil Viscosity (updated correlation)

```python
rtb.oil.oil_viso(
    p,                    # float: Pressure (psia | barsa)
    api,                  # float: API gravity
    degf,                 # float: Temperature (deg F | deg C)
    pb,                   # float: Bubble point pressure (psia | barsa)
    rs,                   # float: Solution GOR (scf/stb | sm3/sm3)
    metric=False          # bool: Metric units
) -> float               # Oil viscosity (cP)

# Uses Beggs-Robinson at saturated pressures, Petrosky-Farshad at undersaturated
# NOTE: Our current MCP tool uses the older signature. This is an updated version.

# Example
vis = rtb.oil.oil_viso(p=5000, api=35, degf=200, pb=3500, rs=800)
```

### 8.3 `OilPVT` Class — Reusable Oil PVT Object

```python
oil_pvt = rtb.oil.OilPVT(
    api,                  # float: Stock tank oil API gravity
    sg_sp,                # float: Separator gas SG
    pb,                   # float: Bubble point pressure (psia | barsa)
    rsb=0,                # float: Solution GOR at Pb. If 0 and degf>0, calculated via harmonize
    sg_g=0,               # float: Weighted average surface gas SG
    degf=0,               # float: Reservoir temperature (for auto-harmonization)
    uo_target=0,          # float: Target viscosity (cP)
    p_uo=0,               # float: Pressure of target viscosity
    vis_frac=1.0,         # float: Viscosity scaling factor
    rsb_frac=1.0,         # float: Rsb scaling factor
    rsmethod='VELAR',     # str: Solution GOR method
    pbmethod='VALMC',     # str: Bubble point method
    bomethod='MCAIN',     # str: Oil FVF method
    metric=False          # bool: Metric units
)

# Methods:
oil_pvt.rs(p, degf)          # Solution GOR at p and T
oil_pvt.bo(p, degf, rs=None) # Oil FVF at p and T
oil_pvt.density(p, degf, rs=None) # Oil density
oil_pvt.viscosity(p, degf, rs=None) # Oil viscosity

# Example
opvt = rtb.oil.OilPVT(api=35, sg_sp=0.75, pb=3500, degf=200)
rs = opvt.rs(p=3000, degf=200)
bo = opvt.bo(p=3000, degf=200)
vis = opvt.viscosity(p=3000, degf=200)
```

**MCP tool design:**
```python
@mcp.tool()
async def create_oil_pvt(
    api: float,
    sg_sp: float,
    bubble_point: float,
    temperature: float,
    rsb: float = 0,
    sg_g: float = 0,
    target_viscosity: float = 0,
    viscosity_pressure: float = 0,
    rs_method: str = "VELAR",
    pb_method: str = "VALMC",
    bo_method: str = "MCAIN",
    pressures: list[float] = [],
    metric: bool = False,
) -> dict:
    """Create an oil PVT object and compute properties at specified pressures.

    Auto-harmonizes Pb and Rsb for internal consistency. Returns Rs, Bo,
    density, and viscosity at each pressure point.
    """
    opvt = rtb.oil.OilPVT(
        api=api, sg_sp=sg_sp, pb=bubble_point, degf=temperature,
        rsb=rsb, sg_g=sg_g, uo_target=target_viscosity, p_uo=viscosity_pressure,
        rsmethod=rs_method, pbmethod=pb_method, bomethod=bo_method, metric=metric
    )
    results = []
    for p in pressures:
        results.append({
            "pressure": p,
            "rs": float(opvt.rs(p, temperature)),
            "bo": float(opvt.bo(p, temperature)),
            "density": float(opvt.density(p, temperature)),
            "viscosity": float(opvt.viscosity(p, temperature)),
        })
    return {
        "oil_pvt_properties": results,
        "bubble_point": bubble_point,
        "api": api,
    }
```

---

## 9. New Simtools Functions

**Priority:** MEDIUM
**Files to update:**
- `src/pyrestoolbox_mcp/tools/simtools_tools.py`
- `src/pyrestoolbox_mcp/models/simtools_models.py`
- `tests/test_simtools_tools.py`

### 9.1 `make_vfpprod` — Generate Eclipse VFPPROD Tables

```python
rtb.simtools.make_vfpprod(
    table_num,            # int: VFP table number (>= 1)
    completion,           # Completion: Wellbore completion object
    well_type='gas',      # str: 'gas' or 'oil'
    vlpmethod='WG',       # str: VLP correlation
    flo_rates=None,       # list: Flow rates (auto-generated if None)
    thp_values=None,      # list: THP values (auto-generated if None)
    wfr_values=None,      # list: Water fraction values
    gfr_values=None,      # list: Gas fraction values
    alq_values=None,      # list: Artificial lift values
    gas_pvt=None,         # GasPVT: Optional
    gsg=0.65,             # float: Gas SG (if no gas_pvt)
    oil_vis=1.0,          # float: Oil viscosity (cP)
    api=45,               # float: Condensate API
    pr=0,                 # float: Reservoir pressure
    oil_pvt=None,         # OilPVT: Optional
    pb=0, rsb=0, sgsp=0.65,
    wsg=1.07,             # float: Water SG
    datum_depth=0,        # float: Reference depth (ft | m)
    export=False,         # bool: Write to file
    filename='',          # str: Output filename
    metric=False          # bool: Metric units
) -> dict                # Contains 'table' (str) and 'data' (arrays)

# For gas wells (FIELD): FLO=GAS (Mscf/d), WFR=WGR (stb/Mscf), GFR=OGR (stb/Mscf)
# For oil wells (FIELD): FLO=OIL (stb/d), WFR=WCT (fraction), GFR=GOR (Mscf/stb)

# Example
comp = rtb.nodal.Completion(tid=2.441, length=10000, tht=80, bht=250, rough=0.0006)
result = rtb.simtools.make_vfpprod(
    table_num=1, completion=comp, well_type='gas',
    vlpmethod='WG', gsg=0.7, export=True, filename='VFPPROD.INC'
)
```

### 9.2 `make_vfpinj` — Generate Eclipse VFPINJ Tables

```python
rtb.simtools.make_vfpinj(
    table_num,            # int: VFP table number (>= 1)
    completion,           # Completion: Wellbore completion object
    flo_type='WAT',       # str: 'WAT', 'GAS', or 'OIL'
    vlpmethod='WG',       # str: VLP correlation
    flo_rates=None,       # list: Flow rates
    thp_values=None,      # list: THP values
    gas_pvt=None,         # GasPVT: Optional
    gsg=0.65,             # float: Gas SG
    wsg=1.07,             # float: Water SG
    oil_pvt=None,         # OilPVT: Optional
    datum_depth=0,        # float: Reference depth
    export=False,         # bool: Write to file
    filename='',          # str: Output filename
    metric=False          # bool: Metric units
) -> dict

# Example
comp = rtb.nodal.Completion(tid=3.5, length=8000, tht=80, bht=200, rough=0.0006)
result = rtb.simtools.make_vfpinj(
    table_num=1, completion=comp, flo_type='WAT',
    wsg=1.02, export=True, filename='VFPINJ.INC'
)
```

### 9.3 `make_bot_og` — Black Oil Table Generation

```python
rtb.simtools.make_bot_og(
    pi,                   # float: Initial pressure (psia | barsa)
    api,                  # float: Oil API gravity
    degf,                 # float: Temperature (deg F | deg C)
    sg_g,                 # float: Gas SG
    pmax,                 # float: Maximum pressure (psia | barsa)
    pb=0,                 # float: Bubble point (0 = calculate)
    rsb=0,                # float: Solution GOR at Pb
    pmin=25,              # float: Minimum pressure
    nrows=20,             # int: Number of rows
    wt=0,                 # float: Brine salinity (wt%)
    ch4_sat=0,            # float: Methane saturation (0-1)
    comethod='EXPLT',     # str: Oil compressibility method
    zmethod='DAK',        # str: Z-factor method
    rsmethod='VELAR',     # str: Solution GOR method
    cmethod='PMC',        # str: Critical properties method
    denomethod='SWMH',    # str: Oil density method
    bomethod='MCAIN',     # str: Oil FVF method
    pbmethod='VELAR',     # str: Bubble point method
    export=False,         # bool: Write PVTO/PVDG/PVDO files
    pvto=False,           # bool: Generate PVTO format (vs PVDO)
    vis_frac=1.0,         # float: Viscosity scaling factor
    metric=False          # bool: Metric units
) -> dict

# Returns dict with:
#   'bot': Pandas DataFrame of black oil data
#   'deno': Stock tank oil density
#   'deng': Stock tank gas density
#   'denw': Water density at Pi
#   'cw': Water compressibility at Pi
#   'uw': Water viscosity at Pi
#   'pb': Bubble point pressure

# Example
result = rtb.simtools.make_bot_og(
    pi=5000, api=35, degf=200, sg_g=0.75, pmax=6000,
    pb=3500, rsb=800, export=True, pvto=True
)
print(result['bot'].head())
```

### 9.4 `make_pvtw_table` — PVTW Water PVT Table

```python
rtb.simtools.make_pvtw_table(
    pi,                   # float: Reference pressure (psia | barsa)
    degf,                 # float: Temperature (deg F | deg C)
    wt=0,                 # float: Salt wt% (0-100)
    ch4_sat=0,            # float: Methane saturation (0-1)
    pmin=500,             # float: Minimum pressure
    pmax=10000,           # float: Maximum pressure
    nrows=20,             # int: Number of rows
    export=False,         # bool: Write PVTW.INC file
    metric=False          # bool: Metric units
) -> dict

# Example
result = rtb.simtools.make_pvtw_table(pi=5000, degf=200, wt=5, export=True)
```

### 9.5 `fit_rel_perm` — Fit Relative Permeability Model

```python
rtb.simtools.fit_rel_perm(
    sw,                   # array-like: Water (or gas) saturation values
    kr,                   # array-like: Measured relative permeability values
    krfamily='COR',       # str: 'COR' (Corey), 'LET', or 'JER' (Jerauld)
    krmax=1.0,            # float: Maximum kr endpoint
    sw_min=0.0,           # float: Minimum saturation endpoint
    sw_max=1.0            # float: Maximum saturation endpoint
) -> dict

# Returns dict with:
#   'params': Fitted parameters (n for Corey; L,E,T for LET; a,b for Jerauld)
#   'kr_fitted': Fitted kr values at input sw
#   'residuals': Fitting residuals
#   'ssr': Sum of squared residuals

# Example
import numpy as np
sw = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
kr = np.array([0.0, 0.02, 0.08, 0.18, 0.35, 0.58, 0.85])
result = rtb.simtools.fit_rel_perm(sw, kr, krfamily='LET', sw_min=0.2, sw_max=0.8)
print(f"LET params: L={result['params'][0]:.2f}, E={result['params'][1]:.2f}, T={result['params'][2]:.2f}")
```

### 9.6 `fit_rel_perm_best` — Auto-Select Best Rel Perm Fit

```python
rtb.simtools.fit_rel_perm_best(
    sw,                   # array-like: Saturation values
    kr,                   # array-like: Measured kr values
    krmax=1.0,            # float: Max kr endpoint
    sw_min=0.0,           # float: Min saturation
    sw_max=1.0            # float: Max saturation
) -> dict

# Fits Corey, LET, and Jerauld, returns best fit (lowest SSR)
# Additional key: 'family' (str) — name of the winning model

result = rtb.simtools.fit_rel_perm_best(sw, kr, sw_min=0.2, sw_max=0.8)
print(f"Best model: {result['family']}, SSR: {result['ssr']:.6f}")
```

### 9.7 `jerauld` — Jerauld Relative Permeability Curve

```python
rtb.simtools.jerauld(
    s,                    # np.ndarray: Normalized saturation
    a,                    # float: Jerauld 'a' parameter (> 0)
    b                     # float: Jerauld 'b' parameter (> 0)
) -> np.ndarray          # Relative permeability values

# kr = ((1+b) * S^a) / (1 + b * S^c)  where c = a * (1 + 1/b)

s = np.linspace(0, 1, 50)
kr = rtb.simtools.jerauld(s, a=2.5, b=3.0)
```

### 9.8 `is_let_physical` — Validate LET Parameters

```python
rtb.simtools.is_let_physical(
    s,                    # np.ndarray: Normalized saturation array (sorted)
    L,                    # float: LET 'L' parameter
    E,                    # float: LET 'E' parameter
    T                     # float: LET 'T' parameter
) -> bool                # True if curve is monotonically increasing and physical

s = np.linspace(0, 1, 100)
valid = rtb.simtools.is_let_physical(s, L=2.0, E=1.5, T=1.8)
```

---

## 10. New Brine Functions

**Priority:** MEDIUM
**Files to update:**
- `src/pyrestoolbox_mcp/tools/brine_tools.py`
- `src/pyrestoolbox_mcp/models/brine_models.py`
- `tests/test_brine_tools.py`

### 10.1 `SoreideWhitson` — Multicomponent Gas-Brine VLE

```python
sw = rtb.brine.SoreideWhitson(
    pres,                 # float: Pressure (barsa for metric=True, psia for False)
    temp,                 # float: Temperature (°C for metric=True, °F for False)
    ppm=0,                # float: Salinity (ppm NaCl)
    y_CO2=0,              # float: CO2 mole fraction in feed gas
    y_H2S=0,              # float: H2S mole fraction in feed gas
    y_N2=0,               # float: N2 mole fraction in feed gas
    y_H2=0,               # float: H2 mole fraction in feed gas
    sg=0.65,              # float: Hydrocarbon gas SG
    metric=True,          # bool: Metric units (default True for this class)
    cw_sat=False          # bool: If True, include water content in gas
)

# The constructor runs the VLE calculation. Access results as attributes:
# Key results available from the object after construction.
# Supports multicomponent gas mixtures: C1, C2, C3, nC4, CO2, H2S, N2, H2

# Example
sw_result = rtb.brine.SoreideWhitson(
    pres=200, temp=80, ppm=50000,
    y_CO2=0.1, y_H2S=0.02, sg=0.7, metric=True
)
```

**MCP tool design:**
```python
@mcp.tool()
async def soreide_whitson_vle(
    pressure: float,
    temperature: float,
    salinity_ppm: float = 0,
    co2_fraction: float = 0,
    h2s_fraction: float = 0,
    n2_fraction: float = 0,
    h2_fraction: float = 0,
    gas_sg: float = 0.65,
    metric: bool = True,
) -> dict:
    """Calculate multicomponent gas-brine VLE using Soreide-Whitson (1992) model.

    Supports gas mixtures containing C1, C2, C3, nC4, CO2, H2S, N2, H2.
    Calculates dissolved gas in brine and water content in gas phase.
    Applications: CO2 sequestration, H2 storage, sour gas processing.

    Args:
        pressure: Pressure (barsa if metric, psia if not)
        temperature: Temperature (°C if metric, °F if not)
        salinity_ppm: Brine salinity (ppm NaCl)
        co2_fraction: CO2 mole fraction in feed gas
        h2s_fraction: H2S mole fraction in feed gas
        n2_fraction: N2 mole fraction in feed gas
        h2_fraction: H2 mole fraction in feed gas
        gas_sg: Hydrocarbon gas specific gravity
        metric: Use metric units (default True)
    """
    sw = rtb.brine.SoreideWhitson(
        pres=pressure, temp=temperature, ppm=salinity_ppm,
        y_CO2=co2_fraction, y_H2S=h2s_fraction, y_N2=n2_fraction,
        y_H2=h2_fraction, sg=gas_sg, metric=metric
    )
    # Extract relevant results from sw object
    ...
```

---

## 11. Metric Unit Support

**Priority:** LOW (but broad impact)
**Files to update:** All existing tool and model files

All pyResToolbox v3.0.4 public functions now accept a `metric=False` parameter. When `metric=True`:

| Property | Field Unit | Metric Unit |
|----------|-----------|-------------|
| Pressure | psia | barsa |
| Temperature | °F | °C |
| Length | ft | m |
| Pipe diameter | inches | mm |
| Oil rate | STB/d | sm3/d |
| Gas rate | MMscf/d or Mscf/d | sm3/d |
| Solution GOR | scf/stb | sm3/sm3 |
| Oil FVF | rb/stb | rm3/sm3 |
| Gas FVF | rcf/scf | rm3/sm3 |
| Density | lb/ft³ | kg/m³ |
| Roughness | inches | mm |

### Implementation approach

Add `metric: bool = False` parameter to every existing MCP tool (all 72 tools) and pass through to the underlying pyResToolbox function.

**Example — updating an existing tool:**
```python
# BEFORE (current)
@mcp.tool()
async def oil_bubble_point(
    api: float,
    temperature: float,
    rsb: float,
    sg_sp: float = 0,
    sg_g: float = 0,
    method: str = "VALMC",
) -> dict:
    pb = rtb.oil.oil_pbub(api=api, degf=temperature, rsb=rsb, sg_sp=sg_sp, sg_g=sg_g)
    return {"bubble_point_psia": pb}

# AFTER (updated)
@mcp.tool()
async def oil_bubble_point(
    api: float,
    temperature: float,
    rsb: float,
    sg_sp: float = 0,
    sg_g: float = 0,
    method: str = "VALMC",
    metric: bool = False,
) -> dict:
    pb = rtb.oil.oil_pbub(api=api, degf=temperature, rsb=rsb, sg_sp=sg_sp, sg_g=sg_g, metric=metric)
    unit = "barsa" if metric else "psia"
    return {f"bubble_point_{unit}": pb}
```

### Update `config.py` resources

Add metric unit documentation to the `config://units` resource so LLM agents know both unit systems are available.

---

## 12. Summary

### New tools to implement (~35-40 tools)

| Category | New Tools | Priority |
|----------|-----------|----------|
| DCA (Decline Curve Analysis) | ~8 tools | HIGH |
| Material Balance | ~2-3 tools | HIGH |
| Nodal Analysis / VLP | ~5-6 tools | HIGH |
| Method Recommendations | ~3-4 tools | MEDIUM |
| Sensitivity Analysis | ~2 tools | MEDIUM |
| New Gas Functions | ~6-7 tools | MEDIUM |
| New Oil Functions | ~3 tools | MEDIUM |
| New Simtools Functions | ~6-7 tools | MEDIUM |
| New Brine Functions | ~1-2 tools | MEDIUM |

### Cross-cutting updates

| Update | Scope | Priority |
|--------|-------|----------|
| Bump `pyrestoolbox>=3.0.4` | `pyproject.toml` | HIGH |
| Add `metric` param to all 72 existing tools | All tool files | LOW |
| Update `config.py` unit resources | `config.py` | LOW |
| Update README with new tools | `README.md` | LOW |
| Update CHANGELOG | `CHANGELOG.md` | LOW |
| Add new examples | `examples/` | LOW |

### New files to create

```
src/pyrestoolbox_mcp/tools/dca_tools.py         # Decline curve analysis tools
src/pyrestoolbox_mcp/tools/matbal_tools.py       # Material balance tools
src/pyrestoolbox_mcp/tools/nodal_tools.py        # Nodal analysis / VLP tools
src/pyrestoolbox_mcp/tools/recommend_tools.py    # Method recommendation tools
src/pyrestoolbox_mcp/tools/sensitivity_tools.py  # Sensitivity analysis tools

src/pyrestoolbox_mcp/models/dca_models.py        # DCA Pydantic models
src/pyrestoolbox_mcp/models/matbal_models.py     # Matbal Pydantic models
src/pyrestoolbox_mcp/models/nodal_models.py      # Nodal Pydantic models
src/pyrestoolbox_mcp/models/recommend_models.py  # Recommend Pydantic models
src/pyrestoolbox_mcp/models/sensitivity_models.py # Sensitivity Pydantic models

tests/test_dca_tools.py                          # DCA tests
tests/test_matbal_tools.py                       # Matbal tests
tests/test_nodal_tools.py                        # Nodal tests
tests/test_recommend_tools.py                    # Recommend tests
tests/test_sensitivity_tools.py                  # Sensitivity tests

examples/decline_curve_analysis.py               # DCA example workflow
examples/material_balance.py                     # Matbal example workflow
examples/nodal_analysis.py                       # Nodal analysis example
examples/method_recommendations.py               # Recommendation example
examples/sensitivity_analysis.py                 # Sensitivity example
```
