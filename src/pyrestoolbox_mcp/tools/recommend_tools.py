"""Method Recommendation tools for FastMCP."""

import pyrestoolbox.recommend as recommend
from fastmcp import FastMCP

from ..models.recommend_models import (
    RecommendMethodsRequest,
    RecommendGasMethodsRequest,
    RecommendOilMethodsRequest,
    RecommendVLPMethodRequest,
)


def _format_recommendation(rec) -> dict:
    """Convert a MethodRecommendation to a dictionary."""
    return {
        "category": rec.category,
        "recommended": rec.recommended,
        "rationale": rec.rationale,
        "alternatives": rec.alternatives,
        "mandatory": rec.mandatory,
    }


def register_recommend_tools(mcp: FastMCP) -> None:
    """Register all method recommendation tools with the MCP server."""

    @mcp.tool()
    def recommend_methods(request: RecommendMethodsRequest) -> dict:
        """Recommend the best PVT and VLP correlations for given fluid properties.

        **METHOD SELECTION TOOL** - Analyzes gas composition, oil gravity, and well
        configuration to suggest optimal calculation methods. Returns recommendations
        for Z-factor, critical properties, bubble point, GOR, FVF, and VLP methods.

        **Parameters:**
        - **gas_sg** (float, optional, default=0.65): Gas specific gravity.
        - **co2, h2s, n2, h2** (float, optional): Contaminant mole fractions.
        - **api** (float, optional): Oil API gravity. Include for oil recommendations.
        - **deviation** (float, optional, default=0): Max wellbore deviation (degrees).
        - **well_type** (str, optional, default="gas"): "gas" or "oil".

        **Returns:** Dictionary of method recommendations with rationale and alternatives.

        **Example:**
        ```json
        {"gas_sg": 0.75, "co2": 0.1, "h2s": 0.05, "api": 35, "deviation": 45}
        ```
        """
        recs = recommend.recommend_methods(
            sg=request.gas_sg, co2=request.co2, h2s=request.h2s,
            n2=request.n2, h2=request.h2, api=request.api,
            deviation=request.deviation, well_type=request.well_type,
        )
        return {key: _format_recommendation(rec) for key, rec in recs.items()}

    @mcp.tool()
    def recommend_gas_methods(request: RecommendGasMethodsRequest) -> dict:
        """Recommend Z-factor and critical property methods for a gas composition.

        **METHOD SELECTION TOOL** - Based on gas SG and contaminant content, recommends
        the most appropriate Z-factor and critical properties methods.

        **Parameters:**
        - **gas_sg** (float, optional, default=0.65): Gas specific gravity.
        - **co2, h2s, n2, h2** (float, optional): Contaminant mole fractions.

        **Returns:** Recommendations for 'zmethod' and 'cmethod'.
        """
        recs = recommend.recommend_gas_methods(
            sg=request.gas_sg, co2=request.co2, h2s=request.h2s,
            n2=request.n2, h2=request.h2,
        )
        return {key: _format_recommendation(rec) for key, rec in recs.items()}

    @mcp.tool()
    def recommend_oil_methods(request: RecommendOilMethodsRequest) -> dict:
        """Recommend oil PVT correlation methods based on API gravity.

        **METHOD SELECTION TOOL** - Returns recommendations for bubble point,
        solution GOR, and oil FVF methods.

        **Parameters:**
        - **api** (float, optional, default=35): Oil API gravity.

        **Returns:** Recommendations for 'pbmethod', 'rsmethod', 'bomethod'.
        """
        recs = recommend.recommend_oil_methods(api=request.api)
        return {key: _format_recommendation(rec) for key, rec in recs.items()}

    @mcp.tool()
    def recommend_vlp_method(request: RecommendVLPMethodRequest) -> dict:
        """Recommend VLP multiphase flow correlation.

        **METHOD SELECTION TOOL** - Returns the best VLP method based on
        wellbore deviation and well type.

        **Parameters:**
        - **deviation** (float, optional, default=0): Max deviation from vertical (degrees).
        - **well_type** (str, optional, default="gas"): "gas" or "oil".

        **Returns:** Recommendation for 'vlp_method'.
        """
        recs = recommend.recommend_vlp_method(
            deviation=request.deviation, well_type=request.well_type,
        )
        return {key: _format_recommendation(rec) for key, rec in recs.items()}
