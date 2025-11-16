"""Basic usage examples for pyResToolbox MCP server.

This example demonstrates how to use the MCP server for basic PVT calculations.
"""

import asyncio
import json
from fastmcp.client import Client
from pyrestoolbox_mcp import mcp


async def main():
    """Run basic PVT calculation examples."""

    async with Client(mcp) as client:
        print("=" * 80)
        print("pyResToolbox MCP Server - Basic Usage Examples")
        print("=" * 80)

        # Example 1: Calculate bubble point pressure
        print("\n1. Calculate Bubble Point Pressure")
        print("-" * 80)
        pb_result = await client.call_tool(
            "oil_bubble_point",
            {
                "request": {
                    "api": 35.0,
                    "degf": 180.0,
                    "rsb": 800.0,
                    "sg_g": 0.75,
                    "method": "VALMC",
                }
            },
        )
        pb_data = json.loads(pb_result.content[0].text)
        print(f"Bubble Point: {pb_data['value']:.2f} {pb_data['units']}")
        print(f"Method: {pb_data['method']}")

        # Example 2: Calculate gas Z-factor
        print("\n2. Calculate Gas Z-Factor")
        print("-" * 80)
        z_result = await client.call_tool(
            "gas_z_factor",
            {
                "request": {
                    "sg": 0.7,
                    "degf": 180.0,
                    "p": 3500.0,
                    "h2s": 0.0,
                    "co2": 0.0,
                    "n2": 0.0,
                    "method": "DAK",
                }
            },
        )
        z_data = json.loads(z_result.content[0].text)
        print(f"Z-Factor: {z_data['value']:.4f}")
        print(f"Method: {z_data['method']}")

        # Example 3: Calculate oil solution GOR at a single pressure
        print("\n3. Calculate Oil Solution GOR")
        print("-" * 80)
        rs_result = await client.call_tool(
            "oil_solution_gor",
            {
                "request": {
                    "api": 35.0,
                    "degf": 180.0,
                    "p": 3000.0,
                    "sg_g": 0.75,
                    "pb": 3456.7,
                    "rsb": 800.0,
                    "method": "VELAR",
                }
            },
        )
        rs_data = json.loads(rs_result.content[0].text)
        print(f"Solution GOR at 3000 psia: {rs_data['value']:.2f} {rs_data['units']}")
        print(f"Method: {rs_data['method']}")

        # Example 4: Calculate oil production rate
        print("\n4. Calculate Oil Production Rate (Radial Flow)")
        print("-" * 80)
        qo_result = await client.call_tool(
            "oil_rate_radial",
            {
                "request": {
                    "pi": 4000.0,
                    "pb": 3456.7,
                    "api": 35.0,
                    "degf": 180.0,
                    "sg_g": 0.75,
                    "psd": 1500.0,
                    "h": 50.0,
                    "k": 100.0,
                    "s": 0.0,
                    "re": 1000.0,
                    "rw": 0.5,
                    "rsb": 800.0,
                    "vogel": False,
                }
            },
        )
        qo_data = json.loads(qo_result.content[0].text)
        print(f"Oil Rate: {qo_data['value']:.2f} {qo_data['units']}")
        print(f"Method: {qo_data['method']}")

        # Example 5: Access configuration resources
        print("\n5. Access Server Configuration")
        print("-" * 80)
        version = await client.read_resource("config://version")
        print("Server Version Info:")
        print(version[0].text)

        print("\n" + "=" * 80)
        print("Examples completed successfully!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
