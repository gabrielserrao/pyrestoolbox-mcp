#!/usr/bin/env python3
"""Test all MCP tools to ensure they work correctly.

This test suite validates all 47 pyResToolbox MCP tools including:
- 17 Oil PVT tools
- 11 Gas PVT tools  
- 4 Inflow Performance tools
- 3 Simulation tools
- 2 Brine Property tools
- 5 Layer/Heterogeneity tools
- 1 Component Library tool
- 4 Configuration resources

Note: One tool (gas_sg_from_gradient) has an internal pyrestoolbox library issue
and is expected to fail until the upstream library is fixed.
"""

import sys
import warnings
import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp

# Suppress pkg_resources deprecation warning from pyrestoolbox
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources.*")

async def test_all_tools():
    """Test each tool with sample data."""
    print("=" * 80)
    print("Testing All MCP Tools")
    print("=" * 80)
    
    tests_passed = 0
    tests_failed = 0
    failed_tools = []

    async with Client(mcp) as client:
        # Test Oil PVT Tools
        print("\n[Oil PVT Tools]")
        print("-" * 80)
        
        oil_tools = [
            ("oil_bubble_point", {"request": {
                "api": 35.0, "degf": 180.0, "rsb": 800.0, "sg_g": 0.75, "method": "VALMC"
            }}),
            ("oil_solution_gor", {"request": {
                "api": 35.0, "degf": 180.0, "p": 3000.0, "sg_g": 0.75, "pb": 3500.0, "rsb": 800.0, "method": "VELAR"
            }}),
            ("oil_formation_volume_factor", {"request": {
                "api": 35.0, "degf": 180.0, "p": 3000.0, "sg_g": 0.75, "pb": 3500.0, "rs": 600.0, "rsb": 800.0, "method": "MCAIN"
            }}),
            ("oil_viscosity", {"request": {
                "api": 35.0, "degf": 180.0, "p": 3000.0, "pb": 3500.0, "rs": 600.0
            }}),
            ("oil_density", {"request": {
                "api": 35.0, "degf": 180.0, "p": 3000.0, "rs": 600.0, "sg_g": 0.75, "bo": 1.2
            }}),
            ("oil_compressibility", {"request": {
                "api": 35.0, "degf": 180.0, "p": 3000.0, "sg_g": 0.75, "pb": 3500.0, "rs": 600.0, "rsb": 800.0
            }}),
            ("oil_api_from_sg", {"request": {"sg": 0.85}}),
            ("oil_sg_from_api", {"request": {"api": 35.0}}),
            ("oil_rs_at_bubble_point", {"request": {
                "api": 35.0, "degf": 180.0, "rsb": 800.0, "sg_g": 0.75, "method": "VALMC"
            }}),
            ("evolved_gas_sg", {"request": {
                "api": 35.0, "degf": 180.0, "sg_g": 0.75, "p": 3500.0
            }}),
            ("stock_tank_gas_sg", {"request": {
                "api": 35.0, "degf": 180.0, "sg_g": 0.75, "p": 3500.0
            }}),
            ("oil_sg_from_jacoby", {"request": {"mw": 200.0, "ja": 0.3}}),
            ("weighted_average_gas_sg", {"request": {
                "sg_sp": 0.75, "rsp": 700.0, "sg_st": 1.2, "rst": 100.0
            }}),
            ("generate_black_oil_table", {"request": {
                "pi": 4000.0, "api": 35.0, "degf": 180.0, "sg_g": 0.75, "pmax": 5000.0, "pb": 3500.0, "rsb": 800.0, "nrows": 20
            }}),
            ("oil_twu_critical_properties", {"request": {"mw": 200.0, "sg": 0.85}}),
            ("stock_tank_incremental_gor", {"request": {"psp": 100.0, "degf_sp": 100.0, "api": 35.0}}),
            ("validate_gas_gravities", {"request": {
                "rst": 100.0, "rsp": 700.0, "sg_st": 1.2
            }}),
        ]
        
        for tool_name, params in oil_tools:
            try:
                result = await client.call_tool(tool_name, params)
                print(f"✓ {tool_name}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {tool_name}: {str(e)[:100]}")
                tests_failed += 1
                failed_tools.append((tool_name, str(e)[:200]))
        
        # Test Gas PVT Tools
        print("\n[Gas PVT Tools]")
        print("-" * 80)
        
        gas_tools = [
            ("gas_z_factor", {"request": {
                "sg": 0.7, "degf": 180.0, "p": 3500.0, "method": "DAK"
            }}),
            ("gas_critical_properties", {"request": {"sg": 0.7, "method": "PMC"}}),
            ("gas_formation_volume_factor", {"request": {
                "sg": 0.7, "degf": 180.0, "p": 3500.0, "method": "DAK"
            }}),
            ("gas_viscosity", {"request": {
                "sg": 0.7, "degf": 180.0, "p": 3500.0, "method": "DAK"
            }}),
            ("gas_density", {"request": {
                "sg": 0.7, "degf": 180.0, "p": 3500.0, "method": "DAK"
            }}),
            ("gas_compressibility", {"request": {
                "sg": 0.7, "degf": 180.0, "p": 3500.0, "method": "DAK"
            }}),
            ("gas_pseudopressure", {"request": {
                "sg": 0.7, "degf": 180.0, "p1": 1000.0, "p2": 3500.0, "method": "DAK"
            }}),
            ("gas_pressure_from_pz", {"request": {
                "pz": 5000.0, "sg": 0.7, "degf": 180.0, "method": "DAK"
            }}),
            ("gas_sg_from_gradient", {"request": {
                "grad": 0.1, "degf": 180.0, "p": 3500.0
            }}),
            ("gas_water_content", {"request": {
                "p": 3500.0, "degf": 180.0
            }}),
            ("gas_sg_from_composition", {"request": {
                "hc_mw": 20.5, "co2": 0.05, "h2s": 0.01, "n2": 0.02
            }}),
        ]
        
        for tool_name, params in gas_tools:
            try:
                result = await client.call_tool(tool_name, params)
                print(f"✓ {tool_name}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {tool_name}: {str(e)[:100]}")
                tests_failed += 1
                failed_tools.append((tool_name, str(e)[:200]))
        
        # Test Inflow Performance Tools
        print("\n[Inflow Performance Tools]")
        print("-" * 80)
        
        inflow_tools = [
            ("oil_rate_radial", {"request": {
                "pi": 4000.0, "pb": 3500.0, "api": 35.0, "degf": 180.0, "sg_g": 0.75,
                "psd": 1500.0, "h": 50.0, "k": 100.0, "s": 0.0, "re": 1000.0,
                "rw": 0.5, "rsb": 800.0, "vogel": False
            }}),
            ("oil_rate_linear", {"request": {
                "pi": 4000.0, "pb": 3500.0, "api": 35.0, "degf": 180.0, "sg_g": 0.75,
                "psd": 1500.0, "h": 50.0, "k": 100.0, "area": 1000.0, "length": 500.0, "rsb": 800.0
            }}),
            ("gas_rate_radial", {"request": {
                "pi": 5000.0, "sg": 0.7, "degf": 180.0, "psd": 2000.0, "h": 50.0,
                "k": 100.0, "s": 0.0, "re": 1000.0, "rw": 0.5, "co2": 0.0, "h2s": 0.0, "n2": 0.0
            }}),
            ("gas_rate_linear", {"request": {
                "pi": 5000.0, "sg": 0.7, "degf": 180.0, "psd": 2000.0, "h": 50.0,
                "k": 100.0, "area": 1000.0, "length": 500.0, "co2": 0.0, "h2s": 0.0, "n2": 0.0
            }}),
        ]
        
        for tool_name, params in inflow_tools:
            try:
                result = await client.call_tool(tool_name, params)
                print(f"✓ {tool_name}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {tool_name}: {str(e)[:100]}")
                tests_failed += 1
                failed_tools.append((tool_name, str(e)[:200]))
        
        # Test Simulation Tools
        print("\n[Simulation Tools]")
        print("-" * 80)
        
        simtools_tools = [
            ("generate_rel_perm_table", {"request": {
                "rows": 25, "krtable": "SWOF", "krfamily": "COR", "kromax": 1.0,
                "krwmax": 0.25, "swc": 0.15, "swcr": 0.2, "sorw": 0.15, "no": 2.5, "nw": 1.5
            }}),
            ("generate_aquifer_influence", {"request": {
                "start": 0.01, "end": 1000.0, "rows": 25, "res": 10
            }}),
            ("rachford_rice_flash", {"request": {
                "zis": [0.5, 0.3, 0.2],
                "Kis": [2.5, 1.8, 0.6]
            }}),
            # Note: extract_eclipse_problem_cells and validate_simulation_deck
            # require actual files, so they are skipped in automated tests
        ]
        
        for tool_name, params in simtools_tools:
            try:
                result = await client.call_tool(tool_name, params)
                print(f"✓ {tool_name}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {tool_name}: {str(e)[:100]}")
                tests_failed += 1
                failed_tools.append((tool_name, str(e)[:200]))
        
        # Test Brine Tools
        print("\n[Brine Properties Tools]")
        print("-" * 80)
        
        brine_tools = [
            ("calculate_brine_properties", {"request": {
                "p": 3000.0, "degf": 180.0, "wt": 10.0, "ch4": 0.0, "co2": 0.02
            }}),
            ("co2_brine_mutual_solubility", {"request": {
                "pres": 3000.0, "temp": 180.0, "ppm": 50000.0, "metric": False
            }}),
        ]
        
        for tool_name, params in brine_tools:
            try:
                result = await client.call_tool(tool_name, params)
                print(f"✓ {tool_name}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {tool_name}: {str(e)[:100]}")
                tests_failed += 1
                failed_tools.append((tool_name, str(e)[:200]))
        
        # Test Layer/Heterogeneity Tools
        print("\n[Layer/Heterogeneity Tools]")
        print("-" * 80)
        
        layer_tools = [
            ("lorenz_to_beta", {"request": {"value": 0.5}}),
            ("beta_to_lorenz", {"request": {"value": 0.7}}),
            ("lorenz_from_flow_fractions", {"request": {
                "flow_frac": [0.25, 0.25, 0.25, 0.25],
                "perm_frac": [0.1, 0.2, 0.3, 0.4]
            }}),
            ("flow_fractions_from_lorenz", {"request": {"value": 0.5}}),
            ("generate_layer_distribution", {"request": {
                "lorenz": 0.5, "nlay": 10, "k_avg": 100.0
            }}),
        ]
        
        for tool_name, params in layer_tools:
            try:
                result = await client.call_tool(tool_name, params)
                print(f"✓ {tool_name}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {tool_name}: {str(e)[:100]}")
                tests_failed += 1
                failed_tools.append((tool_name, str(e)[:200]))
        
        # Test Library Tools
        print("\n[Component Library Tools]")
        print("-" * 80)
        
        library_tools = [
            ("get_component_properties", {"request": {"component": "methane", "eos": "PR79"}}),
        ]
        
        for tool_name, params in library_tools:
            try:
                result = await client.call_tool(tool_name, params)
                print(f"✓ {tool_name}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {tool_name}: {str(e)[:100]}")
                tests_failed += 1
                failed_tools.append((tool_name, str(e)[:200]))
        
        # Test Resources
        print("\n[Configuration Resources]")
        print("-" * 80)
        
        resources = [
            "config://version",
            "config://units",
            "config://methods",
            "config://constants",
        ]
        
        for resource_uri in resources:
            try:
                result = await client.read_resource(resource_uri)
                print(f"✓ {resource_uri}")
                tests_passed += 1
            except Exception as e:
                print(f"✗ {resource_uri}: {str(e)[:100]}")
                tests_failed += 1
                failed_tools.append((resource_uri, str(e)[:200]))
    
    # Summary
    print("\n" + "=" * 80)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print("=" * 80)
    
    if failed_tools:
        print("\nFailed Tools (first 5):")
        for tool_name, error in failed_tools[:5]:
            print(f"  - {tool_name}")
            print(f"    {error[:150]}")
    
    if tests_failed == 0:
        print("\n✓ All tests PASSED!")
        return 0
    else:
        print(f"\n✗ {tests_failed} tests FAILED!")
        return 1

if __name__ == "__main__":
    result = asyncio.run(test_all_tools())
    sys.exit(result)
