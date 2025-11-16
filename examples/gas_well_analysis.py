"""Gas well performance analysis example.

This example demonstrates comprehensive gas well analysis including
IPR generation, pseudopressure calculations, and rate optimization.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def gas_well_analysis():
    """Complete gas well performance analysis workflow."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Gas Well Performance Analysis")
        print("=" * 80)

        # Gas and reservoir properties
        sg = 0.7
        degf = 200.0
        co2 = 0.02
        h2s = 0.01
        n2 = 0.03
        pi = 5000.0  # Initial reservoir pressure

        # Well and reservoir parameters
        h = 100.0  # Net pay thickness (ft)
        k = 50.0  # Permeability (mD)
        s = -1.0  # Skin (stimulated well)
        re = 2000.0  # Drainage radius (ft)
        rw = 0.25  # Wellbore radius (ft)

        print("\nGas Properties:")
        print("-" * 80)
        print(f"Gas Specific Gravity: {sg:.3f}")
        print(f"Temperature: {degf:.1f} degF")
        print(f"CO2: {co2*100:.1f}%")
        print(f"H2S: {h2s*100:.1f}%")
        print(f"N2: {n2*100:.1f}%")
        print(f"Initial Pressure: {pi:.1f} psia")

        print("\nWell Properties:")
        print("-" * 80)
        print(f"Net Pay: {h:.1f} ft")
        print(f"Permeability: {k:.1f} mD")
        print(f"Skin: {s:.1f}")
        print(f"Drainage Radius: {re:.1f} ft")
        print(f"Wellbore Radius: {rw:.2f} ft")

        # Step 1: Calculate critical properties
        print("\nStep 1: Calculate Critical Properties")
        print("-" * 80)
        tc_pc = await client.call_tool(
            "gas_critical_properties",
            {
                "sg": sg,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
                "method": "PMC",
            },
        )
        tc = tc_pc["value"]["tc"]
        pc = tc_pc["value"]["pc"]
        print(f"Critical Temperature: {tc:.2f} degR")
        print(f"Critical Pressure: {pc:.2f} psia")

        # Step 2: Generate IPR curve
        print("\nStep 2: Generate Gas IPR Curve")
        print("-" * 80)
        pwf_values = [pi * (1 - i / 20) for i in range(21)]

        qg_result = await client.call_tool(
            "gas_rate_radial",
            {
                "pi": pi,
                "psd": pwf_values,
                "sg": sg,
                "degf": degf,
                "h": h,
                "k": k,
                "rw": rw,
                "re": re,
                "s": s,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
            },
        )

        print(f"\n{'Pwf (psia)':>12} | {'Drawdown (psi)':>15} | {'Rate (MSCF/day)':>18}")
        print("=" * 50)
        for pwf, qg in zip(pwf_values, qg_result["value"]):
            drawdown = pi - pwf
            print(f"{pwf:12.1f} | {drawdown:15.1f} | {qg:18.2f}")

        max_rate = max(qg_result["value"])
        print(f"\nMaximum Rate (AOF): {max_rate:.2f} MSCF/day")

        # Step 3: Compare Z-factor methods
        print("\nStep 3: Z-Factor Method Comparison")
        print("-" * 80)
        methods = ["DAK", "HY", "WYW"]
        p_test = 3000.0

        print(f"\nZ-Factor at {p_test:.0f} psia:")
        print(f"{'Method':>10} | {'Z-Factor':>10} | {'Rate (MSCF/day)':>18}")
        print("-" * 45)
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

            qg_method = await client.call_tool(
                "gas_rate_radial",
                {
                    "pi": pi,
                    "psd": pwf_test,
                    "sg": sg,
                    "degf": degf,
                    "h": h,
                    "k": k,
                    "rw": rw,
                    "re": re,
                    "s": s,
                    "co2": co2,
                    "h2s": h2s,
                    "n2": n2,
                },
            )

            z_val = z_comp["value"]
            qg_val = qg_method["value"]
            if isinstance(qg_val, list):
                qg_val = qg_val[0]
            print(f"{method:>10} | {z_val:10.4f} | {qg_val:18.2f}")

        # Step 4: Linear flow (horizontal well)
        print("\nStep 4: Linear Flow (Horizontal Well)")
        print("-" * 80)
        area = 5000  # Cross-sectional area (ft²)
        length = 2000  # Horizontal length (ft)

        qg_linear = await client.call_tool(
            "gas_rate_linear",
            {
                "pi": pi,
                "psd": pwf_test,
                "sg": sg,
                "degf": degf,
                "area": area,
                "length": length,
                "h": h,
                "k": k,
                "co2": co2,
                "h2s": h2s,
                "n2": n2,
            },
        )

        qg_l = qg_linear["value"]
        if isinstance(qg_l, list):
            qg_l = qg_l[0]

        print(f"\nHorizontal Well Performance:")
        print(f"  Cross-sectional Area: {area:.0f} ft²")
        print(f"  Horizontal Length: {length:.0f} ft")
        print(f"  Rate at {pwf_test:.0f} psia: {qg_l:.2f} MSCF/day")

        # Step 5: Sensitivity to gas composition
        print("\nStep 5: Sensitivity to Gas Composition")
        print("-" * 80)
        sg_scenarios = [0.6, 0.65, 0.7, 0.75, 0.8]

        print(f"\nRate vs Gas Specific Gravity:")
        print(f"{'SG':>8} | {'Rate (MSCF/day)':>18}")
        print("-" * 30)
        for sg_test in sg_scenarios:
            qg_sg = await client.call_tool(
                "gas_rate_radial",
                {
                    "pi": pi,
                    "psd": pwf_test,
                    "sg": sg_test,
                    "degf": degf,
                    "h": h,
                    "k": k,
                    "rw": rw,
                    "re": re,
                    "s": s,
                    "co2": 0.0,
                    "h2s": 0.0,
                    "n2": 0.0,
                },
            )
            qg_val = qg_sg["value"]
            if isinstance(qg_val, list):
                qg_val = qg_val[0]
            print(f"{sg_test:8.3f} | {qg_val:18.2f}")

        print("\n" + "=" * 80)
        print("Gas Well Analysis completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(gas_well_analysis())

