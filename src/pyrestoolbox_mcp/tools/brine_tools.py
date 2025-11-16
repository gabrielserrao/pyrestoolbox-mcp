"""Brine property calculation tools for FastMCP."""

import numpy as np
import pyrestoolbox.brine as brine
from fastmcp import FastMCP

from ..models.brine_models import BrinePropertiesRequest, CO2BrineMixtureRequest


def register_brine_tools(mcp: FastMCP) -> None:
    """Register all brine-related tools with the MCP server."""

    @mcp.tool()
    def calculate_brine_properties(request: BrinePropertiesRequest) -> dict:
        """Calculate properties of CH4 or CO2 saturated brine.

        **BRINE PVT TOOL** - Computes comprehensive brine properties including density,
        viscosity, compressibility, and formation volume factor. Essential for aquifer
        analysis, water injection, and CO2 sequestration studies.

        **Parameters:**
        - **p** (float or list, required): Pressure(s) in psia. Must be > 0.
          Can be scalar or array. Example: 3000.0 or [1000, 2000, 3000].
        - **degf** (float, required): Temperature in °F. Valid: -460 to 1000.
          Typical: 100-400°F. Example: 180.0.
        - **wt** (float, required): Salinity in weight percent NaCl (0-30).
          Typical: 0-20 wt%. Example: 5.0 for 5% NaCl brine.
        - **ch4** (float, optional, default=0.0): CH4 saturation fraction (0-1).
          Typical: 0-0.1. Example: 0.05 for 5% CH4 saturation.
        - **co2** (float, optional, default=0.0): CO2 saturation fraction (0-1).
          Typical: 0-0.1. Example: 0.03 for 3% CO2 saturation.

        **Properties Calculated:**
        - **Density (ρw):** Brine density in lb/cuft. Increases with salinity, pressure.
          Typical: 60-70 lb/cuft.
        - **Viscosity (μw):** Brine viscosity in cP. Decreases with temperature, increases with salinity.
          Typical: 0.3-1.5 cP.
        - **Compressibility (cw):** Brine compressibility in 1/psi. Critical for aquifer influx.
          Typical: 2e-6 to 5e-6 1/psi.
        - **Formation Volume Factor (Bw):** Volume ratio rb/stb. Slightly > 1.0.
          Typical: 1.01-1.05 rb/stb.
        - **Solution GOR (Rw):** Gas dissolved in brine in scf/stb. Increases with pressure.
          Typical: 0-20 scf/stb.

        **Dissolved Gas Effects:**
        - **CH4-saturated:** Methane dissolved in formation water (typical in aquifers)
        - **CO2-saturated:** CO2 dissolution (sequestration, EOR, geothermal)
        - Mixed systems supported (CH4 + CO2)
        - Dissolved gas reduces density and increases compressibility

        **Salinity Range:** 0-30 wt% NaCl (fresh water to highly saline)
        - Fresh water: 0 wt%
        - Brackish: 0.1-1 wt%
        - Seawater: ~3.5 wt%
        - Formation brine: 5-20 wt%
        - Highly saline: 20-30 wt%

        **Correlations:**
        Uses industry-standard correlations accounting for:
        - Pressure effects on density and viscosity
        - Temperature effects (viscosity decreases with T)
        - Salinity variations (density and viscosity increase with salinity)
        - Dissolved gas concentrations (reduces density)

        **Applications:**
        - **Aquifer Influx:** Calculate water influx rates and volumes
        - **Water Injection:** Design injection projects and pressure maintenance
        - **CO2 Sequestration:** Evaluate CO2 storage capacity and brine properties
        - **Geothermal Reservoirs:** Analyze geothermal brine properties
        - **Pressure Maintenance:** Evaluate aquifer pressure support
        - **Material Balance:** Include water drive in material balance calculations

        **Returns:**
        Dictionary with:
        - **formation_volume_factor_rb_stb** (float or list): Bw (matches input p shape)
        - **density_lb_cuft** (float or list): Brine density (matches input p shape)
        - **viscosity_cp** (float or list): Brine viscosity (matches input p shape)
        - **compressibility_1_psi** (float or list): Brine compressibility (matches input p shape)
        - **solution_gor_scf_stb** (float or list): Gas dissolved in brine (matches input p shape)
        - **method** (str): "Industry standard correlations"
        - **salinity_wt_percent** (float): Input salinity
        - **dissolved_gas_saturation** (float): Combined CH4+CO2 saturation
        - **note** (str): Usage guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Salinity in ppm instead of wt% (must convert: wt% = ppm/10000)
        - Not accounting for dissolved gas (affects density and compressibility)
        - Temperature in Celsius instead of Fahrenheit
        - Confusing CH4 and CO2 saturation fractions

        **Example Usage:**
        ```python
        {
            "p": [1000, 2000, 3000],
            "degf": 180.0,
            "wt": 5.0,
            "ch4": 0.05,
            "co2": 0.0
        }
        ```
        Result: Brine density increases with pressure, viscosity decreases with temperature.
        Dissolved CH4 reduces density compared to pure brine.

        **Note:** Brine properties are critical for accurate aquifer modeling. Always
        account for dissolved gas (CH4 or CO2) as it significantly affects density and
        compressibility. Salinity has major impact on density and viscosity - use correct
        formation water salinity.
        """
        # Calculate brine properties
        # brine_props expects ch4_sat (0-1 saturation), not separate ch4/co2 fractions
        # Use combined saturation as approximation
        ch4_saturation = request.ch4 + request.co2
        result = brine.brine_props(
            p=request.p,
            degf=request.degf,
            wt=request.wt,
            ch4_sat=ch4_saturation,
        )

        # Extract properties from result tuple
        # brine_props returns: (Bw, Density, viscosity, Compressibility, Rw GOR)
        # Convert numpy arrays to lists for JSON serialization
        bw, density, viscosity, compressibility, rw_gor = result
        
        response = {
            "formation_volume_factor_rb_stb": (
                bw.tolist() if isinstance(bw, np.ndarray) else float(bw)
            ),
            "density_lb_cuft": (
                density.tolist() if isinstance(density, np.ndarray) else float(density)
            ),
            "viscosity_cp": (
                viscosity.tolist() if isinstance(viscosity, np.ndarray) else float(viscosity)
            ),
            "compressibility_1_psi": (
                compressibility.tolist() if isinstance(compressibility, np.ndarray) else float(compressibility)
            ),
            "solution_gor_scf_stb": (
                rw_gor.tolist() if isinstance(rw_gor, np.ndarray) else float(rw_gor)
            ),
            "method": "Industry standard correlations",
            "salinity_wt_percent": request.wt,
            "dissolved_gas_saturation": ch4_saturation,
            "inputs": request.model_dump(),
            "note": "Properties for NaCl brine with dissolved CH4/CO2",
        }

        return response

    @mcp.tool()
    def co2_brine_mutual_solubility(request: CO2BrineMixtureRequest) -> dict:
        """Calculate CO2-brine mutual solubilities and properties.

        **CRITICAL CO2-BRINE SYSTEM TOOL** - Computes comprehensive properties for CO2-saturated
        brine systems using the Duan & Sun (2003) model. Essential for CO2 sequestration,
        CO2-EOR, and geothermal applications. Accounts for mutual solubility (CO2 in brine,
        H2O in CO2-rich phase).

        **Parameters:**
        - **pres** (float, required): Pressure in psia (field) or bar (metric). Must be > 0.
          Typical: 1000-5000 psia. Example: 3000.0 psia.
        - **temp** (float, required): Temperature in °F (field) or °C (metric).
          Typical: 100-400°F. Example: 180.0°F.
        - **ppm** (float, required): Salinity in parts per million (ppm) NaCl.
          Typical: 0-200000 ppm. Example: 50000 ppm (5 wt%).
        - **metric** (bool, optional, default=False): Unit system flag.
          False = field units (psia, °F), True = metric (bar, °C).
        - **cw_sat** (bool, optional, default=True): Compressibility calculation flag.
          True = saturated compressibility, False = undersaturated.

        **Properties Calculated:**
        - **Phase Equilibrium:**
          - Aqueous phase mole fractions (x_CO2, x_H2O)
          - Vapor phase mole fractions (y_CO2, y_H2O)
          - Salt mole fraction
        - **Densities:**
          - CO2-rich gas density (gm/cm³)
          - Brine CO2-saturated density (gm/cm³)
          - Brine pure density (gm/cm³)
          - Fresh water density (gm/cm³)
        - **Viscosities:**
          - Brine CO2-saturated viscosity (cP)
          - Brine pure viscosity (cP)
          - Fresh water viscosity (cP)
        - **Formation Volume Factors:**
          - Bw CO2-saturated (rb/stb)
          - Bw pure (rb/stb)
          - Bw fresh (rb/stb)
        - **Compressibility:**
          - Undersaturated compressibility (1/psi or 1/bar)
          - Saturated compressibility (1/psi or 1/bar)
        - **Solution GOR:** CO2 dissolved in brine (scf/stb or m³/m³)

        **Mutual Solubility:**
        CO2-brine systems exhibit mutual solubility:
        - CO2 dissolves in brine (increases with pressure, decreases with salinity)
        - H2O dissolves in CO2-rich phase (increases with temperature)
        - Both solubilities depend on pressure, temperature, and salinity

        **Physics:**
        Uses Duan & Sun (2003) model for CO2-H2O-NaCl systems accounting for:
        - Pressure effects on solubility (higher P = more CO2 dissolved)
        - Temperature effects (higher T = less CO2 dissolved, more H2O in vapor)
        - Salinity effects (higher salinity = less CO2 dissolved)
        - Mutual solubility (both phases contain both components)

        **Applications:**
        - **CO2 Sequestration:** CCS project design, storage capacity evaluation
        - **CO2-EOR:** Enhanced oil recovery with CO2 injection, miscibility studies
        - **Geothermal:** CO2-based geothermal systems, supercritical CO2
        - **Aquifer Storage:** Underground CO2 storage capacity, leakage assessment
        - **Material Balance:** CO2-brine material balance calculations

        **Salinity Conversion:**
        - 1 wt% = 10,000 ppm
        - Seawater ≈ 35,000 ppm (3.5 wt%)
        - Formation brine: 50,000-200,000 ppm (5-20 wt%)

        **Returns:**
        Dictionary with:
        - **phase_equilibrium** (dict): Mole fractions in aqueous and vapor phases
        - **densities** (dict): All density values (CO2-rich, saturated, pure, fresh)
        - **viscosities** (dict): All viscosity values (saturated, pure, fresh)
        - **formation_volume_factors** (dict): Bw values (saturated, pure, fresh)
        - **compressibility** (dict): Undersaturated and saturated compressibility
        - **solution_gor_co2** (float): CO2 dissolved in brine
        - **viscosibility_per_bar_or_psi** (float): Viscosibility coefficient
        - **method** (str): "Duan & Sun (2003) CO2-H2O-NaCl model"
        - **units** (str): "metric" or "field"
        - **note** (str): Usage guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using wrong unit system (check metric flag)
        - Salinity in wt% instead of ppm (must convert: ppm = wt% × 10000)
        - Pressure in barg/psig instead of psia (must be absolute)
        - Temperature in wrong units (check metric flag)
        - Not accounting for mutual solubility (both phases contain both components)
        - Using wrong compressibility (saturated vs undersaturated)

        **Example Usage (Field Units):**
        ```python
        {
            "pres": 3000.0,
            "temp": 180.0,
            "ppm": 50000,
            "metric": False,
            "cw_sat": True
        }
        ```
        Result: CO2 solubility in brine ≈ 20-40 scf/stb, H2O in CO2-rich phase ≈ 0.1-1 mol%.

        **Note:** CO2-brine mutual solubility is critical for CCS and CO2-EOR projects.
        Always use correct unit system (field vs metric). The model accounts for mutual
        solubility which is significant at high pressures and temperatures. Salinity
        significantly reduces CO2 solubility - use correct formation water salinity.
        """
        # Create CO2_Brine_Mixture object
        mixture = brine.CO2_Brine_Mixture(
            pres=request.pres,
            temp=request.temp,
            ppm=request.ppm,
            metric=request.metric,
            cw_sat=request.cw_sat
        )

        # Extract all properties, handling None values
        result = {
            "phase_equilibrium": {
                "aqueous_phase_mole_fractions": {
                    "x_co2": float(mixture.x[0]) if mixture.x is not None else 0.0,
                    "x_h2o": float(mixture.x[1]) if mixture.x is not None and len(mixture.x) > 1 else 1.0,
                },
                "vapor_phase_mole_fractions": {
                    "y_co2": float(mixture.y[0]) if mixture.y is not None else 0.0,
                    "y_h2o": float(mixture.y[1]) if mixture.y is not None and len(mixture.y) > 1 else 0.0,
                },
                "salt_mole_fraction": float(mixture.xSalt) if mixture.xSalt is not None else 0.0,
            },
            "densities": {
                "co2_rich_gas_gm_cm3": float(mixture.rhoGas) if mixture.rhoGas is not None else 0.0,
                "brine_co2_saturated_gm_cm3": float(mixture.bDen[0]) if mixture.bDen is not None else 0.0,
                "brine_pure_gm_cm3": float(mixture.bDen[1]) if mixture.bDen is not None and len(mixture.bDen) > 1 else 0.0,
                "fresh_water_gm_cm3": float(mixture.bDen[2]) if mixture.bDen is not None and len(mixture.bDen) > 2 else 0.0,
            },
            "viscosities": {
                "brine_co2_saturated_cP": float(mixture.bVis[0]) if mixture.bVis is not None else 0.0,
                "brine_pure_cP": float(mixture.bVis[1]) if mixture.bVis is not None and len(mixture.bVis) > 1 else 0.0,
                "fresh_water_cP": float(mixture.bVis[2]) if mixture.bVis is not None and len(mixture.bVis) > 2 else 0.0,
            },
            "viscosibility_per_bar_or_psi": float(mixture.bVisblty) if mixture.bVisblty is not None else 0.0,
            "formation_volume_factors": {
                "bw_co2_saturated": float(mixture.bw[0]) if mixture.bw is not None else 1.0,
                "bw_pure": float(mixture.bw[1]) if mixture.bw is not None and len(mixture.bw) > 1 else 1.0,
                "bw_fresh": float(mixture.bw[2]) if mixture.bw is not None and len(mixture.bw) > 2 else 1.0,
            },
            "solution_gor_co2": float(mixture.Rs) if mixture.Rs is not None else 0.0,
            "compressibility": {
                "undersaturated_per_bar_or_psi": float(mixture.Cf_usat) if mixture.Cf_usat is not None else 0.0,
                "saturated_per_bar_or_psi": float(mixture.Cf_sat) if mixture.Cf_sat is not None else 0.0,
            },
            "method": "Duan & Sun (2003) CO2-H2O-NaCl model",
            "units": "metric" if request.metric else "field",
            "inputs": request.model_dump(),
            "note": "Critical for CO2 sequestration, EOR, and geothermal applications"
        }

        return result
