"""Brine properties calculation example.

This example demonstrates brine property calculations for various
salinities and dissolved gas conditions.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def brine_properties_example():
    """Brine properties calculation examples."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Brine Properties Calculation Examples")
        print("=" * 80)

        # Example 1: Fresh water properties
        print("\nExample 1: Fresh Water Properties")
        print("-" * 80)
        fresh_result = await client.call_tool(
            "calculate_brine_properties",
            {
                "p": 3000.0,
                "degf": 175.0,
                "wt": 0.0,
                "ch4": 0.0,
                "co2": 0.0,
            },
        )
        print(f"Pressure: {3000:.0f} psia, Temperature: {175:.0f} degF")
        units = fresh_result['units']
        print(f"Density: {fresh_result['density']:.4f} {units['density']}")
        print(f"Viscosity: {fresh_result['viscosity']:.4f} {units['viscosity']}")
        print(f"Compressibility: {fresh_result['compressibility']:.2e} {units['compressibility']}")
        print(f"Formation Volume Factor: {fresh_result['formation_volume_factor']:.4f} {units['formation_volume_factor']}")

        # Example 2: Saline brine (5% NaCl)
        print("\nExample 2: Saline Brine (5% NaCl)")
        print("-" * 80)
        saline_result = await client.call_tool(
            "calculate_brine_properties",
            {
                "p": 3000.0,
                "degf": 175.0,
                "wt": 5.0,
                "ch4": 0.0,
                "co2": 0.0,
            },
        )
        print(f"Pressure: {3000:.0f} psia, Temperature: {175:.0f} degF, Salinity: 5% NaCl")
        units = saline_result['units']
        print(f"Density: {saline_result['density']:.4f} {units['density']}")
        print(f"Viscosity: {saline_result['viscosity']:.4f} {units['viscosity']}")
        print(f"Compressibility: {saline_result['compressibility']:.2e} {units['compressibility']}")
        print(f"Formation Volume Factor: {saline_result['formation_volume_factor']:.4f} {units['formation_volume_factor']}")

        # Example 3: Methane-saturated brine
        print("\nExample 3: Methane-Saturated Brine")
        print("-" * 80)
        ch4_result = await client.call_tool(
            "calculate_brine_properties",
            {
                "p": 3000.0,
                "degf": 175.0,
                "wt": 3.0,
                "ch4": 1.0,
                "co2": 0.0,
            },
        )
        print(f"Pressure: {3000:.0f} psia, Temperature: {175:.0f} degF")
        print(f"Salinity: 3% NaCl, CH4: Saturated")
        units = ch4_result['units']
        print(f"Density: {ch4_result['density']:.4f} {units['density']}")
        print(f"Viscosity: {ch4_result['viscosity']:.4f} {units['viscosity']}")
        print(f"Compressibility: {ch4_result['compressibility']:.2e} {units['compressibility']}")
        print(f"Formation Volume Factor: {ch4_result['formation_volume_factor']:.4f} {units['formation_volume_factor']}")

        # Example 4: Pressure and temperature effects
        print("\nExample 4: Pressure and Temperature Effects")
        print("-" * 80)
        pressures = [1000, 2000, 3000, 4000, 5000]
        temperatures = [100, 150, 200, 250]

        print("\nBrine Density (lb/cuft) vs Pressure and Temperature:")
        print(f"{'T (degF)':>10}", end="")
        for p in pressures:
            print(f" | P={p:4.0f}", end="")
        print()

        for temp in temperatures:
            result = await client.call_tool(
                "calculate_brine_properties",
                {
                    "p": pressures,
                    "degf": temp,
                    "wt": 5.0,
                    "ch4": 0.0,
                    "co2": 0.0,
                },
            )
            densities = result["density"]
            print(f"{temp:10.0f}", end="")
            for den in densities:
                print(f" | {den:7.4f}", end="")
            print()

        # Example 5: Salinity effects
        print("\nExample 5: Salinity Effects on Brine Properties")
        print("-" * 80)
        salinities = [0, 1, 3, 5, 10, 15, 20]

        print(f"{'Salinity (%NaCl)':>18} | {'Density (lb/cf)':>15} | {'Viscosity (cP)':>15}")
        print("-" * 55)
        for wt in salinities:
            result = await client.call_tool(
                "calculate_brine_properties",
                {
                    "p": 3000.0,
                    "degf": 175.0,
                    "wt": wt,
                    "ch4": 0.0,
                    "co2": 0.0,
                },
            )
            print(
                f"{wt:18.1f} | {result['density']:15.4f} | "
                f"{result['viscosity']:15.4f}"
            )

        print("\n" + "=" * 80)
        print("Brine Properties Examples completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(brine_properties_example())


