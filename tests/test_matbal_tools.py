"""Tests for Material Balance tools."""

import pytest


@pytest.mark.asyncio
async def test_gas_material_balance(mcp_client):
    """Test gas material balance (P/Z analysis)."""
    result = await mcp_client.call_tool(
        "gas_material_balance",
        {
            "request": {
                "pressures": [5000, 4500, 4000, 3500, 3000],
                "cumulative_gas": [0, 5, 12, 21, 32],
                "temperature": 220,
                "gas_sg": 0.7,
            }
        },
    )
    result = result.data
    assert "ogip" in result
    assert result["ogip"] > 0
    assert "pz_values" in result
    assert len(result["pz_values"]) == 5
    assert "slope" in result
    assert "intercept" in result
