#!/usr/bin/env python3
"""Simple test to verify the MCP server works."""

import sys

try:
    from pyrestoolbox_mcp import mcp

    print("=" * 80)
    print("pyResToolbox MCP Server - Test")
    print("=" * 80)
    print(f"\nServer Name: {mcp.name}")
    print("\nServer imported and initialized successfully!")
    print("\nTo run the server, use:")
    print("  fastmcp run server.py")
    print("\nTo integrate with Claude Desktop, add to config:")
    print('  "pyrestoolbox": {')
    print('    "command": "fastmcp",')
    print('    "args": ["run", "/path/to/pyrestoolbox-mcp/server.py"]')
    print('  }')
    print("\n" + "=" * 80)
    print("Test PASSED!")
    print("=" * 80)
    sys.exit(0)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
