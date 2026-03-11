"""Nodal Analysis / VLP / IPR tools for FastMCP."""

import numpy as np
import pyrestoolbox.nodal as nodal
from fastmcp import FastMCP

import pyrestoolbox.simtools as simtools

from ..models.nodal_models import (
    CompletionModel,
    ReservoirModel,
    FBHPRequest,
    IPRCurveRequest,
    OutflowCurveRequest,
    OperatingPointRequest,
    VFPProdRequest,
    VFPInjRequest,
)


def _build_completion(comp_model: CompletionModel):
    """Build a nodal.Completion object from the Pydantic model."""
    if comp_model.segments:
        segs = [
            nodal.WellSegment(
                md=s.md,
                id=s.id,
                deviation=s.deviation,
                roughness=s.roughness,
                metric=comp_model.metric,
            )
            for s in comp_model.segments
        ]
        return nodal.Completion(
            segments=segs,
            tht=comp_model.wellhead_temp,
            bht=comp_model.bht,
            metric=comp_model.metric,
        )
    else:
        return nodal.Completion(
            tid=comp_model.tubing_id,
            length=comp_model.tubing_length,
            tht=comp_model.wellhead_temp,
            bht=comp_model.bht,
            rough=comp_model.roughness,
            cid=comp_model.casing_id,
            crough=comp_model.casing_roughness,
            metric=comp_model.metric,
        )


def _build_reservoir(res_model: ReservoirModel):
    """Build a nodal.Reservoir object from the Pydantic model."""
    return nodal.Reservoir(
        pr=res_model.pr,
        degf=res_model.degf,
        k=res_model.k,
        h=res_model.h,
        re=res_model.re,
        rw=res_model.rw,
        S=res_model.S,
        D=res_model.D,
        metric=res_model.metric,
    )


def register_nodal_tools(mcp: FastMCP) -> None:
    """Register all nodal analysis tools with the MCP server."""

    @mcp.tool()
    def flowing_bhp(request: FBHPRequest) -> dict:
        """Calculate flowing bottom hole pressure using VLP correlations.

        **WELL PERFORMANCE TOOL** - Computes BHP from tubing head pressure, flow rates,
        and wellbore geometry using multiphase flow correlations. Supports gas and oil wells.

        **VLP Methods:**
        - **WG** (Woldesemayat-Ghajar): Recommended for most applications.
        - **HB** (Hagedorn-Brown): Classic correlation.
        - **GRAY**: Good for gas wells with condensate.
        - **BB** (Beggs & Brill): General purpose.

        **Parameters:**
        - **thp** (float, required): Tubing head pressure (psia | barsa).
        - **completion** (object, required): Wellbore completion with tubing_id, tubing_length,
          wellhead_temp, bht, roughness, or multi-segment definition.
        - **vlp_method** (str, optional, default="WG"): VLP correlation.
        - **well_type** (str, optional, default="gas"): "gas" or "oil".
        - **gas_rate_mmscfd** (float): Gas rate for gas wells (MMscf/d).
        - **cgr** (float): Condensate-gas ratio (STB/MMscf).
        - **water_rate_bwpd** (float): Water rate (STB/d).
        - **total_liquid_stbpd** (float): Total liquid rate for oil wells (STB/d).
        - **gor** (float): Producing GOR for oil wells (scf/stb).
        - **water_cut** (float): Water cut fraction (0-1).
        - **gas_sg** (float, optional, default=0.65): Gas specific gravity.
        - **metric** (bool, optional, default=false): Use metric units.

        **Returns:** Flowing bottom hole pressure.

        **Example (gas well):**
        ```json
        {
          "thp": 500,
          "completion": {"tubing_id": 2.441, "tubing_length": 10000, "wellhead_temp": 80, "bht": 250, "roughness": 0.0006},
          "well_type": "gas", "gas_rate_mmscfd": 5.0, "gas_sg": 0.7
        }
        ```
        """
        comp = _build_completion(request.completion)
        bhp = nodal.fbhp(
            thp=request.thp,
            completion=comp,
            vlpmethod=request.vlp_method,
            well_type=request.well_type,
            qg_mmscfd=request.gas_rate_mmscfd,
            cgr=request.cgr,
            qw_bwpd=request.water_rate_bwpd,
            oil_vis=request.oil_viscosity,
            api=request.api,
            pr=request.reservoir_pressure,
            qt_stbpd=request.total_liquid_stbpd,
            gor=request.gor,
            wc=request.water_cut,
            wsg=request.water_sg,
            injection=request.injection,
            gsg=request.gas_sg,
            metric=request.metric,
        )
        unit = "barsa" if request.metric else "psia"
        return {"fbhp": float(bhp), "units": unit}

    @mcp.tool()
    def ipr_curve(request: IPRCurveRequest) -> dict:
        """Generate an Inflow Performance Relationship (IPR) curve.

        **WELL PERFORMANCE TOOL** - Computes the relationship between flowing BHP and
        production rate for a reservoir. Essential for well deliverability analysis.

        **Parameters:**
        - **reservoir** (object, required): Reservoir description with pr, degf, k, h, re, rw, S, D.
        - **well_type** (str, optional, default="gas"): "gas", "oil", or "water".
        - **n_points** (int, optional, default=20): Number of pressure points.
        - **min_pwf** (float, optional): Minimum flowing BHP.
        - **water_cut** (float): Water cut fraction for oil wells.
        - **bo** (float): Oil FVF if no OilPVT object.
        - **uo** (float): Oil viscosity if no OilPVT object.
        - **gas_sg** (float): Gas SG if no GasPVT object.
        - **metric** (bool, optional, default=false): Use metric units.

        **Returns:** Arrays of flowing BHP (pwf) and corresponding production rates.

        **Example:**
        ```json
        {
          "reservoir": {"pr": 5000, "degf": 250, "k": 10, "h": 50, "re": 1490, "rw": 0.354, "S": 2, "D": 0},
          "well_type": "gas", "gas_sg": 0.7
        }
        ```
        """
        res = _build_reservoir(request.reservoir)
        result = nodal.ipr_curve(
            reservoir=res,
            well_type=request.well_type,
            n_points=request.n_points,
            min_pwf=request.min_pwf,
            wc=request.water_cut,
            wsg=request.water_sg,
            bo=request.bo,
            uo=request.uo,
            gsg=request.gas_sg,
            metric=request.metric,
        )
        return {
            "pwf": [float(x) for x in result["pwf"]],
            "rate": [float(x) for x in result["rate"]],
            "well_type": request.well_type,
            "units": {
                "pressure": "barsa" if request.metric else "psia",
                "rate": (
                    "sm3/d"
                    if request.metric
                    else ("MMscf/d" if request.well_type == "gas" else "STB/d")
                ),
            },
        }

    @mcp.tool()
    def outflow_curve(request: OutflowCurveRequest) -> dict:
        """Generate a VLP outflow (tubing performance) curve.

        **WELL PERFORMANCE TOOL** - Computes BHP as a function of flow rate using
        multiphase VLP correlations. Used for nodal analysis and operating point determination.

        **Parameters:**
        - **thp** (float, required): Tubing head pressure (psia | barsa).
        - **completion** (object, required): Wellbore completion description.
        - **vlp_method** (str, optional, default="WG"): VLP correlation.
        - **well_type** (str, optional, default="gas"): "gas" or "oil".
        - **rates** (list[float], optional): Rates to evaluate. Auto-generated if None.
        - **n_rates** (int, optional, default=20): Number of rate points.
        - **max_rate** (float, optional): Maximum rate for auto-generation.
        - **metric** (bool, optional, default=false): Use metric units.

        **Returns:** Arrays of flow rates and corresponding BHP values.
        """
        comp = _build_completion(request.completion)
        result = nodal.outflow_curve(
            thp=request.thp,
            completion=comp,
            vlpmethod=request.vlp_method,
            well_type=request.well_type,
            rates=request.rates,
            n_rates=request.n_rates,
            max_rate=request.max_rate,
            cgr=request.cgr,
            qw_bwpd=request.water_rate_bwpd,
            oil_vis=request.oil_viscosity,
            api=request.api,
            gor=request.gor,
            wc=request.water_cut,
            wsg=request.water_sg,
            injection=request.injection,
            gsg=request.gas_sg,
            metric=request.metric,
        )
        return {
            "rates": [float(x) for x in result["rates"]],
            "bhp": [float(x) for x in result["bhp"]],
            "well_type": request.well_type,
        }

    @mcp.tool()
    def operating_point(request: OperatingPointRequest) -> dict:
        """Find the VLP/IPR operating point (intersection of inflow and outflow curves).

        **WELL DELIVERABILITY TOOL** - Determines the stable operating rate and BHP
        by finding where the VLP outflow curve intersects the IPR inflow curve.
        This is the key result of nodal analysis.

        **Parameters:**
        - **thp** (float, required): Tubing head pressure (psia | barsa).
        - **completion** (object, required): Wellbore completion.
        - **reservoir** (object, required): Reservoir description.
        - **vlp_method** (str, optional, default="WG"): VLP correlation.
        - **well_type** (str, optional, default="gas"): "gas" or "oil".
        - **gas_sg** (float, optional, default=0.65): Gas SG.
        - **n_points** (int, optional, default=25): Points for curves.
        - **metric** (bool, optional, default=false): Use metric units.

        **Returns:** Operating rate, BHP, and full VLP/IPR curves.

        **Example:**
        ```json
        {
          "thp": 500,
          "completion": {"tubing_id": 2.441, "tubing_length": 10000, "wellhead_temp": 80, "bht": 250},
          "reservoir": {"pr": 5000, "degf": 250, "k": 10, "h": 50, "re": 1490, "rw": 0.354, "S": 2, "D": 0},
          "well_type": "gas", "gas_sg": 0.7
        }
        ```
        """
        comp = _build_completion(request.completion)
        res = _build_reservoir(request.reservoir)
        result = nodal.operating_point(
            thp=request.thp,
            completion=comp,
            reservoir=res,
            vlpmethod=request.vlp_method,
            well_type=request.well_type,
            cgr=request.cgr,
            qw_bwpd=request.water_rate_bwpd,
            oil_vis=request.oil_viscosity,
            api=request.api,
            gor=request.gor,
            wc=request.water_cut,
            wsg=request.water_sg,
            gsg=request.gas_sg,
            bo=request.bo,
            uo=request.uo,
            n_points=request.n_points,
            metric=request.metric,
        )
        rate_unit = (
            "sm3/d" if request.metric else ("MMscf/d" if request.well_type == "gas" else "STB/d")
        )
        p_unit = "barsa" if request.metric else "psia"
        response = {
            "operating_rate": float(result["rate"]),
            "operating_bhp": float(result["bhp"]),
            "rate_units": rate_unit,
            "pressure_units": p_unit,
        }
        if "vlp" in result:
            response["vlp_curve"] = {
                "rates": [float(x) for x in result["vlp"]["rates"]],
                "bhp": [float(x) for x in result["vlp"]["bhp"]],
            }
        if "ipr" in result:
            response["ipr_curve"] = {
                "pwf": [float(x) for x in result["ipr"]["pwf"]],
                "rate": [float(x) for x in result["ipr"]["rate"]],
            }
        return response

    @mcp.tool()
    def generate_vfp_prod_table(request: VFPProdRequest) -> dict:
        """Generate VFPPROD table for ECLIPSE/Intersect simulation.

        **VFP TABLE TOOL** - Creates production VFP (Vertical Flow Performance) tables
        for use with VFPPROD keyword in reservoir simulators. Tables map flow rate,
        THP, water fraction, gas fraction, and artificial lift to BHP.

        **Parameters:**
        - **table_num** (int, required): VFP table number (>=1).
        - **completion** (object, required): Wellbore completion description.
        - **well_type** (str): "gas" or "oil".
        - **vlp_method** (str): VLP correlation (WG, HB, GRAY, BB).
        - **flo_rates** (list[float]): Flow rates. Auto if None.
        - **thp_values** (list[float]): THP values. Auto if None.
        - **wfr_values** (list[float]): Water fraction values.
        - **gfr_values** (list[float]): Gas fraction values.
        - **alq_values** (list[float]): Artificial lift values.
        - **gas_sg** (float): Gas specific gravity.
        - **api** (float): Oil API gravity.
        - **datum_depth** (float): Reference depth.
        - **metric** (bool): Use metric units.

        **Returns:** VFP table data ready for simulator input.
        """
        comp = _build_completion(request.completion)
        result = simtools.make_vfpprod(
            table_num=request.table_num,
            completion=comp,
            well_type=request.well_type,
            vlpmethod=request.vlp_method,
            flo_rates=request.flo_rates,
            thp_values=request.thp_values,
            wfr_values=request.wfr_values,
            gfr_values=request.gfr_values,
            alq_values=request.alq_values,
            gsg=request.gas_sg,
            oil_vis=request.oil_viscosity,
            api=request.api,
            pr=request.reservoir_pressure,
            wsg=request.water_sg,
            datum_depth=request.datum_depth,
            metric=request.metric,
        )
        response = {}
        for key, val in result.items():
            if hasattr(val, "tolist"):
                response[key] = val.tolist()
            elif isinstance(val, (np.floating, np.integer)):
                response[key] = float(val)
            else:
                response[key] = val
        return response

    @mcp.tool()
    def generate_vfp_inj_table(request: VFPInjRequest) -> dict:
        """Generate VFPINJ table for ECLIPSE/Intersect simulation.

        **VFP TABLE TOOL** - Creates injection VFP tables for use with VFPINJ keyword
        in reservoir simulators. Maps flow rate and THP to BHP for injectors.

        **Parameters:**
        - **table_num** (int, required): VFP table number (>=1).
        - **completion** (object, required): Wellbore completion description.
        - **flo_type** (str): Flow type: "WAT", "GAS", or "OIL".
        - **vlp_method** (str): VLP correlation.
        - **flo_rates** (list[float]): Flow rates. Auto if None.
        - **thp_values** (list[float]): THP values. Auto if None.
        - **gas_sg** (float): Gas specific gravity.
        - **water_sg** (float): Water specific gravity.
        - **api** (float): Oil API gravity.
        - **datum_depth** (float): Reference depth.
        - **metric** (bool): Use metric units.

        **Returns:** VFP injection table data.
        """
        comp = _build_completion(request.completion)
        result = simtools.make_vfpinj(
            table_num=request.table_num,
            completion=comp,
            flo_type=request.flo_type,
            vlpmethod=request.vlp_method,
            flo_rates=request.flo_rates,
            thp_values=request.thp_values,
            gsg=request.gas_sg,
            wsg=request.water_sg,
            api=request.api,
            datum_depth=request.datum_depth,
            metric=request.metric,
        )
        response = {}
        for key, val in result.items():
            if hasattr(val, "tolist"):
                response[key] = val.tolist()
            elif isinstance(val, (np.floating, np.integer)):
                response[key] = float(val)
            else:
                response[key] = val
        return response
