"""Reservoir heterogeneity analysis example.

This example demonstrates Lorenz coefficient calculations and
layer property generation for reservoir simulation.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def heterogeneity_analysis():
    """Reservoir heterogeneity analysis workflow."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Reservoir Heterogeneity Analysis")
        print("=" * 80)

        # Example 1: Convert Lorenz to Beta
        print("\nExample 1: Lorenz Coefficient to Beta Conversion")
        print("-" * 80)
        lorenz_values = [0.2, 0.4, 0.6, 0.8]

        print(f"{'Lorenz Coeff':>15} | {'Beta':>10} | {'Interpretation':>20}")
        print("-" * 50)
        for lc in lorenz_values:
            beta_result = await client.call_tool(
                "lorenz_to_beta",
                {"value": lc},
            )
            beta = beta_result["beta"]
            if lc < 0.3:
                interp = "Homogeneous"
            elif lc < 0.6:
                interp = "Moderate"
            else:
                interp = "Heterogeneous"
            print(f"{lc:15.3f} | {beta:10.4f} | {interp:>20}")

        # Example 2: Convert Beta to Lorenz
        print("\nExample 2: Beta to Lorenz Coefficient Conversion")
        print("-" * 80)
        beta_values = [0.3, 0.5, 0.7, 0.9]

        print(f"{'Beta':>10} | {'Lorenz Coeff':>15} | {'Interpretation':>20}")
        print("-" * 50)
        for beta_val in beta_values:
            lorenz_result = await client.call_tool(
                "beta_to_lorenz",
                {"value": beta_val},
            )
            lc = lorenz_result["lorenz_coefficient"]
            if lc < 0.3:
                interp = "Homogeneous"
            elif lc < 0.6:
                interp = "Moderate"
            else:
                interp = "Heterogeneous"
            print(f"{beta_val:10.3f} | {lc:15.4f} | {interp:>20}")

        # Example 3: Calculate Lorenz from flow fractions
        print("\nExample 3: Lorenz from Production Data")
        print("-" * 80)
        # Simulated PLT data: flow fractions and kh fractions for 5 layers
        flow_fracs = [0.45, 0.25, 0.15, 0.10, 0.05]  # Flow allocation
        perm_fracs = [0.30, 0.25, 0.20, 0.15, 0.10]  # kh allocation

        lorenz_from_data = await client.call_tool(
            "lorenz_from_flow_fractions",
            {
                "flow_frac": flow_fracs,
                "perm_frac": perm_fracs,
            },
        )

        print(f"Number of Layers: {lorenz_from_data['number_of_layers']}")
        print(f"Lorenz Coefficient: {lorenz_from_data['lorenz_coefficient']:.4f}")
        print(f"Interpretation: {lorenz_from_data['interpretation']}")

        print("\nLayer-by-Layer Analysis:")
        print(f"{'Layer':>8} | {'Flow %':>10} | {'kh %':>10} | {'Ratio':>10}")
        print("-" * 45)
        for i, (ff, pf) in enumerate(zip(flow_fracs, perm_fracs)):
            ratio = ff / pf if pf > 0 else 0
            print(f"{i+1:8d} | {ff*100:10.2f} | {pf*100:10.2f} | {ratio:10.2f}")

        # Example 4: Generate layer distribution
        print("\nExample 4: Generate Layer Permeability Distribution")
        print("-" * 80)
        lorenz_target = 0.6
        n_layers = 10
        total_h = 100.0  # Total thickness (ft)
        avg_k = 150.0  # Average permeability (mD)

        layer_dist = await client.call_tool(
            "generate_layer_distribution",
            {
                "lorenz": lorenz_target,
                "nlay": n_layers,
                "h": total_h,
                "k_avg": avg_k,
            },
        )

        print(f"Target Lorenz Coefficient: {lorenz_target:.2f}")
        print(f"Number of Layers: {n_layers}")
        print(f"Total Thickness: {total_h:.1f} ft")
        print(f"Average Permeability: {avg_k:.1f} mD")

        print(f"\n{'Layer':>8} | {'h (ft)':>10} | {'k (mD)':>10} | {'h_frac':>10} | {'kh_frac':>10}")
        print("-" * 55)
        for layer in layer_dist["layers"]:
            print(
                f"{layer['layer']:8d} | {layer['thickness_ft']:10.2f} | "
                f"{layer['permeability_md']:10.2f} | {layer['thickness_fraction']:10.4f} | "
                f"{layer['kh_fraction']:10.4f}"
            )

        stats = layer_dist["statistics"]
        print("\nPermeability Statistics:")
        print(f"  Minimum: {stats['k_min_md']:.2f} mD")
        print(f"  Maximum: {stats['k_max_md']:.2f} mD")
        print(f"  Average: {stats['k_avg_md']:.2f} mD")
        print(f"  Median: {stats['k_median_md']:.2f} mD")
        print(f"  Std Dev: {stats['k_std_md']:.2f} mD")
        print(f"  Heterogeneity Ratio: {stats['heterogeneity_ratio']:.2f}")

        # Example 5: Flow fractions from Lorenz
        print("\nExample 5: Flow Fractions from Lorenz Coefficient")
        print("-" * 80)
        flow_profile = await client.call_tool(
            "flow_fractions_from_lorenz",
            {"value": lorenz_target},
        )

        print(f"Lorenz Coefficient: {lorenz_target:.2f}")
        print(f"\nLorenz Curve Data (first 10 points):")
        print(f"{'Cum Flow':>12} | {'Cum Storage':>15}")
        print("-" * 30)
        flow_cap = flow_profile["cumulative_flow_capacity"]
        storage_cap = flow_profile["cumulative_storage_capacity"]
        for i in range(min(10, len(flow_cap))):
            print(f"{flow_cap[i]:12.4f} | {storage_cap[i]:15.4f}")

        # Example 6: Compare different heterogeneity levels
        print("\nExample 6: Compare Different Heterogeneity Levels")
        print("-" * 80)
        lorenz_levels = [0.2, 0.4, 0.6, 0.8]

        print(f"\n{'Lorenz':>10} | {'k_min (mD)':>15} | {'k_max (mD)':>15} | {'Ratio':>10}")
        print("-" * 55)
        for lc in lorenz_levels:
            dist = await client.call_tool(
                "generate_layer_distribution",
                {
                    "lorenz": lc,
                    "nlay": 10,
                    "h": 100.0,
                    "k_avg": 150.0,
                },
            )
            stats = dist["statistics"]
            print(
                f"{lc:10.2f} | {stats['k_min_md']:15.2f} | {stats['k_max_md']:15.2f} | "
                f"{stats['heterogeneity_ratio']:10.2f}"
            )

        print("\n" + "=" * 80)
        print("Reservoir Heterogeneity Analysis completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(heterogeneity_analysis())


