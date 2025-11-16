"""Configuration resources for FastMCP."""

from fastmcp import FastMCP
import json
from ..config import (
    SERVER_VERSION,
    UNIT_SYSTEM,
    CALCULATION_METHODS,
    CONSTANTS,
)


def register_config_resources(mcp: FastMCP) -> None:
    """Register all configuration resources with the MCP server."""

    @mcp.resource("config://version")
    def get_version() -> str:
        """Get pyResToolbox MCP server version information.

        Returns version number and basic server info.
        """
        return json.dumps(
            {
                "mcp_server_version": SERVER_VERSION,
                "server_name": "pyResToolbox MCP",
                "description": "Reservoir Engineering PVT calculations and simulation tools",
            },
            indent=2,
        )

    @mcp.resource("config://units")
    def get_units() -> str:
        """Get complete unit system documentation.

        Returns all units used in the pyResToolbox library (Field Units/US Oilfield).
        All calculations must use these units for inputs and will return results in these units.
        """
        return json.dumps(UNIT_SYSTEM, indent=2)

    @mcp.resource("config://methods")
    def get_methods() -> str:
        """Get available calculation methods and correlations.

        Returns all supported correlation methods for PVT calculations including:
        - Z-factor methods (DAK, HY, WYW, BUR)
        - Critical properties methods (PMC, SUT, BUR)
        - Bubble point methods (STAN, VALMC, VELAR)
        - Solution GOR methods (VELAR, STAN, VALMC)
        - Oil FVF methods (MCAIN, STAN)
        - Oil viscosity methods (BR)
        - Relative permeability families (COR, LET)
        """
        return json.dumps(CALCULATION_METHODS, indent=2)

    @mcp.resource("config://constants")
    def get_constants() -> str:
        """Get physical constants used in calculations.

        Returns fundamental physical constants including:
        - R: Gas constant
        - psc: Standard pressure
        - tsc: Standard temperature
        - MW_AIR: Molecular weight of air
        """
        return json.dumps(CONSTANTS, indent=2)

    @mcp.resource("help://overview")
    def get_overview() -> str:
        """Get overview of pyResToolbox MCP capabilities.

        Returns comprehensive guide to using the MCP server for reservoir engineering
        calculations including available tools and typical workflows.
        """
        overview = """
# pyResToolbox MCP Server - Overview

A FastMCP server providing AI agents access to reservoir engineering calculations.

## Available Tool Categories

### Oil PVT Tools
- oil_bubble_point: Calculate bubble point pressure
- oil_solution_gor: Calculate solution gas-oil ratio (Rs)
- oil_formation_volume_factor: Calculate oil FVF (Bo)
- oil_viscosity: Calculate oil viscosity
- oil_density: Calculate oil density
- oil_compressibility: Calculate oil compressibility

### Gas PVT Tools
- gas_z_factor: Calculate gas Z-factor (compressibility factor)
- gas_critical_properties: Calculate pseudo-critical temperature and pressure
- gas_formation_volume_factor: Calculate gas FVF (Bg)
- gas_viscosity: Calculate gas viscosity
- gas_density: Calculate gas density
- gas_compressibility: Calculate gas compressibility

### Inflow Performance Tools
- oil_rate_radial: Oil production rate (radial flow)
- oil_rate_linear: Oil production rate (linear flow)
- gas_rate_radial: Gas production rate (radial flow)
- gas_rate_linear: Gas production rate (linear flow)

## Unit System

All tools use **Field Units (US Oilfield)**:
- Pressure: psia
- Temperature: degrees Fahrenheit
- Length: feet
- Permeability: millidarcies
- Viscosity: centipoise
- Oil rate: STB/day
- Gas rate: MSCF/day

## Typical Workflows

### Basic PVT Analysis
1. Calculate bubble point pressure
2. Calculate solution GOR at various pressures
3. Calculate formation volume factors
4. Calculate viscosities and densities

### Well Performance Analysis
1. Gather reservoir and fluid properties
2. Calculate PVT properties at reservoir conditions
3. Use inflow tools to estimate production rates
4. Generate IPR curves by calculating rates at multiple pressures

### Resources Available
- config://version - Server version info
- config://units - Complete unit documentation
- config://methods - Available correlation methods
- config://constants - Physical constants
- help://overview - This overview

## Notes
- All tools accept both scalar and array inputs
- Array inputs enable efficient batch calculations
- Multiple correlation methods available - use recommended defaults unless specific correlation needed
- Error handling: Invalid inputs will return descriptive error messages
"""
        return overview
