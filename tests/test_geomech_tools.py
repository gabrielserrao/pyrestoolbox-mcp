"""Tests for geomechanics calculation tools via MCP client."""

import pytest


@pytest.mark.asyncio
async def test_vertical_stress_onshore(mcp_client):
    """Test onshore vertical stress calculation."""
    result = await mcp_client.call_tool(
        "geomech_vertical_stress",
        {
            "request": {
                "depth": 10000.0,
                "water_depth": 0.0,
                "avg_density": 144.0,
                "water_density": 64.0,
            }
        },
    )
    result = result.data
    assert "value" in result
    assert "gradient" in result
    assert result["value"] > 0
    assert 0.9 < result["gradient"] < 1.1


@pytest.mark.asyncio
async def test_vertical_stress_offshore(mcp_client):
    """Test offshore vertical stress with water column."""
    result = await mcp_client.call_tool(
        "geomech_vertical_stress",
        {
            "request": {
                "depth": 10000.0,
                "water_depth": 2000.0,
                "avg_density": 144.0,
                "water_density": 64.0,
            }
        },
    )
    result = result.data
    assert result["value"] > 0
    assert 0.8 < result["gradient"] < 1.0


@pytest.mark.asyncio
async def test_pore_pressure_eaton_sonic(mcp_client):
    """Test Eaton's method with sonic data showing overpressure."""
    result = await mcp_client.call_tool(
        "geomech_pore_pressure_eaton",
        {
            "request": {
                "depth": 10000.0,
                "observed_value": 100.0,
                "normal_value": 70.0,
                "overburden_psi": 10400.0,
                "eaton_exponent": 3.0,
                "method": "sonic",
            }
        },
    )
    result = result.data
    assert result["value"] > 0
    assert result["gradient"] > 0.465
    assert result["overpressure"] > 0


@pytest.mark.asyncio
async def test_pore_pressure_eaton_resistivity(mcp_client):
    """Test Eaton's method with resistivity data."""
    result = await mcp_client.call_tool(
        "geomech_pore_pressure_eaton",
        {
            "request": {
                "depth": 10000.0,
                "observed_value": 5.0,
                "normal_value": 10.0,
                "overburden_psi": 10400.0,
                "eaton_exponent": 1.2,
                "method": "resistivity",
            }
        },
    )
    result = result.data
    assert result["value"] > 0
    assert result["gradient"] > 0


@pytest.mark.asyncio
async def test_effective_stress_scalar(mcp_client):
    """Test effective stress with scalar inputs."""
    result = await mcp_client.call_tool(
        "geomech_effective_stress",
        {
            "request": {
                "total_stress": 10400.0,
                "pore_pressure": 4680.0,
                "biot_coefficient": 1.0,
            }
        },
    )
    result = result.data
    assert isinstance(result["value"], float)
    assert abs(result["value"] - 5720.0) < 100


@pytest.mark.asyncio
async def test_effective_stress_array(mcp_client):
    """Test effective stress with array inputs."""
    result = await mcp_client.call_tool(
        "geomech_effective_stress",
        {
            "request": {
                "total_stress": [10000.0, 10400.0, 10800.0],
                "pore_pressure": [4500.0, 4680.0, 4860.0],
                "biot_coefficient": 0.9,
            }
        },
    )
    result = result.data
    assert isinstance(result["value"], list)
    assert len(result["value"]) == 3
    assert all(v > 0 for v in result["value"])


@pytest.mark.asyncio
async def test_horizontal_stress_normal(mcp_client):
    """Test horizontal stress in normal faulting regime."""
    result = await mcp_client.call_tool(
        "geomech_horizontal_stress",
        {
            "request": {
                "vertical_stress": 10400.0,
                "pore_pressure": 4680.0,
                "poisson_ratio": 0.25,
                "tectonic_factor": 0.0,
                "biot_coefficient": 1.0,
            }
        },
    )
    result = result.data
    assert result["sigma_h_min"] > 0
    assert result["sigma_h_max"] >= result["sigma_h_min"]
    assert result["stress_regime"] == "normal"


@pytest.mark.asyncio
async def test_horizontal_stress_strike_slip(mcp_client):
    """Test horizontal stress in strike-slip regime."""
    result = await mcp_client.call_tool(
        "geomech_horizontal_stress",
        {
            "request": {
                "vertical_stress": 10400.0,
                "pore_pressure": 4680.0,
                "poisson_ratio": 0.25,
                "tectonic_factor": 0.5,
                "biot_coefficient": 1.0,
            }
        },
    )
    result = result.data
    assert result["stress_regime"] == "strike-slip"


@pytest.mark.asyncio
async def test_elastic_moduli_E_nu(mcp_client):
    """Test conversion from Young's modulus and Poisson's ratio."""
    result = await mcp_client.call_tool(
        "geomech_elastic_moduli_conversion",
        {
            "request": {
                "youngs_modulus": 1000000.0,
                "poisson_ratio": 0.25,
            }
        },
    )
    result = result.data
    assert all(
        k in result
        for k in [
            "youngs_modulus",
            "bulk_modulus",
            "shear_modulus",
            "poisson_ratio",
            "lame_parameter",
        ]
    )
    assert result["youngs_modulus"] == 1000000.0
    assert result["poisson_ratio"] == 0.25
    assert result["shear_modulus"] > 0
    assert result["bulk_modulus"] > 0


@pytest.mark.asyncio
async def test_elastic_moduli_K_G(mcp_client):
    """Test conversion from bulk and shear moduli."""
    result = await mcp_client.call_tool(
        "geomech_elastic_moduli_conversion",
        {
            "request": {
                "bulk_modulus": 666667.0,
                "shear_modulus": 400000.0,
            }
        },
    )
    result = result.data
    assert result["youngs_modulus"] > 0
    assert 0 < result["poisson_ratio"] < 0.5


@pytest.mark.asyncio
async def test_rock_strength_mohr_coulomb(mcp_client):
    """Test Mohr-Coulomb failure criterion."""
    result = await mcp_client.call_tool(
        "geomech_rock_strength_mohr_coulomb",
        {
            "request": {
                "cohesion": 500.0,
                "friction_angle": 30.0,
                "effective_stress_min": 2000.0,
            }
        },
    )
    result = result.data
    assert result["max_principal_stress"] > 0
    assert result["unconfined_strength"] > 0
    assert result["q_factor"] > 1.0
    assert result["shear_strength"] > 500.0


@pytest.mark.asyncio
async def test_dynamic_to_static_moduli(mcp_client):
    """Test Eissa-Kazi correlation for sandstone."""
    result = await mcp_client.call_tool(
        "geomech_dynamic_to_static_moduli",
        {
            "request": {
                "dynamic_youngs": 1500000.0,
                "dynamic_poisson": 0.20,
                "correlation": "eissa_kazi",
                "lithology": "sandstone",
            }
        },
    )
    result = result.data
    assert result["static_youngs"] < 1500000.0
    assert result["static_poisson"] < 0.20
    assert 0.4 < result["correction_factor"] < 0.8


@pytest.mark.asyncio
async def test_breakout_width(mcp_client):
    """Test breakout calculation for stable wellbore."""
    result = await mcp_client.call_tool(
        "geomech_breakout_width",
        {
            "request": {
                "sigma_h_max": 8500.0,
                "sigma_h_min": 7500.0,
                "pore_pressure": 4680.0,
                "mud_weight": 12.0,
                "wellbore_azimuth": 45.0,
                "ucs": 3000.0,
                "friction_angle": 30.0,
            }
        },
    )
    result = result.data
    assert "breakout_width" in result
    assert "failure_status" in result
    assert result["breakout_width"] >= 0


@pytest.mark.asyncio
async def test_fracture_gradient_eaton(mcp_client):
    """Test fracture gradient using Eaton method."""
    result = await mcp_client.call_tool(
        "geomech_fracture_gradient",
        {
            "request": {
                "depth": 10000.0,
                "vertical_stress": 10400.0,
                "pore_pressure": 4680.0,
                "poisson_ratio": 0.25,
                "method": "eaton",
            }
        },
    )
    result = result.data
    assert result["fracture_pressure"] > 4680.0
    assert 0.5 < result["fracture_gradient"] < 1.0
    assert result["equivalent_mud_weight"] > 0


@pytest.mark.asyncio
async def test_mud_weight_window(mcp_client):
    """Test safe mud weight window."""
    result = await mcp_client.call_tool(
        "geomech_safe_mud_weight_window",
        {
            "request": {
                "pore_pressure": 4680.0,
                "fracture_pressure": 7800.0,
                "depth": 10000.0,
                "safety_margin_overbalance": 0.5,
                "safety_margin_fracture": 0.5,
            }
        },
    )
    result = result.data
    assert result["max_mud_weight"] > result["min_mud_weight"]
    assert result["window_width"] > 0


@pytest.mark.asyncio
async def test_critical_mud_weight(mcp_client):
    """Test critical mud weight for collapse prevention."""
    result = await mcp_client.call_tool(
        "geomech_critical_mud_weight_collapse",
        {
            "request": {
                "sigma_h_max": 8500.0,
                "sigma_h_min": 6500.0,
                "pore_pressure": 4680.0,
                "cohesion": 500.0,
                "friction_angle": 30.0,
                "wellbore_azimuth": 45.0,
                "wellbore_inclination": 0.0,
                "depth": 10000.0,
            }
        },
    )
    result = result.data
    assert result["critical_mud_weight"] > 0
    assert result["collapse_pressure"] > 4680.0


@pytest.mark.asyncio
async def test_reservoir_compaction(mcp_client):
    """Test reservoir compaction from pressure depletion."""
    result = await mcp_client.call_tool(
        "geomech_reservoir_compaction",
        {
            "request": {
                "pressure_drop": 1000.0,
                "reservoir_thickness": 100.0,
                "youngs_modulus": 500000.0,
                "poisson_ratio": 0.25,
                "biot_coefficient": 1.0,
            }
        },
    )
    result = result.data
    assert result["compaction"] > 0
    assert result["subsidence"] > 0
    assert result["subsidence"] < result["compaction"]
    assert result["strain"] > 0


@pytest.mark.asyncio
async def test_pore_compressibility(mcp_client):
    """Test pore compressibility from elastic moduli."""
    result = await mcp_client.call_tool(
        "geomech_pore_compressibility",
        {
            "request": {
                "porosity": 0.20,
                "youngs_modulus": 500000.0,
                "poisson_ratio": 0.25,
                "grain_compressibility": 3e-7,
            }
        },
    )
    result = result.data
    assert result["pore_compressibility"] > 0
    assert result["bulk_compressibility"] > 0
    assert result["pore_compressibility"] > result["bulk_compressibility"]


@pytest.mark.asyncio
async def test_leak_off_pressure(mcp_client):
    """Test LOT analysis."""
    result = await mcp_client.call_tool(
        "geomech_leak_off_pressure",
        {
            "request": {
                "leak_off_pressure": 2500.0,
                "mud_weight": 9.0,
                "test_depth": 10000.0,
                "pore_pressure": 4680.0,
                "test_type": "LOT",
            }
        },
    )
    result = result.data
    assert result["sigma_h_min"] > 0
    assert result["sigma_h_min"] > 4680.0
    assert result["fracture_gradient"] > 0
    assert result["breakdown_pressure"] is not None


@pytest.mark.asyncio
async def test_fracture_width_pkn(mcp_client):
    """Test PKN fracture width model."""
    result = await mcp_client.call_tool(
        "geomech_hydraulic_fracture_width",
        {
            "request": {
                "net_pressure": 500.0,
                "fracture_height": 100.0,
                "fracture_half_length": 500.0,
                "youngs_modulus": 1000000.0,
                "poisson_ratio": 0.25,
                "model": "PKN",
            }
        },
    )
    result = result.data
    assert result["avg_width"] > 0
    assert result["max_width"] > result["avg_width"]
    assert result["model_used"] == "PKN"


@pytest.mark.asyncio
async def test_fracture_width_kgd(mcp_client):
    """Test KGD fracture width model."""
    result = await mcp_client.call_tool(
        "geomech_hydraulic_fracture_width",
        {
            "request": {
                "net_pressure": 500.0,
                "fracture_height": 100.0,
                "fracture_half_length": 500.0,
                "youngs_modulus": 1000000.0,
                "poisson_ratio": 0.25,
                "model": "KGD",
            }
        },
    )
    result = result.data
    assert result["avg_width"] > 0
    assert result["max_width"] > result["avg_width"]
    assert result["model_used"] == "KGD"
