"""Tests for new Simtools functions."""

import pytest


@pytest.mark.asyncio
async def test_fit_relative_permeability(mcp_client):
    """Test relative permeability curve fitting."""
    result = await mcp_client.call_tool(
        "fit_relative_permeability",
        {
            "request": {
                "sw": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "kr": [0.0, 0.01, 0.05, 0.15, 0.4, 1.0],
                "krfamily": "COR",
                "krmax": 1.0,
                "sw_min": 0.0,
                "sw_max": 1.0,
            }
        },
    )
    result = result.data
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_fit_relative_permeability_best(mcp_client):
    """Test best-fit relative permeability model selection."""
    result = await mcp_client.call_tool(
        "fit_relative_permeability_best",
        {
            "request": {
                "sw": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "kr": [0.0, 0.01, 0.05, 0.15, 0.4, 1.0],
                "krmax": 1.0,
                "sw_min": 0.0,
                "sw_max": 1.0,
            }
        },
    )
    result = result.data
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_check_let_physical(mcp_client):
    """Test LET physical validity check."""
    result = await mcp_client.call_tool(
        "check_let_physical",
        {
            "request": {
                "s": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                "L": 2.0,
                "E": 1.0,
                "T": 2.0,
            }
        },
    )
    result = result.data
    assert "is_physical" in result
    assert isinstance(result["is_physical"], bool)


@pytest.mark.asyncio
async def test_evaluate_jerauld(mcp_client):
    """Test Jerauld relative permeability evaluation."""
    result = await mcp_client.call_tool(
        "evaluate_jerauld",
        {
            "request": {
                "s": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
                "a": 0.5,
                "b": 0.3,
            }
        },
    )
    result = result.data
    assert "kr" in result
    assert len(result["kr"]) == 6


@pytest.mark.asyncio
async def test_generate_pvtw_table(mcp_client):
    """Test PVTW table generation."""
    result = await mcp_client.call_tool(
        "generate_pvtw_table",
        {
            "request": {
                "pi": 4000.0,
                "degf": 200.0,
                "wt": 5.0,
                "nrows": 10,
            }
        },
    )
    result = result.data
    assert isinstance(result, dict)
