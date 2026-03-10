"""Tests for new Brine tools (SoreideWhitson)."""

import pytest


@pytest.mark.asyncio
async def test_soreide_whitson_vle(mcp_client):
    """Test Soreide-Whitson VLE brine calculation."""
    result = await mcp_client.call_tool(
        "soreide_whitson_vle",
        {
            "request": {
                "pres": 3000.0,
                "temp": 180.0,
                "ppm": 50000,
                "sg": 0.65,
                "metric": False,
            }
        },
    )
    result = result.data
    assert "solution_gor_by_component" in result
    assert "solution_gor_total" in result
    assert result["solution_gor_total"] > 0
    assert "densities" in result
    assert "viscosities" in result
    assert "formation_volume_factors" in result
    assert result["method"] == "Soreide-Whitson (1992) VLE"


@pytest.mark.asyncio
async def test_brine_properties_with_metric(mcp_client):
    """Test brine properties with metric units."""
    result = await mcp_client.call_tool(
        "calculate_brine_properties",
        {
            "request": {
                "p": 200.0,
                "degf": 80.0,
                "wt": 5.0,
                "metric": True,
            }
        },
    )
    result = result.data
    assert "formation_volume_factor_rb_stb" in result
    assert "density_lb_cuft" in result
