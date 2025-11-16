"""Pytest configuration and fixtures for MCP server tests."""

import pytest
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


@pytest.fixture
async def mcp_client():
    """Create an MCP client for testing."""
    async with Client(mcp) as client:
        yield client


@pytest.fixture
def sample_oil_params():
    """Sample oil PVT parameters for testing."""
    return {
        "api": 35.0,
        "degf": 180.0,
        "sg_g": 0.75,
        "rsb": 800.0,
        "pb": 3500.0,
    }


@pytest.fixture
def sample_gas_params():
    """Sample gas PVT parameters for testing."""
    return {
        "sg": 0.7,
        "degf": 180.0,
        "h2s": 0.0,
        "co2": 0.0,
        "n2": 0.0,
    }


@pytest.fixture
def sample_inflow_params():
    """Sample inflow performance parameters for testing."""
    return {
        "pi": 4000.0,
        "h": 50.0,
        "k": 100.0,
        "re": 1000.0,
        "rw": 0.5,
        "s": 0.0,
    }
