"""Main FastMCP Server for pyResToolbox."""

from fastmcp import FastMCP
from .config import SERVER_NAME, SERVER_VERSION, SERVER_DESCRIPTION

# Initialize FastMCP server
mcp = FastMCP(
    name=SERVER_NAME,
)

# Import and register resources
from .resources.config_resources import register_config_resources
register_config_resources(mcp)

# Import and register tools
from .tools.oil_tools import register_oil_tools
from .tools.gas_tools import register_gas_tools
from .tools.inflow_tools import register_inflow_tools
from .tools.simtools_tools import register_simtools_tools
from .tools.brine_tools import register_brine_tools
from .tools.layer_tools import register_layer_tools
from .tools.library_tools import register_library_tools

register_oil_tools(mcp)
register_gas_tools(mcp)
register_inflow_tools(mcp)
register_simtools_tools(mcp)
register_brine_tools(mcp)
register_layer_tools(mcp)
register_library_tools(mcp)

__all__ = ["mcp"]
