"""Inflow Performance calculation tools for FastMCP."""

import warnings
import numpy as np
import pyrestoolbox.oil as oil
import pyrestoolbox.gas as gas
from pyrestoolbox.classes import rs_method, bo_method
from fastmcp import FastMCP

# Suppress pkg_resources deprecation warning from pyrestoolbox
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources.*")

from ..models.inflow_models import (
    OilRateRadialRequest,
    OilRateLinearRequest,
    GasRateRadialRequest,
    GasRateLinearRequest,
)


def register_inflow_tools(mcp: FastMCP) -> None:
    """Register all inflow performance tools with the MCP server."""

    @mcp.tool()
    def oil_rate_radial(request: OilRateRadialRequest) -> dict:
        """Calculate oil production rate for radial flow (vertical well).

        **INFLOW PERFORMANCE TOOL** - Computes oil production rate for vertical wells
        with radial flow geometry using Darcy's law. Automatically calculates PVT properties
        (Rs, Bo, μo) at average pressure. Optionally applies Vogel IPR model for
        two-phase flow below bubble point.

        **Parameters:**
        - **pi** (float, required): Initial/reservoir pressure in psia. Must be > 0.
          Example: 4000.0.
        - **pb** (float, required): Bubble point pressure in psia. Must be ≥ 0.
          Example: 3500.0. If pi < pb, reservoir is saturated (gas cap present).
        - **api** (float, required): Oil API gravity in degrees. Valid: 0-100.
          Example: 35.0.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0.
        - **sg_g** (float, required): Gas specific gravity (air=1). Valid: 0-3.
          Typical: 0.6-1.2. Example: 0.75.
        - **psd** (float or list, required): Sandface/draining pressure(s) in psia.
          Must be > 0 and < pi. Can be scalar or array. Example: 1500.0 or [1000, 1500, 2000].
        - **h** (float, required): Net pay thickness in feet. Must be > 0.
          Typical: 10-200 ft. Example: 50.0.
        - **k** (float, required): Permeability in millidarcies (mD). Must be > 0.
          Typical: 1-1000 mD. Example: 100.0.
        - **s** (float, optional, default=0.0): Skin factor (dimensionless).
          Negative = stimulation, positive = damage. Typical: -5 to +20.
          Example: 0.0 for undamaged well.
        - **re** (float, required): Drainage radius in feet. Must be > rw.
          Typical: 500-5000 ft. Example: 1000.0.
        - **rw** (float, required): Wellbore radius in feet. Must be > 0.
          Typical: 0.25-0.5 ft. Example: 0.5.
        - **rsb** (float, required): Solution GOR at bubble point in scf/stb.
          Must be ≥ 0. Example: 800.0.
        - **vogel** (bool, optional, default=False): Apply Vogel IPR model.
          Set True when pi < pb (saturated reservoir). Example: False.

        **Flow Regime:**
        - **Undersaturated (pi > pb)**: Single-phase oil flow, Darcy's law applies
        - **Saturated (pi < pb)**: Two-phase flow, use Vogel=True for accurate IPR

        **Darcy's Law Formula:**
        qo = (0.00708 × k × h × (pi - pwf)) / (μo × Bo × (ln(re/rw) + S))

        Where PVT properties (μo, Bo) are calculated at average pressure (pi + pwf)/2.

        **Returns:**
        Dictionary with:
        - **value** (float or list): Oil rate in STB/day (matches input psd shape)
        - **method** (str): "Darcy radial flow" or "Vogel IPR"
        - **units** (str): "STB/day"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not setting vogel=True when pi < pb (underestimates rate)
        - Using wrong drainage radius (re) - should be well spacing/2
        - Confusing net pay (h) with gross thickness
        - Not accounting for skin factor (s)

        **Example Usage:**
        ```python
        {
            "pi": 4000.0,
            "pb": 3500.0,
            "api": 35.0,
            "degf": 180.0,
            "sg_g": 0.75,
            "psd": [1500, 2000, 2500],
            "h": 50.0,
            "k": 100.0,
            "s": 0.0,
            "re": 1000.0,
            "rw": 0.5,
            "rsb": 800.0,
            "vogel": False
        }
        ```
        Result: Oil rate decreases as sandface pressure increases (typical IPR curve).

        **Note:** This tool automatically calculates PVT properties. You don't need to
        provide Rs, Bo, or μo - they are computed internally at average pressure.
        For saturated reservoirs (pi < pb), set vogel=True for accurate two-phase flow.
        """
        # Convert psd to numpy array for processing
        psd_array = np.asarray(request.psd)
        is_scalar = psd_array.ndim == 0
        if is_scalar:
            psd_array = np.array([psd_array])
        
        # Calculate oil specific gravity from API
        sg_o = oil.oil_sg(api_value=request.api)
        
        # Calculate solution GOR at sandface pressure(s)
        # oil_rs uses sg_sp (separator gas SG), use sg_g as separator gas SG
        rs_values = oil.oil_rs(
            api=request.api,
            degf=request.degf,
            p=psd_array,
            sg_sp=request.sg_g,  # Use sg_g as separator gas SG
            pb=request.pb,
            rsb=request.rsb,
            rsmethod=rs_method.VELAR,
        )
        
        # Calculate PVT properties at sandface pressure(s)
        # Use average pressure for PVT calculation (between reservoir and sandface)
        avg_pressures = (request.pi + psd_array) / 2.0
        
        # Calculate Rs at average pressures for PVT
        rs_avg = oil.oil_rs(
            api=request.api,
            degf=request.degf,
            p=avg_pressures,
            sg_sp=request.sg_g,  # Use sg_g as separator gas SG
            pb=request.pb,
            rsb=request.rsb,
            rsmethod=rs_method.VELAR,
        )
        
        # Calculate Bo and uo at average pressures
        bo_values = oil.oil_bo(
            p=avg_pressures,
            pb=request.pb,
            degf=request.degf,
            rs=rs_avg,
            rsb=request.rsb,
            sg_o=sg_o,
            sg_g=request.sg_g,
            bomethod=bo_method.MCAIN,
        )
        
        uo_values = oil.oil_viso(
            p=avg_pressures,
            api=request.api,
            degf=request.degf,
            pb=request.pb,
            rs=rs_avg,
        )
        
        # Convert to scalars if needed
        if is_scalar:
            bo_values = float(bo_values[0]) if isinstance(bo_values, np.ndarray) else float(bo_values)
            uo_values = float(uo_values[0]) if isinstance(uo_values, np.ndarray) else float(uo_values)
            psd_array = psd_array[0]
        
        # Call oil_rate_radial with correct parameters
        qo = oil.oil_rate_radial(
            k=request.k,
            h=request.h,
            pr=request.pi,
            pwf=psd_array,
            r_w=request.rw,
            r_ext=request.re,
            uo=uo_values,
            bo=bo_values,
            S=request.s,
            vogel=request.vogel,
            pb=request.pb,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(qo, np.ndarray):
            value = qo.tolist()
        else:
            value = float(qo)

        method = "Darcy radial flow"
        # Ensure scalar comparison (not array) to avoid "ambiguous truth value" error
        pi_scalar = float(request.pi) if isinstance(request.pi, (np.ndarray, list)) else request.pi
        pb_scalar = float(request.pb) if isinstance(request.pb, (np.ndarray, list)) else request.pb
        if request.vogel and pi_scalar < pb_scalar:
            method = "Vogel IPR"

        return {
            "value": value,
            "method": method,
            "units": "STB/day",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def oil_rate_linear(request: OilRateLinearRequest) -> dict:
        """Calculate oil production rate for linear flow.

        **INFLOW PERFORMANCE TOOL** - Computes oil production rate for horizontal wells
        or wells with linear flow geometry using Darcy's law. Automatically calculates PVT
        properties (Rs, Bo, μo) at average pressure. Essential for horizontal well
        performance analysis and completion design.

        **Parameters:**
        - **pi** (float, required): Initial/reservoir pressure in psia. Must be > 0.
          Example: 4000.0.
        - **pb** (float, required): Bubble point pressure in psia. Must be ≥ 0.
          Example: 3500.0. If pi < pb, reservoir is saturated (gas cap present).
        - **api** (float, required): Oil API gravity in degrees. Valid: 0-100.
          Example: 35.0.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0.
        - **sg_g** (float, required): Gas specific gravity (air=1). Valid: 0-3.
          Typical: 0.6-1.2. Example: 0.75.
        - **psd** (float or list, required): Sandface/draining pressure(s) in psia.
          Must be > 0 and < pi. Can be scalar or array. Example: 1500.0 or [1000, 1500, 2000].
        - **h** (float, required): Net pay thickness in feet. Must be > 0.
          Typical: 10-200 ft. Example: 50.0.
        - **k** (float, required): Permeability in millidarcies (mD). Must be > 0.
          Typical: 1-1000 mD. Example: 100.0.
        - **area** (float, required): Cross-sectional flow area in square feet.
          Must be > 0. Typical: 100-10000 ft². Example: 1000.0.
        - **length** (float, required): Flow length in feet. Must be > 0.
          Typical: 100-5000 ft. Example: 500.0.
        - **rsb** (float, required): Solution GOR at bubble point in scf/stb.
          Must be ≥ 0. Example: 800.0.

        **Flow Geometry:**
        Linear flow occurs in:
        - Horizontal wells (early-time flow)
        - Hydraulically fractured vertical wells (fracture flow)
        - Channelized reservoirs
        - Edge water drive systems

        **Darcy's Law Formula (Linear):**
        qo = (0.001127 × k × area × (pi - pwf)) / (μo × Bo × length)

        Where PVT properties (μo, Bo) are calculated at average pressure (pi + pwf)/2.

        **Linear vs Radial Flow:**
        - Linear: Flow perpendicular to wellbore (horizontal wells)
        - Radial: Flow converging to wellbore (vertical wells)
        - Linear flow typically has higher productivity than radial

        **Returns:**
        Dictionary with:
        - **value** (float or list): Oil rate in STB/day (matches input psd shape)
        - **method** (str): "Darcy linear flow"
        - **units** (str): "STB/day"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Confusing flow area (perpendicular to flow) with wellbore area
        - Using wrong flow length (should be distance from boundary to well)
        - Not accounting for net pay thickness correctly
        - Confusing linear flow (horizontal wells) with radial flow (vertical wells)

        **Example Usage:**
        ```python
        {
            "pi": 4000.0,
            "pb": 3500.0,
            "api": 35.0,
            "degf": 180.0,
            "sg_g": 0.75,
            "psd": [1500, 2000, 2500],
            "h": 50.0,
            "k": 100.0,
            "area": 1000.0,
            "length": 500.0,
            "rsb": 800.0
        }
        ```
        Result: Oil rate decreases as sandface pressure increases (typical IPR curve).

        **Note:** This tool automatically calculates PVT properties. You don't need to
        provide Rs, Bo, or μo - they are computed internally at average pressure.
        Linear flow is characteristic of horizontal wells and hydraulically fractured wells.
        """
        # Convert psd to numpy array for processing
        psd_array = np.asarray(request.psd)
        is_scalar = psd_array.ndim == 0
        if is_scalar:
            psd_array = np.array([psd_array])
        
        # Calculate oil specific gravity from API
        sg_o = oil.oil_sg(api_value=request.api)
        
        # Calculate average pressures for PVT
        avg_pressures = (request.pi + psd_array) / 2.0
        
        # Calculate Rs at average pressures
        rs_avg = oil.oil_rs(
            api=request.api,
            degf=request.degf,
            p=avg_pressures,
            sg_sp=request.sg_g,  # Use sg_g as separator gas SG
            pb=request.pb,
            rsb=request.rsb,
            rsmethod=rs_method.VELAR,
        )
        
        # Calculate Bo and uo at average pressures
        bo_values = oil.oil_bo(
            p=avg_pressures,
            pb=request.pb,
            degf=request.degf,
            rs=rs_avg,
            rsb=request.rsb,
            sg_o=sg_o,
            sg_g=request.sg_g,
            bomethod=bo_method.MCAIN,
        )
        
        uo_values = oil.oil_viso(
            p=avg_pressures,
            api=request.api,
            degf=request.degf,
            pb=request.pb,
            rs=rs_avg,
        )
        
        # Convert to scalars if needed
        if is_scalar:
            bo_values = float(bo_values[0]) if isinstance(bo_values, np.ndarray) else float(bo_values)
            uo_values = float(uo_values[0]) if isinstance(uo_values, np.ndarray) else float(uo_values)
            psd_array = psd_array[0]
        
        # Call oil_rate_linear with correct parameters
        qo = oil.oil_rate_linear(
            k=request.k,
            pr=request.pi,
            pwf=psd_array,
            area=request.area,
            length=request.length,
            uo=uo_values,
            bo=bo_values,
            vogel=False,
            pb=request.pb,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(qo, np.ndarray):
            value = qo.tolist()
        else:
            value = float(qo)

        return {
            "value": value,
            "method": "Darcy linear flow",
            "units": "STB/day",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_rate_radial(request: GasRateRadialRequest) -> dict:
        """Calculate gas production rate for radial flow (vertical well).

        **INFLOW PERFORMANCE TOOL** - Computes gas production rate for vertical wells
        with radial flow geometry using real gas pseudopressure formulation. This accounts
        for pressure-dependent gas properties (Z-factor, viscosity) which are significant
        for gas systems. More accurate than simplified Darcy's law for gas.

        **Parameters:**
        - **pi** (float, required): Initial/reservoir pressure in psia. Must be > 0.
          Example: 5000.0.
        - **sg** (float, required): Gas specific gravity (air=1). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0.
        - **psd** (float or list, required): Sandface/draining pressure(s) in psia.
          Must be > 0 and < pi. Can be scalar or array. Example: 2000.0 or [1000, 2000, 3000].
        - **h** (float, required): Net pay thickness in feet. Must be > 0.
          Typical: 10-200 ft. Example: 50.0.
        - **k** (float, required): Permeability in millidarcies (mD). Must be > 0.
          Typical: 1-1000 mD. Example: 100.0.
        - **s** (float, optional, default=0.0): Skin factor (dimensionless).
          Negative = stimulation, positive = damage. Typical: -5 to +20.
          Example: 0.0 for undamaged well.
        - **re** (float, required): Drainage radius in feet. Must be > rw.
          Typical: 500-5000 ft. Example: 1000.0.
        - **rw** (float, required): Wellbore radius in feet. Must be > 0.
          Typical: 0.25-0.5 ft. Example: 0.5.
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.0.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.0.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.0.

        **Pseudopressure Method:**
        Uses real gas pseudopressure (m(p)) which linearizes the gas diffusivity equation:
        m(p) = 2∫(p/(μZ))dp from pb to p

        This accounts for:
        - Z-factor variation with pressure
        - Gas viscosity variation with pressure
        - Non-linear pressure behavior

        **Flow Formula:**
        qg = (kh × (m(pi) - m(pwf))) / (1422 × T × (ln(re/rw) + S))

        Where PVT properties are integrated over pressure range.

        **Returns:**
        Dictionary with:
        - **value** (float or list): Gas rate in MSCF/day (matches input psd shape)
        - **method** (str): "Pseudopressure radial flow"
        - **units** (str): "MSCF/day"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions (H2S, CO2, N2)
        - Using wrong drainage radius (re) - should be well spacing/2
        - Confusing net pay (h) with gross thickness
        - Not accounting for skin factor (s)

        **Example Usage:**
        ```python
        {
            "pi": 5000.0,
            "sg": 0.7,
            "degf": 180.0,
            "psd": [2000, 3000, 4000],
            "h": 50.0,
            "k": 100.0,
            "s": 0.0,
            "re": 1000.0,
            "rw": 0.5,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0
        }
        ```
        Result: Gas rate decreases as sandface pressure increases (typical IPR curve).

        **Note:** This tool uses pseudopressure method which is more accurate than
        simplified Darcy's law for gas. Always account for non-hydrocarbon components
        (H2S, CO2, N2) as they affect Z-factor and flow calculations significantly.
        """
        # Convert psd to numpy array for processing
        psd_array = np.asarray(request.psd)
        is_scalar = psd_array.ndim == 0
        if is_scalar:
            psd_array = np.array([psd_array])
        
        # Call gas_rate_radial with correct parameters
        qg = gas.gas_rate_radial(
            k=request.k,
            h=request.h,
            pr=request.pi,
            pwf=psd_array,
            r_w=request.rw,
            r_ext=request.re,
            degf=request.degf,
            S=request.s,
            sg=request.sg,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(qg, np.ndarray):
            value = qg.tolist()
        else:
            value = float(qg)

        return {
            "value": value,
            "method": "Pseudopressure radial flow",
            "units": "MSCF/day",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def gas_rate_linear(request: GasRateLinearRequest) -> dict:
        """Calculate gas production rate for linear flow.

        **INFLOW PERFORMANCE TOOL** - Computes gas production rate for horizontal wells
        or wells with linear flow geometry using real gas pseudopressure formulation.
        This accounts for pressure-dependent gas properties (Z-factor, viscosity) which
        are significant for gas systems. More accurate than simplified Darcy's law for gas.

        **Parameters:**
        - **pi** (float, required): Initial/reservoir pressure in psia. Must be > 0.
          Example: 5000.0.
        - **sg** (float, required): Gas specific gravity (air=1). Valid: 0.55-3.0.
          Typical: 0.6-1.2. Example: 0.7.
        - **degf** (float, required): Reservoir temperature in °F. Valid: -460 to 1000.
          Example: 180.0.
        - **psd** (float or list, required): Sandface/draining pressure(s) in psia.
          Must be > 0 and < pi. Can be scalar or array. Example: 2000.0 or [1000, 2000, 3000].
        - **h** (float, required): Net pay thickness in feet. Must be > 0.
          Typical: 10-200 ft. Example: 50.0.
        - **k** (float, required): Permeability in millidarcies (mD). Must be > 0.
          Typical: 1-1000 mD. Example: 100.0.
        - **area** (float, required): Cross-sectional flow area in square feet.
          Must be > 0. Typical: 100-10000 ft². Example: 1000.0.
        - **length** (float, required): Flow length in feet. Must be > 0.
          Typical: 100-5000 ft. Example: 500.0.
        - **h2s** (float, optional, default=0.0): H2S mole fraction (0-1).
          Typical: 0-0.05. Example: 0.0.
        - **co2** (float, optional, default=0.0): CO2 mole fraction (0-1).
          Typical: 0-0.20. Example: 0.0.
        - **n2** (float, optional, default=0.0): N2 mole fraction (0-1).
          Typical: 0-0.10. Example: 0.0.

        **Flow Geometry:**
        Linear flow occurs in:
        - Horizontal wells (early-time flow)
        - Hydraulically fractured vertical wells (fracture flow)
        - Channelized gas reservoirs
        - Edge water drive systems

        **Pseudopressure Method:**
        Uses real gas pseudopressure (m(p)) which linearizes the gas diffusivity equation:
        m(p) = 2∫(p/(μZ))dp from pb to p

        This accounts for:
        - Z-factor variation with pressure
        - Gas viscosity variation with pressure
        - Non-linear pressure behavior

        **Flow Formula (Linear):**
        qg = (k × area × (m(pi) - m(pwf))) / (1422 × T × length)

        Where PVT properties are integrated over pressure range.

        **Linear vs Radial Flow:**
        - Linear: Flow perpendicular to wellbore (horizontal wells)
        - Radial: Flow converging to wellbore (vertical wells)
        - Linear flow typically has higher productivity than radial

        **Returns:**
        Dictionary with:
        - **value** (float or list): Gas rate in MSCF/day (matches input psd shape)
        - **method** (str): "Pseudopressure linear flow"
        - **units** (str): "MSCF/day"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Using separator temperature instead of reservoir temperature
        - Pressure in barg/psig instead of psia (must be absolute)
        - Not accounting for non-hydrocarbon fractions (H2S, CO2, N2)
        - Confusing flow area (perpendicular to flow) with wellbore area
        - Using wrong flow length (should be distance from boundary to well)
        - Confusing linear flow (horizontal wells) with radial flow (vertical wells)
        - Not accounting for net pay thickness correctly

        **Example Usage:**
        ```python
        {
            "pi": 5000.0,
            "sg": 0.7,
            "degf": 180.0,
            "psd": [2000, 3000, 4000],
            "h": 50.0,
            "k": 100.0,
            "area": 1000.0,
            "length": 500.0,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0
        }
        ```
        Result: Gas rate decreases as sandface pressure increases (typical IPR curve).

        **Note:** This tool uses pseudopressure method which is more accurate than
        simplified Darcy's law for gas. Always account for non-hydrocarbon components
        (H2S, CO2, N2) as they affect Z-factor and flow calculations significantly.
        Linear flow is characteristic of horizontal wells and hydraulically fractured wells.
        """
        # Convert psd to numpy array for processing
        psd_array = np.asarray(request.psd)
        is_scalar = psd_array.ndim == 0
        if is_scalar:
            psd_array = np.array([psd_array])
        
        # Call gas_rate_linear with correct parameters
        qg = gas.gas_rate_linear(
            k=request.k,
            pr=request.pi,
            pwf=psd_array,
            area=request.area,
            length=request.length,
            degf=request.degf,
            sg=request.sg,
            h2s=request.h2s,
            co2=request.co2,
            n2=request.n2,
        )

        # Convert numpy array to list for JSON serialization
        if isinstance(qg, np.ndarray):
            value = qg.tolist()
        else:
            value = float(qg)

        return {
            "value": value,
            "method": "Pseudopressure linear flow",
            "units": "MSCF/day",
            "inputs": request.model_dump(),
        }
