"""Component library access example.

This example demonstrates accessing critical properties for
hydrocarbon components from the component database.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def component_library_example():
    """Component library access examples."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Component Library Access Examples")
        print("=" * 80)

        # Example 1: Get properties for methane
        print("\nExample 1: Methane (C1) Properties")
        print("-" * 80)
        c1_props = await client.call_tool(
            "get_component_properties",
            {
                "component": "C1",
                "model": "PR79",
            },
        )

        print(f"Component: {c1_props['component']}")
        print(f"EOS Model: {c1_props['model']}")
        print(f"\nCritical Properties:")
        print(f"  Molecular Weight: {c1_props['MW']:.4f} lb/lbmol")
        print(f"  Critical Temperature: {c1_props['Tc_R']:.2f} degR ({c1_props['Tc_R']-459.67:.2f} degF)")
        print(f"  Critical Pressure: {c1_props['Pc_psia']:.2f} psia")
        print(f"  Critical Compressibility: {c1_props['Zc']:.4f}")
        print(f"  Critical Volume: {c1_props['Vc_cuft_per_lbmol']:.4f} cuft/lbmol")
        print(f"\nThermodynamic Properties:")
        print(f"  Acentric Factor: {c1_props['Acentric']:.4f}")
        print(f"  Normal Boiling Point: {c1_props['Tb_F']:.2f} degF")
        print(f"  Specific Gravity: {c1_props['SpGr']:.4f}")

        # Example 2: Compare different components
        print("\nExample 2: Compare Light Hydrocarbons")
        print("-" * 80)
        components = ["C1", "C2", "C3", "nC4", "nC5"]

        print(f"{'Component':>12} | {'MW':>8} | {'Tc (degR)':>12} | {'Pc (psia)':>12} | {'Acentric':>10}")
        print("-" * 65)
        for comp in components:
            props = await client.call_tool(
                "get_component_properties",
                {
                    "component": comp,
                    "model": "PR79",
                },
            )
            print(
                f"{comp:>12} | {props['MW']:8.2f} | {props['Tc_R']:12.2f} | "
                f"{props['Pc_psia']:12.2f} | {props['Acentric']:10.4f}"
            )

        # Example 3: Compare EOS models
        print("\nExample 3: Compare EOS Models for Propane")
        print("-" * 80)
        models = ["PR79", "PR77", "SRK", "RK"]

        print(f"{'Model':>8} | {'Acentric':>10} | {'Tb (degF)':>12} | {'SpGr':>8}")
        print("-" * 45)
        for model in models:
            props = await client.call_tool(
                "get_component_properties",
                {
                    "component": "C3",
                    "model": model,
                },
            )
            print(
                f"{model:>8} | {props['Acentric']:10.4f} | {props['Tb_F']:12.2f} | "
                f"{props['SpGr']:8.4f}"
            )

        # Example 4: Aromatics
        print("\nExample 4: Aromatic Components")
        print("-" * 80)
        aromatics = ["BENZENE", "TOLUENE", "m-XYLENE"]

        print(f"{'Component':>12} | {'MW':>8} | {'Tc (degR)':>12} | {'Pc (psia)':>12}")
        print("-" * 50)
        for comp in aromatics:
            props = await client.call_tool(
                "get_component_properties",
                {
                    "component": comp,
                    "model": "PR79",
                },
            )
            print(
                f"{comp:>12} | {props['MW']:8.2f} | {props['Tc_R']:12.2f} | "
                f"{props['Pc_psia']:12.2f}"
            )

        # Example 5: Non-hydrocarbons
        print("\nExample 5: Non-Hydrocarbon Components")
        print("-" * 80)
        non_hc = ["N2", "CO2", "H2S", "H2O"]

        print(f"{'Component':>12} | {'MW':>8} | {'Tc (degR)':>12} | {'Pc (psia)':>12}")
        print("-" * 50)
        for comp in non_hc:
            props = await client.call_tool(
                "get_component_properties",
                {
                    "component": comp,
                    "model": "PR79",
                },
            )
            print(
                f"{comp:>12} | {props['MW']:8.2f} | {props['Tc_R']:12.2f} | "
                f"{props['Pc_psia']:12.2f}"
            )

        # Example 6: Heavy components
        print("\nExample 6: Heavy Normal Paraffins")
        print("-" * 80)
        heavy_comps = ["nC10", "nC15", "nC20", "nC25", "nC30"]

        print(f"{'Component':>12} | {'MW':>8} | {'Tc (degR)':>12} | {'Tb (degF)':>12}")
        print("-" * 50)
        for comp in heavy_comps:
            props = await client.call_tool(
                "get_component_properties",
                {
                    "component": comp,
                    "model": "PR79",
                },
            )
            print(
                f"{comp:>12} | {props['MW']:8.2f} | {props['Tc_R']:12.2f} | "
                f"{props['Tb_F']:12.2f}"
            )

        print("\n" + "=" * 80)
        print("Component Library Examples completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(component_library_example())

