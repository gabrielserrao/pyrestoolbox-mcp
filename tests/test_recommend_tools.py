"""Tests for Method Recommendation tools."""

import pytest


@pytest.mark.asyncio
async def test_recommend_gas_methods(mcp_client):
    """Test gas method recommendation."""
    result = await mcp_client.call_tool(
        "recommend_gas_methods",
        {
            "request": {
                "sg": 0.7,
                "co2": 0.05,
                "h2s": 0.01,
                "n2": 0.02,
            }
        },
    )
    result = result.data
    assert "zmethod" in result or "cmethod" in result or "recommendations" in result


@pytest.mark.asyncio
async def test_recommend_oil_methods(mcp_client):
    """Test oil method recommendation."""
    result = await mcp_client.call_tool(
        "recommend_oil_methods",
        {
            "request": {
                "api": 35.0,
                "rsb": 800.0,
                "degf": 180.0,
            }
        },
    )
    result = result.data
    assert isinstance(result, dict)
