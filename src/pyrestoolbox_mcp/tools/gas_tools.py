"""Gas PVT calculation tools for FastMCP."""

import numpy as np
import pyrestoolbox.gas as gas
from pyrestoolbox.classes import z_method, c_method
from fastmcp import FastMCP

# Import fixed version of gas_grad2sg
from .gas_fixes import gas_grad2sg_fixed

from ..models.gas_models import (
    ZFactorRequest,
    CriticalPropertiesRequest,
    GasFVFRequest,
    GasViscosityRequest,
    GasDensityRequest,
    GasCompressibilityRequest,
    GasPseudopressureRequest,
    GasPressureFromPZRequest,
    GasSGFromGradientRequest,
    GasWaterContentRequest,
    GasSGFromCompositionRequest,
)


def register_gas_tools(mcp: FastMCP) -> None:
    """Register all gas-related tools with the MCP server."""

    @mcp.tool()
    def gas_z_factor(request: ZFactorRequest) -> dict:
        """Calculate gas compressibility factor (Z-factor).

        **CRITICAL GAS PVT PROPERTY** - The Z-factor corrects the ideal gas law (PV=nRT)
        for real gas behavior. Z = 1.0 for ideal gas, Z < 1.0 for most real gases at
        reservoir conditions. Essential for all gas reservoir calculations including
        material balance, reserve estimation, and flow calculations.

        **Parameters:**
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7 for dry gas, 0.85 for associated gas.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Typical: 100-400°F. Example: 180.0.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3500.0 or [1000, 2000, 3000, 4000].
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.02 for 2% H2S. High H2S requires special handling.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.05 for 5% CO2.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.01 for 1% N2.
        - **method** (str, optional, default="DAK"): Correlation method.
          Options: "DAK", "HY", "WYW", "BUR". DAK recommended.

        **Z-Factor Behavior:**
        - Low pressure: Z ≈ 1.0 (ideal gas behavior)
        - Medium pressure: Z < 1.0 (attractive forces dominate)
        - High pressure: Z > 1.0 (repulsive forces dominate)
        - Typical range: 0.7-1.2 for reservoir conditions

        **Method Selection:**
        - **DAK** (Dranchuk & Abou-Kassem 1975): **RECOMMENDED**. Most accurate,
          widely validated. Use for: All applications, high accuracy requirements.
        - **HY** (Hall & Yarborough 1973): Classic method, fast. Use for: Quick estimates,
          compatibility with older methods.
        - **WYW** (Wang, Ye & Wu 2021): Newer correlation. Use for: Comparison studies,
          modern applications.
        - **BUR** (Burrows 1981): Alternative method. Use for: Specific regional correlations.

        **Non-Hydrocarbon Effects:**
        - H2S and CO2 increase Z-factor (reduce compressibility)
        - N2 has minimal effect
        - For sour gas (H2S > 5%), use Wichert-Aziz correction (not included here)

        **Returns:**
        Dictionary with:
        - **value** (float or list): Z-factor (dimensionless, matches input p shape)
        - **method** (str): Method used
        - **units** (str): "dimensionless"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions (H2S, CO2, N2)
        - Using wrong gas gravity (must be separator gas gravity, not sales gas)
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "sg": 0.7,
            "degf": 180.0,
            "p": [1000, 2000, 3000, 4000],
            "h2s": 0.0,
            "co2": 0.05,
            "n2": 0.01,
            "method": "DAK"
        }
        ```
        Result: Z decreases from ~0.95 at 1000 psia to ~0.85 at 3000 psia,
        then increases to ~0.90 at 4000 psia (typical behavior).

        **Note:** Z-factor is critical for accurate gas calculations. Always use DAK method
        unless specific compatibility requirements exist. Account for all non-hydrocarbon
        components for accurate results.
        """
        method_enum = getattr(z_method, request.method)

        z = gas.gas_z(
            sg=request.sg,
            degf=request.degf,
            p=request.p,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
            zmethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(z, np.ndarray):
            value = z.tolist()
        else:
            value = float(z)

        return {
            "value": value,
            "method": request.method,
            "units": "dimensionless",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_critical_properties(request: CriticalPropertiesRequest) -> dict:
        """Calculate gas pseudo-critical properties (Tc and Pc).

        **CRITICAL GAS PROPERTY CALCULATION** - Computes pseudo-critical temperature and
        pressure for real gas mixtures. Required for Z-factor calculations and all gas
        property correlations. Pseudo-critical properties are weighted averages of pure
        component critical properties, adjusted for non-hydrocarbon components.

        **Parameters:**
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7 for dry gas.
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.02 for 2% H2S. High H2S significantly affects Tc/Pc.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.05 for 5% CO2.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.01 for 1% N2.
        - **method** (str, optional, default="PMC"): Correlation method.
          Options: "PMC", "SUT", "BUR". PMC recommended.

        **Pseudo-Critical Properties:**
        - **Tc (Pseudo-critical Temperature)**: Temperature above which gas cannot be
          liquefied regardless of pressure. Typical: 300-500°R for natural gas.
        - **Pc (Pseudo-critical Pressure)**: Pressure at critical temperature.
          Typical: 600-800 psia for natural gas.

        **Method Selection:**
        - **PMC** (Piper, McCain & Corredor 1993): **RECOMMENDED**. Most accurate for
          wide range of gas compositions. Accounts for non-hydrocarbon effects.
        - **SUT** (Sutton 1985): Classic method. Use for compatibility with older methods.
        - **BUR** (Burrows 1981): Alternative method. Use for specific applications.

        **Non-Hydrocarbon Effects:**
        - H2S: Increases both Tc and Pc significantly
        - CO2: Increases Tc, decreases Pc slightly
        - N2: Increases Pc, decreases Tc slightly
        - Always account for non-hydrocarbons for accurate Z-factor calculations

        **Returns:**
        Dictionary with:
        - **value** (dict): Contains "tc" (degR) and "pc" (psia)
        - **method** (str): Method used
        - **units** (dict): {"tc": "degR", "pc": "psia"}
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Not accounting for non-hydrocarbon fractions (H2S, CO2, N2)
        - Using wrong gas gravity (must be separator gas, not sales gas)
        - Confusing pseudo-critical with true critical properties
        - Using critical properties for pure components instead of mixtures

        **Example Usage:**
        ```python
        {
            "sg": 0.7,
            "h2s": 0.0,
            "co2": 0.05,
            "n2": 0.01,
            "method": "PMC"
        }
        ```
        Result: Tc ≈ 380-420°R, Pc ≈ 650-750 psia for typical natural gas.

        **Note:** Critical properties are used internally by gas_z_factor and other
        gas property tools. Always use PMC method unless specific compatibility required.
        Account for all non-hydrocarbon components - even small amounts affect results.
        """
        method_enum = getattr(c_method, request.method)

        tc, pc = gas.gas_tc_pc(
            sg=request.sg,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
            cmethod=method_enum,
        )

        return {
            "value": {"tc": float(tc), "pc": float(pc)},
            "method": request.method,
            "units": {"tc": "degR", "pc": "psia"},
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_formation_volume_factor(request: GasFVFRequest) -> dict:
        """Calculate gas formation volume factor (Bg).

        **CRITICAL GAS PVT PROPERTY** - Computes ratio of gas volume at reservoir conditions
        to volume at standard conditions. Bg << 1.0 because gas compresses significantly
        at reservoir pressure. Essential for material balance, reserve calculations, and
        production forecasting.

        **Parameters:**
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Typical: 100-400°F. Example: 180.0.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3500.0 or [1000, 2000, 3000, 4000].
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.02.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.05.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.01.
        - **zmethod** (str, optional, default="DAK"): Z-factor method for Bg calculation.
          Options: "DAK", "HY", "WYW", "BUR". DAK recommended.

        **Bg Behavior:**
        - Bg decreases with increasing pressure (gas compresses)
        - Bg increases with increasing temperature (gas expands)
        - Typical range: 0.001-0.01 rcf/scf at reservoir conditions
        - At standard conditions (14.7 psia, 60°F): Bg = 1.0 rcf/scf

        **Formula:**
        Bg = (Z × T × Psc) / (P × Tsc) = 0.02827 × Z × T / P (field units)

        Where:
        - Z = gas compressibility factor (from gas_z_factor tool)
        - T = reservoir temperature (°R)
        - P = reservoir pressure (psia)
        - Psc = 14.7 psia, Tsc = 520°R (standard conditions)

        **Returns:**
        Dictionary with:
        - **value** (float or list): Bg in rcf/scf (matches input p shape)
        - **method** (str): Z-factor method used
        - **units** (str): "rcf/scf"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions
        - Confusing Bg (gas FVF) with Bo (oil FVF)
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "sg": 0.7,
            "degf": 180.0,
            "p": [1000, 2000, 3000, 4000],
            "h2s": 0.0,
            "co2": 0.05,
            "n2": 0.01,
            "zmethod": "DAK"
        }
        ```
        Result: Bg decreases from ~0.005 rcf/scf at 1000 psia to ~0.002 rcf/scf at 4000 psia.

        **Note:** Bg is inversely proportional to pressure. Always use reservoir conditions,
        not separator conditions. Account for all non-hydrocarbon components for accuracy.
        """
        method_enum = getattr(z_method, request.zmethod)

        bg = gas.gas_bg(
            sg=request.sg,
            degf=request.degf,
            p=request.p,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
            zmethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(bg, np.ndarray):
            value = bg.tolist()
        else:
            value = float(bg)

        return {
            "value": value,
            "method": request.zmethod,
            "units": "rcf/scf",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_viscosity(request: GasViscosityRequest) -> dict:
        """Calculate gas viscosity (μg).

        **CRITICAL GAS PVT PROPERTY** - Computes gas viscosity at reservoir conditions
        using Lee, Gonzalez & Eakin (1966) correlation, industry standard for natural gas.
        Viscosity affects flow rates, pressure drops, and well performance. Gas viscosity
        increases with pressure and temperature, opposite to liquid behavior.

        **Parameters:**
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Typical: 100-400°F. Example: 180.0.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3500.0 or [1000, 2000, 3000, 4000].
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.02.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.05.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.01.
        - **zmethod** (str, optional, default="DAK"): Z-factor method for viscosity calculation.
          Options: "DAK", "HY", "WYW", "BUR". DAK recommended.

        **Viscosity Behavior:**
        - Increases with pressure (gas molecules closer together)
        - Increases with temperature (molecular motion increases)
        - Typical range: 0.01-0.05 cP at reservoir conditions
        - At standard conditions: ~0.01 cP

        **Lee-Gonzalez-Eakin Correlation:**
        Uses Z-factor internally to account for real gas behavior. More accurate than
        ideal gas assumptions, especially at high pressures.

        **Returns:**
        Dictionary with:
        - **value** (float or list): Viscosity in cP (matches input p shape)
        - **method** (str): "Lee-Gonzalez-Eakin"
        - **units** (str): "cP"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions
        - Confusing gas viscosity (increases with P) with oil viscosity (decreases with P)
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "sg": 0.7,
            "degf": 180.0,
            "p": [1000, 2000, 3000, 4000],
            "h2s": 0.0,
            "co2": 0.05,
            "n2": 0.01,
            "zmethod": "DAK"
        }
        ```
        Result: Viscosity increases from ~0.012 cP at 1000 psia to ~0.025 cP at 4000 psia.

        **Note:** Gas viscosity is much lower than oil viscosity (typically 0.01-0.05 cP
        vs 0.5-10 cP). Always use reservoir conditions, not separator conditions.
        Account for all non-hydrocarbon components for accuracy.
        """
        method_enum = getattr(z_method, request.zmethod)

        ug = gas.gas_ug(
            sg=request.sg,
            degf=request.degf,
            p=request.p,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
            zmethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(ug, np.ndarray):
            value = ug.tolist()
        else:
            value = float(ug)

        return {
            "value": value,
            "method": "Lee-Gonzalez-Eakin",
            "units": "cP",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_density(request: GasDensityRequest) -> dict:
        """Calculate gas density (ρg) at reservoir conditions.

        **CRITICAL GAS PVT PROPERTY** - Computes gas density from real gas equation of state.
        Essential for gradient calculations, well pressure analysis, and material balance.
        Gas density increases significantly with pressure due to compressibility.

        **Parameters:**
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Typical: 100-400°F. Example: 180.0.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3500.0 or [1000, 2000, 3000, 4000].
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.02.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.05.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.01.
        - **zmethod** (str, optional, default="DAK"): Z-factor method for density calculation.
          Options: "DAK", "HY", "WYW", "BUR". DAK recommended.

        **Density Formula:**
        ρg = (P × MW) / (Z × R × T)

        Where:
        - P = pressure (psia)
        - MW = molecular weight = sg × 28.97 lb/lbmol
        - Z = gas compressibility factor
        - R = gas constant = 10.732 psia·ft³/(lbmol·°R)
        - T = temperature (°R = °F + 460)

        **Density Behavior:**
        - Increases with pressure (gas compresses)
        - Decreases with temperature (gas expands)
        - Typical range: 5-20 lb/cuft at reservoir conditions
        - At standard conditions: ~0.05-0.1 lb/cuft

        **Returns:**
        Dictionary with:
        - **value** (float or list): Density in lb/cuft (matches input p shape)
        - **method** (str): Z-factor method used
        - **units** (str): "lb/cuft"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions
        - Using ideal gas law (Z=1) instead of real gas (Z<1)
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "sg": 0.7,
            "degf": 180.0,
            "p": [1000, 2000, 3000, 4000],
            "h2s": 0.0,
            "co2": 0.05,
            "n2": 0.01,
            "zmethod": "DAK"
        }
        ```
        Result: Density increases from ~8 lb/cuft at 1000 psia to ~18 lb/cuft at 4000 psia.

        **Note:** Gas density is much lower than oil density (typically 5-20 lb/cuft
        vs 40-60 lb/cuft). Always use reservoir conditions. Account for all non-hydrocarbon
        components - they significantly affect molecular weight and density.
        """
        method_enum = getattr(z_method, request.zmethod)

        den = gas.gas_den(
            sg=request.sg,
            degf=request.degf,
            p=request.p,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
            zmethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(den, np.ndarray):
            value = den.tolist()
        else:
            value = float(den)

        return {
            "value": value,
            "method": request.zmethod,
            "units": "lb/cuft",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_compressibility(request: GasCompressibilityRequest) -> dict:
        """Calculate gas compressibility (Cg).

        **CRITICAL GAS PVT PROPERTY** - Computes gas compressibility coefficient, which
        measures how much gas volume changes with pressure. Essential for material balance
        calculations, pressure transient analysis, and reserve estimation. Gas compressibility
        is much higher than oil compressibility (typically 100-1000 × 10⁻⁶ 1/psi vs 5-50 × 10⁻⁶).

        **Parameters:**
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Typical: 100-400°F. Example: 180.0.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3500.0 or [1000, 2000, 3000, 4000].
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.02.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.05.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.01.
        - **zmethod** (str, optional, default="DAK"): Z-factor method for compressibility.
          Options: "DAK", "HY", "WYW", "BUR". DAK recommended.

        **Compressibility Behavior:**
        - Decreases with increasing pressure (gas becomes less compressible)
        - Typical range: 50-500 × 10⁻⁶ 1/psi at reservoir conditions
        - At low pressure: Cg ≈ 1/P (ideal gas behavior)
        - At high pressure: Cg decreases significantly

        **Formula:**
        Cg = (1/Z) × (∂Z/∂P) - (1/P)

        Where Z-factor and its pressure derivative are calculated using specified method.

        **Returns:**
        Dictionary with:
        - **value** (float or list): Compressibility in 1/psi (matches input p shape)
        - **method** (str): Z-factor method used
        - **units** (str): "1/psi"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions
        - Confusing gas compressibility (high, 100-1000 × 10⁻⁶) with oil compressibility (low, 5-50 × 10⁻⁶)
        - Using ideal gas approximation (Cg = 1/P) instead of real gas

        **Example Usage:**
        ```python
        {
            "sg": 0.7,
            "degf": 180.0,
            "p": [1000, 2000, 3000, 4000],
            "h2s": 0.0,
            "co2": 0.05,
            "n2": 0.01,
            "zmethod": "DAK"
        }
        ```
        Result: Cg decreases from ~1000 × 10⁻⁶ 1/psi at 1000 psia to ~250 × 10⁻⁶ 1/psi at 4000 psia.

        **Note:** Gas compressibility is critical for material balance calculations.
        Always use reservoir conditions. Account for all non-hydrocarbon components.
        Cg values are small (micro-1/psi), so results are typically in scientific notation.
        """
        method_enum = getattr(z_method, request.zmethod)

        cg = gas.gas_cg(
            sg=request.sg,
            degf=request.degf,
            p=request.p,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
            zmethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(cg, np.ndarray):
            value = cg.tolist()
        else:
            value = float(cg)

        return {
            "value": value,
            "method": request.zmethod,
            "units": "1/psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_pseudopressure(request: GasPseudopressureRequest) -> dict:
        """Calculate gas pseudopressure difference (m(p)).

        **CRITICAL GAS ANALYSIS TOOL** - Computes pseudopressure difference, a pressure
        transformation that linearizes the gas diffusivity equation. This makes gas flow
        analysis mathematically similar to liquid flow, enabling use of liquid flow solutions
        for gas systems. Essential for accurate gas well performance analysis.

        **Parameters:**
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Typical: 100-400°F. Example: 180.0.
        - **p1** (float, required): Initial pressure in psia. Must be > 0.
          Typically reservoir pressure. Example: 1000.0.
        - **p2** (float, required): Final pressure in psia. Must be > 0.
          Typically sandface pressure. Example: 3500.0.
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.0.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.0.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.0.
        - **zmethod** (str, optional, default="DAK"): Z-factor method for integration.
          Options: "DAK", "HY", "WYW", "BUR". DAK recommended.

        **Pseudopressure Formula:**
        m(p) = 2∫(p/(μZ))dp from p1 to p2

        Where:
        - p = pressure (psia)
        - μ = gas viscosity (cP)
        - Z = gas compressibility factor

        **Why Pseudopressure:**
        Gas properties (Z, μ) vary significantly with pressure, making gas flow non-linear.
        Pseudopressure transformation accounts for these variations, enabling:
        - Use of liquid flow solutions for gas
        - Linear pressure analysis
        - Accurate well test interpretation
        - Material balance calculations

        **Applications:**
        - **Gas Well Testing:** Pressure transient analysis, rate transient analysis
        - **Material Balance:** P/Z vs cumulative production plots
        - **Reservoir Simulation:** Input for gas flow calculations
        - **IPR Curves:** Inflow performance relationship generation

        **Returns:**
        Dictionary with:
        - **value** (float): Pseudopressure difference in psia²/cP
        - **method** (str): Integration method with Z-factor method used
        - **units** (str): "psia²/cP"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions
        - Confusing pseudopressure with actual pressure
        - Using wrong pressure order (p1 should be lower than p2 typically)
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "sg": 0.7,
            "degf": 180.0,
            "p1": 1000.0,
            "p2": 3500.0,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "zmethod": "DAK"
        }
        ```
        Result: Pseudopressure difference ≈ 1-5 × 10⁶ psia²/cP (typical range).

        **Note:** Pseudopressure is essential for accurate gas flow calculations.
        Always use reservoir conditions. Account for all non-hydrocarbon components.
        The integration is performed numerically, so results are approximate but highly accurate.
        """
        method_enum = getattr(z_method, request.zmethod)

        dmp = gas.gas_dmp(
            sg=request.sg,
            degf=request.degf,
            p1=request.p1,
            p2=request.p2,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
            zmethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(dmp, np.ndarray):
            value = dmp.tolist()
        else:
            value = float(dmp)

        return {
            "value": value,
            "method": f"Pseudopressure integration using {request.zmethod}",
            "units": "psia²/cP",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_pressure_from_pz(request: GasPressureFromPZRequest) -> dict:
        """Calculate pressure from P/Z value.

        **MATERIAL BALANCE TOOL** - Solves for pressure given a P/Z (pressure/Z-factor) value.
        Essential for gas material balance analysis where P/Z vs cumulative production is plotted.
        Uses iterative solution to find pressure that yields the specified P/Z value.

        **Parameters:**
        - **pz** (float or list, required): P/Z value(s) in psia. Must be > 0.
          Can be scalar or array. Example: 5000.0 or [4000, 5000, 6000].
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Typical: 100-400°F. Example: 180.0.
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.0.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.0.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.0.
        - **zmethod** (str, optional, default="DAK"): Z-factor method for calculation.
          Options: "DAK", "HY", "WYW", "BUR". DAK recommended.

        **P/Z Method Applications:**
        - **Volumetric Gas Reserves:** P/Z vs Gp plot gives GIIP (Gas Initially In Place)
        - **Aquifer Influx Detection:** Deviation from straight line indicates water drive
        - **Drive Mechanism Identification:** Volumetric vs water drive vs gas cap
        - **Production Forecasting:** Extrapolate P/Z to abandonment pressure

        **Material Balance Principle:**
        For volumetric gas reservoirs: P/Z = (Pi/Zi) × (1 - Gp/G)
        Where Gp = cumulative production, G = GIIP

        A straight line on P/Z vs Gp indicates volumetric depletion.
        Deviation suggests water influx, changing pore volume, or gas cap expansion.

        **Solution Method:**
        Iterative Newton-Raphson method to solve: P/Z - pz_target = 0
        Converges rapidly for well-posed problems.

        **Returns:**
        Dictionary with:
        - **value** (float or list): Pressure in psia (matches input pz shape)
        - **method** (str): Iterative solution method with Z-factor method
        - **units** (str): "psia"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Not accounting for non-hydrocarbon fractions
        - Confusing P/Z (pressure/Z-factor) with pressure
        - Using wrong Z-factor method (must match method used in material balance)
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "pz": 5000.0,
            "sg": 0.7,
            "degf": 180.0,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "zmethod": "DAK"
        }
        ```
        Result: Pressure ≈ 4500-5500 psia (depends on Z-factor at that pressure).

        **Note:** P/Z method is fundamental to gas material balance. Always use the same
        Z-factor method throughout your analysis for consistency. Account for all
        non-hydrocarbon components as they affect Z-factor and thus P/Z values.
        """
        method_enum = getattr(z_method, request.zmethod)

        p = gas.gas_ponz2p(
            poverz=request.pz,  # Function expects poverz not pz
            sg=request.sg,
            degf=request.degf,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
            zmethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(p, np.ndarray):
            value = p.tolist()
        else:
            value = float(p)

        return {
            "value": value,
            "method": f"Iterative solution using {request.zmethod}",
            "units": "psia",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_sg_from_gradient(request: GasSGFromGradientRequest) -> dict:
        """Calculate gas specific gravity from pressure gradient.

        **DIAGNOSTIC TOOL** - Determines gas specific gravity from measured pressure gradient
        in a gas column. Uses standalone Newton-Raphson solver (fixed implementation) to
        solve the inverse problem. Essential for formation fluid identification and gas
        property verification when only gradient data is available.

        **Parameters:**
        - **gradient** (float, required): Pressure gradient in psi/ft. Must be > 0.
          Typical: 0.05-0.15 psi/ft. Example: 0.1 psi/ft.
        - **degf** (float, required): Temperature in °F at measurement depth.
          Valid: -460 to 1000. Typical: 100-400°F. Example: 180.0.
        - **p** (float, required): Pressure in psia at measurement depth. Must be > 0.
          Example: 3500.0.
        - **method** (str, optional, default="DAK"): Z-factor method for calculation.
          Options: "DAK", "HY", "WYW", "BUR". DAK recommended.

        **Gradient Principle:**
        Gas gradient = dP/dh = (ρg × g) / 144 = (P × MW) / (Z × R × T × 144)

        Where:
        - ρg = gas density (lb/cuft)
        - MW = molecular weight = sg × 28.97 lb/lbmol
        - Z = gas compressibility factor
        - R = gas constant = 10.732 psia·ft³/(lbmol·°R)
        - T = temperature (°R = °F + 460)

        **Applications:**
        - **Formation Fluid ID:** Identify gas vs oil vs water from gradient
        - **Gas Density Verification:** Check measured gas gravity against gradient
        - **Completion Fluid Design:** Design mud weight based on gas gradient
        - **Wellbore Pressure Modeling:** Calculate pressure profiles in gas columns

        **Typical Gradients:**
        - Dry gas (sg=0.6): ~0.08 psi/ft
        - Associated gas (sg=0.8): ~0.11 psi/ft
        - Heavy gas (sg=1.0): ~0.14 psi/ft

        **Solution Method:**
        Uses Newton-Raphson iterative solver to find sg that yields the specified gradient.
        This is a standalone fixed implementation that avoids upstream library bugs.

        **Returns:**
        Dictionary with:
        - **value** (float): Gas specific gravity (dimensionless, air=1)
        - **method** (str): "Gradient correlation (Newton-Raphson)"
        - **units** (str): "dimensionless (air=1)"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions (affects MW and Z)
        - Using wrong gradient units (must be psi/ft, not psi/100ft)
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "gradient": 0.1,
            "degf": 180.0,
            "p": 3500.0,
            "method": "DAK"
        }
        ```
        Result: Gas SG ≈ 0.7-0.8 for typical natural gas gradient.

        **Note:** This tool uses a standalone fixed implementation to avoid upstream bugs.
        Always use reservoir conditions (pressure and temperature at measurement depth).
        Gradient is sensitive to temperature - use correct temperature for accurate results.
        """
        # Use fixed version that doesn't have the bisect_solve bug
        sg = gas_grad2sg_fixed(
            grad=request.grad,
            degf=request.degf,
            p=request.p,
            zmethod='DAK',
            cmethod='PMC',
        )

        value = float(sg)

        return {
            "value": value,
            "method": "Gradient correlation (Newton-Raphson)",
            "units": "dimensionless (air=1)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_water_content(request: GasWaterContentRequest) -> dict:
        """Calculate water content of natural gas.

        **CRITICAL GAS PROCESSING TOOL** - Computes the amount of water vapor that natural
        gas can hold at given pressure and temperature conditions. Essential for hydrate
        prevention, dehydration unit design, and pipeline operation. Water content decreases
        with increasing pressure and decreasing temperature.

        **Parameters:**
        - **sg** (float, required): Gas specific gravity (air=1.0). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Temperature in °F. Valid: -460 to 1000.
          Typical: 40-200°F. Example: 100.0.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 1000.0 or [500, 1000, 2000].

        **Water Content Behavior:**
        - Decreases with increasing pressure (less water can dissolve)
        - Decreases with decreasing temperature (less water vapor)
        - Typical range: 5-200 lb/MMSCF at pipeline conditions
        - At high pressure/low temperature: <10 lb/MMSCF

        **Hydrate Formation:**
        Gas-water systems form solid hydrates (ice-like structures) at certain P-T conditions.
        Hydrates can block pipelines and equipment. Gas must be dehydrated below:
        - Hydrate formation temperature at operating pressure
        - Typical target: <7 lb/MMSCF for pipeline operation
        - Typical target: <0.1 lb/MMSCF for LNG/cryogenic processes

        **Correlation:**
        Uses McCain correlation (1990) based on experimental data for sweet natural gas.
        Valid for typical pipeline and processing conditions.

        **Applications:**
        - **Hydrate Prevention:** Determine minimum dehydration requirement
        - **Dehydration Unit Design:** Size glycol contactors and regenerators
        - **Pipeline Corrosion:** Assess water-related corrosion risk
        - **Gas Processing:** Design dehydration systems for sales gas
        - **Sales Gas Specs:** Ensure compliance with water content limits

        **Returns:**
        Dictionary with:
        - **value** (float or list): Water content in lb/MMSCF (matches input p shape)
        - **method** (str): "McCain (1990) correlation"
        - **units** (str): "lb/MMSCF"
        - **inputs** (dict): Echo of input parameters
        - **note** (str): Hydrate prevention guidance

        **Common Mistakes:**
        - Using separator temperature instead of pipeline/processing temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not understanding hydrate formation conditions
        - Confusing water content (lb/MMSCF) with water dew point (°F)
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "sg": 0.7,
            "degf": 100.0,
            "p": [500, 1000, 2000]
        }
        ```
        Result: Water content decreases from ~50 lb/MMSCF at 500 psia to ~20 lb/MMSCF at 2000 psia.

        **Note:** Water content is critical for pipeline operation. Always check against
        hydrate formation curve. For hydrate prevention, compare to hydrate formation
        temperature at operating pressure. Typical pipeline requirement: <7 lb/MMSCF.
        """
        wc = gas.gas_water_content(
            p=request.p,
            degf=request.degf,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(wc, np.ndarray):
            value = wc.tolist()
        else:
            value = float(wc)

        return {
            "value": value,
            "method": "McCain (1990) correlation",
            "units": "lb/MMSCF",
            "inputs": request.model_dump(),
            "note": "For hydrate prevention, compare to hydrate formation curve",
        }

    @mcp.tool()
    def gas_sg_from_composition(request: GasSGFromCompositionRequest) -> dict:
        """Calculate gas specific gravity from composition.

        **COMPOSITIONAL GAS CHARACTERIZATION** - Computes gas specific gravity from
        hydrocarbon molecular weight and non-hydrocarbon mole fractions. Uses molecular
        weight weighted average method. Essential when gas composition is known but SG
        measurement is unavailable or unreliable.

        **Parameters:**
        - **hc_mw** (float, required): Hydrocarbon molecular weight in lb/lbmol.
          Valid: 10-200. Typical: 16-50. Example: 18.5 for typical natural gas.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.05 for 5% CO2.
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.02 for 2% H2S (sour gas).
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.01 for 1% N2.
        - **h2** (float, optional, default=0.0): H2 mole fraction (0-1).
          Typical: 0-0.01. Example: 0.0 (rare in natural gas).

        **Calculation Method:**
        Weighted average based on molecular weights:
        - HC fraction: User-provided MW (hc_mw)
        - CO2: MW = 44.01 lb/lbmol
        - H2S: MW = 34.08 lb/lbmol
        - N2: MW = 28.01 lb/lbmol
        - H2: MW = 2.02 lb/lbmol
        - Air: MW = 28.97 lb/lbmol (reference for SG)

        Formula: MW_avg = hc_fraction × hc_mw + co2 × 44.01 + h2s × 34.08 + n2 × 28.01 + h2 × 2.02
        SG = MW_avg / 28.97

        **Typical Hydrocarbon MW:**
        - Pure methane: 16.04
        - Dry gas (C1-C2): 16-18
        - Associated gas (C1-C4): 18-25
        - Wet gas (C1-C6): 25-35
        - Condensate gas: 35-50

        **Applications:**
        - **Compositional Simulation:** Convert composition to SG for black oil models
        - **Gas Plant Feed:** Characterize feed gas from composition analysis
        - **Sales Gas Specs:** Calculate SG for pipeline specifications
        - **Contaminated Gas:** Analyze gas with high non-hydrocarbon content
        - **Laboratory Data:** Convert GC analysis to SG

        **Non-Hydrocarbon Effects:**
        - CO2 increases SG (MW=44.01 > air MW=28.97)
        - H2S increases SG (MW=34.08 > air MW=28.97)
        - N2 slightly decreases SG (MW=28.01 ≈ air MW=28.97)
        - H2 significantly decreases SG (MW=2.02 << air MW=28.97)

        **Returns:**
        Dictionary with:
        - **gas_specific_gravity** (float): Gas SG (dimensionless, air=1)
        - **composition** (dict): Detailed composition breakdown
          - hydrocarbon_fraction: Mole fraction of hydrocarbons
          - hydrocarbon_mw: Provided hydrocarbon MW
          - co2_fraction: CO2 mole fraction
          - h2s_fraction: H2S mole fraction
          - n2_fraction: N2 mole fraction
          - h2_fraction: H2 mole fraction
        - **method** (str): "Molecular weight weighted average"
        - **units** (str): "dimensionless (air=1)"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using weight fraction instead of mole fraction
        - Incorrect hydrocarbon MW (must be average MW of HC fraction)
        - Mole fractions don't sum to 1.0 (should sum to 1.0)
        - Using component MW instead of mixture MW for hydrocarbons
        - Not accounting for all non-hydrocarbon components

        **Example Usage:**
        ```python
        {
            "hc_mw": 18.5,
            "co2": 0.05,
            "h2s": 0.0,
            "n2": 0.01,
            "h2": 0.0
        }
        ```
        Result: SG ≈ 0.65-0.70 (typical natural gas with 5% CO2, 1% N2).

        **Note:** Mole fractions must sum to 1.0. If only HC fraction is provided,
        ensure hc_fraction = 1.0 - (co2 + h2s + n2 + h2). Hydrocarbon MW should be
        the average MW of the hydrocarbon fraction, not individual component MW.
        """
        sg = gas.gas_sg(
            hc_mw=request.hc_mw,
            co2=request.co2,
            h2s=request.h2s,
            n2=request.n2,
            h2=request.h2
        )

        # Calculate composition details
        total_non_hc = request.co2 + request.h2s + request.n2 + request.h2
        hc_fraction = 1.0 - total_non_hc

        return {
            "gas_specific_gravity": float(sg),
            "composition": {
                "hydrocarbon_fraction": float(hc_fraction),
                "hydrocarbon_mw": request.hc_mw,
                "co2_fraction": request.co2,
                "h2s_fraction": request.h2s,
                "n2_fraction": request.n2,
                "h2_fraction": request.h2,
            },
            "method": "Molecular weight weighted average",
            "units": "dimensionless (air=1)",
            "inputs": request.model_dump(),
        }
