"""Tests for Nodal Analysis / VLP tools."""

import pytest


@pytest.fixture
def sample_completion():
    """Sample completion for testing."""
    return {
        "tubing_id": 2.441,
        "tubing_length": 10000,
        "wellhead_temp": 80,
        "bht": 250,
        "roughness": 0.0006,
    }


@pytest.fixture
def sample_reservoir():
    """Sample reservoir for testing."""
    return {
        "pr": 5000,
        "degf": 250,
        "k": 10,
        "h": 50,
        "re": 1490,
        "rw": 0.354,
        "S": 2,
        "D": 0,
    }


@pytest.mark.asyncio
async def test_flowing_bhp(mcp_client, sample_completion):
    """Test flowing BHP calculation."""
    result = await mcp_client.call_tool(
        "flowing_bhp",
        {
            "request": {
                "thp": 500,
                "completion": sample_completion,
                "well_type": "gas",
                "gas_rate_mmscfd": 5.0,
                "gas_sg": 0.7,
            }
        },
    )
    result = result.data
    assert "fbhp" in result
    assert result["fbhp"] > 500  # BHP should be > THP


@pytest.mark.asyncio
async def test_ipr_curve(mcp_client, sample_reservoir):
    """Test IPR curve generation."""
    result = await mcp_client.call_tool(
        "ipr_curve",
        {
            "request": {
                "reservoir": sample_reservoir,
                "well_type": "gas",
                "gas_sg": 0.7,
                "n_points": 10,
            }
        },
    )
    result = result.data
    assert "pwf" in result
    assert "rate" in result
    assert len(result["pwf"]) == len(result["rate"])
