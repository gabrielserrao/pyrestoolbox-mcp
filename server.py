#!/usr/bin/env python3
"""Entry point for pyResToolbox MCP server.

Run with:
    fastmcp run server.py

Or for HTTP:
    fastmcp run server.py --transport http --port 8000
"""

from pyrestoolbox_mcp import mcp

if __name__ == "__main__":
    # Run the MCP server
    # Default is STDIO transport for local Claude Desktop integration
    mcp.run()
