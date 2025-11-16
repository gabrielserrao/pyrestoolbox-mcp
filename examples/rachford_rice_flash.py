"""Rachford-Rice flash calculation example.

This example demonstrates vapor-liquid equilibrium calculations
using the Rachford-Rice equation for phase behavior analysis.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def rachford_rice_example():
    """Rachford-Rice flash calculation examples."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Rachford-Rice Flash Calculation Examples")
        print("=" * 80)

        # Example 1: Simple binary system
        print("\nExample 1: Binary System (Methane + Propane)")
        print("-" * 80)
        flash1 = await client.call_tool(
            "rachford_rice_flash",
            {
                "zis": [0.6, 0.4],  # Overall composition: 60% C1, 40% C3
                "Kis": [3.0, 0.3],  # K-values at P, T
            },
        )

        print(f"Overall Composition: C1={0.6:.1%}, C3={0.4:.1%}")
        print(f"K-values: K_C1={3.0:.2f}, K_C3={0.3:.2f}")
        print(f"\nResults:")
        print(f"  Vapor Fraction (β): {flash1['vapor_fraction']:.4f}")
        print(f"  Liquid Fraction: {1 - flash1['vapor_fraction']:.4f}")
        print(f"\n  Liquid Composition:")
        for i, xi in enumerate(flash1["liquid_composition"]):
            comp = "C1" if i == 0 else "C3"
            print(f"    {comp}: {xi:.4f}")
        print(f"\n  Vapor Composition:")
        for i, yi in enumerate(flash1["vapor_composition"]):
            comp = "C1" if i == 0 else "C3"
            print(f"    {comp}: {yi:.4f}")

        # Example 2: Three-component system
        print("\nExample 2: Three-Component System")
        print("-" * 80)
        flash2 = await client.call_tool(
            "rachford_rice_flash",
            {
                "zis": [0.5, 0.3, 0.2],  # C1, C2, C3
                "Kis": [2.5, 1.2, 0.4],
            },
        )

        components = ["C1", "C2", "C3"]
        print(f"Overall Composition: {', '.join([f'{c}={z:.1%}' for c, z in zip(components, [0.5, 0.3, 0.2])])}")
        print(f"K-values: {', '.join([f'K_{c}={k:.2f}' for c, k in zip(components, [2.5, 1.2, 0.4])])}")
        print(f"\nResults:")
        print(f"  Vapor Fraction: {flash2['vapor_fraction']:.4f}")
        print(f"\n  Liquid Composition:")
        for comp, xi in zip(components, flash2["liquid_composition"]):
            print(f"    {comp}: {xi:.4f}")
        print(f"\n  Vapor Composition:")
        for comp, yi in zip(components, flash2["vapor_composition"]):
            print(f"    {comp}: {yi:.4f}")

        # Example 3: Near-critical conditions
        print("\nExample 3: Near-Critical Conditions")
        print("-" * 80)
        flash3 = await client.call_tool(
            "rachford_rice_flash",
            {
                "zis": [0.7, 0.2, 0.1],  # High C1 content
                "Kis": [1.1, 0.9, 0.8],  # K-values near 1.0
            },
        )

        print(f"Overall Composition: C1=70%, C2=20%, C3=10%")
        print(f"K-values: K_C1=1.1, K_C2=0.9, K_C3=0.8 (near critical)")
        print(f"\nResults:")
        print(f"  Vapor Fraction: {flash3['vapor_fraction']:.4f}")
        print(f"  Note: Near-critical conditions result in small phase split")

        # Example 4: Separator flash calculation
        print("\nExample 4: Separator Flash Calculation")
        print("-" * 80)
        # Typical separator conditions: 100 psia, 80 degF
        # K-values would be calculated from EOS or correlations
        separator_flash = await client.call_tool(
            "rachford_rice_flash",
            {
                "zis": [0.65, 0.20, 0.10, 0.05],  # C1, C2, C3, nC4
                "Kis": [8.5, 2.2, 0.6, 0.15],  # K-values at separator conditions
            },
        )

        sep_components = ["C1", "C2", "C3", "nC4"]
        print(f"Feed to Separator:")
        print(f"  Composition: {', '.join([f'{c}={z:.1%}' for c, z in zip(sep_components, [0.65, 0.20, 0.10, 0.05])])}")
        print(f"\nSeparator Conditions: 100 psia, 80 degF")
        print(f"K-values: {', '.join([f'K_{c}={k:.2f}' for c, k in zip(sep_components, [8.5, 2.2, 0.6, 0.15])])}")
        print(f"\nResults:")
        print(f"  Vapor Fraction (Gas): {separator_flash['vapor_fraction']:.4f}")
        print(f"  Liquid Fraction (Oil): {1 - separator_flash['vapor_fraction']:.4f}")
        print(f"\n  Separator Gas Composition:")
        for comp, yi in zip(sep_components, separator_flash["vapor_composition"]):
            print(f"    {comp}: {yi:.4f} ({yi*100:.2f}%)")
        print(f"\n  Separator Oil Composition:")
        for comp, xi in zip(sep_components, separator_flash["liquid_composition"]):
            print(f"    {comp}: {xi:.4f} ({xi*100:.2f}%)")

        # Example 5: Sensitivity to K-values
        print("\nExample 5: Sensitivity to K-Values")
        print("-" * 80)
        z_feed = [0.6, 0.4]
        k_scenarios = [
            [2.0, 0.5],
            [3.0, 0.3],
            [4.0, 0.2],
            [5.0, 0.15],
        ]

        print(f"Feed Composition: C1=60%, C3=40%")
        print(f"\n{'K_C1':>8} | {'K_C3':>8} | {'Vapor Frac':>12} | {'y_C1':>10} | {'x_C1':>10}")
        print("-" * 55)
        for k_vals in k_scenarios:
            flash_sens = await client.call_tool(
                "rachford_rice_flash",
                {
                    "zis": z_feed,
                    "Kis": k_vals,
                },
            )
            y_c1 = flash_sens["vapor_composition"][0]
            x_c1 = flash_sens["liquid_composition"][0]
            print(
                f"{k_vals[0]:8.2f} | {k_vals[1]:8.2f} | {flash_sens['vapor_fraction']:12.4f} | "
                f"{y_c1:10.4f} | {x_c1:10.4f}"
            )

        print("\n" + "=" * 80)
        print("Rachford-Rice Flash Examples completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(rachford_rice_example())

