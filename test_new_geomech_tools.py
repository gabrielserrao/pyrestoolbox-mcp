#!/usr/bin/env python3
"""Direct test of the 12 new advanced geomechanics tools via MCP call_tool."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from pyrestoolbox_mcp.server import mcp


async def call(tool: str, **kwargs):
    result = await mcp.call_tool(tool, {"request": kwargs})
    return result


async def run_tests():
    import json

    print("=" * 70)
    print("NEW ADVANCED GEOMECHANICS TOOLS - DIRECT MCP TEST")
    print("12 tools added in latest release")
    print("=" * 70)

    passed = failed = 0

    tests = [
        # (name, tool, inputs, assert_key, assert_fn)
        (
            "Stress Polygon",
            "geomech_stress_polygon",
            dict(vertical_stress=10000.0, pore_pressure=4500.0, friction_coefficient=0.6,
                 sigma_h_min=6500.0, sigma_h_max=8500.0),
            "actual_stress_state",
            lambda r: r.get("actual_stress_state") is not None,
        ),
        (
            "Sand Production",
            "geomech_sand_production",
            dict(sigma_h_max=8500.0, sigma_h_min=6500.0, pore_pressure=4500.0,
                 ucs=3000.0, cohesion=500.0, friction_angle=30.0,
                 permeability=100.0, porosity=0.20),
            "critical_drawdown",
            lambda r: "critical_drawdown" in r,
        ),
        (
            "Fault Stability",
            "geomech_fault_stability",
            dict(sigma_1=10000.0, sigma_3=6000.0, pore_pressure=4500.0,
                 fault_strike=45.0, fault_dip=60.0, friction_coefficient=0.6),
            "slip_tendency",
            lambda r: r.get("slip_tendency") is not None,
        ),
        (
            "Deviated Well Stress",
            "geomech_deviated_well_stress",
            dict(sigma_v=10000.0, sigma_h_max=8500.0, sigma_h_min=6500.0,
                 sigma_h_max_azimuth=45.0, well_azimuth=90.0, well_inclination=60.0,
                 pore_pressure=4500.0, mud_weight=10.0, depth=10000.0),
            "wellbore_wall_stresses",
            lambda r: r.get("wellbore_wall_stresses") is not None,
        ),
        (
            "Tensile Failure",
            "geomech_tensile_failure",
            dict(sigma_h_max=8500.0, sigma_h_min=6500.0, pore_pressure=4500.0,
                 tensile_strength=500.0),
            "fracture_initiation_pressure",
            lambda r: r.get("fracture_initiation_pressure", 0) > 0,
        ),
        (
            "Shear Failure Criteria",
            "geomech_shear_failure_criteria",
            dict(sigma_1=10000.0, sigma_2=7500.0, sigma_3=5000.0,
                 ucs=8000.0, cohesion=1500.0, friction_angle=30.0),
            "criteria_results",
            lambda r: r.get("criteria_results") is not None,
        ),
        (
            "Breakout Stress Inversion",
            "geomech_breakout_stress_inversion",
            dict(breakout_width=60.0, sigma_v=10000.0, pore_pressure=4500.0,
                 mud_weight=10.0, ucs=5000.0, friction_angle=30.0, depth=10000.0),
            "estimated_sigma_h_max",
            lambda r: r.get("estimated_sigma_h_max", 0) > 0,
        ),
        (
            "Breakdown Pressure",
            "geomech_breakdown_pressure",
            dict(sigma_h_max=8500.0, sigma_h_min=6500.0, pore_pressure=4500.0,
                 tensile_strength=500.0),
            "breakdown_pressure",
            lambda r: r.get("breakdown_pressure", 0) > 0,
        ),
        (
            "Stress Path During Depletion",
            "geomech_stress_path",
            dict(initial_pore_pressure=5000.0, final_pore_pressure=3000.0,
                 vertical_stress=10000.0, initial_sigma_h=7000.0,
                 poisson_ratio=0.25),
            "final_sigma_h",
            lambda r: r.get("final_sigma_h", 0) > 0,
        ),
        (
            "Thermal Stress",
            "geomech_thermal_stress",
            dict(temperature_change=-50.0, youngs_modulus=1000000.0,
                 poisson_ratio=0.25, thermal_expansion_coefficient=6e-6),
            "thermal_stress",
            lambda r: r.get("thermal_stress") is not None,
        ),
        (
            "UCS from Logs",
            "geomech_ucs_from_logs",
            dict(sonic_dt=70.0, lithology="sandstone", correlation="mcnally"),
            "ucs",
            lambda r: r.get("ucs", 0) > 0,
        ),
        (
            "Critical Drawdown",
            "geomech_critical_drawdown",
            dict(sigma_h_max=8500.0, sigma_h_min=6500.0, reservoir_pressure=5000.0,
                 ucs=3000.0, cohesion=500.0, friction_angle=30.0),
            "critical_drawdown",
            lambda r: "critical_drawdown" in r,
        ),
    ]

    for name, tool, inputs, key, check in tests:
        print(f"\n--- {name} ({tool}) ---")
        try:
            result = await call(tool, **inputs)
            text = result.content[0].text if result.content else "{}"
            data = json.loads(text)

            if check(data):
                print(f"  PASSED  |  {key} = {data.get(key)}")
                passed += 1
            else:
                print(f"  FAIL    |  Expected '{key}' in result but got: {list(data.keys())[:5]}")
                failed += 1
        except Exception as e:
            print(f"  ERROR   |  {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed / {len(tests)} total")
    if failed == 0:
        print("ALL 12 NEW GEOMECHANICS TOOLS VERIFIED")
    print("=" * 70)
    return failed == 0


if __name__ == "__main__":
    ok = asyncio.run(run_tests())
    sys.exit(0 if ok else 1)
