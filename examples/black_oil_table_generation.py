"""Black oil table generation example.

This example demonstrates generation of comprehensive black oil tables
for reservoir simulation using make_bot_og function.
Note: This example uses direct pyrestoolbox calls as make_bot_og
may not be available as an MCP tool.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import pyrestoolbox
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pyrestoolbox import oil
from pyrestoolbox.classes import *


async def black_oil_table_example():
    """Generate black oil tables for reservoir simulation."""

    print("=" * 80)
    print("Black Oil Table Generation Example")
    print("=" * 80)

    # Reservoir and fluid properties
    pi = 4000.0  # Initial reservoir pressure (psia)
    api = 38.0  # Oil API gravity
    degf = 175.0  # Reservoir temperature (degF)
    sg_g = 0.68  # Gas specific gravity
    pmax = 5000.0  # Maximum pressure for table
    pb = 3500.0  # Bubble point pressure (psia)
    rsb = 750.0  # Solution GOR at bubble point (scf/stb)
    nrows = 50  # Number of table rows

    print("\nReservoir Fluid Properties:")
    print("-" * 80)
    print(f"Initial Pressure: {pi:.1f} psia")
    print(f"Oil API Gravity: {api:.1f} degrees")
    print(f"Temperature: {degf:.1f} degF")
    print(f"Gas Specific Gravity: {sg_g:.3f}")
    print(f"Bubble Point: {pb:.1f} psia")
    print(f"Solution GOR at Pb: {rsb:.1f} scf/stb")

    # Generate black oil table
    print("\nGenerating Black Oil Table...")
    print("-" * 80)

    results = oil.make_bot_og(
        pi=pi,
        api=api,
        degf=degf,
        sg_g=sg_g,
        pmax=pmax,
        pb=pb,
        rsb=rsb,
        pmin=25,
        nrows=nrows,
        wt=0,  # Salt wt%
        ch4_sat=0,  # Methane saturation
        comethod=co_method.EXPLT,
        zmethod=z_method.DAK,
        rsmethod=rs_method.VELAR,
        cmethod=c_method.PMC,
        denomethod=deno_method.SWMH,
        bomethod=bo_method.MCAIN,
        pbmethod=pb_method.VALMC,
        export=False,
        pvto=False,
    )

    # Display results
    df = results["bot"]
    print(f"\nGenerated Table with {len(df)} rows")
    print("\nBlack Oil Table (first 10 rows):")
    print("=" * 100)
    print(df.head(10).to_string(index=False))

    print("\n\nTable Summary:")
    print("-" * 80)
    print(f"Stock Tank Oil Density: {results['deno']:.4f} lb/cuft")
    print(f"Stock Tank Gas Density: {results['deng']:.4f} lb/cuft")
    print(f"Water Density at Pi: {results['denw']:.4f} lb/cuft")
    print(f"Water Compressibility at Pi: {results['cw']:.2e} 1/psi")
    print(f"Water Viscosity at Pi: {results['uw']:.4f} cP")
    print(f"Bubble Point Pressure: {results['pb']:.2f} psia")
    print(f"Solution GOR at Pb: {results['rsb']:.2f} scf/stb")
    print(f"Rsb Scaling Factor: {results['rsb_scale']:.6f}")

    # Generate PVTO format
    print("\n\nGenerating PVTO Format Table...")
    print("-" * 80)

    results_pvto = oil.make_bot_og(
        pi=pi,
        api=api,
        degf=degf,
        sg_g=sg_g,
        pmax=pmax,
        pb=pb,
        rsb=rsb,
        pmin=25,
        nrows=nrows,
        wt=0,
        ch4_sat=0,
        comethod=co_method.EXPLT,
        zmethod=z_method.DAK,
        rsmethod=rs_method.VELAR,
        cmethod=c_method.PMC,
        denomethod=deno_method.SWMH,
        bomethod=bo_method.MCAIN,
        pbmethod=pb_method.VALMC,
        export=True,
        pvto=True,
    )

    print("PVTO table generated and exported to PVTO.INC")
    print(f"Undersaturated data available: {len(results_pvto['usat']) > 0}")

    # Display pressure vs properties
    print("\n\nPressure vs Properties Summary:")
    print("-" * 80)
    print(
        f"{'P (psia)':>10} | {'Rs (mscf/stb)':>15} | {'Bo (rb/stb)':>12} | "
        f"{'uo (cP)':>10} | {'Co (1/psi)':>12}"
    )
    print("=" * 70)
    for idx in [0, len(df) // 4, len(df) // 2, 3 * len(df) // 4, len(df) - 1]:
        row = df.iloc[idx]
        marker = " <- Pb" if abs(row["Pressure (psia)"] - pb) < 1.0 else ""
        print(
            f"{row['Pressure (psia)']:10.1f} | {row['Rs (mscf/stb)']:15.4f} | "
            f"{row['Bo (rb/stb)']:12.4f} | {row['uo (cP)']:10.4f} | "
            f"{row['Co (1/psi)']:12.2e}{marker}"
        )

    print("\n" + "=" * 80)
    print("Black Oil Table Generation completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(black_oil_table_example())


