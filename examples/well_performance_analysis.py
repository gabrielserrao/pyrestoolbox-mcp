"""Well performance analysis example.

This example demonstrates comprehensive well performance analysis including
IPR generation, sensitivity analysis, and optimization.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def well_performance_analysis():
    """Complete well performance analysis workflow."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Well Performance Analysis")
        print("=" * 80)

        # Reservoir and fluid properties
        api = 38.0
        degf = 175.0
        sg_g = 0.68
        rsb = 750.0
        pi = 4000.0  # Initial reservoir pressure
        pb = 3500.0  # Bubble point pressure

        # Well and reservoir parameters
        h = 75.0  # Net pay thickness (ft)
        k = 150.0  # Permeability (mD)
        s = -2.0  # Skin (stimulated well)
        re = 1500.0  # Drainage radius (ft)
        rw = 0.5  # Wellbore radius (ft)

        print("\nReservoir Properties:")
        print("-" * 80)
        print(f"Oil API: {api:.1f} degrees")
        print(f"Temperature: {degf:.1f} degF")
        print(f"Gas SG: {sg_g:.3f}")
        print(f"Solution GOR at Pb: {rsb:.1f} scf/stb")
        print(f"Initial Pressure: {pi:.1f} psia")
        print(f"Bubble Point: {pb:.1f} psia")

        print("\nWell Properties:")
        print("-" * 80)
        print(f"Net Pay: {h:.1f} ft")
        print(f"Permeability: {k:.1f} mD")
        print(f"Skin: {s:.1f}")
        print(f"Drainage Radius: {re:.1f} ft")
        print(f"Wellbore Radius: {rw:.2f} ft")

        # Step 1: Generate IPR curve
        print("\nStep 1: Generate IPR Curve")
        print("-" * 80)
        pwf_values = [pi * (1 - i / 20) for i in range(21)]  # 0% to 100% drawdown

        qo_result = await client.call_tool(
            "oil_rate_radial",
            {
                "pi": pi,
                "pb": pb,
                "api": api,
                "degf": degf,
                "sg_g": sg_g,
                "psd": pwf_values,
                "h": h,
                "k": k,
                "s": s,
                "re": re,
                "rw": rw,
                "rsb": rsb,
                "vogel": False,
            },
        )

        print(f"\n{'Pwf (psia)':>12} | {'Drawdown (psi)':>15} | {'Rate (STB/day)':>15} | {'PI':>10}")
        print("=" * 60)
        for pwf, qo in zip(pwf_values, qo_result["value"]):
            drawdown = pi - pwf
            pi_value = qo / drawdown if drawdown > 0 else 0
            print(f"{pwf:12.1f} | {drawdown:15.1f} | {qo:15.2f} | {pi_value:10.2f}")

        max_rate = max(qo_result["value"])
        print(f"\nMaximum Rate (AOF): {max_rate:.2f} STB/day")

        # Step 2: Sensitivity analysis - Permeability
        print("\nStep 2: Sensitivity Analysis - Permeability")
        print("-" * 80)
        k_values = [50, 100, 150, 200, 250]
        pwf_test = pi * 0.5  # 50% drawdown

        print(f"\nRate vs Permeability at {pwf_test:.0f} psia BHFP:")
        print(f"{'Permeability (mD)':>20} | {'Rate (STB/day)':>15}")
        print("-" * 40)
        for k_test in k_values:
            qo_k = await client.call_tool(
                "oil_rate_radial",
                {
                    "pi": pi,
                    "pb": pb,
                    "api": api,
                    "degf": degf,
                    "sg_g": sg_g,
                    "psd": pwf_test,
                    "h": h,
                    "k": k_test,
                    "s": s,
                    "re": re,
                    "rw": rw,
                    "rsb": rsb,
                    "vogel": False,
                },
            )
            qo_val = qo_k["value"]
            if isinstance(qo_val, list):
                qo_val = qo_val[0]
            print(f"{k_test:20.0f} | {qo_val:15.2f}")

        # Step 3: Sensitivity analysis - Skin
        print("\nStep 3: Sensitivity Analysis - Skin Factor")
        print("-" * 80)
        s_values = [-5, -2, 0, 2, 5, 10]

        print(f"\nRate vs Skin at {pwf_test:.0f} psia BHFP:")
        print(f"{'Skin':>8} | {'Rate (STB/day)':>15} | {'% of Max':>10}")
        print("-" * 40)
        max_qo_s = None
        for s_test in s_values:
            qo_s = await client.call_tool(
                "oil_rate_radial",
                {
                    "pi": pi,
                    "pb": pb,
                    "api": api,
                    "degf": degf,
                    "sg_g": sg_g,
                    "psd": pwf_test,
                    "h": h,
                    "k": k,
                    "s": s_test,
                    "re": re,
                    "rw": rw,
                    "rsb": rsb,
                    "vogel": False,
                },
            )
            qo_val = qo_s["value"]
            if isinstance(qo_val, list):
                qo_val = qo_val[0]
            if max_qo_s is None:
                max_qo_s = qo_val
            pct = (qo_val / max_qo_s) * 100 if max_qo_s > 0 else 0
            print(f"{s_test:8.1f} | {qo_val:15.2f} | {pct:10.1f}%")

        # Step 4: Compare radial vs linear flow
        print("\nStep 4: Radial vs Linear Flow Comparison")
        print("-" * 80)
        area = 10000  # Cross-sectional area for linear flow (ft²)
        length = 1000  # Length for linear flow (ft)

        qo_radial = await client.call_tool(
            "oil_rate_radial",
            {
                "pi": pi,
                "pb": pb,
                "api": api,
                "degf": degf,
                "sg_g": sg_g,
                "psd": pwf_test,
                "h": h,
                "k": k,
                "s": s,
                "re": re,
                "rw": rw,
                "rsb": rsb,
                "vogel": False,
            },
        )

        qo_linear = await client.call_tool(
            "oil_rate_linear",
            {
                "pi": pi,
                "pb": pb,
                "api": api,
                "degf": degf,
                "sg_g": sg_g,
                "psd": pwf_test,
                "area": area,
                "length": length,
                "k": k,
                "rsb": rsb,
                "vogel": False,
            },
        )

        qo_r = qo_radial["value"]
        qo_l = qo_linear["value"]
        if isinstance(qo_r, list):
            qo_r = qo_r[0]
        if isinstance(qo_l, list):
            qo_l = qo_l[0]

        print(f"\nFlow Geometry Comparison at {pwf_test:.0f} psia BHFP:")
        print(f"{'Flow Type':>15} | {'Rate (STB/day)':>15}")
        print("-" * 35)
        print(f"{'Radial':>15} | {qo_r:15.2f}")
        print(f"{'Linear':>15} | {qo_l:15.2f}")
        print(f"{'Ratio (R/L)':>15} | {qo_r/qo_l if qo_l > 0 else 0:15.2f}")

        # Step 5: Vogel IPR for below bubble point
        print("\nStep 5: Vogel IPR (Below Bubble Point)")
        print("-" * 80)
        pwf_vogel = [pb * (1 - i / 10) for i in range(11)]  # From Pb to 0

        qo_vogel = await client.call_tool(
            "oil_rate_radial",
            {
                "pi": pi,
                "pb": pb,
                "api": api,
                "degf": degf,
                "sg_g": sg_g,
                "psd": pwf_vogel,
                "h": h,
                "k": k,
                "s": s,
                "re": re,
                "rw": rw,
                "rsb": rsb,
                "vogel": True,
            },
        )

        print(f"\nVogel IPR (Below Bubble Point):")
        print(f"{'Pwf (psia)':>12} | {'Pwf/Pb':>10} | {'Rate (STB/day)':>15}")
        print("-" * 45)
        for pwf, qo in zip(pwf_vogel, qo_vogel["value"]):
            ratio = pwf / pb if pb > 0 else 0
            print(f"{pwf:12.1f} | {ratio:10.3f} | {qo:15.2f}")

        print("\n" + "=" * 80)
        print("Well Performance Analysis completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(well_performance_analysis())


