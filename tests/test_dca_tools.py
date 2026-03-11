"""Tests for DCA (Decline Curve Analysis) tools."""

import pytest


@pytest.mark.asyncio
async def test_arps_rate(mcp_client):
    """Test Arps decline rate calculation."""
    result = await mcp_client.call_tool(
        "arps_rate",
        {
            "request": {
                "qi": 1000.0,
                "di": 0.5,
                "b": 0.5,
                "t": [0, 30, 60, 90, 120, 180, 365],
            }
        },
    )
    result = result.data
    assert "rate" in result
    rates = result["rate"]
    assert len(rates) == 7


@pytest.mark.asyncio
async def test_arps_cumulative(mcp_client):
    """Test Arps cumulative production calculation."""
    result = await mcp_client.call_tool(
        "arps_cumulative",
        {
            "request": {
                "qi": 1000.0,
                "di": 0.5,
                "b": 0.5,
                "t": [30, 60, 90, 180, 365],
            }
        },
    )
    result = result.data
    assert "cumulative" in result
    cum = result["cumulative"]
    assert len(cum) == 5
    assert cum[-1] > cum[0]


@pytest.mark.asyncio
async def test_estimated_ultimate_recovery(mcp_client):
    """Test EUR calculation."""
    result = await mcp_client.call_tool(
        "estimated_ultimate_recovery",
        {
            "request": {
                "qi": 1000.0,
                "di": 0.5,
                "b": 0.5,
                "q_min": 10.0,
            }
        },
    )
    result = result.data
    assert "eur" in result
    assert result["eur"] > 0


@pytest.mark.asyncio
async def test_fit_decline(mcp_client):
    """Test decline curve fitting."""
    result = await mcp_client.call_tool(
        "fit_decline",
        {
            "request": {
                "time": [1, 2, 3, 6, 12, 18, 24, 36],
                "rates": [1000, 800, 650, 400, 200, 130, 90, 50],
            }
        },
    )
    result = result.data
    assert "qi" in result
    assert "di" in result
    assert result["qi"] > 0
    assert result["di"] > 0
