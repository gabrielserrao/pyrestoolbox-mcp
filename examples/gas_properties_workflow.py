"""Gas properties workflow example.

This example demonstrates comprehensive gas PVT property calculations
including Z-factor, viscosity, density, compressibility, and formation volume factor.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def gas_properties_workflow():
    """Complete gas PVT properties analysis workflow."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Gas PVT Properties Workflow")
        print("=" * 80)

        # Gas composition and conditions
        sg = 0.7
        degf = 180.0
        co2 = 0.02
        h2s = 0.01
        n2 = 0.03
        pressures = [500, 1000, 2000, 3000, 4000, 5000]

        print("\nGas Composition:")
        print("-" * 80)
        print(f"Specific Gravity: {sg:.3f}")
        print(f"Temperature: {degf:.1f} degF")
        print(f"CO2: {co2*100:.1f}%")
        print(f"H2S: {h2s*100:.1f}%")
        print(f"N2: {n2*100:.1f}%")

        # Step 1: Calculate critical properties
        print("\nStep 1: Calculate Critical Properties")
        print("-" * 80)
        tc_pc_result = await client.call_tool(
            "gas_critical_properties",
            {
                "sg": sg,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
                "method": "PMC",
            },
        )
        tc = tc_pc_result["tc_degR"]
        pc = tc_pc_result["pc_psia"]
        print(f"Critical Temperature: {tc:.2f} degR ({tc-459.67:.2f} degF)")
        print(f"Critical Pressure: {pc:.2f} psia")
        print(f"Method: {tc_pc_result['method']}")

        # Step 2: Calculate Z-factors at multiple pressures
        print("\nStep 2: Calculate Z-Factors")
        print("-" * 80)
        z_result = await client.call_tool(
            "gas_z_factor",
            {
                "sg": sg,
                "degf": degf,
                "p": pressures,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
                "method": "DAK",
            },
        )
        z_values = z_result["value"]

        # Step 3: Calculate gas viscosity
        print("\nStep 3: Calculate Gas Viscosity")
        print("-" * 80)
        ug_result = await client.call_tool(
            "gas_viscosity",
            {
                "sg": sg,
                "degf": degf,
                "p": pressures,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
                "method": "DAK",
            },
        )
        ug_values = ug_result["value"]

        # Step 4: Calculate gas density
        print("\nStep 4: Calculate Gas Density")
        print("-" * 80)
        den_result = await client.call_tool(
            "gas_density",
            {
                "sg": sg,
                "degf": degf,
                "p": pressures,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
                "method": "DAK",
            },
        )
        den_values = den_result["value"]

        # Step 5: Calculate gas compressibility
        print("\nStep 5: Calculate Gas Compressibility")
        print("-" * 80)
        cg_result = await client.call_tool(
            "gas_compressibility",
            {
                "sg": sg,
                "degf": degf,
                "p": pressures,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
                "method": "DAK",
            },
        )
        cg_values = cg_result["value"]

        # Step 6: Calculate gas formation volume factor
        print("\nStep 6: Calculate Gas Formation Volume Factor")
        print("-" * 80)
        bg_result = await client.call_tool(
            "gas_formation_volume_factor",
            {
                "sg": sg,
                "degf": degf,
                "p": pressures,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
                "method": "DAK",
            },
        )
        bg_values = bg_result["value"]

        # Print comprehensive gas properties table
        print("\n" + "=" * 100)
        print(
            f"{'P (psia)':>10} | {'Z':>8} | {'Visc (cP)':>10} | "
            f"{'Den (lb/cf)':>12} | {'Cg (1/psi)':>12} | {'Bg (rcf/scf)':>13}"
        )
        print("=" * 100)
        for i, p in enumerate(pressures):
            z = z_values[i] if isinstance(z_values, list) else z_values
            ug = ug_values[i] if isinstance(ug_values, list) else ug_values
            den = den_values[i] if isinstance(den_values, list) else den_values
            cg = cg_values[i] if isinstance(cg_values, list) else cg_values
            bg = bg_values[i] if isinstance(bg_values, list) else bg_values
            print(
                f"{p:10.1f} | {z:8.4f} | {ug:10.4f} | "
                f"{den:12.4f} | {cg:12.2e} | {bg:13.6f}"
            )
        print("=" * 100)

        # Step 7: Compare different Z-factor methods
        print("\nStep 7: Compare Z-Factor Methods")
        print("-" * 80)
        methods = ["DAK", "HY", "WYW"]
        p_test = 3000.0

        print(f"\nZ-Factor Comparison at {p_test:.0f} psia:")
        print(f"{'Method':>10} | {'Z-Factor':>10}")
        print("-" * 25)
        for method in methods:
            z_comp = await client.call_tool(
                "gas_z_factor",
                {
                    "sg": sg,
                    "degf": degf,
                    "p": p_test,
                    "co2": co2,
                    "h2s": h2s,
                    "n2": n2,
                    "method": method,
                },
            )
            z_val = z_comp["value"]
            print(f"{method:>10} | {z_val:10.4f}")

        print("\n" + "=" * 80)
        print("Gas Properties Workflow completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(gas_properties_workflow())

