"""Tests for gas PVT calculation tools."""

import pytest


@pytest.mark.asyncio
async def test_gas_z_factor(mcp_client, sample_gas_params):
    """Test gas Z-factor calculation."""
    result = await mcp_client.call_tool(
        "gas_z_factor",
        {
            "sg": sample_gas_params["sg"],
            "degf": sample_gas_params["degf"],
            "p": 3500.0,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "method": "DAK",
        },
    )

    assert "value" in result
    assert isinstance(result["value"], float)
    assert 0 < result["value"] <= 2.0  # Z-factor typically in this range
    assert result["method"] == "DAK"
    assert result["units"] == "dimensionless"


@pytest.mark.asyncio
async def test_gas_z_factor_array(mcp_client, sample_gas_params):
    """Test gas Z-factor calculation with array input."""
    pressures = [1000.0, 2000.0, 3000.0, 4000.0]

    result = await mcp_client.call_tool(
        "gas_z_factor",
        {
            "sg": sample_gas_params["sg"],
            "degf": sample_gas_params["degf"],
            "p": pressures,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "method": "DAK",
        },
    )

    assert "value" in result
    assert isinstance(result["value"], list)
    assert len(result["value"]) == len(pressures)
    assert all(0 < v <= 2.0 for v in result["value"])


@pytest.mark.asyncio
async def test_gas_critical_properties(mcp_client, sample_gas_params):
    """Test gas critical properties calculation."""
    result = await mcp_client.call_tool(
        "gas_critical_properties",
        {
            "sg": sample_gas_params["sg"],
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "method": "PMC",
        },
    )

    assert "value" in result
    assert isinstance(result["value"], dict)
    assert "tc" in result["value"]
    assert "pc" in result["value"]
    assert result["value"]["tc"] > 0
    assert result["value"]["pc"] > 0
    assert result["units"]["tc"] == "degR"
    assert result["units"]["pc"] == "psia"


@pytest.mark.asyncio
async def test_gas_formation_volume_factor(mcp_client, sample_gas_params):
    """Test gas FVF calculation."""
    result = await mcp_client.call_tool(
        "gas_formation_volume_factor",
        {
            "sg": sample_gas_params["sg"],
            "degf": sample_gas_params["degf"],
            "p": 3000.0,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "zmethod": "DAK",
        },
    )

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
    assert result["units"] == "rcf/scf"


@pytest.mark.asyncio
async def test_gas_viscosity(mcp_client, sample_gas_params):
    """Test gas viscosity calculation."""
    result = await mcp_client.call_tool(
        "gas_viscosity",
        {
            "sg": sample_gas_params["sg"],
            "degf": sample_gas_params["degf"],
            "p": 3000.0,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "zmethod": "DAK",
        },
    )

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
    assert result["units"] == "cP"


@pytest.mark.asyncio
async def test_gas_density(mcp_client, sample_gas_params):
    """Test gas density calculation."""
    result = await mcp_client.call_tool(
        "gas_density",
        {
            "sg": sample_gas_params["sg"],
            "degf": sample_gas_params["degf"],
            "p": 3000.0,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "zmethod": "DAK",
        },
    )

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
    assert result["units"] == "lb/cuft"


@pytest.mark.asyncio
async def test_gas_compressibility(mcp_client, sample_gas_params):
    """Test gas compressibility calculation."""
    result = await mcp_client.call_tool(
        "gas_compressibility",
        {
            "sg": sample_gas_params["sg"],
            "degf": sample_gas_params["degf"],
            "p": 3000.0,
            "h2s": 0.0,
            "co2": 0.0,
            "n2": 0.0,
            "zmethod": "DAK",
        },
    )

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
    assert result["units"] == "1/psi"


@pytest.mark.asyncio
async def test_gas_with_impurities(mcp_client):
    """Test gas calculations with non-hydrocarbon impurities."""
    result = await mcp_client.call_tool(
        "gas_z_factor",
        {
            "sg": 0.7,
            "degf": 180.0,
            "p": 3000.0,
            "h2s": 0.05,
            "co2": 0.10,
            "n2": 0.02,
            "method": "DAK",
        },
    )

    assert "value" in result
    assert isinstance(result["value"], float)
    assert result["value"] > 0
