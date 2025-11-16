# pyResToolbox MCP Quick Start Guide

## Installation

### Using uv (Recommended)

1. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Navigate to the project directory:
```bash
cd /Users/gabrielseabra/Local/Playground/pyResToolbox-main/pyrestoolbox-mcp
```

3. Create virtual environment and install dependencies:
```bash
make uv-install
# Or manually:
uv venv
uv sync
```

### Using pip (Alternative)

1. Navigate to the project directory:
```bash
cd /Users/gabrielseabra/Local/Playground/pyResToolbox-main/pyrestoolbox-mcp
```

2. Install the package:
```bash
pip install -e .
```

## Running the Server

### Using uv (Recommended)

### Option 1: Run with FastMCP CLI (Default - STDIO)
```bash
make uv-server
# Or manually:
uv run fastmcp run server.py
```

### Option 2: Run as HTTP Server
```bash
uv run fastmcp run server.py --transport http --port 8000
```

### Option 3: Test the Server
```bash
make uv-test
# Or manually:
uv run python test_server.py
```

### Using pip (Alternative)

### Option 1: Run with FastMCP CLI (Default - STDIO)
```bash
make server
# Or manually:
fastmcp run server.py
```

### Option 2: Run as HTTP Server
```bash
fastmcp run server.py --transport http --port 8000
```

### Option 3: Test the Server
```bash
make test
# Or manually:
python test_server.py
```

## Integration with Claude Desktop

1. Locate your Claude Desktop config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the MCP server configuration:

**Using uv (Recommended):**
```json
{
  "mcpServers": {
    "pyrestoolbox": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/gabrielseabra/Local/Playground/pyResToolbox-main/pyrestoolbox-mcp",
        "fastmcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

**Using pip (Alternative):**
```json
{
  "mcpServers": {
    "pyrestoolbox": {
      "command": "fastmcp",
      "args": [
        "run",
        "/Users/gabrielseabra/Local/Playground/pyResToolbox-main/pyrestoolbox-mcp/server.py"
      ]
    }
  }
}
```

3. Restart Claude Desktop

4. The pyRestToolbox tools should now be available in Claude

## Available Tools

### Oil PVT
- `oil_bubble_point` - Calculate bubble point pressure
- `oil_solution_gor` - Calculate solution GOR (Rs)
- `oil_formation_volume_factor` - Calculate oil FVF (Bo)
- `oil_viscosity` - Calculate oil viscosity
- `oil_density` - Calculate oil density
- `oil_compressibility` - Calculate oil compressibility

### Gas PVT
- `gas_z_factor` - Calculate gas Z-factor
- `gas_critical_properties` - Calculate Tc and Pc
- `gas_formation_volume_factor` - Calculate gas FVF (Bg)
- `gas_viscosity` - Calculate gas viscosity
- `gas_density` - Calculate gas density
- `gas_compressibility` - Calculate gas compressibility

### Inflow Performance
- `oil_rate_radial` - Oil production rate (radial flow)
- `oil_rate_linear` - Oil production rate (linear flow)
- `gas_rate_radial` - Gas production rate (radial flow)
- `gas_rate_linear` - Gas production rate (linear flow)

### Resources
- `config://version` - Server version info
- `config://units` - Unit system documentation
- `config://methods` - Available calculation methods
- `config://constants` - Physical constants
- `help://overview` - Complete overview

## Example Usage in Claude

Once integrated, you can ask Claude:

> "Calculate the bubble point pressure for an oil with API 35, temperature 180 degF, solution GOR of 800 scf/stb, and gas gravity of 0.75"

> "Generate an IPR curve for a well with reservoir pressure 4000 psia, permeability 100 mD, and net pay 50 ft"

> "What is the gas Z-factor at 3500 psia and 180 degF for a gas with specific gravity 0.7?"

## Running Examples

Test the implementation with included examples:

### Using uv (Recommended)

```bash
cd examples
uv run python basic_usage.py
uv run python pvt_workflow.py
uv run python gas_properties_workflow.py
# etc.
```

### Using pip (Alternative)

```bash
cd examples
python basic_usage.py
python pvt_workflow.py
python gas_properties_workflow.py
# etc.
```

## Testing

### Using uv (Recommended)

Run the test suite:
```bash
uv run pytest
```

Run specific tests:
```bash
uv run pytest tests/test_oil_tools.py
uv run pytest tests/test_gas_tools.py
```

### Using pip (Alternative)

Run the test suite:
```bash
pytest
```

Run specific tests:
```bash
pytest tests/test_oil_tools.py
pytest tests/test_gas_tools.py
```

## Troubleshooting

### ImportError: cannot import name 'InMemoryTransport'
The FastMCP API has changed. Use `test_server.py` instead of the examples for now.

### Server not appearing in Claude Desktop
1. Check that the path in `claude_desktop_config.json` is correct
2. Restart Claude Desktop completely
3. Check Claude Desktop logs for errors

### Calculation errors
All inputs must use Field Units:
- Pressure: psia
- Temperature: degF
- API gravity: degrees
- Gas gravity: dimensionless (air=1)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples/](examples/) for workflow examples
- See [tests/](tests/) for usage patterns
- Explore the [CLAUDE.md](../CLAUDE.md) file for project context

## Support

For issues:
- MCP server: Create an issue in this repository
- pyResToolbox calculations: See main pyResToolbox documentation
- FastMCP framework: See FastMCP GitHub repository
