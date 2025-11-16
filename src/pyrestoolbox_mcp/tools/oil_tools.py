"""Oil PVT calculation tools for FastMCP."""

import numpy as np
import pyrestoolbox.oil as oil
from pyrestoolbox.classes import pb_method, rs_method, bo_method, uo_method
from fastmcp import FastMCP

from ..models.oil_models import (
    BubblePointRequest,
    SolutionGORRequest,
    OilFVFRequest,
    OilViscosityRequest,
    OilDensityRequest,
    OilCompressibilityRequest,
    APIConversionRequest,
    SGConversionRequest,
    BlackOilTableRequest,
    EvolvedGasSGRequest,
    JacobyAromaticitySGRequest,
    TwuPropertiesRequest,
    WeightedAverageGasSGRequest,
    StockTankGORRequest,
    CheckGasSGsRequest,
)


def register_oil_tools(mcp: FastMCP) -> None:
    """Register all oil-related tools with the MCP server."""

    @mcp.tool()
    def oil_bubble_point(request: BubblePointRequest) -> dict:
        """Calculate oil bubble point pressure (Pb).

        **CRITICAL PVT PROPERTY** - The bubble point is the pressure at which gas first
        begins to evolve from solution in oil. Essential for all oil reservoir calculations.

        **Parameters:**
        - **api** (float, required): Oil API gravity in degrees. Valid range: 0-100.
          Typical values: 20-50. Example: 35.0 for medium gravity crude.
        - **degf** (float, required): Reservoir temperature in degrees Fahrenheit.
          Valid range: -460 to 1000. Typical: 100-300°F. Example: 180.0.
        - **rsb** (float, required): Solution gas-oil ratio at bubble point in scf/stb.
          Must be ≥ 0. Typical: 100-3000 scf/stb. Example: 800.0.
        - **sg_g** (float, optional, default=0.0): Gas specific gravity (air=1.0).
          Valid range: 0-3. Typical: 0.6-1.2. Example: 0.75 for associated gas.
        - **method** (str, optional, default="VALMC"): Correlation method.
          Options: "STAN", "VALMC", "VELAR". VALMC recommended for wider applicability.

        **Method Selection:**
        - **VALMC** (Valko-McCain 2003): Recommended. Best for wide range of conditions.
          Use for: Most applications, high GOR oils, wide temperature ranges.
        - **STAN** (Standing 1947): Classic correlation. Use for: Standard conditions,
          quick estimates, compatibility with older methods.
        - **VELAR** (Velarde 1997): Alternative method. Use for: Specific regional
          correlations, comparison studies.

        **Returns:**
        Dictionary with:
        - **value** (float): Bubble point pressure in psia
        - **method** (str): Method used
        - **units** (str): "psia"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Confusing rsb (solution GOR at bubble point) with separator GOR
        - Using gas gravity from wrong separator stage
        - Temperature in Celsius instead of Fahrenheit

        **Example Usage:**
        ```python
        {
            "api": 35.0,
            "degf": 180.0,
            "rsb": 800.0,
            "sg_g": 0.75,
            "method": "VALMC"
        }
        ```
        Expected result: Pb ≈ 3000-4000 psia for typical oil.

        **Note:** If Pb > reservoir pressure, reservoir is undersaturated (no free gas).
        If Pb < reservoir pressure, reservoir is saturated (gas cap present).
        """
        method_enum = getattr(pb_method, request.method)

        # VALMC and VELAR methods require sg_sp (separator gas), STAN requires sg_g
        # If sg_sp is not provided but method needs it, use sg_g as fallback
        # This is a common assumption when separator gas gravity is not available
        if request.method in ['VALMC', 'VELAR']:
            sg_sp = getattr(request, 'sg_sp', None) or request.sg_g
            sg_g_param = 0
        else:  # STAN method
            sg_sp = 0
            sg_g_param = request.sg_g

        # Validate inputs before calling to avoid sys.exit() in pyrestoolbox
        if request.api <= 0 or request.degf <= 0 or request.rsb <= 0:
            raise ValueError(
                f"Invalid input parameters: api ({request.api}), degf ({request.degf}), "
                f"and rsb ({request.rsb}) must all be greater than 0"
            )
        
        if request.method in ['VALMC', 'VELAR'] and sg_sp <= 0:
            raise ValueError(
                f"Invalid input: {request.method} method requires sg_sp (separator gas gravity) > 0. "
                f"Provided: sg_g={request.sg_g}. Please provide a valid gas specific gravity."
            )
        
        if request.method == 'STAN' and sg_g_param <= 0:
            raise ValueError(
                f"Invalid input: STAN method requires sg_g (weighted average gas gravity) > 0. "
                f"Provided: sg_g={request.sg_g}"
            )

        try:
            pbub = oil.oil_pbub(
                api=request.api,
                degf=request.degf,
                rsb=request.rsb,
                sg_g=sg_g_param,
                sg_sp=sg_sp,
                pbmethod=method_enum,
            )
        except (SystemExit, BaseException) as e:
            # Catch sys.exit() calls from pyrestoolbox validation
            # SystemExit is a BaseException, not Exception
            if isinstance(e, SystemExit):
                raise ValueError(
                    f"Invalid input parameters for {request.method} method. "
                    f"For VALMC/VELAR: requires sg_sp (separator gas gravity) > 0. "
                    f"For STAN: requires sg_g (weighted average gas gravity) > 0. "
                    f"All methods require: api > 0, degf > 0, rsb > 0"
                ) from None
            raise

        return {
            "value": float(pbub),
            "method": request.method,
            "units": "psia",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_solution_gor(request: SolutionGORRequest) -> dict:
        """Calculate solution gas-oil ratio (Rs) at specified pressure.

        **CRITICAL PVT PROPERTY** - Computes volume of gas dissolved in oil at given
        pressure and temperature. Rs increases with pressure up to bubble point, then
        remains constant (equal to rsb) above bubble point.

        **Parameters:**
        - **api** (float, required): Oil API gravity in degrees. Valid: 0-100.
          Example: 35.0.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3000.0 or [2000, 3000, 4000].
        - **sg_g** (float, optional, default=0.0): Separator gas specific gravity (air=1).
          Valid: 0-3. Typical: 0.6-1.2. Example: 0.75.
        - **pb** (float, optional, default=0.0): Bubble point pressure in psia.
          If 0, will be calculated. Must be ≥ 0. Example: 3500.0.
        - **rsb** (float, optional, default=0.0): Solution GOR at bubble point in scf/stb.
          If 0 and pb provided, will be calculated. Must be ≥ 0. Example: 800.0.
        - **method** (str, optional, default="VELAR"): Correlation method.
          Options: "VELAR", "STAN", "VALMC".

        **Pressure Behavior:**
        - **p < pb**: Rs calculated from correlation (increases with pressure)
        - **p ≥ pb**: Rs = rsb (constant, no additional gas dissolves)

        **Method Selection:**
        - **VELAR** (Velarde 1997): Default, good accuracy. Use for most cases.
        - **STAN** (Standing 1947): Classic, widely used. Use for compatibility.
        - **VALMC** (Valko-McCain 2003): Alternative method.

        **Returns:**
        Dictionary with:
        - **value** (float or list): Rs in scf/stb (matches input p shape)
        - **method** (str): Method used
        - **units** (str): "scf/stb"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator gas gravity instead of separator gas gravity (sg_g parameter)
        - Not providing pb when p > pb (will calculate incorrectly)
        - Pressure in barg/psig instead of psia (must be absolute)
        - Confusing rsb (at bubble point) with separator GOR

        **Example Usage:**
        ```python
        {
            "api": 35.0,
            "degf": 180.0,
            "p": [2000, 3000, 4000],
            "sg_g": 0.75,
            "pb": 3500.0,
            "rsb": 800.0,
            "method": "VELAR"
        }
        ```
        Result: Rs increases from ~400 scf/stb at 2000 psia to 800 scf/stb at 3500 psia,
        then remains 800 scf/stb at 4000 psia (above bubble point).

        **Note:** Always provide pb and rsb when available for accurate results.
        If unknown, set pb=0 and rsb=0 to auto-calculate, but accuracy may be reduced.
        """
        method_enum = getattr(rs_method, request.method)

        rs = oil.oil_rs(
            api=request.api,
            degf=request.degf,
            p=request.p,
            sg_sp=request.sg_g,  # oil_rs uses sg_sp not sg_g
            pb=request.pb,
            rsb=request.rsb,
            rsmethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(rs, np.ndarray):
            value = rs.tolist()
        else:
            value = float(rs)

        return {
            "value": value,
            "method": request.method,
            "units": "scf/stb",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_formation_volume_factor(request: OilFVFRequest) -> dict:
        """Calculate oil formation volume factor (Bo).

        **CRITICAL PVT PROPERTY** - Computes ratio of oil volume at reservoir conditions
        to volume at standard conditions. Bo > 1.0 because oil expands due to dissolved gas
        and thermal expansion. Essential for material balance, reserve calculations, and
        production forecasting.

        **Parameters:**
        - **api** (float, required): Oil API gravity in degrees. Valid: 0-100. Example: 35.0.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3000.0 or [2000, 3000, 4000].
        - **sg_g** (float, optional, default=0.0): Gas specific gravity (air=1).
          Valid: 0-3. Typical: 0.6-1.2. Example: 0.75.
        - **pb** (float, optional, default=0.0): Bubble point pressure in psia.
          Required for accurate calculation. Example: 3500.0.
        - **rs** (float or list, optional, default=0.0): Solution GOR at pressure p in scf/stb.
          If 0, will be calculated from p. Must match p shape. Example: 600.0 or [400, 600, 800].
        - **rsb** (float, optional, default=0.0): Solution GOR at bubble point in scf/stb.
          Required if pb provided. Example: 800.0.
        - **method** (str, optional, default="MCAIN"): Correlation method.
          Options: "MCAIN", "STAN". MCAIN recommended.

        **Pressure Behavior:**
        - **p < pb**: Bo increases with pressure (more gas dissolves)
        - **p = pb**: Bo reaches maximum (Bob, typically 1.2-2.0 rb/stb)
        - **p > pb**: Bo decreases with pressure (oil compressibility dominates)

        **Method Selection:**
        - **MCAIN** (McCain et al. 1988): Recommended. More accurate, wider range.
        - **STAN** (Standing 1947): Classic method. Use for compatibility.

        **Returns:**
        Dictionary with:
        - **value** (float or list): Bo in rb/stb (matches input p shape)
        - **method** (str): Method used
        - **units** (str): "rb/stb"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Not providing rs when p < pb (will calculate incorrectly)
        - Using separator GOR instead of solution GOR at reservoir pressure
        - Pressure in barg/psig instead of psia
        - Confusing Bo (reservoir volume) with Bg (gas FVF)

        **Example Usage:**
        ```python
        {
            "api": 35.0,
            "degf": 180.0,
            "p": [2000, 3000, 4000],
            "sg_g": 0.75,
            "pb": 3500.0,
            "rs": [400, 600, 800],
            "rsb": 800.0,
            "method": "MCAIN"
        }
        ```
        Result: Bo increases from ~1.15 rb/stb at 2000 psia to ~1.35 rb/stb at 3500 psia,
        then decreases to ~1.33 rb/stb at 4000 psia (above bubble point).

        **Note:** Always provide rs for pressures below bubble point. If rs=0, tool will
        calculate it, but providing it explicitly improves accuracy.
        """
        method_enum = getattr(bo_method, request.method)
        
        # Calculate sg_o from API
        sg_o = oil.oil_sg(api_value=request.api)

        bo = oil.oil_bo(
            p=request.p,
            pb=request.pb,
            degf=request.degf,
            rs=request.rs,
            rsb=request.rsb,
            sg_o=sg_o,
            sg_g=request.sg_g,
            bomethod=method_enum,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(bo, np.ndarray):
            value = bo.tolist()
        else:
            value = float(bo)

        return {
            "value": value,
            "method": request.method,
            "units": "rb/stb",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_viscosity(request: OilViscosityRequest) -> dict:
        """Calculate oil viscosity (μo).

        **CRITICAL PVT PROPERTY** - Computes oil viscosity at reservoir conditions.
        Viscosity affects flow rates, pressure drops, and recovery efficiency.
        Uses Beggs-Robinson (1975) correlation, industry standard for oil viscosity.

        **Parameters:**
        - **api** (float, required): Oil API gravity in degrees. Valid: 0-100.
          Example: 35.0. Higher API = lighter oil = lower viscosity.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0. Higher temperature = lower viscosity.
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3000.0 or [2000, 3000, 4000].
        - **pb** (float, optional, default=0.0): Bubble point pressure in psia.
          Required for accurate calculation. Example: 3500.0.
        - **rs** (float or list, optional, default=0.0): Solution GOR at pressure p in scf/stb.
          If 0, will be calculated. Must match p shape. Example: 600.0.
        - **rsb** (float, optional, default=0.0): Solution GOR at bubble point in scf/stb.
          Required if pb provided. Example: 800.0.
        - **method** (str, optional, default="BR"): Correlation method. Only "BR" available.

        **Viscosity Behavior:**
        - **p < pb**: Viscosity decreases with pressure (more gas dissolves, oil thins)
        - **p = pb**: Viscosity reaches minimum (μob, typically 0.5-5 cP)
        - **p > pb**: Viscosity increases with pressure (oil compression)

        **Typical Ranges:**
        - Light oils (API > 35): 0.5-2 cP at bubble point
        - Medium oils (API 25-35): 1-10 cP at bubble point
        - Heavy oils (API < 25): 10-1000+ cP at bubble point

        **Returns:**
        Dictionary with:
        - **value** (float or list): Viscosity in cP (matches input p shape)
        - **method** (str): "BR" (Beggs-Robinson)
        - **units** (str): "cP"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Not providing rs when p < pb (will calculate incorrectly)
        - Using dead oil viscosity instead of live oil viscosity
        - Temperature in Celsius instead of Fahrenheit
        - Pressure in barg/psig instead of psia

        **Example Usage:**
        ```python
        {
            "api": 35.0,
            "degf": 180.0,
            "p": [2000, 3000, 4000],
            "pb": 3500.0,
            "rs": [400, 600, 800],
            "rsb": 800.0,
            "method": "BR"
        }
        ```
        Result: Viscosity decreases from ~1.2 cP at 2000 psia to ~0.8 cP at 3500 psia,
        then increases to ~0.85 cP at 4000 psia (above bubble point).

        **Note:** Viscosity is highly sensitive to temperature and dissolved gas content.
        Always use reservoir temperature, not separator temperature.
        """
        method_enum = getattr(uo_method, request.method)

        uo = oil.oil_viso(
            p=request.p,
            api=request.api,
            degf=request.degf,
            pb=request.pb,
            rs=request.rs,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(uo, np.ndarray):
            value = uo.tolist()
        else:
            value = float(uo)

        return {
            "value": value,
            "method": request.method,
            "units": "cP",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_density(request: OilDensityRequest) -> dict:
        """Calculate oil density (ρo) at reservoir conditions.

        **CRITICAL PVT PROPERTY** - Computes oil density from PVT properties using
        mass balance approach. Essential for gradient calculations, well pressure analysis,
        and material balance calculations.

        **Parameters:**
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3000.0.
        - **api** (float, required): Oil API gravity in degrees. Valid: 0-100.
          Example: 35.0.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0.
        - **rs** (float or list, required): Solution GOR at pressure p in scf/stb.
          Must match p shape. Example: 600.0 or [400, 600, 800].
        - **sg_g** (float, required): Gas specific gravity (air=1). Valid: 0-3.
          Typical: 0.6-1.2. Example: 0.75.
        - **bo** (float or list, required): Oil formation volume factor at pressure p in rb/stb.
          Must match p shape. Calculate using oil_formation_volume_factor tool first.
          Example: 1.25 or [1.15, 1.25, 1.30].

        **Calculation Method:**
        Density = (Stock tank oil mass + Dissolved gas mass) / Reservoir volume
        ρo = (sg_o × 62.372 + 0.01357 × Rs × sg_g) / Bo

        Where:
        - sg_o = oil specific gravity (calculated from API)
        - 62.372 = water density at standard conditions (lb/cuft)
        - 0.01357 = gas density conversion factor

        **Typical Ranges:**
        - Light oils: 40-50 lb/cuft
        - Medium oils: 50-55 lb/cuft
        - Heavy oils: 55-65 lb/cuft

        **Returns:**
        Dictionary with:
        - **value** (float or list): Density in lb/cuft (matches input p shape)
        - **method** (str): "Standard"
        - **units** (str): "lb/cuft"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using stock tank density instead of reservoir density
        - Not providing matching rs and bo arrays
        - Using wrong bo value (must be at same pressure as p)
        - Confusing density (mass/volume) with specific gravity (dimensionless)

        **Example Usage:**
        ```python
        {
            "p": 3000.0,
            "api": 35.0,
            "degf": 180.0,
            "rs": 600.0,
            "sg_g": 0.75,
            "bo": 1.25
        }
        ```
        Result: Density ≈ 48-52 lb/cuft for typical medium gravity oil.

        **Note:** Always calculate Bo first using oil_formation_volume_factor tool,
        then use matching rs and bo values for accurate density calculation.
        """
        # Calculate sg_o from API
        sg_o = oil.oil_sg(api_value=request.api)
        
        # Calculate density - note: oil_deno doesn't calculate from bo,
        # it calculates density directly. We use bo to back-calculate rs if needed.
        # For simple density, we can use the formula: density = (sg_o * 62.372 + 0.01357 * rs * sg_g) / bo
        density = (sg_o * 62.372 + 0.01357 * request.rs * request.sg_g) / request.bo
        deno = density

        # Convert numpy array to list for JSON serialization
        if isinstance(deno, np.ndarray):
            value = deno.tolist()
        else:
            value = float(deno)

        return {
            "value": value,
            "method": "Standard",
            "units": "lb/cuft",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_compressibility(request: OilCompressibilityRequest) -> dict:
        """Calculate oil compressibility (Co).

        **CRITICAL PVT PROPERTY** - Computes oil compressibility coefficient, which measures
        how much oil volume changes with pressure. Essential for material balance calculations,
        pressure transient analysis, and reserve estimation. Co is typically 5-50 × 10⁻⁶ 1/psi.

        **Parameters:**
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3000.0 or [2000, 3000, 4000].
        - **api** (float, required): Oil API gravity in degrees. Valid: 0-100.
          Example: 35.0.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0.
        - **pb** (float, required): Bubble point pressure in psia. Must be ≥ 0.
          Example: 3500.0.
        - **sg_g** (float, required): Gas specific gravity (air=1). Valid: 0-3.
          Typical: 0.6-1.2. Example: 0.75.
        - **rs** (float or list, optional, default=0.0): Solution GOR at pressure p in scf/stb.
          If 0, will be calculated. Must match p shape. Example: 600.0.
        - **rsb** (float, optional, default=0.0): Solution GOR at bubble point in scf/stb.
          Required if pb provided. Example: 800.0.

        **Compressibility Behavior:**
        - **p < pb**: Co is relatively constant (oil + dissolved gas compressibility)
        - **p = pb**: Co increases sharply (gas evolution begins)
        - **p > pb**: Co decreases with pressure (gas compressibility dominates)

        **Typical Ranges:**
        - Undersaturated oil: 5-20 × 10⁻⁶ 1/psi
        - At bubble point: 20-50 × 10⁻⁶ 1/psi
        - Above bubble point: 10-30 × 10⁻⁶ 1/psi

        **Returns:**
        Dictionary with:
        - **value** (float or list): Compressibility in 1/psi (matches input p shape)
        - **method** (str): "McCain"
        - **units** (str): "1/psi"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Not providing pb (required for accurate calculation)
        - Using wrong pressure (must be reservoir pressure, not separator)
        - Confusing oil compressibility with gas compressibility
        - Not accounting for dissolved gas effects

        **Example Usage:**
        ```python
        {
            "p": [2000, 3000, 4000],
            "api": 35.0,
            "degf": 180.0,
            "pb": 3500.0,
            "sg_g": 0.75,
            "rs": [400, 600, 800],
            "rsb": 800.0
        }
        ```
        Result: Co ≈ 10-15 × 10⁻⁶ 1/psi below bubble point, increases near pb.

        **Note:** Compressibility is critical for material balance calculations.
        Always provide pb for accurate results. Co values are small (micro-1/psi),
        so results are typically in scientific notation.
        """
        co = oil.oil_co(
            p=request.p,
            api=request.api,
            degf=request.degf,
            pb=request.pb,
            sg_g=request.sg_g,
            rsb=request.rsb,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(co, np.ndarray):
            value = co.tolist()
        else:
            value = float(co)

        return {
            "value": value,
            "method": "McCain",
            "units": "1/psi",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_api_from_sg(request: SGConversionRequest) -> dict:
        """Convert oil specific gravity to API gravity.

        **UNIT CONVERSION TOOL** - Converts oil specific gravity (dimensionless, water=1.0)
        to API gravity (degrees). API gravity is an inverse measure of density - higher API
        means lighter oil. Essential for standardizing oil property reporting.

        **Parameters:**
        - **sg** (float or list, required): Oil specific gravity (water=1.0).
          Valid range: 0.1-1.5. Typical: 0.8-1.0. Example: 0.85 or [0.80, 0.85, 0.90].
          Can be scalar or array.

        **Conversion Formula:**
        API = (141.5 / SG) - 131.5

        **API Gravity Ranges:**
        - Heavy oil: API < 22° (SG > 0.922)
        - Medium oil: API 22-35° (SG 0.922-0.850)
        - Light oil: API > 35° (SG < 0.850)
        - Water: API = 10° (SG = 1.0)

        **Returns:**
        Dictionary with:
        - **value** (float or list): API gravity in degrees (matches input sg shape)
        - **method** (str): "Standard conversion"
        - **units** (str): "degrees API"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using gas specific gravity instead of oil specific gravity
        - Confusing API gravity with specific gravity (inverse relationship)
        - Using density (lb/cuft) instead of specific gravity
        - Not understanding that higher API = lighter oil

        **Example Usage:**
        ```python
        {
            "sg": 0.85
        }
        ```
        Result: API = (141.5 / 0.85) - 131.5 ≈ 35.0° (medium gravity oil)

        **Note:** API gravity is the industry standard for oil classification.
        Use this conversion when you have specific gravity but need API gravity
        for correlations or reporting.
        """
        api = oil.oil_api(sg_value=request.sg)

        # Convert numpy array to list for JSON serialization
        if isinstance(api, np.ndarray):
            value = api.tolist()
        else:
            value = float(api)

        return {
            "value": value,
            "method": "Standard conversion",
            "units": "degrees API",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_sg_from_api(request: APIConversionRequest) -> dict:
        """Convert API gravity to oil specific gravity.

        **UNIT CONVERSION TOOL** - Converts API gravity (degrees) to specific gravity
        (dimensionless, water=1.0). Specific gravity is the ratio of oil density to water
        density at standard conditions. Essential for calculations requiring specific gravity.

        **Parameters:**
        - **api** (float or list, required): Oil API gravity in degrees.
          Valid range: 0-100. Typical: 20-50. Example: 35.0 or [30, 35, 40].
          Can be scalar or array.

        **Conversion Formula:**
        SG = 141.5 / (API + 131.5)

        **Specific Gravity Ranges:**
        - Heavy oil: SG > 0.922 (API < 22°)
        - Medium oil: SG 0.850-0.922 (API 22-35°)
        - Light oil: SG < 0.850 (API > 35°)
        - Water: SG = 1.0 (API = 10°)

        **Returns:**
        Dictionary with:
        - **value** (float or list): Specific gravity (dimensionless, matches input api shape)
        - **method** (str): "Standard conversion"
        - **units** (str): "dimensionless (water=1)"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using gas API gravity instead of oil API gravity
        - Confusing API gravity with specific gravity (inverse relationship)
        - Not understanding that lower SG = lighter oil (higher API)
        - Using wrong conversion formula

        **Example Usage:**
        ```python
        {
            "api": 35.0
        }
        ```
        Result: SG = 141.5 / (35.0 + 131.5) ≈ 0.850 (medium gravity oil)

        **Note:** Most PVT correlations use API gravity directly, but some require
        specific gravity. Use this conversion when needed. Remember: API and SG are
        inversely related - higher API means lower SG (lighter oil).
        """
        sg = oil.oil_sg(api_value=request.api)

        # Convert numpy array to list for JSON serialization
        if isinstance(sg, np.ndarray):
            value = sg.tolist()
        else:
            value = float(sg)

        return {
            "value": value,
            "method": "Standard conversion",
            "units": "dimensionless (water=1)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def generate_black_oil_table(request: BlackOilTableRequest) -> dict:
        """Generate comprehensive black oil PVT table.

        **COMPREHENSIVE PVT TABLE GENERATOR** - Creates complete black oil PVT table with
        all properties (Rs, Bo, μo, ρo, Co) at pressures from 14.7 psia to specified maximum.
        This is the most comprehensive PVT tool, generating complete tables for reservoir
        simulation input or analysis. Optionally exports ECLIPSE-compatible keywords.

        **Parameters:**
        - **pi** (float, required): Initial reservoir pressure in psia. Must be > 0.
          Example: 4000.0. Table starts from 14.7 psia and goes up to pmax.
        - **api** (float, required): Oil API gravity in degrees. Valid: 0-100.
          Example: 38.0.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 175.0.
        - **sg_g** (float, required): Gas specific gravity (air=1). Valid: 0-3.
          Typical: 0.6-1.2. Example: 0.68.
        - **pmax** (float, optional, default=0.0): Maximum pressure for table in psia.
          If 0, auto-calculates as pi × 1.5. Must be > pi. Example: 5000.0.
        - **pb** (float, optional, default=0.0): Bubble point pressure in psia.
          If 0, will be calculated. Example: 3900.0.
        - **rsb** (float, optional, default=0.0): Solution GOR at bubble point in scf/stb.
          If 0, will be calculated. Example: 2300.0.
        - **nrows** (int, optional, default=50): Number of table rows. Valid: 1-200.
          More rows = finer resolution. Typical: 20-100. Example: 50.
        - **export** (bool, optional, default=False): Export ECLIPSE-compatible files.
          If True, creates PVTO.INC, PVDO.INC, DENSITY.INC files. Example: False.
        - **pb_method** (str, optional, default="VALMC"): Bubble point method.
          Options: "STAN", "VALMC", "VELAR". VALMC recommended.
        - **rs_method** (str, optional, default="VELAR"): Solution GOR method.
          Options: "VELAR", "STAN", "VALMC". VELAR recommended.
        - **bo_method** (str, optional, default="MCAIN"): Oil FVF method.
          Options: "MCAIN", "STAN". MCAIN recommended.
        - **uo_method** (str, optional, default="BR"): Oil viscosity method.
          Only "BR" available.

        **Generated Properties:**
        - **Rs**: Solution gas-oil ratio (scf/stb) - increases with pressure up to pb
        - **Bo**: Formation volume factor (rb/stb) - peaks at bubble point
        - **μo**: Oil viscosity (cP) - minimum at bubble point
        - **ρo**: Oil density (lb/cuft) - calculated from mass balance
        - **Co**: Oil compressibility (1/psi) - increases near bubble point

        **Table Structure:**
        Pressure values are logarithmically spaced from 14.7 psia to pmax, with
        finer spacing near bubble point for accuracy.

        **ECLIPSE Export:**
        When export=True, generates:
        - **PVTO.INC**: Pressure-dependent oil properties (for undersaturated oil)
        - **PVDO.INC**: Dead oil properties (for heavy oils)
        - **DENSITY.INC**: Oil density table

        **Returns:**
        Dictionary with:
        - **table** (list of dicts): PVT table data, each dict contains pressure and all properties
        - **summary** (dict): Key values (bubble point, rsb, Bob, μob, etc.)
        - **columns** (list): Column names in table
        - **methods** (dict): Methods used for each property
        - **export_files** (dict, optional): File names if export=True
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Setting pmax too low (should be > pi for complete table)
        - Not providing pb and rsb when known (reduces accuracy)
        - Using wrong correlation methods (use recommended defaults)
        - Too few rows (nrows < 20) causing poor resolution
        - Not understanding table format for simulation input

        **Example Usage:**
        ```python
        {
            "pi": 4000.0,
            "api": 38.0,
            "degf": 175.0,
            "sg_g": 0.68,
            "pmax": 5000.0,
            "pb": 3900.0,
            "rsb": 2300.0,
            "nrows": 50,
            "export": False,
            "pb_method": "VALMC",
            "rs_method": "VELAR",
            "bo_method": "MCAIN",
            "uo_method": "BR"
        }
        ```
        Result: Complete PVT table with 50 rows covering 14.7-5000 psia with all properties.

        **Note:** This is the most comprehensive PVT tool. Use for complete reservoir
        analysis or simulation input preparation. Always provide pb and rsb when available
        for best accuracy. For simulation, set export=True to generate ECLIPSE keywords.
        """
        result = oil.make_bot_og(
            pi=request.pi,
            api=request.api,
            degf=request.degf,
            sg_g=request.sg_g,
            pmax=request.pmax if request.pmax > 0 else request.pi * 1.5,
            pb=request.pb,
            rsb=request.rsb,
            nrows=request.nrows,
            export=request.export,
            pbmethod=request.pb_method,
            rsmethod=request.rs_method,
            bomethod=request.bo_method,
        )

        # Convert DataFrame to list of dicts
        table_data = result["bot"].to_dict(orient="records")

        response = {
            "table": table_data,
            "summary": {
                "bubble_point_psia": float(result.get("pb", 0)),
                "solution_gor_scf_stb": float(result.get("rsb", 0)),
                "oil_fvf_at_pb_rb_stb": float(result.get("bob", result.get("Bo", 1.0))),
                "oil_viscosity_at_pb_cp": float(result.get("uob", result.get("uo", 1.0))),
                "oil_density_at_pb_lb_cuft": float(result.get("deno_oil", result.get("den", 50.0))),
                "gas_sg": float(result.get("sg_sp", result.get("sg_g", 0.75))),
                "rows": len(table_data),
            },
            "columns": list(result["bot"].columns),
            "methods": {
                "pb_method": request.pb_method,
                "rs_method": request.rs_method,
                "bo_method": request.bo_method,
                "uo_method": request.uo_method,
            },
            "inputs": request.model_dump(),
        }

        if request.export:
            response["export_files"] = {
                "pvto_file": "PVTO.INC",
                "pvdo_file": "PVDO.INC",
                "density_file": "DENSITY.INC",
                "note": "Files exported to current working directory",
            }

        return response

    @mcp.tool()
    def oil_rs_at_bubble_point(request: BubblePointRequest) -> dict:
        """Calculate solution GOR at bubble point using Standing correlation.

        Computes Rs specifically at the bubble point pressure based on
        reservoir fluid properties. Uses Standing (1947) correlation.

        This is useful when you know the bubble point pressure and need
        to calculate the corresponding solution GOR.

        Returns Rs in scf/stb.

        Args:
            request: Bubble point parameters (API, temperature, bubble point, gas gravity)

        Returns:
            Dictionary with Rs at bubble point, method, units, and inputs
        """
        # Calculate pb first to get rsb
        pb = oil.oil_pbub(
            api=request.api,
            degf=request.degf,
            rsb=request.rsb,
            sg_g=request.sg_g,
            pbmethod=request.method
        )
        
        # rsb is the solution GOR at bubble point
        rsb = request.rsb

        return {
            "value": float(rsb),
            "bubble_point_psia": float(pb),
            "method": "Standing",
            "units": "scf/stb",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def evolved_gas_sg(request: EvolvedGasSGRequest) -> dict:
        """Calculate evolved gas specific gravity.

        Computes the specific gravity of gas evolved from oil as pressure
        decreases below bubble point. This is important for:
        - Material balance calculations
        - Surface facility design
        - Gas sales forecasting

        The evolved gas composition changes with pressure, and this function
        accounts for that variation.

        Returns dimensionless specific gravity (air = 1.0).

        Args:
            request: Evolved gas parameters including oil properties, pressure(s),
                    and separator conditions

        Returns:
            Dictionary with evolved gas SG value(s), units, and inputs
        """
        sg_evolved = oil.sg_evolved_gas(
            p=request.p,
            degf=request.degf,
            rsb=800.0,  # Typical value
            api=request.api,
            sg_sp=request.sg_g,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(sg_evolved, np.ndarray):
            value = sg_evolved.tolist()
        else:
            value = float(sg_evolved)

        return {
            "value": value,
            "method": "Valko-McCain correlation",
            "units": "dimensionless (air=1)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def stock_tank_gas_sg(request: EvolvedGasSGRequest) -> dict:
        """Calculate stock tank gas specific gravity.

        Computes the specific gravity of gas liberated at stock tank conditions.
        This is the gas that comes out of solution when oil reaches atmospheric
        pressure and temperature.

        Stock tank gas properties are needed for:
        - Sales gas quality specifications
        - Flare gas calculations  
        - VOC emissions estimation
        - Safety assessments

        Returns dimensionless specific gravity (air = 1.0).

        Args:
            request: Stock tank gas parameters including oil properties and
                    separator conditions

        Returns:
            Dictionary with stock tank gas SG value(s), units, and inputs
        """
        # Calculate stock tank gas SG
        # Estimate separator GOR as 90% of total
        rsp = 800.0 * 0.9
        sg_st = oil.sg_st_gas(
            psp=request.psep,
            rsp=rsp,
            api=request.api,
            sg_sp=request.sg_g,
            degf_sp=100.0,  # Typical separator temp
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(sg_st, np.ndarray):
            value = sg_st.tolist()
        else:
            value = float(sg_st)

        return {
            "value": value,
            "method": "McCain correlation",
            "units": "dimensionless (air=1)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_sg_from_jacoby(request: JacobyAromaticitySGRequest) -> dict:
        """Calculate oil specific gravity from molecular weight and Jacoby aromaticity.

        **HYDROCARBON CHARACTERIZATION TOOL** - Estimates specific gravity
        for undefined petroleum fractions using molecular weight and aromaticity.

        **Jacoby Aromaticity Factor (JA):**
        - 0.0 = Pure paraffinic (alkanes)
        - 0.5 = Mixed (typical crude oils)
        - 1.0 = Pure aromatic

        **Applications:**
        - Plus fraction (C7+) characterization
        - Undefined heavy end lumping
        - EOS fluid modeling
        - Pseudo-component generation

        Returns specific gravity (dimensionless, water=1).

        Args:
            request: Molecular weight and Jacoby aromaticity factor

        Returns:
            Dictionary with specific gravity, method, and inputs
        """
        sg = oil.oil_ja_sg(mw=request.mw, ja=request.ja)

        if isinstance(sg, np.ndarray):
            value = sg.tolist()
        else:
            value = float(sg)

        return {
            "value": value,
            "method": "Jacoby aromaticity correlation",
            "units": "dimensionless (water=1)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_twu_critical_properties(request: TwuPropertiesRequest) -> dict:
        """Calculate critical properties using Twu (1984) correlation.

        **CRITICAL PROPERTIES ESTIMATION** - Most widely used method for
        estimating Tc, Pc, Vc for petroleum fractions and plus fractions.

        **Twu Method:**
        - More accurate than older correlations (Riazi-Daubert, Kesler-Lee)
        - Uses molecular weight and specific gravity
        - Optional boiling point for improved accuracy
        - Damping factor for heavy ends

        **Returns:**
        - Tc: Critical temperature (°R)
        - Pc: Critical pressure (psia)
        - Vc: Critical volume (cuft/lbmol)
        - Also returns: SG, Tb (if not provided)

        **Critical for:**
        - EOS (PR, SRK) fluid characterization
        - Plus fraction splitting
        - Compositional simulation
        - Phase behavior modeling

        Args:
            request: Molecular weight, specific gravity, optional boiling point, damping

        Returns:
            Dictionary with all critical properties
        """
        # oil_twu_props doesn't take tb as input, it calculates it
        result = oil.oil_twu_props(
            mw=request.mw,
            sg=request.sg,
            damp=request.damp
        )

        # result is tuple: (sg, tb, tc, pc, vc)
        return {
            "specific_gravity": float(result[0]) if not isinstance(result[0], np.ndarray) else result[0].tolist(),
            "boiling_point_degR": float(result[1]) if not isinstance(result[1], np.ndarray) else result[1].tolist(),
            "critical_temperature_degR": float(result[2]) if not isinstance(result[2], np.ndarray) else result[2].tolist(),
            "critical_pressure_psia": float(result[3]) if not isinstance(result[3], np.ndarray) else result[3].tolist(),
            "critical_volume_cuft_lbmol": float(result[4]) if not isinstance(result[4], np.ndarray) else result[4].tolist(),
            "method": "Twu (1984) correlation",
            "inputs": request.model_dump(),
            "note": "Use for plus fraction characterization and EOS modeling"
        }

    @mcp.tool()
    def weighted_average_gas_sg(request: WeightedAverageGasSGRequest) -> dict:
        """Calculate weighted average gas specific gravity from separator stages.

        **SURFACE FACILITIES CALCULATION** - Combines gas gravities from
        separator and stock tank weighted by GORs.

        **Use Cases:**
        - Multi-stage separation optimization
        - Surface facility design
        - Gas sales allocation
        - Material balance

        **Formula:**
        sg_avg = (sg_sp * rsp + sg_st * rst) / (rsp + rst)

        Returns weighted average gas SG (dimensionless, air=1).

        Args:
            request: Separator and stock tank gas properties

        Returns:
            Dictionary with weighted average SG and breakdown
        """
        sg_avg = oil.sgg_wt_avg(
            sg_sp=request.sg_sp,
            rsp=request.rsp,
            sg_st=request.sg_st,
            rst=request.rst
        )

        return {
            "weighted_average_sg": float(sg_avg),
            "separator_contribution": float(request.sg_sp * request.rsp / (request.rsp + request.rst)),
            "stock_tank_contribution": float(request.sg_st * request.rst / (request.rsp + request.rst)),
            "total_gor_scf_stb": float(request.rsp + request.rst),
            "method": "Weighted average by GOR",
            "units": "dimensionless (air=1)",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def stock_tank_incremental_gor(request: StockTankGORRequest) -> dict:
        """Calculate incremental GOR from separator to stock tank.

        **SEPARATOR DESIGN TOOL** - Estimates gas evolved between
        separator and stock tank conditions.

        **Physics:**
        As oil flows from separator (higher P, T) to stock tank (14.7 psia, ~60°F),
        additional gas comes out of solution.

        **Applications:**
        - Separator optimization
        - Gas recovery calculations
        - Tank venting requirements
        - VOC emissions estimation

        Returns stock tank incremental GOR in scf/stb.

        Args:
            request: Separator pressure, temperature, and oil API

        Returns:
            Dictionary with incremental GOR and guidance
        """
        rst = oil.oil_rs_st(
            psp=request.psp,
            degf_sp=request.degf_sp,
            api=request.api
        )

        return {
            "stock_tank_gor_scf_stb": float(rst),
            "method": "Empirical correlation",
            "units": "scf/stb",
            "inputs": request.model_dump(),
            "note": "Add to separator GOR for total solution GOR at reservoir conditions"
        }

    @mcp.tool()
    def validate_gas_gravities(request: CheckGasSGsRequest) -> dict:
        """Validate and impute missing gas gravities.

        **DATA VALIDATION TOOL** - Checks consistency of gas gravities
        and calculates missing values when one is unknown.

        **Logic:**
        - If sg_g provided: Calculate sg_sp from sg_g
        - If sg_sp provided: Calculate sg_g from sg_sp
        - If both provided: Validate consistency

        **Use Cases:**
        - QC PVT data before analysis
        - Fill gaps in incomplete data
        - Validate separator gas measurements

        Returns tuple of (sg_g, sg_sp) with calculated/validated values.

        Args:
            request: Available gas gravities and GORs

        Returns:
            Dictionary with validated/calculated gas gravities
        """
        sg_g_out, sg_sp_out = oil.check_sgs(
            sg_g=request.sg_g if request.sg_g is not None else 0,
            sg_sp=request.sg_sp if request.sg_sp is not None else 0,
            rst=request.rst,
            rsp=request.rsp,
            sg_st=request.sg_st
        )

        return {
            "sg_g_weighted_average": float(sg_g_out),
            "sg_sp_separator": float(sg_sp_out),
            "method": "Weighted average calculation",
            "units": "dimensionless (air=1)",
            "inputs": request.model_dump(),
            "note": "sg_g and sg_sp are now consistent and validated"
        }
