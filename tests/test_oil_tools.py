"""Tests for oil PVT calculation tools."""

import pytest


@pytest.mark.asyncio
async def test_oil_bubble_point(mcp_client, sample_oil_params):
    """Test bubble point pressure calculation."""
    result = await mcp_client.call_tool(
        "oil_bubble_point",
        {
            "request": {
                "api": sample_oil_params["api"],
                "degf": sample_oil_params["degf"],
                "rsb": sample_oil_params["rsb"],
                "sg_g": sample_oil_params["sg_g"],
                "method": "VALMC",
            }
        },
    )
    result = result.data

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
    assert result["method"] == "VALMC"
    assert result["units"] == "psia"


@pytest.mark.asyncio
async def test_oil_solution_gor(mcp_client, sample_oil_params):
    """Test solution GOR calculation."""
    result = await mcp_client.call_tool(
        "oil_solution_gor",
        {
            "request": {
                "api": sample_oil_params["api"],
                "degf": sample_oil_params["degf"],
                "p": 3000.0,
                "sg_g": sample_oil_params["sg_g"],
                "pb": sample_oil_params["pb"],
                "rsb": sample_oil_params["rsb"],
                "method": "VELAR",
            }
        },
    )
    result = result.data

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] >= 0
    assert result["units"] == "scf/stb"


@pytest.mark.asyncio
async def test_oil_solution_gor_array(mcp_client, sample_oil_params):
    """Test solution GOR calculation with array input."""
    pressures = [2000.0, 3000.0, 4000.0]

    result = await mcp_client.call_tool(
        "oil_solution_gor",
        {
            "request": {
                "api": sample_oil_params["api"],
                "degf": sample_oil_params["degf"],
                "p": pressures,
                "sg_g": sample_oil_params["sg_g"],
                "pb": sample_oil_params["pb"],
                "rsb": sample_oil_params["rsb"],
                "method": "VELAR",
            }
        },
    )
    result = result.data

    assert "value" in result
    assert isinstance(result["value"], list)
    assert len(result["value"]) == len(pressures)
    assert all(v >= 0 for v in result["value"])


@pytest.mark.asyncio
async def test_oil_formation_volume_factor(mcp_client, sample_oil_params):
    """Test oil FVF calculation."""
    result = await mcp_client.call_tool(
        "oil_formation_volume_factor",
        {
            "request": {
                "api": sample_oil_params["api"],
                "degf": sample_oil_params["degf"],
                "p": 3000.0,
                "sg_g": sample_oil_params["sg_g"],
                "pb": sample_oil_params["pb"],
                "rs": 750.0,
                "rsb": sample_oil_params["rsb"],
                "method": "MCAIN",
            }
        },
    )
    result = result.data

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] >= 1.0  # Bo should be >= 1
    assert result["units"] == "rb/stb"


@pytest.mark.asyncio
async def test_oil_viscosity(mcp_client, sample_oil_params):
    """Test oil viscosity calculation."""
    result = await mcp_client.call_tool(
        "oil_viscosity",
        {
            "request": {
                "api": sample_oil_params["api"],
                "degf": sample_oil_params["degf"],
                "p": 3000.0,
                "pb": sample_oil_params["pb"],
                "rs": 750.0,
                "rsb": sample_oil_params["rsb"],
                "method": "BR",
            }
        },
    )
    result = result.data

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
    assert result["units"] == "cP"


@pytest.mark.asyncio
async def test_oil_density(mcp_client, sample_oil_params):
    """Test oil density calculation."""
    result = await mcp_client.call_tool(
        "oil_density",
        {
            "request": {
                "p": 3000.0,
                "api": sample_oil_params["api"],
                "degf": sample_oil_params["degf"],
                "rs": 750.0,
                "sg_g": sample_oil_params["sg_g"],
                "bo": 1.3,
            }
        },
    )
    result = result.data

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
    assert result["units"] == "lb/cuft"


@pytest.mark.asyncio
async def test_oil_compressibility(mcp_client, sample_oil_params):
    """Test oil compressibility calculation."""
    result = await mcp_client.call_tool(
        "oil_compressibility",
        {
            "request": {
                "p": 4000.0,
                "api": sample_oil_params["api"],
                "degf": sample_oil_params["degf"],
                "pb": sample_oil_params["pb"],
                "sg_g": sample_oil_params["sg_g"],
                "rs": sample_oil_params["rsb"],
                "rsb": sample_oil_params["rsb"],
            }
        },
    )
    result = result.data

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
    assert result["units"] == "1/psi"
