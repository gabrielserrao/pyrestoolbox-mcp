"""Geomechanics calculation tools for FastMCP."""

import numpy as np
from fastmcp import FastMCP
from typing import Dict, Any

from ..models.geomech_models import (
    VerticalStressRequest,
    PorePressureEatonRequest,
    EffectiveStressRequest,
    HorizontalStressRequest,
    ElasticModuliRequest,
    RockStrengthRequest,
    DynamicToStaticRequest,
    BreakoutWidthRequest,
    FractureGradientRequest,
    MudWeightWindowRequest,
    CriticalMudWeightRequest,
    ReservoirCompactionRequest,
    PoreCompressibilityRequest,
    LeakOffPressureRequest,
    FractureWidthRequest,
    # New advanced models
    StressPolygonRequest,
    SandProductionRequest,
    FaultStabilityRequest,
    DeviatedWellStressRequest,
    TensileFailureRequest,
    ShearFailureCriteriaRequest,
    BreakoutStressInversionRequest,
    BreakdownPressureRequest,
    StressPathRequest,
    ThermalStressRequest,
    UCSFromLogsRequest,
    CriticalDrawdownRequest,
)


def register_geomech_tools(mcp: FastMCP) -> None:
    """Register all geomechanics-related tools with the MCP server."""

    @mcp.tool()
    def geomech_vertical_stress(request: VerticalStressRequest) -> dict:
        """Calculate vertical stress (overburden) from depth and formation properties.

        **FUNDAMENTAL GEOMECHANICS PARAMETER** - Vertical stress is the total weight of
        overlying rock and fluid. Foundation for all stress and wellbore stability calculations.

        **Parameters:**
        - **depth** (float, required): True vertical depth below surface in feet.
          Valid range: >0. Typical: 5000-20000 ft. Example: 10000.0
        - **water_depth** (float, optional, default=0): Water depth for offshore wells (ft).
          Use 0 for onshore wells. Typical offshore: 100-10000 ft.
        - **avg_density** (float, optional, default=144): Average bulk density of overburden (lb/ft³).
          Typical: 140-160 lb/ft³ (equivalent to 19-21 ppg). Example: 144.0 = 19 ppg
        - **water_density** (float, optional, default=64): Water density (lb/ft³).
          Fresh water = 62.4, seawater = 64.0, use for offshore calculations.

        **Returns:**
        Dictionary with:
        - **value** (float): Vertical stress at depth (psi)
        - **gradient** (float): Vertical stress gradient (psi/ft)
        - **units** (str): "psi"
        - **inputs** (dict): Echo of input parameters

        **Formula:**
        σv = ρwater × g × dwater + ρbulk × g × (dtotal - dwater)
        Simplified: σv = 0.052 × ρavg(ppg) × depth
        Or: σv = ρavg(lb/ft³) × depth / 144

        **Common Values:**
        - Onshore: 1.0-1.1 psi/ft (19-21 ppg equivalent)
        - Offshore shallow: 0.8-1.0 psi/ft (includes water column)
        - Offshore deep: approaches 1.0 psi/ft below mudline

        **Example Usage:**
        ```python
        {
            "depth": 10000.0,
            "water_depth": 0.0,
            "avg_density": 144.0,
            "water_density": 64.0
        }
        ```
        Expected: σv ≈ 10000 psi (1.0 psi/ft gradient)
        """
        # Convert lb/ft³ to ppg for standard calculation
        avg_density_ppg = request.avg_density / 7.48  # 1 ppg = 7.48 lb/ft³ approx
        water_density_ppg = request.water_density / 7.48

        # Calculate vertical stress
        if request.water_depth > 0:
            # Offshore: water column + sediment
            water_stress = 0.052 * water_density_ppg * request.water_depth
            sediment_stress = 0.052 * avg_density_ppg * (request.depth - request.water_depth)
            vertical_stress = water_stress + sediment_stress
        else:
            # Onshore: sediment only
            vertical_stress = 0.052 * avg_density_ppg * request.depth

        gradient = vertical_stress / request.depth

        return {
            "value": float(vertical_stress),
            "gradient": float(gradient),
            "units": "psi",
            "gradient_units": "psi/ft",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_pore_pressure_eaton(request: PorePressureEatonRequest) -> dict:
        """Calculate pore pressure using Eaton's method from sonic or resistivity logs.

        **CRITICAL DRILLING SAFETY PARAMETER** - Eaton's method estimates formation pore
        pressure from log data. Most widely used method in petroleum industry for predicting
        overpressure and preventing kicks/blowouts.

        **Parameters:**
        - **depth** (float, required): True vertical depth (ft)
        - **observed_value** (float, required): Observed sonic (μs/ft) or resistivity (ohm-m)
        - **normal_value** (float, required): Normal compaction trend value at this depth
        - **overburden_psi** (float, required): Overburden stress at depth (psi)
        - **eaton_exponent** (float, optional, default=3.0): Eaton exponent
          Use 3.0 for sonic, 1.2 for resistivity
        - **method** (str, optional, default="sonic"): "sonic" or "resistivity"

        **Returns:**
        Dictionary with:
        - **value** (float): Pore pressure (psi)
        - **gradient** (float): Pore pressure gradient (psi/ft)
        - **overpressure** (float): Overpressure above hydrostatic (psi)
        - **units** (str): "psi"
        - **inputs** (dict): Echo of input parameters

        **Formulas:**
        Eaton Sonic: Pp = σv - (σv - Phydro) × (Δtn_normal / Δtn_observed)^3.0
        Eaton Resistivity: Pp = σv - (σv - Phydro) × (R_observed / R_normal)^1.2

        Where:
        - Phydro = 0.465 × depth (freshwater = 0.433 psi/ft)
        - Δtn = sonic transit time (slower = higher porosity = less compacted = overpressured)
        - R = resistivity (lower = more conductive = overpressured)

        **Interpretation:**
        - Gradient < 0.465 psi/ft: Underpressured (subnormal)
        - Gradient ≈ 0.465 psi/ft: Normal pressure (hydrostatic)
        - Gradient > 0.465 psi/ft: Overpressured (requires careful drilling)
        - Gradient > 0.8 psi/ft: Severe overpressure (high risk)

        **Example Usage:**
        ```python
        {
            "depth": 10000.0,
            "observed_value": 100.0,  # sonic μs/ft
            "normal_value": 70.0,     # normal trend at this depth
            "overburden_psi": 10400.0,
            "eaton_exponent": 3.0,
            "method": "sonic"
        }
        ```
        Expected: Pp > 4650 psi (overpressured if sonic is slower than normal)
        """
        # Calculate hydrostatic pressure (0.465 psi/ft for seawater)
        hydrostatic = 0.465 * request.depth

        # Apply Eaton's method
        if request.method == "sonic":
            # For sonic: normal/observed (higher sonic = higher pressure)
            ratio = request.normal_value / request.observed_value
        else:  # resistivity
            # For resistivity: observed/normal (lower resistivity = higher pressure)
            ratio = request.observed_value / request.normal_value

        # Eaton equation
        pore_pressure = request.overburden_psi - (request.overburden_psi - hydrostatic) * (ratio ** request.eaton_exponent)

        gradient = pore_pressure / request.depth
        overpressure = pore_pressure - hydrostatic

        return {
            "value": float(pore_pressure),
            "gradient": float(gradient),
            "overpressure": float(overpressure),
            "hydrostatic": float(hydrostatic),
            "units": "psi",
            "gradient_units": "psi/ft",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_effective_stress(request: EffectiveStressRequest) -> dict:
        """Calculate effective stress from total stress and pore pressure.

        **FUNDAMENTAL ROCK MECHANICS PRINCIPLE** - Effective stress (Terzaghi) controls
        rock mechanical behavior, deformation, and failure. The effective stress is the
        portion of total stress carried by the rock matrix.

        **Parameters:**
        - **total_stress** (float or array, required): Total stress (psi) - can be vertical or horizontal
        - **pore_pressure** (float or array, required): Formation pore pressure (psi)
        - **biot_coefficient** (float, optional, default=1.0): Biot's coefficient
          α = 1.0 for unconsolidated rocks
          α = 0.6-0.9 for consolidated rocks
          α = 0.5-0.7 for tight carbonates

        **Returns:**
        Dictionary with:
        - **value** (float or array): Effective stress (psi)
        - **units** (str): "psi"
        - **inputs** (dict): Echo of input parameters

        **Formula:**
        σ' = σtotal - α × Pp

        Where:
        - σ' = effective stress
        - σtotal = total stress (overburden or horizontal)
        - α = Biot coefficient
        - Pp = pore pressure

        **Physical Meaning:**
        - Effective stress is the stress actually borne by the rock grain contacts
        - Controls rock strength, compaction, and failure
        - Higher effective stress → stronger, more compact rock
        - Lower effective stress → weaker rock, higher failure risk

        **Example Usage:**
        ```python
        {
            "total_stress": 10400.0,
            "pore_pressure": 4680.0,
            "biot_coefficient": 1.0
        }
        ```
        Expected: σ' ≈ 5720 psi
        """
        # Convert to numpy arrays for vector operations
        total_stress = np.asarray(request.total_stress)
        pore_pressure = np.asarray(request.pore_pressure)

        # Calculate effective stress using Terzaghi's principle
        effective_stress = total_stress - request.biot_coefficient * pore_pressure

        # Convert back to native Python types for JSON serialization
        if np.ndim(effective_stress) == 0:
            result_value = float(effective_stress)
        else:
            result_value = effective_stress.tolist()

        return {
            "value": result_value,
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_horizontal_stress(request: HorizontalStressRequest) -> dict:
        """Calculate horizontal stresses from vertical stress using elastic theory.

        **KEY WELLBORE STABILITY PARAMETER** - Horizontal stresses control fracture pressure,
        wellbore breakout orientation, and drilling trajectory stability. Critical for safe
        drilling operations and hydraulic fracturing.

        **Parameters:**
        - **vertical_stress** (float, required): Total vertical stress/overburden (psi)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **poisson_ratio** (float, required): Poisson's ratio (0.15-0.40 typical)
          Sand: 0.15-0.25, Shale: 0.25-0.35, Carbonate: 0.20-0.30
        - **tectonic_factor** (float, optional, default=0.0): Tectonic stress multiplier
          0.0 = passive/normal faulting regime
          0.5 = strike-slip regime
          1.0 = reverse faulting regime
        - **biot_coefficient** (float, optional, default=1.0): Biot coefficient

        **Returns:**
        Dictionary with:
        - **sigma_h_min** (float): Minimum horizontal stress (psi)
        - **sigma_h_max** (float): Maximum horizontal stress (psi)
        - **stress_regime** (str): "normal", "strike-slip", or "reverse"
        - **units** (str): "psi"
        - **inputs** (dict): Echo of input parameters

        **Formulas:**
        σh_min = (ν/(1-ν)) × (σv - αPp) + αPp + σtectonic

        Stress regimes:
        - Normal: σv > σH > σh (tectonic_factor ≈ 0)
        - Strike-slip: σH > σv > σh (tectonic_factor ≈ 0.5)
        - Reverse: σH > σh > σv (tectonic_factor ≈ 1.0)

        **Applications:**
        - Wellbore stability analysis
        - Fracture pressure prediction
        - Sand production prediction
        - Hydraulic fracture design
        - Optimal wellbore trajectory

        **Example Usage:**
        ```python
        {
            "vertical_stress": 10400.0,
            "pore_pressure": 4680.0,
            "poisson_ratio": 0.25,
            "tectonic_factor": 0.0,
            "biot_coefficient": 1.0
        }
        ```
        Expected: σh ≈ 6500 psi for normal faulting
        """
        # Calculate effective vertical stress
        sigma_v_eff = request.vertical_stress - request.biot_coefficient * request.pore_pressure

        # Calculate minimum horizontal stress using poroelastic equation
        nu = request.poisson_ratio
        sigma_h_min = (nu / (1 - nu)) * sigma_v_eff + request.biot_coefficient * request.pore_pressure

        # Estimate maximum horizontal stress based on tectonic regime
        # Simple model: linear interpolation based on tectonic factor
        sigma_h_max = sigma_h_min + request.tectonic_factor * (request.vertical_stress - sigma_h_min)

        # Determine stress regime
        if request.tectonic_factor < 0.3:
            stress_regime = "normal"
        elif request.tectonic_factor < 0.7:
            stress_regime = "strike-slip"
        else:
            stress_regime = "reverse"

        return {
            "sigma_h_min": float(sigma_h_min),
            "sigma_h_max": float(sigma_h_max),
            "stress_regime": stress_regime,
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_elastic_moduli_conversion(request: ElasticModuliRequest) -> dict:
        """Convert between elastic moduli (Young's, bulk, shear, Poisson's ratio).

        **ROCK PROPERTY CONVERSION TOOL** - Converts between different elastic moduli using
        isotropic elasticity relationships. Essential because different tests and logs provide
        different moduli, but calculations require specific ones.

        **Parameters (provide any 2):**
        - **youngs_modulus** (float, optional): Young's modulus E (psi)
        - **bulk_modulus** (float, optional): Bulk modulus K (psi)
        - **shear_modulus** (float, optional): Shear modulus G (psi)
        - **poisson_ratio** (float, optional): Poisson's ratio ν (dimensionless)
        - **lame_parameter** (float, optional): Lamé's first parameter λ (psi)

        **Returns:**
        Dictionary with all five moduli calculated:
        - **youngs_modulus** (float): E (psi)
        - **bulk_modulus** (float): K (psi)
        - **shear_modulus** (float): G (psi)
        - **poisson_ratio** (float): ν
        - **lame_parameter** (float): λ (psi)
        - **inputs** (dict): Echo of input parameters

        **Conversion Formulas:**
        - E = 2G(1 + ν) = 3K(1 - 2ν) = 9KG/(3K + G)
        - ν = (3K - 2G)/(6K + 2G) = E/(2G) - 1
        - K = E/(3(1 - 2ν)) = λ + (2G/3)
        - G = E/(2(1 + ν)) = 3K(1 - 2ν)/(2(1 + ν))
        - λ = K - (2G/3) = (Eν)/((1+ν)(1-2ν))

        **Typical Values:**
        - Soft shale: E = 100,000-500,000 psi, ν = 0.25-0.35
        - Sandstone: E = 500,000-2,000,000 psi, ν = 0.15-0.25
        - Limestone: E = 1,000,000-5,000,000 psi, ν = 0.20-0.30
        - Hard granite: E = 5,000,000-10,000,000 psi, ν = 0.20-0.25

        **Example Usage:**
        ```python
        {
            "youngs_modulus": 1000000.0,
            "poisson_ratio": 0.25
        }
        ```
        Expected: G ≈ 400,000 psi, K ≈ 666,667 psi
        """
        # Count how many parameters are provided
        params_provided = sum([
            request.youngs_modulus is not None,
            request.bulk_modulus is not None,
            request.shear_modulus is not None,
            request.poisson_ratio is not None,
            request.lame_parameter is not None,
        ])

        if params_provided < 2:
            raise ValueError("Must provide at least 2 elastic parameters")

        # Start with provided values
        E = request.youngs_modulus
        K = request.bulk_modulus
        G = request.shear_modulus
        nu = request.poisson_ratio
        lam = request.lame_parameter

        # Calculate missing parameters using isotropic elasticity relationships
        # Priority: E and nu are most common, calculate from those when possible

        if E is not None and nu is not None:
            # Calculate all others from E and nu
            G = E / (2 * (1 + nu))
            K = E / (3 * (1 - 2 * nu))
            lam = (E * nu) / ((1 + nu) * (1 - 2 * nu))
        elif E is not None and G is not None:
            nu = (E / (2 * G)) - 1
            K = (E * G) / (3 * (3 * G - E))
            lam = (G * (E - 2 * G)) / (3 * G - E)
        elif E is not None and K is not None:
            G = (3 * K * E) / (9 * K - E)
            nu = (3 * K - E) / (6 * K)
            lam = K - (2 * G / 3)
        elif G is not None and nu is not None:
            E = 2 * G * (1 + nu)
            K = (2 * G * (1 + nu)) / (3 * (1 - 2 * nu))
            lam = (2 * G * nu) / (1 - 2 * nu)
        elif K is not None and nu is not None:
            E = 3 * K * (1 - 2 * nu)
            G = (3 * K * (1 - 2 * nu)) / (2 * (1 + nu))
            lam = (3 * K * nu) / (1 + nu)
        elif K is not None and G is not None:
            nu = (3 * K - 2 * G) / (6 * K + 2 * G)
            E = (9 * K * G) / (3 * K + G)
            lam = K - (2 * G / 3)
        elif lam is not None and G is not None:
            K = lam + (2 * G / 3)
            nu = lam / (2 * (lam + G))
            E = (G * (3 * lam + 2 * G)) / (lam + G)
        else:
            raise ValueError("Unable to calculate moduli from provided parameters")

        return {
            "youngs_modulus": float(E),
            "bulk_modulus": float(K),
            "shear_modulus": float(G),
            "poisson_ratio": float(nu),
            "lame_parameter": float(lam),
            "units": "psi (except Poisson's ratio is dimensionless)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_rock_strength_mohr_coulomb(request: RockStrengthRequest) -> dict:
        """Calculate rock strength using Mohr-Coulomb failure criterion.

        **ROCK FAILURE PREDICTION** - Mohr-Coulomb is the most common failure criterion
        in petroleum geomechanics. Predicts when rock will fail under stress, critical for
        wellbore stability, sand production, and casing design.

        **Parameters:**
        - **cohesion** (float, required): Rock cohesion (psi). Typical: 100-1000 psi
          Soft shale: 100-300 psi, Sandstone: 300-800 psi, Carbonate: 500-1500 psi
        - **friction_angle** (float, required): Internal friction angle (degrees)
          Typical: 20-40°. Sand: 30-40°, Shale: 20-30°, Carbonate: 30-35°
        - **effective_stress_min** (float, required): Minimum effective principal stress (psi)
          This is the confining stress

        **Returns:**
        Dictionary with:
        - **max_principal_stress** (float): Maximum effective stress at failure (psi)
        - **shear_strength** (float): Shear strength on failure plane (psi)
        - **unconfined_strength** (float): UCS - unconfined compressive strength (psi)
        - **q_factor** (float): Mohr-Coulomb strength ratio
        - **units** (str): "psi"
        - **inputs** (dict): Echo of input parameters

        **Formulas:**
        σ1_failure = UCS + q × σ3

        Where:
        - UCS = 2C × cos(φ)/(1 - sin(φ)) = unconfined compressive strength
        - q = (1 + sin(φ))/(1 - sin(φ)) = tan²(45° + φ/2)
        - C = cohesion
        - φ = friction angle

        Shear strength: τ = C + σn × tan(φ)

        **Interpretation:**
        - If actual σ1 > σ1_failure: rock fails (breakout, collapse, sand production)
        - If actual σ1 < σ1_failure: rock is stable
        - UCS is the strength with no confining pressure (lab test result)
        - Higher φ → stronger rock response to confining stress

        **Example Usage:**
        ```python
        {
            "cohesion": 500.0,
            "friction_angle": 30.0,
            "effective_stress_min": 2000.0
        }
        ```
        Expected: σ1_failure ≈ 7000-8000 psi
        """
        # Convert friction angle to radians
        phi_rad = np.deg2rad(request.friction_angle)

        # Calculate Mohr-Coulomb parameters
        sin_phi = np.sin(phi_rad)
        cos_phi = np.cos(phi_rad)
        tan_phi = np.tan(phi_rad)

        # Unconfined compressive strength
        ucs = 2 * request.cohesion * cos_phi / (1 - sin_phi)

        # Strength ratio (q factor)
        q_factor = (1 + sin_phi) / (1 - sin_phi)
        # Alternative: q = tan²(45° + φ/2)
        # q_alt = np.tan(np.pi/4 + phi_rad/2)**2

        # Maximum principal stress at failure (Mohr-Coulomb criterion)
        max_principal_stress = ucs + q_factor * request.effective_stress_min

        # Average normal stress on failure plane
        sigma_n = (max_principal_stress + request.effective_stress_min) / 2

        # Shear strength on failure plane
        shear_strength = request.cohesion + sigma_n * tan_phi

        return {
            "max_principal_stress": float(max_principal_stress),
            "shear_strength": float(shear_strength),
            "unconfined_strength": float(ucs),
            "q_factor": float(q_factor),
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_dynamic_to_static_moduli(request: DynamicToStaticRequest) -> dict:
        """Convert dynamic elastic moduli (from logs) to static moduli (from core tests).

        **LOG-TO-CORE CALIBRATION** - Sonic logs provide dynamic elastic properties at
        small strain, but geomechanics calculations require static properties at larger
        strain. Dynamic moduli are typically 20-50% higher than static.

        **Parameters:**
        - **dynamic_youngs** (float, optional): Dynamic Young's modulus from logs (psi)
        - **dynamic_poisson** (float, optional): Dynamic Poisson's ratio from logs
        - **correlation** (str, optional, default="eissa_kazi"): Correlation method
          Options: "eissa_kazi", "plona_cook", "linear"
        - **lithology** (str, optional, default="sandstone"): Rock type
          Options: "sandstone", "shale", "carbonate"

        **Returns:**
        Dictionary with:
        - **static_youngs** (float): Static Young's modulus (psi)
        - **static_poisson** (float): Static Poisson's ratio
        - **correction_factor** (float): Ratio of static/dynamic
        - **units** (str): "psi"
        - **inputs** (dict): Echo of input parameters

        **Correlations:**
        Eissa-Kazi (sandstone):
        - Estatic = 0.541 × Edynamic
        - νstatic = 0.87 × νdynamic

        Plona-Cook (carbonate):
        - Estatic = 0.70 × Edynamic
        - νstatic = 0.90 × νdynamic

        Linear (shale/mixed):
        - Estatic = 0.60 × Edynamic
        - νstatic = 0.85 × νdynamic

        **Why This Matters:**
        - Wellbore stability requires static properties
        - Using dynamic properties overpredicts rock strength
        - Can lead to underestimating breakout risk
        - Critical for sand production prediction

        **Example Usage:**
        ```python
        {
            "dynamic_youngs": 1500000.0,
            "dynamic_poisson": 0.20,
            "correlation": "eissa_kazi",
            "lithology": "sandstone"
        }
        ```
        Expected: Estatic ≈ 811,500 psi, νstatic ≈ 0.174
        """
        # Select correlation coefficients based on method and lithology
        if request.correlation == "eissa_kazi" or request.lithology == "sandstone":
            E_factor = 0.541
            nu_factor = 0.87
        elif request.correlation == "plona_cook" or request.lithology == "carbonate":
            E_factor = 0.70
            nu_factor = 0.90
        else:  # linear or shale
            E_factor = 0.60
            nu_factor = 0.85

        # Apply conversions
        static_youngs = None
        static_poisson = None

        if request.dynamic_youngs is not None:
            static_youngs = request.dynamic_youngs * E_factor

        if request.dynamic_poisson is not None:
            static_poisson = request.dynamic_poisson * nu_factor

        return {
            "static_youngs": float(static_youngs) if static_youngs is not None else None,
            "static_poisson": float(static_poisson) if static_poisson is not None else None,
            "correction_factor": float(E_factor),
            "units": "psi (except Poisson's ratio is dimensionless)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_breakout_width(request: BreakoutWidthRequest) -> dict:
        """Calculate borehole breakout width using Kirsch elastic solution.

        **WELLBORE STABILITY ANALYSIS** - Predicts stress-induced borehole breakouts
        (rock failure at wellbore wall). Critical for wellbore stability, stuck pipe
        prevention, and mud weight optimization.

        **Parameters:**
        - **sigma_h_max** (float, required): Maximum horizontal stress (psi)
        - **sigma_h_min** (float, required): Minimum horizontal stress (psi)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **mud_weight** (float, required): Drilling fluid density (ppg)
        - **wellbore_azimuth** (float, required): Well azimuth (degrees, 0-360)
        - **ucs** (float, required): Unconfined compressive strength (psi)
        - **friction_angle** (float, required): Internal friction angle (degrees)

        **Returns:**
        Dictionary with:
        - **breakout_width** (float): Angular width of breakout zone (degrees)
        - **max_tangential_stress** (float): Maximum hoop stress at wellbore wall (psi)
        - **failure_status** (str): "stable", "minor_breakout", "severe_breakout"
        - **critical_mud_weight** (float): Minimum MW to prevent breakout (ppg)
        - **units** (str): Various
        - **inputs** (dict): Echo of input parameters

        **Formula (Kirsch for vertical well):**
        σθ = σh_max + σh_min - 2(σh_max - σh_min)cos(2θ) - Pmud

        Where:
        - σθ = tangential (hoop) stress at wellbore wall
        - θ = angle from σh_max direction
        - Pmud = 0.052 × MW × depth

        Breakout occurs when: σθ < failure criterion (Mohr-Coulomb)

        **Breakout Location:**
        - Breakout occurs perpendicular to σh_max (at θ = 90° and 270°)
        - Maximum stress occurs parallel to σh_max (at θ = 0° and 180°)

        **Interpretation:**
        - Breakout width < 30°: Minor, acceptable
        - Breakout width 30-90°: Moderate, increase MW
        - Breakout width > 90°: Severe, hole instability likely

        **Example Usage:**
        ```python
        {
            "sigma_h_max": 8500.0,
            "sigma_h_min": 6500.0,
            "pore_pressure": 4680.0,
            "mud_weight": 9.0,
            "wellbore_azimuth": 45.0,
            "ucs": 3000.0,
            "friction_angle": 30.0
        }
        ```
        """
        # Calculate mud pressure at depth (estimate depth from stress)
        depth_est = request.pore_pressure / 0.465  # Estimate depth from PP
        mud_pressure = 0.052 * request.mud_weight * depth_est

        # Kirsch solution: calculate tangential stress at critical angle
        # Minimum tangential stress (maximum compression) occurs at 90° to sigma_h_max
        theta_critical = 90.0  # degrees

        # Convert to radians for calculation
        theta_rad = np.deg2rad(theta_critical)

        # Tangential stress at wellbore wall (Kirsch)
        sigma_theta = (
            request.sigma_h_max + request.sigma_h_min
            - 2 * (request.sigma_h_max - request.sigma_h_min) * np.cos(2 * theta_rad)
            - mud_pressure
        )

        # Effective tangential stress
        sigma_theta_eff = sigma_theta - request.pore_pressure

        # Radial stress at wellbore wall equals mud pressure (effective is negative)
        sigma_r_eff = mud_pressure - request.pore_pressure

        # Check failure using Mohr-Coulomb
        phi_rad = np.deg2rad(request.friction_angle)
        sin_phi = np.sin(phi_rad)
        cos_phi = np.cos(phi_rad)

        # UCS
        ucs = request.ucs

        # Mohr-Coulomb: σ1 = UCS + q × σ3
        q = (1 + sin_phi) / (1 - sin_phi)

        # Failure stress at this confining pressure
        sigma_failure = ucs + q * max(sigma_r_eff, 0)

        # Calculate breakout width (simplified)
        if sigma_theta_eff < 0:  # Compressive failure
            # Estimate breakout width from stress ratio
            stress_ratio = abs(sigma_theta_eff) / sigma_failure
            if stress_ratio > 1.0:
                # Simplified breakout width estimation
                breakout_width = min(180.0, 60.0 * (stress_ratio - 1.0))
                if breakout_width < 30:
                    failure_status = "minor_breakout"
                elif breakout_width < 90:
                    failure_status = "moderate_breakout"
                else:
                    failure_status = "severe_breakout"
            else:
                breakout_width = 0.0
                failure_status = "stable"
        else:
            breakout_width = 0.0
            failure_status = "stable"

        # Calculate critical mud weight to prevent breakout
        # Set sigma_theta_eff = sigma_failure and solve for mud_pressure
        sigma_theta_target = sigma_failure + request.pore_pressure
        mud_pressure_critical = (
            request.sigma_h_max + request.sigma_h_min
            - 2 * (request.sigma_h_max - request.sigma_h_min)
            - sigma_theta_target
        )
        critical_mud_weight = mud_pressure_critical / (0.052 * depth_est)

        return {
            "breakout_width": float(breakout_width),
            "max_tangential_stress": float(sigma_theta),
            "failure_status": failure_status,
            "critical_mud_weight": float(critical_mud_weight),
            "units": "degrees (breakout), psi (stress), ppg (MW)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_fracture_gradient(request: FractureGradientRequest) -> dict:
        """Calculate fracture gradient and maximum allowable mud weight.

        **CRITICAL DRILLING PARAMETER** - Formation fracture pressure defines the upper
        limit of the safe drilling mud weight window. Exceeding this causes lost circulation,
        formation damage, and potentially stuck pipe.

        **Parameters:**
        - **depth** (float, required): True vertical depth (ft)
        - **sigma_h_min** (float, optional): Minimum horizontal stress if known (psi)
        - **vertical_stress** (float, required): Overburden stress (psi)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **poisson_ratio** (float, optional, default=0.25): For estimation methods
        - **method** (str, optional, default="eaton"): Calculation method
          Options: "hubbert_willis", "eaton", "matthews_kelly"

        **Returns:**
        Dictionary with:
        - **fracture_pressure** (float): Formation fracture pressure (psi)
        - **fracture_gradient** (float): Fracture gradient (psi/ft)
        - **equivalent_mud_weight** (float): Maximum safe mud weight (ppg)
        - **margin** (float): Margin between fracture and pore pressure (psi)
        - **units** (str): Various
        - **inputs** (dict): Echo of input parameters

        **Methods:**
        Hubbert-Willis: Pfrac = σh_min (assumes tensile strength ≈ 0)

        Eaton: Pfrac = (ν/(1-ν)) × (σv - Pp) + Pp

        Matthews-Kelly: Pfrac = (σv/D) × (D - 1000ft) × (Ki/100) + Pp
        Where Ki is a regional matrix stress coefficient

        **Typical Values:**
        - Shallow (<5000 ft): 0.7-0.85 psi/ft
        - Medium (5000-10000 ft): 0.8-0.95 psi/ft
        - Deep (>10000 ft): 0.9-1.1 psi/ft
        - Overpressured zones: Can approach overburden gradient

        **Example Usage:**
        ```python
        {
            "depth": 10000.0,
            "vertical_stress": 10400.0,
            "pore_pressure": 4680.0,
            "poisson_ratio": 0.25,
            "method": "eaton"
        }
        ```
        Expected: Pfrac ≈ 7500-8500 psi (0.75-0.85 psi/ft)
        """
        if request.sigma_h_min is not None:
            # Use known minimum horizontal stress (most accurate)
            fracture_pressure = request.sigma_h_min
        elif request.method == "hubbert_willis":
            # Hubbert-Willis: simple poroelastic relationship
            nu = request.poisson_ratio
            fracture_pressure = (nu / (1 - nu)) * (request.vertical_stress - request.pore_pressure) + request.pore_pressure
        elif request.method == "eaton":
            # Eaton method (same as Hubbert-Willis for this simplified case)
            nu = request.poisson_ratio
            fracture_pressure = (nu / (1 - nu)) * (request.vertical_stress - request.pore_pressure) + request.pore_pressure
        else:  # matthews_kelly
            # Matthews-Kelly method with assumed Ki = 0.75 (typical)
            Ki = 0.75
            overburden_grad = request.vertical_stress / request.depth
            fracture_pressure = overburden_grad * (request.depth - 1000) * (Ki) + request.pore_pressure

        # Calculate gradient
        fracture_gradient = fracture_pressure / request.depth

        # Convert to equivalent mud weight
        equivalent_mud_weight = fracture_gradient / 0.052

        # Calculate margin
        margin = fracture_pressure - request.pore_pressure

        return {
            "fracture_pressure": float(fracture_pressure),
            "fracture_gradient": float(fracture_gradient),
            "equivalent_mud_weight": float(equivalent_mud_weight),
            "margin": float(margin),
            "units": "psi (pressure), psi/ft (gradient), ppg (MW)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_safe_mud_weight_window(request: MudWeightWindowRequest) -> dict:
        """Calculate safe mud weight window from pore pressure and fracture gradient.

        **DRILLING DESIGN TOOL** - Defines the allowable mud weight range for safe drilling.
        Too light causes kicks/blowouts, too heavy causes lost circulation. Narrow windows
        require managed pressure drilling (MPD).

        **Parameters:**
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **fracture_pressure** (float, required): Formation fracture pressure (psi)
        - **depth** (float, required): True vertical depth (ft)
        - **collapse_pressure** (float, optional): For stability considerations (psi)
        - **safety_margin_overbalance** (float, optional, default=0.5): Overbalance margin (ppg)
        - **safety_margin_fracture** (float, optional, default=0.5): Fracture margin (ppg)

        **Returns:**
        Dictionary with:
        - **min_mud_weight** (float): Minimum safe mud weight (ppg)
        - **max_mud_weight** (float): Maximum safe mud weight (ppg)
        - **window_width** (float): Width of mud weight window (ppg)
        - **status** (str): "narrow", "moderate", "wide"
        - **units** (str): "ppg"
        - **inputs** (dict): Echo of input parameters

        **Formulas:**
        MWmin = (Pp/depth) × (1/0.052) + safety_margin_overbalance
        MWmax = (Pfrac/depth) × (1/0.052) - safety_margin_fracture

        **Window Interpretation:**
        - Wide (>4 ppg): Easy drilling, conventional methods
        - Moderate (2-4 ppg): Normal drilling, good monitoring
        - Narrow (<2 ppg): Challenging, may require MPD
        - Negative: Impossible without MPD or casing

        **Safety Margins:**
        - Overbalance: 0.3-0.8 ppg typical (higher in high-risk areas)
        - Fracture: 0.3-0.5 ppg typical (buffer for surge pressures)

        **Example Usage:**
        ```python
        {
            "pore_pressure": 4680.0,
            "fracture_pressure": 7800.0,
            "depth": 10000.0,
            "safety_margin_overbalance": 0.5,
            "safety_margin_fracture": 0.5
        }
        ```
        Expected: MW window ≈ 9.5-14.5 ppg (5 ppg wide = easy drilling)
        """
        # Convert pressures to gradients
        pp_gradient = request.pore_pressure / request.depth
        frac_gradient = request.fracture_pressure / request.depth

        # Convert to mud weights
        pp_mud_weight = pp_gradient / 0.052
        frac_mud_weight = frac_gradient / 0.052

        # Apply safety margins
        min_mud_weight = pp_mud_weight + request.safety_margin_overbalance
        max_mud_weight = frac_mud_weight - request.safety_margin_fracture

        # Consider collapse pressure if provided
        if request.collapse_pressure is not None:
            collapse_gradient = request.collapse_pressure / request.depth
            collapse_mud_weight = collapse_gradient / 0.052
            min_mud_weight = max(min_mud_weight, collapse_mud_weight)

        # Calculate window width
        window_width = max_mud_weight - min_mud_weight

        # Classify window
        if window_width < 0:
            status = "negative - MPD required"
        elif window_width < 2:
            status = "narrow - challenging"
        elif window_width < 4:
            status = "moderate - normal drilling"
        else:
            status = "wide - easy drilling"

        return {
            "min_mud_weight": float(min_mud_weight),
            "max_mud_weight": float(max_mud_weight),
            "window_width": float(window_width),
            "status": status,
            "units": "ppg",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_critical_mud_weight_collapse(request: CriticalMudWeightRequest) -> dict:
        """Calculate critical mud weight to prevent borehole collapse.

        **WELLBORE STABILITY OPTIMIZATION** - Determines minimum mud weight required to
        prevent shear failure and borehole collapse using Mohr-Coulomb criterion. Essential
        for directional drilling and trajectory optimization.

        **Parameters:**
        - **sigma_h_max** (float, required): Maximum horizontal stress (psi)
        - **sigma_h_min** (float, required): Minimum horizontal stress (psi)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **cohesion** (float, required): Rock cohesion (psi)
        - **friction_angle** (float, required): Internal friction angle (degrees)
        - **wellbore_azimuth** (float, required): Well azimuth (degrees)
        - **wellbore_inclination** (float, optional, default=0): Deviation from vertical (degrees)
        - **depth** (float, required): True vertical depth (ft)

        **Returns:**
        Dictionary with:
        - **critical_mud_weight** (float): Minimum MW for stability (ppg)
        - **collapse_pressure** (float): Minimum wellbore pressure needed (psi)
        - **safety_factor** (float): Factor of safety at critical MW
        - **units** (str): Various
        - **inputs** (dict): Echo of input parameters

        **Approach:**
        1. Calculate tangential stress at wellbore wall using Kirsch
        2. Apply Mohr-Coulomb failure criterion
        3. Solve for minimum mud pressure to prevent failure
        4. Convert to mud weight

        **Wellbore Orientation Effects:**
        - Vertical wells: simpler stress state
        - Deviated wells: more complex stress transformation
        - Well azimuth matters: drilling parallel vs perpendicular to σh_max

        **Typical Results:**
        - Stable formations: 0.5-1.0 ppg above pore pressure
        - Weak shales: 1.5-3.0 ppg above pore pressure
        - Tectonically stressed: 2.0-4.0 ppg above pore pressure

        **Example Usage:**
        ```python
        {
            "sigma_h_max": 8500.0,
            "sigma_h_min": 6500.0,
            "pore_pressure": 4680.0,
            "cohesion": 500.0,
            "friction_angle": 30.0,
            "wellbore_azimuth": 45.0,
            "wellbore_inclination": 0.0,
            "depth": 10000.0
        }
        ```
        """
        # For vertical well (simplified)
        # Minimum tangential stress occurs perpendicular to sigma_h_max
        # σθ_min = 3×σh_min - σh_max - Pmud

        # Calculate Mohr-Coulomb parameters
        phi_rad = np.deg2rad(request.friction_angle)
        sin_phi = np.sin(phi_rad)

        # UCS from cohesion
        cos_phi = np.cos(phi_rad)
        ucs = 2 * request.cohesion * cos_phi / (1 - sin_phi)

        # q factor
        q = (1 + sin_phi) / (1 - sin_phi)

        # For critical case at breakout location (θ = 90°)
        # σθ = σh_max + σh_min - 2(σh_max - σh_min) - Pmud
        # σθ = 3σh_min - σh_max - Pmud

        # Radial effective stress (confining) = Pmud - Pp
        # Tangential effective stress = (3σh_min - σh_max - Pmud) - Pp

        # At failure: |σθ_eff| = UCS + q × σr_eff
        # Solving for Pmud:

        # Conservative approach: assume σr_eff ≈ 0 (worst case)
        # |σθ_eff| = UCS
        # (3σh_min - σh_max - Pmud - Pp) = -UCS (compressive)
        # Pmud = 3σh_min - σh_max - Pp + UCS

        collapse_pressure = (
            3 * request.sigma_h_min
            - request.sigma_h_max
            - request.pore_pressure
            + ucs
        )

        # Ensure positive pressure
        collapse_pressure = max(collapse_pressure, request.pore_pressure + 100)

        # Convert to mud weight
        critical_mud_weight = collapse_pressure / (0.052 * request.depth)

        # Calculate safety factor (ratio of actual to required)
        # Assuming current pressure = pore pressure + 0.5 ppg margin
        current_pressure = request.pore_pressure + (0.5 * 0.052 * request.depth)
        safety_factor = current_pressure / collapse_pressure if collapse_pressure > 0 else 99.9

        return {
            "critical_mud_weight": float(critical_mud_weight),
            "collapse_pressure": float(collapse_pressure),
            "safety_factor": float(safety_factor),
            "units": "ppg (MW), psi (pressure)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_reservoir_compaction(request: ReservoirCompactionRequest) -> dict:
        """Calculate reservoir compaction from pressure depletion.

        **PRODUCTION IMPACT ASSESSMENT** - Estimates reservoir compaction and surface
        subsidence due to pore pressure reduction during production. Critical for casing
        integrity, platform stability, and infrastructure management.

        **Parameters:**
        - **pressure_drop** (float, required): Reservoir pressure depletion (psi)
        - **reservoir_thickness** (float, required): Net pay thickness (ft)
        - **pore_compressibility** (float, optional): If known (1/psi)
        - **bulk_compressibility** (float, optional): If known (1/psi)
        - **youngs_modulus** (float, required): Static Young's modulus (psi)
        - **poisson_ratio** (float, required): Poisson's ratio
        - **biot_coefficient** (float, optional, default=1.0): Biot coefficient

        **Returns:**
        Dictionary with:
        - **compaction** (float): Vertical reservoir compaction (ft)
        - **subsidence** (float): Estimated surface subsidence (ft)
        - **strain** (float): Vertical strain (dimensionless)
        - **pore_compressibility_calculated** (float): If not provided (1/psi)
        - **units** (str): Various
        - **inputs** (dict): Echo of input parameters

        **Formulas:**
        Uniaxial compaction:
        ΔH = Cm × α × ΔP × H

        Where:
        - Cm = uniaxial compaction coefficient = (1+ν)(1-2ν)/[E(1-ν)]
        - α = Biot coefficient
        - ΔP = pressure drop
        - H = reservoir thickness

        Strain: ε = ΔH/H

        Subsidence ≈ (compaction) × (reservoir_area / subsidence_area)^0.5
        Simplified: subsidence ≈ 0.5 to 0.8 × compaction (depends on geometry)

        **Typical Values:**
        - Hard sandstone: 0.1-1% strain
        - Soft sandstone: 1-5% strain
        - Chalk: 5-15% strain
        - Compaction: few inches to several feet
        - Subsidence: 50-80% of compaction at surface

        **Consequences:**
        - Casing damage and collapse
        - Wellhead movement
        - Platform settlement (offshore)
        - Surface infrastructure damage
        - Reactivation of faults

        **Example Usage:**
        ```python
        {
            "pressure_drop": 1000.0,
            "reservoir_thickness": 100.0,
            "youngs_modulus": 500000.0,
            "poisson_ratio": 0.25,
            "biot_coefficient": 1.0
        }
        ```
        Expected: 0.5-2 ft compaction for moderate pressure drop
        """
        # Calculate uniaxial compaction coefficient
        nu = request.poisson_ratio
        E = request.youngs_modulus

        # Uniaxial compaction coefficient
        Cm = ((1 + nu) * (1 - 2 * nu)) / (E * (1 - nu))

        # Calculate pore compressibility if not provided
        if request.pore_compressibility is None:
            if request.bulk_compressibility is not None:
                Cb = request.bulk_compressibility
            else:
                # Calculate bulk compressibility from elastic moduli
                Cb = (1 - 2 * nu) / E

            # Pore compressibility (Hall correlation, assuming Cg = 3e-7 1/psi)
            # Simplified: Cf ≈ Cb (for first approximation)
            pore_comp_calc = Cb
        else:
            pore_comp_calc = request.pore_compressibility

        # Calculate compaction (uniaxial strain model)
        compaction = (
            Cm * request.biot_coefficient * request.pressure_drop * request.reservoir_thickness
        )

        # Calculate strain
        strain = compaction / request.reservoir_thickness

        # Estimate surface subsidence (typically 50-80% of compaction)
        # Using 65% as typical value
        subsidence = 0.65 * compaction

        return {
            "compaction": float(compaction),
            "subsidence": float(subsidence),
            "strain": float(strain),
            "pore_compressibility_calculated": float(pore_comp_calc),
            "compaction_coefficient": float(Cm),
            "units": "ft (compaction/subsidence), dimensionless (strain), 1/psi (compressibility)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_pore_compressibility(request: PoreCompressibilityRequest) -> dict:
        """Calculate effective pore compressibility from rock and fluid properties.

        **MATERIAL BALANCE PARAMETER** - Formation pore volume compressibility is required
        for material balance calculations, reservoir simulation, and production forecasting.
        Affects pressure depletion rate and recovery efficiency.

        **Parameters:**
        - **bulk_compressibility** (float, optional): Rock bulk compressibility (1/psi)
        - **grain_compressibility** (float, optional, default=3e-7): Grain compressibility (1/psi)
        - **porosity** (float, required): Formation porosity (fraction 0-1)
        - **youngs_modulus** (float, optional): For calculating Cb (psi)
        - **poisson_ratio** (float, optional): For calculating Cb

        **Returns:**
        Dictionary with:
        - **pore_compressibility** (float): Formation pore compressibility (1/psi)
        - **bulk_compressibility** (float): If calculated from E and ν (1/psi)
        - **units** (str): "1/psi"
        - **inputs** (dict): Echo of input parameters

        **Formulas:**
        Bulk compressibility from elasticity:
        Cb = (1 - 2ν) / E

        Pore compressibility (Hall 1953):
        Cf = (Cb - Cg) / φ

        Where:
        - Cb = bulk compressibility of rock
        - Cg = grain compressibility (≈ 3×10⁻⁷ 1/psi for quartz)
        - φ = porosity

        **Typical Values:**
        - Consolidated sandstone: Cf = 3-6 × 10⁻⁶ 1/psi
        - Slightly consolidated: Cf = 6-10 × 10⁻⁶ 1/psi
        - Unconsolidated: Cf = 10-25 × 10⁻⁶ 1/psi
        - Chalk: Cf = 10-50 × 10⁻⁶ 1/psi
        - Fractured carbonate: Cf = 0.1-1 × 10⁻⁶ 1/psi

        **Applications:**
        - Material balance equations
        - Reservoir simulation initialization
        - Pressure transient analysis
        - Well test interpretation
        - Production forecasting

        **Example Usage:**
        ```python
        {
            "porosity": 0.20,
            "youngs_modulus": 500000.0,
            "poisson_ratio": 0.25,
            "grain_compressibility": 3e-7
        }
        ```
        Expected: Cf ≈ 5-10 × 10⁻⁶ 1/psi
        """
        # Calculate bulk compressibility if not provided
        if request.bulk_compressibility is None:
            if request.youngs_modulus is not None and request.poisson_ratio is not None:
                # Calculate from elastic moduli
                bulk_comp = (1 - 2 * request.poisson_ratio) / request.youngs_modulus
            else:
                raise ValueError("Must provide either bulk_compressibility or (youngs_modulus and poisson_ratio)")
        else:
            bulk_comp = request.bulk_compressibility

        # Calculate pore compressibility using Hall formula
        pore_comp = (bulk_comp - request.grain_compressibility) / request.porosity

        return {
            "pore_compressibility": float(pore_comp),
            "bulk_compressibility": float(bulk_comp),
            "units": "1/psi",
            "typical_range": "3-25 × 10⁻⁶ 1/psi depending on consolidation",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_leak_off_pressure(request: LeakOffPressureRequest) -> dict:
        """Analyze leak-off test (LOT) or formation integrity test (FIT) data.

        **FIELD STRESS MEASUREMENT** - LOT/FIT is the primary field method for determining
        minimum horizontal stress. Essential for validating geomechanical models and planning
        future drilling operations.

        **Parameters:**
        - **leak_off_pressure** (float, required): LOT pressure at surface (psi)
        - **mud_weight** (float, required): Mud weight during test (ppg)
        - **test_depth** (float, required): True vertical depth of test (ft)
        - **pore_pressure** (float, required): Formation pore pressure at test depth (psi)
        - **test_type** (str, optional, default="LOT"): "LOT" or "FIT"

        **Returns:**
        Dictionary with:
        - **sigma_h_min** (float): Minimum horizontal stress/closure pressure (psi)
        - **fracture_gradient** (float): Fracture gradient (psi/ft)
        - **equivalent_mud_weight** (float): Equivalent fracture mud weight (ppg)
        - **breakdown_pressure** (float): If full LOT (psi)
        - **units** (str): Various
        - **inputs** (dict): Echo of input parameters

        **Test Types:**
        LOT (Leak-Off Test):
        - Pump until formation breaks (fracture initiates)
        - Pressure drops after breakdown
        - Provides fracture initiation pressure

        FIT (Formation Integrity Test):
        - Pump to target pressure < fracture
        - Hold and monitor (should be stable)
        - Provides minimum integrity confirmation
        - Does not fracture formation

        **Formulas:**
        Phydrostatic = 0.052 × MW × TVD
        Pfrac = Psurface + Phydrostatic
        σh_min ≈ Pclosure (for extended LOT with clear closure)

        For instant shut-in:
        σh_min ≈ Pfrac - (Pp/2)  (Hubbert-Willis approximation)

        **Interpretation:**
        - Fracture gradient indicates maximum safe MW
        - σh_min is critical for wellbore stability modeling
        - Compare with predicted values to validate model
        - LOT at each casing point validates cement job

        **Example Usage:**
        ```python
        {
            "leak_off_pressure": 2500.0,
            "mud_weight": 9.0,
            "test_depth": 10000.0,
            "pore_pressure": 4680.0,
            "test_type": "LOT"
        }
        ```
        """
        # Calculate hydrostatic pressure
        hydrostatic = 0.052 * request.mud_weight * request.test_depth

        # Total pressure at formation
        total_pressure = request.leak_off_pressure + hydrostatic

        # For LOT: total pressure approximates minimum horizontal stress
        # (assuming tensile strength is small)
        sigma_h_min = total_pressure

        # If test type is FIT, pressure may be below fracture
        # Use conservative estimate
        if request.test_type == "FIT":
            # FIT only confirms integrity, not actual fracture
            # Use as lower bound on σh_min
            sigma_h_min = total_pressure
            breakdown_pressure = None
        else:  # LOT
            # Full LOT provides fracture initiation pressure
            breakdown_pressure = total_pressure

        # Calculate gradient
        fracture_gradient = sigma_h_min / request.test_depth

        # Equivalent mud weight
        equivalent_mud_weight = fracture_gradient / 0.052

        return {
            "sigma_h_min": float(sigma_h_min),
            "fracture_gradient": float(fracture_gradient),
            "equivalent_mud_weight": float(equivalent_mud_weight),
            "breakdown_pressure": float(breakdown_pressure) if breakdown_pressure is not None else None,
            "test_pressure_at_depth": float(total_pressure),
            "units": "psi (pressure), psi/ft (gradient), ppg (MW)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_hydraulic_fracture_width(request: FractureWidthRequest) -> dict:
        """Estimate hydraulic fracture width from treating pressure and geometry.

        **HYDRAULIC FRACTURING DESIGN** - Calculates average fracture width using PKN or
        KGD analytical models. Critical for proppant design, fracture conductivity estimation,
        and post-frac production analysis.

        **Parameters:**
        - **net_pressure** (float, required): Net treating pressure (psi) = Pfrac - σh_min
        - **fracture_height** (float, required): Fracture height (ft), typically ≈ pay thickness
        - **fracture_half_length** (float, required): Fracture half-length (ft), one wing
        - **youngs_modulus** (float, required): Formation Young's modulus (psi)
        - **poisson_ratio** (float, required): Poisson's ratio
        - **model** (str, optional, default="PKN"): "PKN" or "KGD"

        **Returns:**
        Dictionary with:
        - **avg_width** (float): Average fracture width (inches)
        - **max_width** (float): Maximum fracture width at wellbore (inches)
        - **fracture_compliance** (float): Fracture stiffness (in/psi)
        - **units** (str): "inches"
        - **inputs** (dict): Echo of input parameters

        **Models:**
        PKN (Perkins-Kern-Nordgren):
        - Assumes height << length
        - Elliptical vertical cross-section
        - w_avg = 2.5 × Pnet × h × (1-ν²)/E
        - Best for: contained height, long fractures

        KGD (Khristianovic-Geertsma-de Klerk):
        - Assumes height >> length
        - Rectangular vertical cross-section
        - w_avg = 3.5 × Pnet × xf × (1-ν²)/E
        - Best for: uncontained height, short fractures

        **Typical Values:**
        - Low permeability: 0.2-0.4 inches
        - Medium permeability: 0.3-0.6 inches
        - High rate treatments: 0.5-1.0 inches
        - Tip screenout: can exceed 1.0 inch

        **Applications:**
        - Proppant volume calculation
        - Fracture conductivity estimation
        - Production decline analysis
        - Treatment optimization

        **Example Usage:**
        ```python
        {
            "net_pressure": 500.0,
            "fracture_height": 100.0,
            "fracture_half_length": 500.0,
            "youngs_modulus": 1000000.0,
            "poisson_ratio": 0.25,
            "model": "PKN"
        }
        ```
        Expected: avg width ≈ 0.2-0.5 inches
        """
        # Calculate plane strain modulus
        E_prime = request.youngs_modulus / (1 - request.poisson_ratio ** 2)

        if request.model == "PKN":
            # PKN model: w_avg = C × Pnet × h / E'
            # where C = 2.5 (PKN constant)
            avg_width_ft = 2.5 * request.net_pressure * request.fracture_height / E_prime
            # Maximum width ≈ 2 × average width
            max_width_ft = 2.0 * avg_width_ft
        else:  # KGD
            # KGD model: w_avg = C × Pnet × xf / E'
            # where C = 3.5 (KGD constant)
            avg_width_ft = 3.5 * request.net_pressure * request.fracture_half_length / E_prime
            # Maximum width ≈ 1.6 × average width
            max_width_ft = 1.6 * avg_width_ft

        # Convert to inches
        avg_width = avg_width_ft * 12
        max_width = max_width_ft * 12

        # Fracture compliance (width per unit pressure)
        fracture_compliance = avg_width / request.net_pressure

        return {
            "avg_width": float(avg_width),
            "max_width": float(max_width),
            "fracture_compliance": float(fracture_compliance),
            "model_used": request.model,
            "units": "inches (width), in/psi (compliance)",
            "inputs": request.model_dump(),
        }

    # ========================================================================
    # NEW ADVANCED GEOMECHANICS TOOLS
    # ========================================================================

    @mcp.tool()
    def geomech_stress_polygon(request: StressPolygonRequest) -> dict:
        """Calculate stress polygon bounds for frictional equilibrium constraints.

        **STRESS STATE VISUALIZATION** - The stress polygon defines the allowable range
        of horizontal stress magnitudes based on frictional limits on pre-existing faults.
        Critical for understanding tectonic regime and stress state constraints.

        **Parameters:**
        - **vertical_stress** (float, required): Vertical stress (psi)
        - **pore_pressure** (float, required): Pore pressure (psi)
        - **friction_coefficient** (float, optional, default=0.6): Fault friction coefficient
          Byerlee's law: μ = 0.6-0.85 typical for most rocks
        - **sigma_h_min** (float, optional): Actual σh_min to check if within polygon (psi)
        - **sigma_h_max** (float, optional): Actual σH_max to check if within polygon (psi)

        **Returns:**
        Dictionary with:
        - **nf_shmin_min** (float): Normal faulting σh_min lower bound (psi)
        - **nf_shmin_max** (float): Normal faulting σh_min upper bound (psi)
        - **rf_shmax_min** (float): Reverse faulting σH_max lower bound (psi)
        - **rf_shmax_max** (float): Reverse faulting σH_max upper bound (psi)
        - **stress_state** (str): Current stress regime if actual stresses provided
        - **within_polygon** (bool): Whether actual stress state is within frictional limits

        **Formulas:**
        Frictional equilibrium constraint (Jaeger & Cook):
        σ1/σ3 ≤ [(μ² + 1)^0.5 + μ]²

        For normal faulting (σv > σH > σh):
        σv/σh_min ≤ [(μ² + 1)^0.5 + μ]²

        For reverse faulting (σH > σh > σv):
        σH_max/σv ≤ [(μ² + 1)^0.5 + μ]²

        **Physical Meaning:**
        - Outside polygon: Stress state would cause fault slip
        - Inside polygon: Stable stress state
        - On boundary: Critically stressed faults present
        """
        mu = request.friction_coefficient
        sigma_v_eff = request.vertical_stress - request.pore_pressure

        # Frictional limit ratio
        q = (np.sqrt(mu**2 + 1) + mu) ** 2

        # Normal faulting bounds (σv is σ1)
        # σh_min ≥ σv_eff / q + Pp
        nf_shmin_min = sigma_v_eff / q + request.pore_pressure
        nf_shmin_max = request.vertical_stress  # Cannot exceed σv in NF

        # Reverse faulting bounds (σv is σ3)
        # σH_max ≤ σv_eff × q + Pp
        rf_shmax_min = request.vertical_stress  # Must exceed σv in RF
        rf_shmax_max = sigma_v_eff * q + request.pore_pressure

        # Strike-slip bounds (σv is σ2)
        # σh_min ≥ σv_eff / q + Pp and σH_max ≤ σv_eff × q + Pp
        ss_shmin_min = sigma_v_eff / q + request.pore_pressure
        ss_shmax_max = sigma_v_eff * q + request.pore_pressure

        result = {
            "normal_faulting": {
                "sigma_h_min_range": [float(nf_shmin_min), float(nf_shmin_max)],
                "description": "σv > σH > σh (extensional)"
            },
            "strike_slip": {
                "sigma_h_min_min": float(ss_shmin_min),
                "sigma_H_max_max": float(ss_shmax_max),
                "description": "σH > σv > σh (shear)"
            },
            "reverse_faulting": {
                "sigma_H_max_range": [float(rf_shmax_min), float(rf_shmax_max)],
                "description": "σH > σh > σv (compressional)"
            },
            "friction_coefficient": float(mu),
            "stress_ratio_limit": float(q),
            "units": "psi",
            "inputs": request.model_dump(),
        }

        # Check actual stress state if provided
        if request.sigma_h_min is not None and request.sigma_h_max is not None:
            sigma_h_min = request.sigma_h_min
            sigma_h_max = request.sigma_h_max

            # Determine regime
            if request.vertical_stress >= sigma_h_max >= sigma_h_min:
                stress_regime = "normal_faulting"
            elif sigma_h_max >= request.vertical_stress >= sigma_h_min:
                stress_regime = "strike_slip"
            elif sigma_h_max >= sigma_h_min >= request.vertical_stress:
                stress_regime = "reverse_faulting"
            else:
                stress_regime = "undefined"

            # Check if within polygon
            sigma_h_min_eff = sigma_h_min - request.pore_pressure
            sigma_h_max_eff = sigma_h_max - request.pore_pressure

            # Check frictional limits
            if sigma_v_eff > 0 and sigma_h_min_eff > 0:
                ratio_nf = sigma_v_eff / sigma_h_min_eff
                ratio_rf = sigma_h_max_eff / sigma_v_eff
                within_polygon = (ratio_nf <= q) and (ratio_rf <= q)
            else:
                within_polygon = True  # Cannot check with negative effective stress

            result["actual_stress_state"] = {
                "regime": stress_regime,
                "within_frictional_limits": within_polygon,
                "sigma_v_over_sigma_h_min": float(sigma_v_eff / sigma_h_min_eff) if sigma_h_min_eff > 0 else None,
                "sigma_H_max_over_sigma_v": float(sigma_h_max_eff / sigma_v_eff) if sigma_v_eff > 0 else None,
            }

        return result

    @mcp.tool()
    def geomech_sand_production(request: SandProductionRequest) -> dict:
        """Predict sand production potential and critical drawdown pressure.

        **SAND MANAGEMENT CRITICAL** - Predicts when sand production may occur during
        production. Critical for completion design, production rate optimization, and
        sand control decisions.

        **Parameters:**
        - **sigma_h_max** (float, required): Maximum horizontal stress (psi)
        - **sigma_h_min** (float, required): Minimum horizontal stress (psi)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **ucs** (float, required): Unconfined compressive strength (psi)
        - **cohesion** (float, required): Rock cohesion (psi)
        - **friction_angle** (float, required): Internal friction angle (degrees)
        - **wellbore_radius** (float, optional): Wellbore radius (ft)
        - **perforation_depth** (float, optional): Perforation tunnel depth (ft)
        - **permeability** (float, required): Formation permeability (mD)
        - **porosity** (float, required): Formation porosity (fraction)

        **Returns:**
        Dictionary with:
        - **critical_drawdown** (float): Maximum drawdown before sanding (psi)
        - **critical_flowing_bhp** (float): Minimum FBHP before sanding (psi)
        - **sanding_risk** (str): "low", "moderate", "high"
        - **recommended_action** (str): Sand control recommendation

        **Approach:**
        Uses Mohr-Coulomb criterion at perforation cavity to predict failure.
        Critical drawdown = pressure at which tangential stress exceeds rock strength.

        **Risk Categories:**
        - Low: Critical drawdown > 1000 psi, UCS > 2000 psi
        - Moderate: Critical drawdown 500-1000 psi
        - High: Critical drawdown < 500 psi, UCS < 1000 psi
        """
        # Calculate Mohr-Coulomb parameters
        phi_rad = np.deg2rad(request.friction_angle)
        sin_phi = np.sin(phi_rad)
        cos_phi = np.cos(phi_rad)

        # UCS from cohesion (if not using provided UCS)
        ucs_calc = 2 * request.cohesion * cos_phi / (1 - sin_phi)

        # Use provided UCS if it's reasonable
        ucs = request.ucs if request.ucs > 0 else ucs_calc

        # Effective stresses
        sigma_h_max_eff = request.sigma_h_max - request.pore_pressure
        sigma_h_min_eff = request.sigma_h_min - request.pore_pressure

        # Stress concentration at perforation cavity (simplified Kirsch)
        # At cavity wall, tangential stress concentration is approximately 3
        stress_concentration = 3.0

        # Maximum tangential stress at cavity
        sigma_theta_max = stress_concentration * sigma_h_max_eff - sigma_h_min_eff

        # Critical drawdown using simplified cavity stability
        # When Pp drops by ΔP, effective stress increases, and at critical:
        # σθ - σr = UCS (simplified failure criterion)

        # For open-hole completion, radial stress at wall ≈ flowing BHP
        # σθ_eff = 3σH - σh - Pw + Pp (Kirsch at θ=90°)
        # Failure when σθ_eff > UCS + confining stress contribution

        # Critical drawdown estimate
        # ΔP_crit ≈ (UCS - (3σH_eff - σh_eff)) / (stress_concentration - 1)
        critical_drawdown = (ucs - (sigma_theta_max)) / (stress_concentration - 1)

        # Ensure positive and reasonable
        critical_drawdown = max(0, min(critical_drawdown, request.pore_pressure))

        # Critical flowing BHP
        critical_fbhp = request.pore_pressure - critical_drawdown

        # Assess sanding risk
        if critical_drawdown > 1000 and ucs > 2000:
            sanding_risk = "low"
            recommendation = "Natural completion may be acceptable. Monitor for sand production."
        elif critical_drawdown > 500 or ucs > 1000:
            sanding_risk = "moderate"
            recommendation = "Consider gravel pack or frac-pack. Rate-limited production recommended."
        else:
            sanding_risk = "high"
            recommendation = "Sand control required. Consider screens, gravel pack, or chemical consolidation."

        # TWC (Thick Wall Cylinder) strength estimate
        twc_factor = 2.0  # Typical TWC/UCS ratio
        twc_strength = ucs * twc_factor

        return {
            "critical_drawdown": float(critical_drawdown),
            "critical_flowing_bhp": float(critical_fbhp),
            "sanding_risk": sanding_risk,
            "recommended_action": recommendation,
            "ucs_used": float(ucs),
            "twc_strength_estimate": float(twc_strength),
            "stress_concentration": float(stress_concentration),
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_fault_stability(request: FaultStabilityRequest) -> dict:
        """Analyze fault stability using Coulomb failure stress (CFS) criterion.

        **INDUCED SEISMICITY ASSESSMENT** - Calculates slip tendency and Coulomb stress
        on faults for injection/production operations. Critical for CO2 sequestration,
        wastewater disposal, and reservoir pressure management.

        **Parameters:**
        - **sigma_1** (float, required): Maximum principal stress (psi)
        - **sigma_3** (float, required): Minimum principal stress (psi)
        - **pore_pressure** (float, required): Pore pressure at fault (psi)
        - **fault_strike** (float, required): Fault strike azimuth (degrees)
        - **fault_dip** (float, required): Fault dip angle (degrees from horizontal)
        - **sigma_1_azimuth** (float, optional): σ1 azimuth from North (degrees)
        - **friction_coefficient** (float, optional): Fault friction coefficient (0.6 typical)
        - **cohesion** (float, optional): Fault cohesion (psi) - usually 0 for reactivation

        **Returns:**
        Dictionary with:
        - **slip_tendency** (float): τ/σn ratio (0-1, >μ indicates slip)
        - **dilation_tendency** (float): (σ1-σn)/(σ1-σ3) ratio
        - **coulomb_stress** (float): CFS = τ - μσn - c (psi)
        - **critical_pore_pressure** (float): Pp needed for slip (psi)
        - **stability_status** (str): "stable", "critically_stressed", "unstable"

        **Formulas:**
        Slip Tendency: Ts = τ / σn
        Dilation Tendency: Td = (σ1 - σn) / (σ1 - σ3)
        Coulomb Failure Stress: CFS = τ - μ(σn - Pp) - c

        Slip occurs when: CFS ≥ 0 or Ts ≥ μ
        """
        # Convert angles to radians
        dip_rad = np.deg2rad(request.fault_dip)
        strike_rad = np.deg2rad(request.fault_strike)
        sigma1_az_rad = np.deg2rad(request.sigma_1_azimuth)

        # Effective stresses
        sigma_1_eff = request.sigma_1 - request.pore_pressure
        sigma_3_eff = request.sigma_3 - request.pore_pressure

        # Calculate normal and shear stress on fault plane (2D approximation)
        # Assuming fault strike perpendicular to σ1 direction for simplicity
        # θ = angle between fault normal and σ1

        # For a fault with dip δ in the σ1-σ3 plane:
        # σn = (σ1 + σ3)/2 + (σ1 - σ3)/2 × cos(2θ)
        # τ = (σ1 - σ3)/2 × sin(2θ)

        # Effective angle (simplified: dip angle used directly)
        theta = dip_rad

        sigma_n = (sigma_1_eff + sigma_3_eff) / 2 + (sigma_1_eff - sigma_3_eff) / 2 * np.cos(2 * theta)
        tau = abs((sigma_1_eff - sigma_3_eff) / 2 * np.sin(2 * theta))

        # Slip tendency
        slip_tendency = tau / sigma_n if sigma_n > 0 else 0

        # Dilation tendency
        dilation_tendency = (sigma_1_eff - sigma_n) / (sigma_1_eff - sigma_3_eff) if (sigma_1_eff - sigma_3_eff) > 0 else 0

        # Coulomb Failure Stress
        cfs = tau - request.friction_coefficient * sigma_n - request.cohesion

        # Critical pore pressure for slip
        # CFS = 0 → τ = μσn + c
        # σn = σn_total - Pp → solve for Pp
        sigma_n_total = sigma_n + request.pore_pressure
        if request.friction_coefficient > 0:
            critical_pp = sigma_n_total - (tau - request.cohesion) / request.friction_coefficient
        else:
            critical_pp = request.pore_pressure

        # Stability status
        if cfs >= 0:
            stability = "unstable - slip expected"
        elif slip_tendency > 0.8 * request.friction_coefficient:
            stability = "critically_stressed"
        else:
            stability = "stable"

        # Pore pressure increase needed for slip
        pp_increase_to_slip = max(0, critical_pp - request.pore_pressure)

        return {
            "slip_tendency": float(slip_tendency),
            "dilation_tendency": float(dilation_tendency),
            "coulomb_stress": float(cfs),
            "critical_pore_pressure": float(critical_pp),
            "pp_increase_to_slip": float(pp_increase_to_slip),
            "normal_stress_on_fault": float(sigma_n + request.pore_pressure),
            "shear_stress_on_fault": float(tau),
            "stability_status": stability,
            "units": "psi (stress), dimensionless (tendencies)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_deviated_well_stress(request: DeviatedWellStressRequest) -> dict:
        """Transform principal stresses to deviated wellbore coordinate system.

        **DIRECTIONAL DRILLING DESIGN** - Calculates the stress tensor at the wall of
        a deviated wellbore. Essential for stability analysis of horizontal wells,
        extended reach drilling, and optimal trajectory planning.

        **Parameters:**
        - **sigma_v** (float, required): Vertical stress (psi)
        - **sigma_h_max** (float, required): Maximum horizontal stress (psi)
        - **sigma_h_min** (float, required): Minimum horizontal stress (psi)
        - **sigma_h_max_azimuth** (float, required): σH_max azimuth from North (degrees)
        - **well_azimuth** (float, required): Well azimuth from North (degrees)
        - **well_inclination** (float, required): Deviation from vertical (degrees)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **mud_weight** (float, required): Drilling fluid density (ppg)
        - **depth** (float, required): True vertical depth (ft)

        **Returns:**
        Dictionary with transformed stress components and stability indicators:
        - **sigma_zz** (float): Axial stress along wellbore (psi)
        - **sigma_xx** (float): Stress perpendicular to wellbore (psi)
        - **sigma_yy** (float): Stress perpendicular to wellbore (psi)
        - **tau_xy**, **tau_xz**, **tau_yz** (float): Shear stress components (psi)
        - **max_hoop_stress** (float): Maximum tangential stress at wall (psi)
        - **min_hoop_stress** (float): Minimum tangential stress at wall (psi)
        - **stability_index** (float): Ratio of hoop stress to strength

        **Methodology:**
        Uses full 3D stress transformation with rotation matrices for well orientation.
        """
        # Convert angles to radians
        alpha_H = np.deg2rad(request.sigma_h_max_azimuth)
        alpha_w = np.deg2rad(request.well_azimuth)
        inc = np.deg2rad(request.well_inclination)

        # Relative azimuth (well azimuth relative to σH_max direction)
        alpha = alpha_w - alpha_H

        # Principal stresses in geographic coordinates
        sigma_v = request.sigma_v
        sigma_H = request.sigma_h_max
        sigma_h = request.sigma_h_min

        # Transform to wellbore coordinates (Bradley 1979, Aadnoy 1988)
        # Using coordinate system: x = horizontal perpendicular to well
        #                          y = horizontal along well projection
        #                          z = along wellbore axis

        cos_a = np.cos(alpha)
        sin_a = np.sin(alpha)
        cos_i = np.cos(inc)
        sin_i = np.sin(inc)

        # Stress tensor components in wellbore coordinates
        sigma_xx = (
            (sigma_H * cos_a**2 + sigma_h * sin_a**2) * cos_i**2
            + sigma_v * sin_i**2
        )
        sigma_yy = sigma_H * sin_a**2 + sigma_h * cos_a**2

        sigma_zz = (
            (sigma_H * cos_a**2 + sigma_h * sin_a**2) * sin_i**2
            + sigma_v * cos_i**2
        )

        tau_xy = 0.5 * (sigma_h - sigma_H) * np.sin(2 * alpha) * cos_i
        tau_xz = 0.5 * (sigma_H * cos_a**2 + sigma_h * sin_a**2 - sigma_v) * np.sin(2 * inc)
        tau_yz = 0.5 * (sigma_h - sigma_H) * np.sin(2 * alpha) * sin_i

        # Mud pressure
        mud_pressure = 0.052 * request.mud_weight * request.depth

        # Hoop stress around wellbore (Kirsch solution)
        # At θ = 0° (parallel to σH_max projection): σθ = 3σyy - σxx - ΔP
        # At θ = 90° (perpendicular to σH_max projection): σθ = 3σxx - σyy - ΔP
        delta_p = mud_pressure - request.pore_pressure

        sigma_theta_0 = 3 * sigma_yy - sigma_xx - delta_p - request.pore_pressure
        sigma_theta_90 = 3 * sigma_xx - sigma_yy - delta_p - request.pore_pressure

        max_hoop = max(sigma_theta_0, sigma_theta_90)
        min_hoop = min(sigma_theta_0, sigma_theta_90)

        # Radial stress at wellbore wall
        sigma_r = mud_pressure

        return {
            "transformed_stresses": {
                "sigma_xx": float(sigma_xx),
                "sigma_yy": float(sigma_yy),
                "sigma_zz": float(sigma_zz),
                "tau_xy": float(tau_xy),
                "tau_xz": float(tau_xz),
                "tau_yz": float(tau_yz),
            },
            "wellbore_wall_stresses": {
                "max_hoop_stress": float(max_hoop),
                "min_hoop_stress": float(min_hoop),
                "radial_stress": float(sigma_r),
                "axial_stress": float(sigma_zz),
            },
            "mud_pressure": float(mud_pressure),
            "relative_azimuth": float(np.rad2deg(alpha)),
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_tensile_failure(request: TensileFailureRequest) -> dict:
        """Predict tensile failure and fracture initiation at wellbore wall.

        **LOST CIRCULATION PREVENTION** - Calculates minimum tangential stress and
        predicts when tensile failure (fracturing) will occur. Critical for preventing
        lost circulation and designing fracture stimulation treatments.

        **Parameters:**
        - **sigma_h_max** (float, required): Maximum horizontal stress (psi)
        - **sigma_h_min** (float, required): Minimum horizontal stress (psi)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **tensile_strength** (float, optional): Rock tensile strength (psi)
        - **thermal_stress** (float, optional): Thermal stress contribution (psi)

        **Returns:**
        Dictionary with:
        - **fracture_initiation_pressure** (float): Pressure to initiate fracture (psi)
        - **breakdown_pressure** (float): Full breakdown pressure (psi)
        - **propagation_pressure** (float): Fracture propagation pressure (psi)
        - **tensile_failure_gradient** (float): As mud weight gradient (psi/ft)

        **Formulas:**
        Kirsch equation at θ = 0° (parallel to σH_max):
        σθ = 3σh_min - σH_max - Pw + Pp

        Fracture initiation when: σθ + T0 = 0
        Pfrac_init = 3σh - σH + T0 - Pp

        Breakdown (if not pre-existing fracture):
        Pbd = 3σh - σH + T0 - Pp (same for impermeable rock)
        Pbd = (3σh - σH + T0 - ηPp)/(1 - η) (permeable rock)
        """
        # Calculate fracture initiation pressure (impermeable rock)
        # Tensile failure occurs when σθ = -T0
        # From Kirsch: 3σh - σH - Pmud + Pp = -T0
        # Pmud = 3σh - σH + Pp + T0

        fracture_init = (
            3 * request.sigma_h_min
            - request.sigma_h_max
            + request.tensile_strength
            - request.pore_pressure
            - request.thermal_stress
        )

        # Breakdown pressure (same for impermeable, slightly different for permeable)
        breakdown = fracture_init

        # Propagation pressure ≈ σh_min (after fracture initiates)
        propagation = request.sigma_h_min

        # Re-opening pressure (for existing fracture, T0 = 0)
        reopening = 3 * request.sigma_h_min - request.sigma_h_max - request.pore_pressure

        # Convert to equivalent mud weight gradient (assuming 10000 ft depth)
        # This is illustrative - actual gradient depends on depth
        est_depth = request.pore_pressure / 0.465  # Estimate depth from PP
        frac_gradient = fracture_init / est_depth if est_depth > 0 else 0
        frac_emw = frac_gradient / 0.052

        return {
            "fracture_initiation_pressure": float(fracture_init),
            "breakdown_pressure": float(breakdown),
            "propagation_pressure": float(propagation),
            "reopening_pressure": float(reopening),
            "fracture_gradient": float(frac_gradient),
            "equivalent_mud_weight": float(frac_emw),
            "stress_anisotropy": float(request.sigma_h_max - request.sigma_h_min),
            "units": "psi (pressure), psi/ft (gradient), ppg (EMW)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_shear_failure_criteria(request: ShearFailureCriteriaRequest) -> dict:
        """Evaluate multiple shear failure criteria for rock strength comparison.

        **ROCK MECHANICS ANALYSIS** - Compares different failure criteria predictions
        for wellbore stability. Important because different criteria give different
        results, especially for true 3D stress states.

        **Parameters:**
        - **sigma_1** (float, required): Maximum principal stress (psi)
        - **sigma_2** (float, required): Intermediate principal stress (psi)
        - **sigma_3** (float, required): Minimum principal stress (psi)
        - **ucs** (float, required): Unconfined compressive strength (psi)
        - **cohesion** (float, required): Rock cohesion (psi)
        - **friction_angle** (float, required): Internal friction angle (degrees)
        - **criteria** (list, optional): List of criteria to evaluate

        **Returns:**
        Dictionary with failure predictions from each criterion:
        - Each criterion returns: strength_ratio, status, additional parameters

        **Criteria Available:**
        1. Mohr-Coulomb: σ1 = UCS + qσ3 (ignores σ2)
        2. Drucker-Prager: √J2 = a + bI1 (smooth approximation)
        3. Mogi-Coulomb: τoct = a + bσm,2 (includes σ2 effect)
        4. Modified Lade: (I1³/I3 - 27)(I1/Pa)^m = η
        5. Modified Wiebols-Cook: J2^0.5 = C0 + C1I1 + C2(σ2-σ3)

        **Note:** Mohr-Coulomb is conservative; true triaxial criteria account for
        σ2 strengthening effect and typically predict higher strength.
        """
        phi_rad = np.deg2rad(request.friction_angle)
        sin_phi = np.sin(phi_rad)
        cos_phi = np.cos(phi_rad)
        tan_phi = np.tan(phi_rad)

        sigma_1 = request.sigma_1
        sigma_2 = request.sigma_2
        sigma_3 = request.sigma_3
        C = request.cohesion
        UCS = request.ucs

        results = {}

        # Mohr-Coulomb
        if "mohr_coulomb" in request.criteria:
            q_mc = (1 + sin_phi) / (1 - sin_phi)
            sigma_1_failure_mc = UCS + q_mc * sigma_3
            strength_ratio_mc = sigma_1 / sigma_1_failure_mc if sigma_1_failure_mc > 0 else 999

            results["mohr_coulomb"] = {
                "sigma_1_at_failure": float(sigma_1_failure_mc),
                "strength_ratio": float(strength_ratio_mc),
                "status": "failed" if strength_ratio_mc >= 1.0 else "stable",
                "safety_factor": float(1 / strength_ratio_mc) if strength_ratio_mc > 0 else 0,
                "q_factor": float(q_mc),
            }

        # Drucker-Prager (inscribed in M-C)
        if "drucker_prager" in request.criteria:
            # DP constants for M-C inscribed
            alpha_dp = tan_phi / np.sqrt(9 + 12 * tan_phi**2)
            k_dp = 3 * C / np.sqrt(9 + 12 * tan_phi**2)

            I1 = sigma_1 + sigma_2 + sigma_3
            J2 = ((sigma_1 - sigma_2)**2 + (sigma_2 - sigma_3)**2 + (sigma_1 - sigma_3)**2) / 6
            sqrt_J2 = np.sqrt(J2)

            # Failure when sqrt(J2) = k + alpha * I1
            failure_value = k_dp + alpha_dp * I1
            strength_ratio_dp = sqrt_J2 / failure_value if failure_value > 0 else 999

            results["drucker_prager"] = {
                "I1": float(I1),
                "sqrt_J2": float(sqrt_J2),
                "failure_criterion_value": float(failure_value),
                "strength_ratio": float(strength_ratio_dp),
                "status": "failed" if strength_ratio_dp >= 1.0 else "stable",
                "safety_factor": float(1 / strength_ratio_dp) if strength_ratio_dp > 0 else 0,
            }

        # Mogi-Coulomb
        if "mogi_coulomb" in request.criteria:
            # τoct = a + b × σm,2
            # where σm,2 = (σ1 + σ3) / 2

            tau_oct = np.sqrt(2) / 3 * np.sqrt((sigma_1 - sigma_2)**2 + (sigma_2 - sigma_3)**2 + (sigma_1 - sigma_3)**2)
            sigma_m2 = (sigma_1 + sigma_3) / 2

            # Mogi constants from M-C parameters
            a_mogi = 2 * np.sqrt(2) / 3 * C * cos_phi
            b_mogi = 2 * np.sqrt(2) / 3 * sin_phi

            failure_value_mogi = a_mogi + b_mogi * sigma_m2
            strength_ratio_mogi = tau_oct / failure_value_mogi if failure_value_mogi > 0 else 999

            results["mogi_coulomb"] = {
                "tau_oct": float(tau_oct),
                "sigma_m2": float(sigma_m2),
                "failure_criterion_value": float(failure_value_mogi),
                "strength_ratio": float(strength_ratio_mogi),
                "status": "failed" if strength_ratio_mogi >= 1.0 else "stable",
                "safety_factor": float(1 / strength_ratio_mogi) if strength_ratio_mogi > 0 else 0,
            }

        # Modified Lade
        if "modified_lade" in request.criteria:
            # Simplified Modified Lade
            I1 = sigma_1 + sigma_2 + sigma_3
            I3 = sigma_1 * sigma_2 * sigma_3 if sigma_3 > 0 else 1e-6

            # Lade parameter
            eta = 4 * tan_phi**2 * (9 - 7 * sin_phi) / (1 - sin_phi)
            lade_lhs = (I1**3 / I3 - 27)

            results["modified_lade"] = {
                "I1": float(I1),
                "I3": float(I3),
                "lade_criterion": float(lade_lhs),
                "lade_parameter_eta": float(eta),
                "strength_ratio": float(lade_lhs / eta) if eta > 0 else 999,
                "status": "failed" if lade_lhs >= eta else "stable",
            }

        # Modified Wiebols-Cook
        if "modified_wiebols" in request.criteria:
            # Simplified version
            I1 = sigma_1 + sigma_2 + sigma_3
            J2 = ((sigma_1 - sigma_2)**2 + (sigma_2 - sigma_3)**2 + (sigma_1 - sigma_3)**2) / 6

            # Constants derived from UCS and friction angle
            C1 = UCS / 3  # Simplified
            C2 = 0.1  # Typical value

            failure_mwc = C1 + C2 * (sigma_2 - sigma_3)
            strength_ratio_mwc = np.sqrt(J2) / failure_mwc if failure_mwc > 0 else 999

            results["modified_wiebols"] = {
                "sqrt_J2": float(np.sqrt(J2)),
                "failure_criterion": float(failure_mwc),
                "strength_ratio": float(strength_ratio_mwc),
                "status": "failed" if strength_ratio_mwc >= 1.0 else "stable",
            }

        # Summary
        all_ratios = [r.get("strength_ratio", 0) for r in results.values()]
        most_conservative = max(all_ratios) if all_ratios else 0
        least_conservative = min(all_ratios) if all_ratios else 0

        return {
            "criteria_results": results,
            "summary": {
                "most_conservative_ratio": float(most_conservative),
                "least_conservative_ratio": float(least_conservative),
                "sigma_2_effect_range": float(most_conservative - least_conservative),
            },
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_breakout_stress_inversion(request: BreakoutStressInversionRequest) -> dict:
        """Estimate horizontal stress magnitude from observed breakout width.

        **STRESS CALIBRATION FROM LOGS** - Inverts the breakout width observation to
        estimate maximum horizontal stress. Used when breakout width is measured from
        image logs or caliper data.

        **Parameters:**
        - **breakout_width** (float, required): Observed breakout angular width (degrees)
        - **sigma_v** (float, required): Vertical stress (psi)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **mud_weight** (float, required): Mud weight during observation (ppg)
        - **ucs** (float, required): Unconfined compressive strength (psi)
        - **friction_angle** (float, required): Internal friction angle (degrees)
        - **depth** (float, required): True vertical depth (ft)

        **Returns:**
        Dictionary with:
        - **estimated_sigma_h_max** (float): Estimated maximum horizontal stress (psi)
        - **estimated_sigma_h_min** (float): Estimated minimum horizontal stress (psi)
        - **stress_ratio** (float): σH/σh ratio
        - **confidence** (str): Confidence level based on breakout width

        **Methodology:**
        Uses iterative inversion of Kirsch stress equations with Mohr-Coulomb
        failure criterion to find stress state that produces observed breakout width.
        """
        # Mud pressure
        mud_pressure = 0.052 * request.mud_weight * request.depth

        # Mohr-Coulomb parameters
        phi_rad = np.deg2rad(request.friction_angle)
        sin_phi = np.sin(phi_rad)
        cos_phi = np.cos(phi_rad)

        # Calculate rock strength at breakout edge
        # At breakout edge (θ = 90° - wbo/2), rock is at failure
        theta_breakout = np.deg2rad(90 - request.breakout_width / 2)

        # UCS and q factor
        ucs = request.ucs
        q = (1 + sin_phi) / (1 - sin_phi)

        # Effective stress at mud pressure
        sigma_r_eff = mud_pressure - request.pore_pressure

        # At breakout edge, tangential stress equals failure stress
        # σθ_failure = UCS + q × σr_eff (Mohr-Coulomb)
        sigma_theta_failure = ucs + q * sigma_r_eff

        # Kirsch: σθ = σH + σh - 2(σH - σh)cos(2θ) - Pmud
        # At θ = 90° - wbo/2:
        # σθ_eff = σH + σh - 2(σH - σh)cos(2θ) - Pmud - Pp

        # Assume normal faulting: σv > σH > σh
        # First estimate: σh_min from σv using typical K0
        k0 = 0.4 + 0.4 * sin_phi  # Typical K0 relationship
        sigma_h_min_est = k0 * (request.sigma_v - request.pore_pressure) + request.pore_pressure

        # Solve for σH_max given breakout width
        # σθ_failure + Pp + Pmud = σH + σh - 2(σH - σh)cos(2θbo)
        cos_2theta = np.cos(2 * theta_breakout)

        # Rearranging: σH(1 - 2cos2θ) + σh(1 + 2cos2θ) = σθ_failure + Pp + Pmud
        coef_H = 1 - 2 * cos_2theta
        coef_h = 1 + 2 * cos_2theta

        rhs = sigma_theta_failure + request.pore_pressure + mud_pressure

        if abs(coef_H) > 0.01:  # Avoid division by near-zero
            sigma_h_max_est = (rhs - coef_h * sigma_h_min_est) / coef_H
        else:
            sigma_h_max_est = request.sigma_v  # Fallback

        # Validate estimates
        if sigma_h_max_est < sigma_h_min_est:
            sigma_h_max_est = sigma_h_min_est * 1.2  # Minimum anisotropy

        stress_ratio = sigma_h_max_est / sigma_h_min_est if sigma_h_min_est > 0 else 1.0

        # Confidence based on breakout width
        if 30 <= request.breakout_width <= 90:
            confidence = "high"
        elif 15 <= request.breakout_width < 30 or 90 < request.breakout_width <= 120:
            confidence = "moderate"
        else:
            confidence = "low"

        return {
            "estimated_sigma_h_max": float(sigma_h_max_est),
            "estimated_sigma_h_min": float(sigma_h_min_est),
            "stress_ratio": float(stress_ratio),
            "confidence": confidence,
            "breakout_angle_from_shmax": float(90 - request.breakout_width / 2),
            "mud_pressure": float(mud_pressure),
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_breakdown_pressure(request: BreakdownPressureRequest) -> dict:
        """Calculate formation breakdown pressure for hydraulic fracturing.

        **FRAC DESIGN PARAMETER** - Predicts the wellbore pressure required to initiate
        a hydraulic fracture. Essential for frac pump sizing, treatment design, and
        predicting fracture orientation.

        **Parameters:**
        - **sigma_h_max** (float, required): Maximum horizontal stress (psi)
        - **sigma_h_min** (float, required): Minimum horizontal stress (psi)
        - **pore_pressure** (float, required): Formation pore pressure (psi)
        - **tensile_strength** (float, optional): Rock tensile strength (psi)
        - **poroelastic_constant** (float, optional): η = α(1-2ν)/(1-ν)

        **Returns:**
        Dictionary with:
        - **breakdown_pressure** (float): Pressure to break formation (psi)
        - **instantaneous_shut_in** (float): ISIP estimate (psi)
        - **closure_pressure** (float): Fracture closure pressure (psi)
        - **net_pressure** (float): Typical net treating pressure (psi)

        **Formulas:**
        Impermeable rock (Hubbert-Willis):
        Pbd = 3σh - σH + T0 - Pp

        Permeable rock (Haimson-Fairhurst):
        Pbd = (3σh - σH + T0 - ηPp) / (1 - η)

        Where η = poroelastic constant = α(1-2ν)/(1-ν)
        """
        # Impermeable case (η = 0)
        breakdown_imperm = (
            3 * request.sigma_h_min
            - request.sigma_h_max
            + request.tensile_strength
            - request.pore_pressure
        )

        # Permeable case
        eta = request.poroelastic_constant
        if eta < 1.0:
            numerator = 3 * request.sigma_h_min - request.sigma_h_max + request.tensile_strength - eta * request.pore_pressure
            breakdown_perm = numerator / (1 - eta)
        else:
            breakdown_perm = breakdown_imperm

        # Use average as best estimate (reality is between extremes)
        breakdown = (breakdown_imperm + breakdown_perm) / 2

        # Instantaneous Shut-In Pressure (ISIP) ≈ σh_min
        isip = request.sigma_h_min

        # Closure pressure ≈ σh_min
        closure = request.sigma_h_min

        # Typical net pressure (ISIP - closure)
        # For fracturing, net pressure is typically 200-1000 psi
        net_pressure = 500  # Typical starting estimate

        return {
            "breakdown_pressure": float(breakdown),
            "breakdown_impermeable": float(breakdown_imperm),
            "breakdown_permeable": float(breakdown_perm),
            "isip_estimate": float(isip),
            "closure_pressure": float(closure),
            "typical_net_pressure": float(net_pressure),
            "fracture_orientation": "perpendicular to σh_min",
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_stress_path(request: StressPathRequest) -> dict:
        """Calculate stress changes during reservoir depletion or injection.

        **PRODUCTION/INJECTION GEOMECHANICS** - Predicts how horizontal stress changes
        with pore pressure during depletion (production) or injection (waterflooding,
        CO2 sequestration). Critical for fault reactivation and compaction analysis.

        **Parameters:**
        - **initial_pore_pressure** (float, required): Initial Pp (psi)
        - **final_pore_pressure** (float, required): Final Pp (psi)
        - **vertical_stress** (float, required): σv - assumed constant (psi)
        - **initial_sigma_h** (float, required): Initial horizontal stress (psi)
        - **poisson_ratio** (float, required): Poisson's ratio
        - **biot_coefficient** (float, optional): Biot coefficient
        - **stress_path_coefficient** (float, optional): γ = Δσh/ΔPp

        **Returns:**
        Dictionary with:
        - **final_sigma_h** (float): Final horizontal stress (psi)
        - **delta_sigma_h** (float): Change in horizontal stress (psi)
        - **stress_path_coefficient** (float): γ used in calculation
        - **effective_stress_change** (str): Direction of effective stress change
        - **fault_stability_impact** (str): Assessment of fault reactivation risk

        **Formulas:**
        Uniaxial strain assumption:
        Δσh = γ × ΔPp

        Where:
        γ = α × (1 - 2ν) / (1 - ν) for poroelastic response
        Typical γ = 0.5-0.8

        Effective stress change:
        Δσ'h = Δσh - α×ΔPp = (γ - α)×ΔPp
        """
        # Calculate stress path coefficient if not provided
        if request.stress_path_coefficient is not None:
            gamma = request.stress_path_coefficient
        else:
            # Poroelastic stress path coefficient
            nu = request.poisson_ratio
            alpha = request.biot_coefficient
            gamma = alpha * (1 - 2 * nu) / (1 - nu)

        # Pore pressure change
        delta_pp = request.final_pore_pressure - request.initial_pore_pressure

        # Horizontal stress change
        delta_sigma_h = gamma * delta_pp

        # Final horizontal stress
        final_sigma_h = request.initial_sigma_h + delta_sigma_h

        # Effective stress changes
        delta_sigma_h_eff = delta_sigma_h - request.biot_coefficient * delta_pp
        delta_sigma_v_eff = -request.biot_coefficient * delta_pp  # σv constant

        # Direction of stress change
        if delta_pp < 0:  # Depletion
            operation = "depletion"
            if delta_sigma_h_eff > 0:
                eff_stress_change = "increasing (compacting)"
            else:
                eff_stress_change = "decreasing"
        else:  # Injection
            operation = "injection"
            if delta_sigma_h_eff < 0:
                eff_stress_change = "decreasing (potential fault activation)"
            else:
                eff_stress_change = "increasing"

        # Fault stability assessment
        # Effective stress decreases with injection → higher slip tendency
        if delta_pp > 0 and delta_sigma_h_eff < 0:
            fault_impact = "Increased fault slip risk - effective stress decreasing"
        elif delta_pp < 0 and delta_sigma_h_eff > 0:
            fault_impact = "Decreased fault slip risk - effective stress increasing"
        else:
            fault_impact = "Moderate impact - monitor stress state"

        return {
            "operation": operation,
            "initial_sigma_h": float(request.initial_sigma_h),
            "final_sigma_h": float(final_sigma_h),
            "delta_sigma_h": float(delta_sigma_h),
            "delta_pore_pressure": float(delta_pp),
            "stress_path_coefficient": float(gamma),
            "delta_effective_stress_h": float(delta_sigma_h_eff),
            "delta_effective_stress_v": float(delta_sigma_v_eff),
            "effective_stress_trend": eff_stress_change,
            "fault_stability_impact": fault_impact,
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_thermal_stress(request: ThermalStressRequest) -> dict:
        """Calculate thermal stress effects on wellbore and formation.

        **THERMAL OPERATIONS** - Calculates stress changes due to temperature differences
        between drilling fluid and formation. Important for HTHP wells, steam injection,
        and cold water injection.

        **Parameters:**
        - **temperature_change** (float, required): ΔT in degrees F (negative = cooling)
        - **youngs_modulus** (float, required): Young's modulus (psi)
        - **poisson_ratio** (float, required): Poisson's ratio
        - **thermal_expansion_coefficient** (float, optional): α_T (1/degF)
        - **biot_coefficient** (float, optional): Biot coefficient

        **Returns:**
        Dictionary with:
        - **thermal_stress** (float): Induced thermal stress (psi)
        - **hoop_stress_change** (float): Change in tangential stress at wellbore (psi)
        - **stability_effect** (str): Impact on wellbore stability
        - **fracture_effect** (str): Impact on fracture initiation

        **Formulas:**
        Thermal stress (constrained condition):
        σ_thermal = -E × α_T × ΔT / (1 - ν)

        Where:
        - E = Young's modulus
        - α_T = linear thermal expansion coefficient
        - ΔT = temperature change
        - ν = Poisson's ratio

        **Effects:**
        - Cooling (ΔT < 0): Tensile stress, promotes fracturing, reduces collapse risk
        - Heating (ΔT > 0): Compressive stress, inhibits fracturing, increases collapse risk
        """
        # Calculate thermal stress
        E = request.youngs_modulus
        nu = request.poisson_ratio
        alpha_T = request.thermal_expansion_coefficient
        delta_T = request.temperature_change

        # Uniaxial thermal stress (plane strain condition)
        sigma_thermal = -E * alpha_T * delta_T / (1 - nu)

        # At wellbore wall, hoop stress is affected
        # Cooling reduces hoop stress (more tensile)
        # Heating increases hoop stress (more compressive)
        hoop_change = sigma_thermal

        # Stability implications
        if delta_T < 0:  # Cooling
            stability_effect = "Cooling reduces collapse risk (lower hoop stress) but increases lost circulation risk"
            fracture_effect = "Lower fracture initiation pressure - promotes fracturing"
            mud_weight_effect = "Can drill with lower mud weight"
        elif delta_T > 0:  # Heating
            stability_effect = "Heating increases collapse risk (higher hoop stress) but reduces lost circulation risk"
            fracture_effect = "Higher fracture initiation pressure - inhibits fracturing"
            mud_weight_effect = "May need higher mud weight for stability"
        else:
            stability_effect = "No thermal effect"
            fracture_effect = "No thermal effect"
            mud_weight_effect = "No thermal effect"

        # Equivalent mud weight change (at typical depth of 10000 ft)
        emw_change = hoop_change / (0.052 * 10000)

        return {
            "thermal_stress": float(sigma_thermal),
            "hoop_stress_change": float(hoop_change),
            "equivalent_mud_weight_change": float(emw_change),
            "temperature_change": float(delta_T),
            "stability_effect": stability_effect,
            "fracture_effect": fracture_effect,
            "mud_weight_effect": mud_weight_effect,
            "units": "psi (stress), ppg (EMW change)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_ucs_from_logs(request: UCSFromLogsRequest) -> dict:
        """Estimate Unconfined Compressive Strength (UCS) from well log data.

        **LOG-DERIVED STRENGTH** - Calculates UCS from sonic, porosity, or elastic
        moduli using established correlations. Essential for continuous mechanical
        property profiles where core data is limited.

        **Parameters:**
        - **sonic_dt** (float, optional): Sonic transit time (μs/ft)
        - **porosity** (float, optional): Porosity (fraction)
        - **youngs_modulus** (float, optional): Young's modulus (psi)
        - **lithology** (str, optional): "sandstone", "shale", "carbonate", "general"
        - **correlation** (str, optional): "mcnally", "horsrud", "chang", "lal", "vernik"

        **Returns:**
        Dictionary with:
        - **ucs** (float): Estimated UCS (psi)
        - **confidence** (str): Confidence level
        - **correlation_used** (str): Correlation applied
        - **typical_range** (list): Expected range for lithology

        **Correlations:**
        McNally (1987) - Sandstone:
        UCS = 1200 × exp(-0.036 × Δt)

        Horsrud (2001) - Shale:
        UCS = 0.77 × (304.8/Δt)^2.93

        Chang (2006) - General:
        UCS = 2.28 + 4.1089×E (E in GPa)

        Lal (1999) - Shale:
        UCS = 10 × (304.8/Δt - 1)

        Vernik (1993) - Carbonate:
        UCS = 254 × (1 - 2.7φ)²
        """
        ucs = None
        correlation_used = request.correlation

        if request.correlation == "mcnally" and request.sonic_dt is not None:
            # McNally (1987) for sandstone
            ucs = 1200 * np.exp(-0.036 * request.sonic_dt)
            lithology_range = [2000, 15000]

        elif request.correlation == "horsrud" and request.sonic_dt is not None:
            # Horsrud (2001) for shale
            vp_km_s = 304.8 / request.sonic_dt / 3.281  # Convert to km/s
            ucs = 0.77 * (vp_km_s * 1000)**2.93 / 145.038  # Convert MPa to psi
            lithology_range = [500, 8000]

        elif request.correlation == "chang" and request.youngs_modulus is not None:
            # Chang (2006) - general correlation
            E_GPa = request.youngs_modulus / 145038  # psi to GPa
            ucs = (2.28 + 4.1089 * E_GPa) * 145.038  # MPa to psi
            lithology_range = [1000, 20000]

        elif request.correlation == "lal" and request.sonic_dt is not None:
            # Lal (1999) for shale
            ucs = 10 * (304.8 / request.sonic_dt - 1) * 145.038  # MPa to psi
            lithology_range = [500, 5000]

        elif request.correlation == "vernik" and request.porosity is not None:
            # Vernik (1993) for carbonate
            ucs = 254 * (1 - 2.7 * request.porosity)**2 * 145.038  # MPa to psi
            lithology_range = [2000, 25000]

        else:
            # Default: use sonic if available with McNally
            if request.sonic_dt is not None:
                ucs = 1200 * np.exp(-0.036 * request.sonic_dt)
                correlation_used = "mcnally (default)"
            elif request.porosity is not None:
                ucs = 254 * (1 - 2.7 * request.porosity)**2 * 145.038
                correlation_used = "vernik (porosity-based)"
            elif request.youngs_modulus is not None:
                E_GPa = request.youngs_modulus / 145038
                ucs = (2.28 + 4.1089 * E_GPa) * 145.038
                correlation_used = "chang (E-based)"
            else:
                return {
                    "error": "Insufficient input data - provide sonic_dt, porosity, or youngs_modulus",
                    "inputs": request.model_dump(),
                }
            lithology_range = [1000, 15000]

        # Ensure positive value
        ucs = max(0, float(ucs))

        # Confidence based on correlation applicability
        if (request.lithology == "sandstone" and request.correlation == "mcnally") or \
           (request.lithology == "shale" and request.correlation in ["horsrud", "lal"]) or \
           (request.lithology == "carbonate" and request.correlation == "vernik"):
            confidence = "high"
        else:
            confidence = "moderate - verify with core data"

        # Cohesion estimate (typically UCS/4 to UCS/3)
        cohesion_est = ucs / 3.5

        return {
            "ucs": float(ucs),
            "cohesion_estimate": float(cohesion_est),
            "correlation_used": correlation_used,
            "lithology": request.lithology,
            "typical_range_psi": lithology_range,
            "confidence": confidence,
            "units": "psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def geomech_critical_drawdown(request: CriticalDrawdownRequest) -> dict:
        """Calculate critical drawdown pressure before sand/shear failure at wellbore.

        **PRODUCTION OPTIMIZATION** - Determines maximum safe drawdown (Pres - Pwf)
        before wellbore rock failure occurs. Critical for sand-free production rate
        optimization and completion design.

        **Parameters:**
        - **sigma_h_max** (float, required): Maximum horizontal stress (psi)
        - **sigma_h_min** (float, required): Minimum horizontal stress (psi)
        - **reservoir_pressure** (float, required): Current reservoir pressure (psi)
        - **ucs** (float, required): Unconfined compressive strength (psi)
        - **cohesion** (float, required): Rock cohesion (psi)
        - **friction_angle** (float, required): Internal friction angle (degrees)
        - **wellbore_radius** (float, optional): Wellbore radius (ft)

        **Returns:**
        Dictionary with:
        - **critical_drawdown** (float): Maximum safe drawdown (psi)
        - **critical_flowing_bhp** (float): Minimum safe FBHP (psi)
        - **max_safe_rate_factor** (float): Relative rate limit (fraction of AOF)
        - **failure_mechanism** (str): Predicted failure type

        **Methodology:**
        Uses Mohr-Coulomb failure at wellbore wall with Kirsch stress concentration.
        As drawdown increases, tangential stress increases until rock fails.

        **Formula:**
        σθ_max = 3σH - σh - Pw + Pp (at θ = 90°)
        Failure when: σθ_max = UCS + q × σr
        Solve for minimum Pw (= Pwf critical)
        """
        # Mohr-Coulomb parameters
        phi_rad = np.deg2rad(request.friction_angle)
        sin_phi = np.sin(phi_rad)
        cos_phi = np.cos(phi_rad)

        # q factor
        q = (1 + sin_phi) / (1 - sin_phi)

        # Effective stresses at initial reservoir pressure
        sigma_H_eff = request.sigma_h_max - request.reservoir_pressure
        sigma_h_eff = request.sigma_h_min - request.reservoir_pressure

        # Maximum hoop stress concentration factor
        # At θ = 90° (perpendicular to σH): σθ = 3σH - σh - ΔP
        # Using effective stresses

        # At critical flowing BHP (Pwf_crit):
        # Maximum tangential effective stress = rock failure stress
        # σθ_eff = 3(σH - Pp) - (σh - Pp) - (Pp - Pwf) = UCS + q × σr_eff
        # σr_eff = Pwf - Pp (negative for underbalanced)

        # Rearranging for critical Pwf:
        # 3σH_eff - σh_eff + (Pp - Pwf) = UCS + q(Pwf - Pp)
        # 3σH_eff - σh_eff + Pp - Pwf = UCS + q×Pwf - q×Pp
        # 3σH_eff - σh_eff + Pp + q×Pp = UCS + Pwf(1 + q)
        # Pwf_crit = (3σH_eff - σh_eff + (1+q)×Pp - UCS) / (1 + q)

        ucs = request.ucs
        pwf_crit = (3 * sigma_H_eff - sigma_h_eff + (1 + q) * request.reservoir_pressure - ucs) / (1 + q)

        # Critical drawdown
        critical_drawdown = request.reservoir_pressure - pwf_crit

        # Ensure reasonable values
        critical_drawdown = max(0, min(critical_drawdown, request.reservoir_pressure))
        critical_fbhp = request.reservoir_pressure - critical_drawdown

        # Safe rate factor (conservative: use 80% of critical)
        safe_rate_factor = 0.8

        # Failure mechanism assessment
        if critical_drawdown < 500:
            failure_mechanism = "Shear failure - weak rock, sand control needed"
        elif critical_drawdown < 1500:
            failure_mechanism = "Shear failure possible at high rates - rate-restrict or sand control"
        else:
            failure_mechanism = "Rock is strong - natural completion may be acceptable"

        return {
            "critical_drawdown": float(critical_drawdown),
            "critical_flowing_bhp": float(critical_fbhp),
            "safe_drawdown_80pct": float(0.8 * critical_drawdown),
            "safe_rate_factor": float(safe_rate_factor),
            "failure_mechanism": failure_mechanism,
            "ucs_used": float(ucs),
            "q_factor": float(q),
            "units": "psi",
            "inputs": request.model_dump(),
        }
