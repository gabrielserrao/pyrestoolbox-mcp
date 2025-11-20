"""Relative permeability table generation example.

This example demonstrates generation of relative permeability tables
for reservoir simulation using Corey and LET correlations.
"""

import asyncio
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def rel_perm_examples():
    """Generate relative permeability tables for different scenarios."""

    # Client context

    async with Client(mcp) as client:
        print("=" * 80)
        print("Relative Permeability Table Generation Examples")
        print("=" * 80)

        # Example 1: Water-Oil (SWOF) with Corey correlation
        print("\nExample 1: Water-Oil Relative Permeability (SWOF) - Corey")
        print("-" * 80)
        swof_corey = await client.call_tool(
            "generate_rel_perm_table",
            {
                "rows": 25,
                "krtable": "SWOF",
                "krfamily": "COR",
                "kromax": 1.0,
                "krwmax": 0.25,
                "swc": 0.15,
                "swcr": 0.20,
                "sorw": 0.15,
                "no": 2.5,
                "nw": 1.5,
            },
        )
        print(f"Table Type: {swof_corey['table_type']}")
        print(f"Correlation: {swof_corey['correlation']}")
        print(f"Number of Rows: {swof_corey['rows']}")
        print(f"\nFirst 5 rows:")
        print(f"{'Sw':>8} | {'Krwo':>8} | {'Krow':>8}")
        print("-" * 30)
        for row in swof_corey["table"][:5]:
            print(f"{row['Sw']:8.4f} | {row['Krwo']:8.4f} | {row['Krow']:8.4f}")

        # Example 2: Gas-Oil (SGOF) with LET correlation
        print("\nExample 2: Gas-Oil Relative Permeability (SGOF) - LET")
        print("-" * 80)
        sgof_let = await client.call_tool(
            "generate_rel_perm_table",
            {
                "rows": 30,
                "krtable": "SGOF",
                "krfamily": "LET",
                "kromax": 1.0,
                "krgmax": 1.0,
                "swc": 0.20,
                "sorg": 0.15,
                "Lo": 2.5,
                "Eo": 1.25,
                "To": 1.75,
                "Lg": 1.2,
                "Eg": 1.5,
                "Tg": 2.0,
            },
        )
        print(f"Table Type: {sgof_let['table_type']}")
        print(f"Correlation: {sgof_let['correlation']}")
        print(f"Number of Rows: {sgof_let['rows']}")
        print(f"\nFirst 5 rows:")
        print(f"{'Sg':>8} | {'Krgo':>8} | {'Krog':>8}")
        print("-" * 30)
        for row in sgof_let["table"][:5]:
            print(f"{row['Sg']:8.4f} | {row['Krgo']:8.4f} | {row['Krog']:8.4f}")

        # Example 3: Three-phase (SGWFN) with Corey
        print("\nExample 3: Three-Phase Gas-Water (SGWFN) - Corey")
        print("-" * 80)
        sgwfn = await client.call_tool(
            "generate_rel_perm_table",
            {
                "rows": 25,
                "krtable": "SGWFN",
                "krfamily": "COR",
                "krgmax": 0.8,
                "krwmax": 0.3,
                "swc": 0.15,
                "sgcr": 0.05,
                "ng": 2.0,
                "nw": 1.8,
            },
        )
        print(f"Table Type: {sgwfn['table_type']}")
        print(f"Correlation: {sgwfn['correlation']}")
        print(f"Number of Rows: {sgwfn['rows']}")
        print(f"\nFirst 5 rows:")
        print(f"{'Sg':>8} | {'Krgw':>8} | {'Krwg':>8}")
        print("-" * 30)
        for row in sgwfn["table"][:5]:
            print(f"{row['Sg']:8.4f} | {row['Krgw']:8.4f} | {row['Krwg']:8.4f}")

        # Example 4: Compare Corey vs LET for same endpoints
        print("\nExample 4: Corey vs LET Comparison (SWOF)")
        print("-" * 80)
        print("Same saturation endpoints, different correlation methods:")
        print(f"{'Sw':>8} | {'Krwo (Corey)':>15} | {'Krwo (LET)':>15}")
        print("-" * 45)

        # Generate both tables
        corey_table = await client.call_tool(
            "generate_rel_perm_table",
            {
                "rows": 20,
                "krtable": "SWOF",
                "krfamily": "COR",
                "kromax": 1.0,
                "krwmax": 0.3,
                "swc": 0.15,
                "sorw": 0.20,
                "no": 2.0,
                "nw": 1.5,
            },
        )

        let_table = await client.call_tool(
            "generate_rel_perm_table",
            {
                "rows": 20,
                "krtable": "SWOF",
                "krfamily": "LET",
                "kromax": 1.0,
                "krwmax": 0.3,
                "swc": 0.15,
                "sorw": 0.20,
                "Lw": 2.0,
                "Ew": 1.0,
                "Tw": 1.5,
                "Lo": 2.0,
                "Eo": 1.0,
                "To": 1.5,
            },
        )

        # Compare at selected saturations
        for i in [0, 5, 10, 15, 19]:
            sw_corey = corey_table["table"][i]["Sw"]
            krw_corey = corey_table["table"][i]["Krwo"]
            krw_let = let_table["table"][i]["Krwo"]
            print(f"{sw_corey:8.4f} | {krw_corey:15.4f} | {krw_let:15.4f}")

        print("\n" + "=" * 80)
        print("Relative Permeability Examples completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(rel_perm_examples())


