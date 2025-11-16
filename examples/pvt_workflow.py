"""Complete PVT workflow example.

This example demonstrates a complete PVT analysis workflow including
bubble point determination, PVT property calculations, and IPR generation.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def pvt_workflow():
    """Complete PVT analysis workflow."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Complete PVT Analysis Workflow")
        print("=" * 80)

        # Reservoir and fluid data
        api = 38.0
        degf = 175.0
        sg_g = 0.68
        rsb = 750.0

        print("\nReservoir Fluid Properties:")
        print("-" * 80)
        print(f"Oil API Gravity: {api:.1f} degrees")
        print(f"Temperature: {degf:.1f} degF")
        print(f"Gas Specific Gravity: {sg_g:.3f}")
        print(f"Solution GOR at Pb: {rsb:.1f} scf/stb")

        # Step 1: Calculate bubble point
        print("\nStep 1: Calculate Bubble Point Pressure")
        print("-" * 80)
        pb_result = await client.call_tool(
            "oil_bubble_point",
            {
                "api": api,
                "degf": degf,
                "rsb": rsb,
                "sg_g": sg_g,
                "method": "VALMC",
            },
        )
        pb = pb_result["value"]
        print(f"Bubble Point: {pb:.2f} psia (using {pb_result['method']} correlation)")

        # Step 2: Generate pressure array for analysis
        print("\nStep 2: Generate PVT Properties Table")
        print("-" * 80)
        pressures = [500, 1000, 1500, 2000, 2500, 3000, 3500, pb, pb + 500, pb + 1000]
        pressures.sort()

        # Calculate Rs at all pressures
        rs_result = await client.call_tool(
            "oil_solution_gor",
            {
                "api": api,
                "degf": degf,
                "p": pressures,
                "sg_g": sg_g,
                "pb": pb,
                "rsb": rsb,
                "method": "VELAR",
            },
        )

        # Calculate Bo at all pressures
        bo_result = await client.call_tool(
            "oil_formation_volume_factor",
            {
                "api": api,
                "degf": degf,
                "p": pressures,
                "sg_g": sg_g,
                "pb": pb,
                "rs": rs_result["value"],
                "rsb": rsb,
                "method": "MCAIN",
            },
        )

        # Calculate viscosity
        uo_result = await client.call_tool(
            "oil_viscosity",
            {
                "api": api,
                "degf": degf,
                "p": pressures,
                "pb": pb,
                "rs": rs_result["value"],
                "rsb": rsb,
                "method": "BR",
            },
        )

        # Calculate density
        deno_result = await client.call_tool(
            "oil_density",
            {
                "p": pressures,
                "api": api,
                "degf": degf,
                "rs": rs_result["value"],
                "sg_g": sg_g,
                "bo": bo_result["value"],
            },
        )

        # Print PVT table
        print("\n" + "=" * 90)
        print(
            f"{'P (psia)':>10} | {'Rs (scf/stb)':>12} | {'Bo (rb/stb)':>12} | "
            f"{'Visc (cP)':>10} | {'Den (lb/cf)':>11}"
        )
        print("=" * 90)
        for i, p in enumerate(pressures):
            rs = rs_result["value"][i]
            bo = bo_result["value"][i]
            uo = uo_result["value"][i]
            deno = deno_result["value"][i]
            marker = " <- Pb" if abs(p - pb) < 1.0 else ""
            print(
                f"{p:10.1f} | {rs:12.2f} | {bo:12.4f} | "
                f"{uo:10.4f} | {deno:11.3f}{marker}"
            )
        print("=" * 90)

        # Step 3: Generate IPR curve
        print("\nStep 3: Generate Inflow Performance Relationship (IPR)")
        print("-" * 80)

        # Well and reservoir parameters
        pi = pb + 1000  # Reservoir pressure
        h = 75.0  # Net pay thickness
        k = 150.0  # Permeability
        s = -2.0  # Skin (stimulated well)
        re = 1500.0  # Drainage radius
        rw = 0.5  # Wellbore radius

        print(f"Reservoir Pressure: {pi:.1f} psia")
        print(f"Net Pay: {h:.1f} ft")
        print(f"Permeability: {k:.1f} mD")
        print(f"Skin: {s:.1f}")
        print(f"Drainage Radius: {re:.1f} ft")
        print(f"Wellbore Radius: {rw:.2f} ft")

        # Generate IPR
        pwf_values = [pi * (1 - i / 10) for i in range(11)]  # 0% to 100% drawdown

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

        print("\n" + "=" * 60)
        print(f"{'Pwf (psia)':>12} | {'Drawdown (psi)':>15} | {'Rate (STB/day)':>15}")
        print("=" * 60)
        for pwf, qo in zip(pwf_values, qo_result["value"]):
            drawdown = pi - pwf
            print(f"{pwf:12.1f} | {drawdown:15.1f} | {qo:15.2f}")
        print("=" * 60)

        max_rate = max(qo_result["value"])
        print(f"\nMaximum Rate (AOF): {max_rate:.2f} STB/day")
        print(
            f"Productivity Index: {max_rate/pi:.2f} STB/day/psi (based on reservoir pressure)"
        )

        print("\n" + "=" * 80)
        print("PVT Workflow completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(pvt_workflow())
