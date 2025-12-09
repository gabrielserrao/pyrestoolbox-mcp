"""Geomechanics workflow example for pyResToolbox MCP server.

This example demonstrates a complete geomechanics workflow for well planning:
1. Calculate stress state from depth and logs
2. Estimate pore pressure and fracture gradient
3. Determine safe mud weight window
4. Analyze wellbore stability
5. Predict reservoir compaction

Typical use case: Pre-drill geomechanics study for a 10,000 ft vertical well.
"""

import asyncio
import json
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def main():
    """Run comprehensive geomechanics workflow."""

    async with Client(mcp) as client:
        print("=" * 80)
        print("pyResToolbox MCP Server - Geomechanics Workflow Example")
        print("=" * 80)
        print("\nScenario: Pre-drill geomechanics study for 10,000 ft vertical well")
        print("Formation: Sandstone with moderate overpressure")
        print("=" * 80)

        # Input parameters
        depth = 10000.0  # ft
        avg_density = 144.0  # lb/ft³ (19 ppg equivalent)
        sonic_observed = 100.0  # μs/ft (slower than normal = overpressure)
        sonic_normal = 70.0  # μs/ft (normal compaction trend)
        poisson_ratio = 0.25
        youngs_modulus = 1000000.0  # psi (moderate sandstone)
        cohesion = 500.0  # psi
        friction_angle = 30.0  # degrees

        # ======================
        # STEP 1: Vertical Stress
        # ======================
        print("\n" + "=" * 80)
        print("STEP 1: Calculate Vertical Stress (Overburden)")
        print("=" * 80)

        stress_result = await client.call_tool(
            "geomech_vertical_stress",
            {
                "request": {
                    "depth": depth,
                    "water_depth": 0.0,
                    "avg_density": avg_density,
                    "water_density": 64.0,
                }
            },
        )
        stress_data = json.loads(stress_result.content[0].text)
        vertical_stress = stress_data['value']

        print(f"Depth: {depth:.0f} ft")
        print(f"Average bulk density: {avg_density:.1f} lb/ft³ ({avg_density/7.48:.1f} ppg)")
        print(f"Vertical stress: {vertical_stress:.0f} psi")
        print(f"Stress gradient: {stress_data['gradient']:.3f} psi/ft")

        # ======================
        # STEP 2: Pore Pressure
        # ======================
        print("\n" + "=" * 80)
        print("STEP 2: Estimate Pore Pressure (Eaton Method)")
        print("=" * 80)

        pp_result = await client.call_tool(
            "geomech_pore_pressure_eaton",
            {
                "request": {
                    "depth": depth,
                    "observed_value": sonic_observed,
                    "normal_value": sonic_normal,
                    "overburden_psi": vertical_stress,
                    "eaton_exponent": 3.0,
                    "method": "sonic",
                }
            },
        )
        pp_data = json.loads(pp_result.content[0].text)
        pore_pressure = pp_data['value']

        print(f"Sonic travel time (observed): {sonic_observed:.1f} μs/ft")
        print(f"Sonic travel time (normal): {sonic_normal:.1f} μs/ft")
        print(f"Pore pressure: {pore_pressure:.0f} psi")
        print(f"PP gradient: {pp_data['gradient']:.3f} psi/ft ({pp_data['gradient']/0.052:.2f} ppg)")
        print(f"Overpressure: {pp_data['overpressure']:.0f} psi")

        if pp_data['gradient'] > 0.465:
            print("⚠ OVERPRESSURED ZONE - Require careful drilling planning")

        # ======================
        # STEP 3: Horizontal Stresses
        # ======================
        print("\n" + "=" * 80)
        print("STEP 3: Calculate Horizontal Stresses")
        print("=" * 80)

        h_stress_result = await client.call_tool(
            "geomech_horizontal_stress",
            {
                "request": {
                    "vertical_stress": vertical_stress,
                    "pore_pressure": pore_pressure,
                    "poisson_ratio": poisson_ratio,
                    "tectonic_factor": 0.0,  # Normal faulting regime
                    "biot_coefficient": 1.0,
                }
            },
        )
        h_stress_data = json.loads(h_stress_result.content[0].text)
        sigma_h_min = h_stress_data['sigma_h_min']
        sigma_h_max = h_stress_data['sigma_h_max']

        print(f"Poisson's ratio: {poisson_ratio:.2f}")
        print(f"σv (vertical): {vertical_stress:.0f} psi")
        print(f"σh_min (minimum horizontal): {sigma_h_min:.0f} psi")
        print(f"σh_max (maximum horizontal): {sigma_h_max:.0f} psi")
        print(f"Stress regime: {h_stress_data['stress_regime'].upper()}")

        # ======================
        # STEP 4: Fracture Gradient
        # ======================
        print("\n" + "=" * 80)
        print("STEP 4: Calculate Fracture Gradient")
        print("=" * 80)

        frac_result = await client.call_tool(
            "geomech_fracture_gradient",
            {
                "request": {
                    "depth": depth,
                    "sigma_h_min": sigma_h_min,
                    "vertical_stress": vertical_stress,
                    "pore_pressure": pore_pressure,
                    "poisson_ratio": poisson_ratio,
                    "method": "hubbert_willis",
                }
            },
        )
        frac_data = json.loads(frac_result.content[0].text)
        fracture_pressure = frac_data['fracture_pressure']

        print(f"Fracture pressure: {fracture_pressure:.0f} psi")
        print(f"Fracture gradient: {frac_data['fracture_gradient']:.3f} psi/ft")
        print(f"Equivalent MW: {frac_data['equivalent_mud_weight']:.2f} ppg")
        print(f"Margin (Pfrac - Pp): {frac_data['margin']:.0f} psi")

        # ======================
        # STEP 5: Mud Weight Window
        # ======================
        print("\n" + "=" * 80)
        print("STEP 5: Safe Mud Weight Window")
        print("=" * 80)

        mw_window_result = await client.call_tool(
            "geomech_safe_mud_weight_window",
            {
                "request": {
                    "pore_pressure": pore_pressure,
                    "fracture_pressure": fracture_pressure,
                    "depth": depth,
                    "safety_margin_overbalance": 0.5,
                    "safety_margin_fracture": 0.5,
                }
            },
        )
        mw_data = json.loads(mw_window_result.content[0].text)

        print(f"Minimum mud weight: {mw_data['min_mud_weight']:.2f} ppg")
        print(f"Maximum mud weight: {mw_data['max_mud_weight']:.2f} ppg")
        print(f"Window width: {mw_data['window_width']:.2f} ppg")
        print(f"Status: {mw_data['status'].upper()}")

        if mw_data['window_width'] < 2:
            print("⚠ NARROW WINDOW - Consider MPD or special drilling procedures")

        # Recommended mud weight (midpoint with bias toward overbalance)
        recommended_mw = mw_data['min_mud_weight'] + 0.6 * mw_data['window_width']
        print(f"\n✓ RECOMMENDED MUD WEIGHT: {recommended_mw:.1f} ppg")

        # ======================
        # STEP 6: Wellbore Stability
        # ======================
        print("\n" + "=" * 80)
        print("STEP 6: Wellbore Stability Analysis")
        print("=" * 80)

        # Calculate UCS from cohesion and friction angle
        rock_strength_result = await client.call_tool(
            "geomech_rock_strength_mohr_coulomb",
            {
                "request": {
                    "cohesion": cohesion,
                    "friction_angle": friction_angle,
                    "effective_stress_min": 2000.0,
                }
            },
        )
        strength_data = json.loads(rock_strength_result.content[0].text)
        ucs = strength_data['unconfined_strength']

        print(f"Rock properties:")
        print(f"  Cohesion: {cohesion:.0f} psi")
        print(f"  Friction angle: {friction_angle:.1f}°")
        print(f"  UCS: {ucs:.0f} psi")

        # Check breakout at recommended mud weight
        breakout_result = await client.call_tool(
            "geomech_breakout_width",
            {
                "request": {
                    "sigma_h_max": sigma_h_max,
                    "sigma_h_min": sigma_h_min,
                    "pore_pressure": pore_pressure,
                    "mud_weight": recommended_mw,
                    "wellbore_azimuth": 45.0,
                    "ucs": ucs,
                    "friction_angle": friction_angle,
                }
            },
        )
        breakout_data = json.loads(breakout_result.content[0].text)

        print(f"\nStability at {recommended_mw:.1f} ppg:")
        print(f"  Breakout width: {breakout_data['breakout_width']:.1f}°")
        print(f"  Status: {breakout_data['failure_status'].upper()}")
        print(f"  Critical MW (prevent breakout): {breakout_data['critical_mud_weight']:.2f} ppg")

        if breakout_data['breakout_width'] > 30:
            print("⚠ WARNING: Moderate to severe breakout expected")

        # ======================
        # STEP 7: Rock Properties
        # ======================
        print("\n" + "=" * 80)
        print("STEP 7: Rock Elastic Properties")
        print("=" * 80)

        moduli_result = await client.call_tool(
            "geomech_elastic_moduli_conversion",
            {
                "request": {
                    "youngs_modulus": youngs_modulus,
                    "poisson_ratio": poisson_ratio,
                }
            },
        )
        moduli_data = json.loads(moduli_result.content[0].text)

        print(f"Young's modulus (E): {moduli_data['youngs_modulus']/1e6:.2f} x 10⁶ psi")
        print(f"Bulk modulus (K): {moduli_data['bulk_modulus']/1e6:.2f} x 10⁶ psi")
        print(f"Shear modulus (G): {moduli_data['shear_modulus']/1e6:.2f} x 10⁶ psi")
        print(f"Poisson's ratio (ν): {moduli_data['poisson_ratio']:.3f}")

        # ======================
        # STEP 8: Production Effects
        # ======================
        print("\n" + "=" * 80)
        print("STEP 8: Reservoir Compaction Prediction")
        print("=" * 80)

        pressure_drop = 1000.0  # psi expected depletion
        reservoir_thickness = 100.0  # ft

        compaction_result = await client.call_tool(
            "geomech_reservoir_compaction",
            {
                "request": {
                    "pressure_drop": pressure_drop,
                    "reservoir_thickness": reservoir_thickness,
                    "youngs_modulus": 500000.0,  # Use lower E for compaction
                    "poisson_ratio": poisson_ratio,
                    "biot_coefficient": 1.0,
                }
            },
        )
        compaction_data = json.loads(compaction_result.content[0].text)

        print(f"Expected pressure depletion: {pressure_drop:.0f} psi")
        print(f"Reservoir thickness: {reservoir_thickness:.0f} ft")
        print(f"Predicted compaction: {compaction_data['compaction']:.3f} ft ({compaction_data['compaction']*12:.2f} inches)")
        print(f"Vertical strain: {compaction_data['strain']*100:.3f}%")
        print(f"Surface subsidence: {compaction_data['subsidence']:.3f} ft ({compaction_data['subsidence']*12:.2f} inches)")

        if compaction_data['compaction'] > 1.0:
            print("⚠ SIGNIFICANT COMPACTION - Monitor casing integrity")

        # ======================
        # SUMMARY
        # ======================
        print("\n" + "=" * 80)
        print("DRILLING RECOMMENDATIONS SUMMARY")
        print("=" * 80)

        print(f"\n1. FORMATION PRESSURE:")
        print(f"   - Pore pressure: {pore_pressure:.0f} psi ({pp_data['gradient']:.3f} psi/ft)")
        print(f"   - Fracture pressure: {fracture_pressure:.0f} psi ({frac_data['fracture_gradient']:.3f} psi/ft)")
        print(f"   - Pressure regime: {'OVERPRESSURED' if pp_data['gradient'] > 0.465 else 'NORMAL'}")

        print(f"\n2. STRESS STATE:")
        print(f"   - Vertical stress: {vertical_stress:.0f} psi")
        print(f"   - Min horizontal: {sigma_h_min:.0f} psi")
        print(f"   - Max horizontal: {sigma_h_max:.0f} psi")
        print(f"   - Regime: {h_stress_data['stress_regime'].upper()}")

        print(f"\n3. MUD WEIGHT RECOMMENDATIONS:")
        print(f"   - Minimum MW: {mw_data['min_mud_weight']:.1f} ppg")
        print(f"   - Maximum MW: {mw_data['max_mud_weight']:.1f} ppg")
        print(f"   - RECOMMENDED: {recommended_mw:.1f} ppg")
        print(f"   - Window status: {mw_data['status']}")

        print(f"\n4. WELLBORE STABILITY:")
        print(f"   - UCS: {ucs:.0f} psi")
        print(f"   - Breakout risk: {breakout_data['failure_status']}")
        print(f"   - Critical MW: {breakout_data['critical_mud_weight']:.1f} ppg")

        print(f"\n5. PRODUCTION CONSIDERATIONS:")
        print(f"   - Expected compaction: {compaction_data['compaction']:.2f} ft")
        print(f"   - Casing strain risk: {'HIGH' if compaction_data['compaction'] > 1.0 else 'MODERATE' if compaction_data['compaction'] > 0.5 else 'LOW'}")

        print("\n" + "=" * 80)
        print("GEOMECHANICS WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("✓ Formation is overpressured - require proper mud weight control")
        print("✓ Normal faulting stress regime - breakouts will be horizontal")
        print(f"✓ Use {recommended_mw:.1f} ppg mud weight with careful monitoring")
        print("✓ Consider compaction effects on casing design for production")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
