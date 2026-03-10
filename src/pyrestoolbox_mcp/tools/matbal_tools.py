"""Material Balance tools for FastMCP."""

import numpy as np
import pyrestoolbox.matbal as matbal
from fastmcp import FastMCP

from ..models.matbal_models import GasMatbalRequest, OilMatbalRequest


def register_matbal_tools(mcp: FastMCP) -> None:
    """Register all material balance tools with the MCP server."""

    @mcp.tool()
    def gas_material_balance(request: GasMatbalRequest) -> dict:
        """Perform P/Z gas material balance for OGIP estimation.

        **RESERVE ESTIMATION TOOL** - Performs linear regression of P/Z vs cumulative
        gas production to determine original gas in place (OGIP). Optionally computes
        Cole plot diagnostics and Havlena-Odeh regression when water influx is provided.

        **Parameters:**
        - **pressures** (list[float], required): Reservoir pressures at each survey
          (psia | barsa). First value is initial pressure.
        - **cumulative_gas** (list[float], required): Cumulative gas production at each
          survey. OGIP will be in the same units (e.g. Bscf, MMscf).
        - **temperature** (float, required): Reservoir temperature (deg F | deg C).
        - **gas_sg** (float, optional, default=0.65): Gas specific gravity (air=1).
        - **co2, h2s, n2, h2** (float, optional): Contaminant mole fractions.
        - **cumulative_water** (list[float], optional): Cumulative water production.
        - **water_fvf** (float, optional, default=1.0): Water FVF (rb/stb).
        - **water_influx** (list[float], optional): Cumulative water influx for Havlena-Odeh.
        - **z_method** (str, optional, default="DAK"): Z-factor method.
        - **c_method** (str, optional, default="PMC"): Critical properties method.
        - **metric** (bool, optional, default=false): Use metric units.

        **Returns:** OGIP, P/Z values, regression slope/intercept, and method used.

        **Example:**
        ```json
        {
          "pressures": [5000, 4500, 4000, 3500, 3000],
          "cumulative_gas": [0, 5, 12, 21, 32],
          "temperature": 220, "gas_sg": 0.7
        }
        ```
        """
        result = matbal.gas_matbal(
            p=request.pressures, Gp=request.cumulative_gas, degf=request.temperature,
            sg=request.gas_sg, co2=request.co2, h2s=request.h2s, n2=request.n2, h2=request.h2,
            Wp=request.cumulative_water, Bw=request.water_fvf, We=request.water_influx,
            zmethod=request.z_method, cmethod=request.c_method, metric=request.metric,
        )
        response = {
            "ogip": float(result.ogip),
            "pz_values": result.pz.tolist() if hasattr(result.pz, 'tolist') else list(result.pz),
            "cumulative_gas": result.gp.tolist() if hasattr(result.gp, 'tolist') else list(result.gp),
            "slope": float(result.slope),
            "intercept": float(result.intercept),
            "method": result.method,
        }
        return response

    @mcp.tool()
    def oil_material_balance(request: OilMatbalRequest) -> dict:
        """Perform Havlena-Odeh oil material balance for OOIP estimation.

        **RESERVE ESTIMATION TOOL** - Computes original oil in place using the
        Havlena-Odeh material balance method. Supports gas cap, water influx,
        water/gas injection, and formation/water compressibility effects.

        **Parameters:**
        - **pressures** (list[float], required): Reservoir pressures (psia | barsa).
          First = initial pressure.
        - **cumulative_oil** (list[float], required): Cumulative oil production
          (STB | sm3) at each pressure step. First entry typically 0.
        - **temperature** (float, required): Reservoir temperature (deg F | deg C).
        - **api** (float): Stock tank oil API gravity.
        - **sg_sp** (float): Separator gas specific gravity.
        - **sg_g** (float): Weighted average surface gas SG.
        - **pb** (float): Bubble point pressure (psia | barsa). 0 = calculate from rsb.
        - **rsb** (float): Solution GOR at Pb (scf/stb | sm3/sm3).
        - **producing_gor** (list[float], optional): Cumulative producing GOR at each step.
        - **cumulative_water** (list[float], optional): Cumulative water production.
        - **water_injection** (list[float], optional): Cumulative water injection.
        - **gas_injection** (list[float], optional): Cumulative gas injection.
        - **gas_cap_ratio** (float, optional, default=0): m = G*Bgi/(N*Boi).
        - **cf** (float, optional): Formation compressibility.
        - **sw_i** (float, optional): Initial water saturation.
        - **cw** (float, optional): Water compressibility.
        - **metric** (bool, optional, default=false): Use metric units.

        **Returns:** OOIP, underground withdrawal (F), expansion terms (Eo, Eg, Efw).

        **Example:**
        ```json
        {
          "pressures": [4500, 4000, 3500, 3000, 2500],
          "cumulative_oil": [0, 1000000, 3000000, 6000000, 10000000],
          "temperature": 200, "api": 35, "sg_sp": 0.75, "pb": 3500, "rsb": 800
        }
        ```
        """
        result = matbal.oil_matbal(
            p=request.pressures, Np=request.cumulative_oil, degf=request.temperature,
            api=request.api, sg_sp=request.sg_sp, sg_g=request.sg_g,
            pb=request.pb, rsb=request.rsb,
            Rp=request.producing_gor, Wp=request.cumulative_water,
            Wi=request.water_injection, Gi=request.gas_injection,
            Bw=request.water_fvf, m=request.gas_cap_ratio,
            cf=request.cf, sw_i=request.sw_i, cw=request.cw,
            rsmethod=request.rs_method, bomethod=request.bo_method,
            zmethod=request.z_method, cmethod=request.c_method,
            metric=request.metric,
        )
        response = {
            "ooip": float(result.ooip),
            "F": result.F.tolist() if hasattr(result.F, 'tolist') else list(result.F),
            "Eo": result.Eo.tolist() if hasattr(result.Eo, 'tolist') else list(result.Eo),
            "Eg": result.Eg.tolist() if hasattr(result.Eg, 'tolist') else list(result.Eg),
            "Efw": result.Efw.tolist() if hasattr(result.Efw, 'tolist') else list(result.Efw),
        }
        return response
