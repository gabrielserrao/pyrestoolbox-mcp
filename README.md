<div align="center">

# pyResToolbox MCP Server

### Bring Reservoir Engineering Calculations to AI

**Power your AI assistants with industry-standard petroleum engineering calculations**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-47%2F47%20passing-brightgreen.svg)](TEST_RESULTS.md)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-purple.svg)](https://github.com/jlowin/fastmcp)
[![Production Ready](https://img.shields.io/badge/production-ready-brightgreen.svg)](PRODUCTION_READY.md)

[![Model Context Protocol](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Built with pyResToolbox](https://img.shields.io/badge/Built%20with-pyResToolbox-orange.svg)](https://github.com/mwburgoyne/pyResToolbox)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?logo=buy-me-a-coffee)](https://buymeacoffee.com/gabrielsero)

**[Quick Start](#quick-start)** • **[Features](#what-can-you-do)** • **[Examples](#example-queries-for-claude)** • **[Documentation](#architecture)** • **[Contributing](#contributing)**

---

### 47 Production-Ready Tools | Field Units | Zero Configuration

**PVT Analysis** • **Well Performance** • **Simulation Support** • **Brine Properties** • **Heterogeneity Analysis**

---

</div>

A production-ready [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that gives AI agents like Claude access to the comprehensive reservoir engineering library [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox). Now Claude can perform sophisticated PVT calculations, well performance analysis, and reservoir simulation tasks through natural conversation.

![pyResToolbox MCP Demo](https://img.shields.io/badge/demo-coming_soon-blue.svg)

---

<div align="center">

## ☕ Support This Project

If you find this project useful, consider buying me a coffee! Your support helps maintain and improve this open-source tool.

<a href="https://buymeacoffee.com/gabrielsero" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >
</a>

</div>

---

## What is This?

This MCP server bridges the gap between AI assistants and petroleum engineering workflows. Instead of manually calculating reservoir properties or writing complex scripts, you can simply ask Claude:

> *"Calculate the bubble point pressure for API 35° oil at 180°F with solution GOR of 800 scf/stb and gas gravity 0.75 using the Valko-McCain correlation"*

> *"Generate an IPR curve for my well with Pi=4000 psia, Pb=3500 psia, API 38°, 175°F, pay thickness 75 ft, permeability 150 mD"*

> *"Create a black oil table for simulation with pressures from 500 to 5000 psia"*

Claude will execute the calculations using industry-standard correlations and return accurate, formatted results.

### Built On
- **[pyResToolbox](https://github.com/mwburgoyne/pyResToolbox)** by Mark Burgoyne - Comprehensive Python library for reservoir engineering calculations
- **[FastMCP](https://github.com/jlowin/fastmcp)** - Modern Python framework for building MCP servers
- **[Model Context Protocol](https://modelcontextprotocol.io/)** by Anthropic - Standard for AI-application integration

### Key Features

- **47 Production-Ready Tools** - All tools tested and validated
- **Industry-Standard Correlations** - Standing, Valko-McCain, Velarde, DAK, Beggs-Robinson, Corey, LET, and more
- **Field Units** - Uses familiar oilfield units (psia, °F, STB/day, MSCF/day)
- **Array Support** - Calculate properties at multiple pressures simultaneously
- **Zero Configuration** - Works out of the box with Claude Desktop
- **GPL-3.0 Licensed** - Free and open source

---

## Quick Start

### Installation

**Prerequisites:** Python 3.10+ (UV package manager recommended but optional)

```bash
# 1. Clone the repository
git clone https://github.com/gabrielserrao/pyrestoolbox-mcp.git
cd pyrestoolbox-mcp

# 2. Install UV (optional but 10-100x faster than pip)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Setup and test
make uv-install    # Creates venv and installs dependencies
make uv-test       # Verifies all 47 tools work correctly
```

### Connect to Claude Desktop

Add this to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pyrestoolbox": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/pyrestoolbox-mcp",
        "fastmcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/pyrestoolbox-mcp` with your actual installation path.

**Restart Claude Desktop** and you're ready to go!

### Your First Query

Open Claude Desktop and try:

> "What's the bubble point pressure for a 35° API oil at 180°F with 800 scf/stb solution GOR and 0.75 gas gravity?"

Claude will use the `oil_bubble_point` tool and return results like:

```
Bubble Point Pressure: 3,456.7 psia
Method: Valko-McCain (VALMC)
Inputs: API=35°, T=180°F, Rs=800 scf/stb, SG_gas=0.75
```

---

## What Can You Do?

### Oil PVT Analysis
- Calculate bubble point pressure (Standing, Valko-McCain, Velarde)
- Solution GOR, formation volume factor, viscosity, density, compressibility
- Generate comprehensive black oil tables for simulators

### Gas PVT Analysis
- Z-factor calculations (DAK, Hall-Yarborough, WYW, Burrows)
- Critical properties with contaminants (CO₂, H₂S, N₂, H₂)
- Gas viscosity, density, compressibility, pseudopressure
- Formation volume factors

### Well Performance & IPR
- Oil and gas production rates (radial and linear flow)
- IPR curve generation for vertical and horizontal wells
- Vogel IPR for pressures below bubble point
- Sensitivity analysis for permeability, skin, reservoir pressure

### Reservoir Simulation Support
- Relative permeability tables (SWOF, SGOF, SGWFN)
- Corey and LET correlations
- Van Everdingen & Hurst aquifer influence functions (AQUTAB)
- Rachford-Rice flash calculations for phase behavior

### Advanced Calculations
- Brine properties (methane and CO₂ saturated)
- CO₂ sequestration studies
- Reservoir heterogeneity analysis (Lorenz coefficient, beta parameter)
- Layer permeability distributions
- Component library (critical properties for 100+ hydrocarbons)

### Configuration & Help
- Query available calculation methods and correlations
- Access unit system documentation
- Get physical constants
- Comprehensive usage guides

---

## Example Queries for Claude

### Basic PVT Calculations
```
"Calculate Z-factor for gas with SG 0.7 at 3500 psia and 180°F using DAK method"

"What's the oil formation volume factor for 38° API oil at 3000 psia, 175°F with Rs=600?"

"Compare bubble point pressures using Standing, Valko-McCain, and Velarde for 35° API oil"
```

### Well Performance Analysis
```
"Generate IPR curve for well: Pi=4000 psia, Pb=3500 psia, API 38, T=175°F,
 h=75 ft, k=150 mD, skin=-2, re=1500 ft, rw=0.5 ft"

"Calculate oil production rate at 2000 psia flowing pressure for the same well"

"Show me how permeability affects production - test 50, 100, 150, 200, 250 mD"
```

### Simulation Preparation
```
"Generate a SWOF relative permeability table using Corey correlation with 25 rows,
 kromax=1.0, krwmax=0.25, swc=0.15, sorw=0.15, no=2.5, nw=1.5"

"Create aquifer influence functions for dimensionless radius 10.0"

"Generate black oil table from 500 to 5000 psia for 38° API oil at 175°F"
```

### Reservoir Heterogeneity
```
"Convert Lorenz coefficient 0.5 to Dykstra-Parsons beta"

"Generate layered permeability distribution for Lorenz coefficient 0.6,
 10 layers, average permeability 100 mD"
```

### Multi-Step Workflows
```
"Perform complete reservoir analysis: Calculate bubble point, generate PVT table,
 create IPR curve, and analyze well performance for 38° API oil at 175°F with
 initial pressure 4000 psia"

"Design a well completion: Calculate optimal flowing pressure, generate IPR,
 and compare different skin factors"

"Evaluate a gas reservoir: Calculate critical properties, generate IPR,
 and compare different Z-factor methods"
```

### Advanced Queries

#### Comprehensive PVT Workflows
```
"Generate a complete PVT table for API 38 oil at 175°F with gas gravity 0.68
 and solution GOR 750 scf/stb. Include pressures from 500 to 4000 psia and
 show Rs, Bo, viscosity, and density"

"Compare bubble point pressures using Standing, Valko-McCain, and Velarde
 correlations for API 35 oil at 180°F with GOR 800 scf/stb"

"Calculate PVT properties at multiple pressures: 1000, 2000, 3000, and 4000 psia
 for API 38 oil at 175°F"
```

#### Gas Analysis
```
"Calculate the critical properties (Tc and Pc) for a gas with specific gravity 0.7
 containing 2% CO2, 1% H2S, and 3% N2"

"Compare Z-factors using DAK, HY, and WYW methods for a gas at 3500 psia and 180°F"

"Calculate gas pseudopressure from 1000 to 3500 psia for a gas with SG 0.7 at 180°F"
```

#### Well Performance & IPR
```
"Generate an IPR curve for an oil well with reservoir pressure 4000 psia,
 bubble point 3500 psia, API 38 oil at 175°F. Well has 75 ft net pay,
 150 mD permeability, skin -2, drainage radius 1500 ft"

"What's the oil production rate at 2000 psia flowing pressure for a well with
 Pi=4000 psia, Pb=3500 psia, API 35, 180°F, 50 ft pay, 100 mD permeability?"

"Generate a Vogel IPR curve for pressures below bubble point for API 38 oil"
```

#### Sensitivity Analysis
```
"How does oil rate change with permeability? Test values from 50 to 250 mD"

"What's the impact of skin factor on production? Compare rates for skin values
 from -5 to +10"

"Analyze the effect of net pay thickness on production rate: test 25, 50, 75,
 and 100 ft"

"How does reservoir pressure depletion affect production? Calculate rates at
 4000, 3500, 3000, and 2500 psia"
```

#### Brine & CO₂ Sequestration
```
"Calculate brine properties for fresh water at 3000 psia and 175°F"

"What are the properties of saline brine (5% NaCl) at reservoir conditions:
 3000 psia, 175°F?"

"Calculate CO₂-brine mutual solubility at 3000 psia and 180°F with salinity
 50000 ppm"

"Compare brine properties with and without CO₂ saturation at sequestration conditions"
```

#### Reservoir Heterogeneity
```
"Convert Lorenz coefficient 0.5 to Dykstra-Parsons beta parameter"

"Calculate Lorenz coefficient from production logging data: flow fractions
 [0.45, 0.25, 0.15, 0.10, 0.05] and permeability fractions [0.30, 0.25, 0.20, 0.15, 0.10]"

"Generate a layered permeability distribution for Lorenz coefficient 0.5,
 10 layers, average permeability 100 mD"
```

#### Phase Behavior & Flash Calculations
```
"Solve Rachford-Rice flash for a mixture with compositions [0.5, 0.3, 0.2]
 and K-values [2.5, 1.8, 0.6]"

"Calculate vapor-liquid equilibrium for a three-component system"
```

#### Component Library
```
"What are the critical properties for methane?"

"Get critical temperature and pressure for ethane, propane, and butane"

"What's the molecular weight of n-heptane?"
```

#### Economic & Optimization
```
"What's the optimal flowing pressure to maximize production? Generate IPR
 and find the sweet spot"

"Compare production rates for stimulated (skin -2) vs damaged (skin +5) wells"

"Analyze the impact of reservoir pressure depletion on well performance over time"
```

#### Comparison & Benchmarking
```
"Compare Standing vs Valko-McCain vs Velarde bubble point correlations for the same oil"

"Compare DAK vs HY vs WYW Z-factor methods and their impact on gas rate calculations"

"Compare radial vs linear flow geometries for the same reservoir properties"
```

#### Educational Queries
```
"Explain what bubble point pressure means and calculate it for API 35 oil"

"What's the difference between solution GOR and producing GOR? Calculate both"

"How does gas gravity affect Z-factor? Show me calculations for different gravities"

"Explain Lorenz coefficient and calculate it for a heterogeneous reservoir"
```

#### Troubleshooting & Validation
```
"Validate my PVT data: bubble point 3500 psia, API 38, 175°F, GOR 750 scf/stb -
 does this make sense?"

"Check if my gas composition is realistic: SG 0.7 with 5% CO2, 3% H2S, 2% N2"

"Verify my well performance calculation: Are these rates reasonable for the
 given reservoir properties?"
```

### Tips for Better Queries

1. **Be Specific** - Include all relevant parameters (API, temperature, pressure, etc.)
2. **Specify Methods** - Mention which correlation you want (VALMC, DAK, Corey, LET, etc.)
3. **Include Units** - Always specify units (psia, degF, mD, ft, etc.)
4. **Ask for Comparisons** - Request comparisons between methods or scenarios
5. **Request Tables** - Ask for tabulated results when you need multiple values
6. **Follow-up Questions** - Build on previous answers for complex workflows

---

## Unit System

All calculations use **Field Units (US Oilfield)** per industry standard:

| Property | Unit | Example |
|----------|------|---------|
| Pressure | psia | 3000 psia |
| Temperature | °F | 180°F |
| Permeability | mD | 100 mD |
| Pay Thickness | ft | 50 ft |
| Viscosity | cP | 0.85 cP |
| Oil Rate | STB/day | 542 STB/day |
| Gas Rate | MSCF/day | 1250 MSCF/day |
| Oil Gravity | API° or SG | 35° API |
| Gas Gravity | SG (air=1) | 0.75 |
| Solution GOR | scf/stb | 800 scf/stb |
| Oil FVF | rb/stb | 1.25 rb/stb |
| Gas FVF | rcf/scf | 0.0045 rcf/scf |
| Compressibility | 1/psi | 1.2×10⁻⁵ 1/psi |
| Density | lb/ft³ | 42.5 lb/ft³ |

Access complete unit documentation anytime by asking Claude: *"What units does pyRestToolbox use?"*

---

## Architecture

### Project Structure
```
pyrestoolbox-mcp/
├── src/pyrestoolbox_mcp/
│   ├── server.py              # Main MCP server (FastMCP)
│   ├── config.py              # Server configuration & constants
│   ├── tools/                 # 47 MCP tool implementations (~13,800 LOC)
│   │   ├── oil_tools.py       # 17 oil PVT tools
│   │   ├── gas_tools.py       # 11 gas PVT tools
│   │   ├── inflow_tools.py    # 4 well performance tools
│   │   ├── simtools_tools.py  # 3 simulation support tools
│   │   ├── brine_tools.py     # 2 brine property tools
│   │   ├── layer_tools.py     # 5 heterogeneity tools
│   │   └── library_tools.py   # 1 component library tool
│   ├── models/                # Pydantic validation models
│   │   ├── oil_models.py
│   │   ├── gas_models.py
│   │   ├── inflow_models.py
│   │   ├── simtools_models.py
│   │   ├── brine_models.py
│   │   ├── layer_models.py
│   │   └── library_models.py
│   └── resources/             # MCP configuration resources
│       └── config_resources.py
├── tests/                     # Test suite (pytest + custom)
│   ├── test_oil_tools.py
│   ├── test_gas_tools.py
│   └── conftest.py
├── examples/                  # 10 comprehensive workflow examples
│   ├── basic_usage.py
│   ├── pvt_workflow.py
│   ├── gas_well_analysis.py
│   └── ...
├── server.py                  # Entry point
├── pyproject.toml            # UV/pip configuration
├── Makefile                  # Development commands
├── Dockerfile                # Docker deployment
└── docker-compose.yml        # Multi-transport deployment
```

### How It Works

1. **FastMCP Server** - Handles MCP protocol communication (STDIO, HTTP, SSE)
2. **Pydantic Models** - Validate all inputs with descriptive error messages
3. **Tool Layer** - 47 functions wrapping pyrestoolbox calculations
4. **pyRestToolbox** - Performs actual reservoir engineering calculations
5. **Type Conversion** - Handles numpy/pandas/mpmath serialization for JSON

### Tool Categories

| Category | Count | Description |
|----------|-------|-------------|
| Oil PVT | 17 | Bubble point, Rs, Bo, viscosity, density, compressibility, black oil tables |
| Gas PVT | 11 | Z-factor, critical properties, Bg, viscosity, density, pseudopressure |
| Inflow | 4 | Oil/gas rates for radial/linear flow, IPR generation |
| Simulation | 3 | Relative permeability, aquifer functions, Rachford-Rice flash |
| Brine | 2 | CH₄ and CO₂ saturated brine properties |
| Heterogeneity | 5 | Lorenz coefficient, beta conversion, layer distributions |
| Library | 1 | Critical properties for 100+ components |
| Config | 4 | Units, methods, constants, help resources |

---

## Development

### Running Tests

```bash
# Quick validation (all 47 tools)
make uv-test
# or
uv run python test_tools.py

# Full pytest suite
uv run pytest

# With coverage report
uv run pytest --cov=pyrestoolbox_mcp --cov-report=html

# Specific test modules
uv run pytest tests/test_oil_tools.py
uv run pytest tests/test_gas_tools.py
```

See [TEST_RESULTS.md](TEST_RESULTS.md) for complete validation report.

### Running Examples

```bash
# Run all examples
make uv-examples

# Run specific example
make uv-example EXAMPLE=basic_usage.py
make uv-example EXAMPLE=gas_well_analysis.py

# Or manually
cd examples
uv run python basic_usage.py
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/

# Type checking (if mypy added)
uv run mypy src/
```

### Docker Deployment

```bash
# Build image
make docker-build

# Run HTTP server (port 8000)
make docker-up-http

# Run SSE server (port 8001)
make docker-up-sse

# View logs
make docker-logs

# Stop services
make docker-down
```

See [DOCKER.md](DOCKER.md) for complete Docker documentation.

### Adding New Tools

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed instructions. Quick overview:

1. **Define Pydantic Model** in `src/pyrestoolbox_mcp/models/`
2. **Implement Tool Function** in appropriate `src/pyrestoolbox_mcp/tools/` file
3. **Register Tool** in the module's `register_*_tools()` function
4. **Add Tests** to `test_tools.py` and appropriate pytest file
5. **Update Documentation** in README and examples

---

## Available Calculation Methods

### Oil Correlations

**Bubble Point Pressure**
- **VALMC** - Valko & McCain (2003) - *Recommended for most applications*
- **STAN** - Standing (1947) - *Classic correlation*
- **VELAR** - Velarde (1997) - *For specific regions*

**Solution GOR (Rs)**
- **VELAR** - Velarde (1997)
- **STAN** - Standing (1947)
- **VALMC** - Valko & McCain (2003)

**Formation Volume Factor (Bo)**
- **MCAIN** - McCain et al. (1988) - *Recommended*
- **STAN** - Standing (1947)

**Viscosity**
- **BR** - Beggs & Robinson (1975)

### Gas Correlations

**Z-Factor**
- **DAK** - Dranchuk & Abou-Kassem (1975) - *Recommended, most accurate*
- **HY** - Hall & Yarborough (1973) - *Fast, good for most conditions*
- **WYW** - Wang, Ye & Wu (2021) - *Latest, handles high pressure*
- **BUR** - Burrows (1981) - *Special applications*

**Critical Properties**
- **PMC** - Piper, McCain & Corredor (1993) - *Recommended*
- **SUT** - Sutton (1985)
- **BUR** - Burrows (1981)

**Viscosity**
- **LGE** - Lee, Gonzalez & Eakin (1966)

### Relative Permeability

**Curve Types**
- **COR** - Corey (1954) - *Power law, simple*
- **LET** - Lomeland, Ebeltoft & Thomas (2005) - *Flexible, complex shapes*

**Table Types**
- **SWOF** - Water-oil saturation functions
- **SGOF** - Gas-oil saturation functions
- **SGWFN** - Gas-water saturation functions (3-phase)

---

## Programmatic Usage

While this server is designed for Claude Desktop integration, you can also use it programmatically:

### Python Client

```python
import asyncio
from fastmcp.client import InMemoryTransport
from pyrestoolbox_mcp import mcp

async def calculate_pvt():
    transport = InMemoryTransport(mcp)

    async with transport.get_client() as client:
        # Calculate bubble point
        pb_result = await client.call_tool(
            "oil_bubble_point",
            {
                "api": 35.0,
                "degf": 180.0,
                "rsb": 800.0,
                "sg_g": 0.75,
                "method": "VALMC"
            }
        )
        pb = pb_result['value']
        print(f"Bubble Point: {pb:.2f} psia")

        # Calculate Rs at multiple pressures
        rs_result = await client.call_tool(
            "oil_solution_gor",
            {
                "api": 35.0,
                "degf": 180.0,
                "p": [1000, 2000, 3000, pb, 4000],
                "sg_g": 0.75,
                "pb": pb,
                "rsb": 800.0,
                "method": "VELAR"
            }
        )
        print(f"Rs values: {rs_result['value']}")

        # Access configuration resources
        methods = await client.read_resource("config://methods")
        print(f"Available methods:\n{methods.content}")

asyncio.run(calculate_pvt())
```

### HTTP/SSE Transport

```bash
# Start HTTP server
uv run fastmcp run server.py --transport http --port 8000

# Or using Docker
docker-compose --profile http up -d
```

Then connect using any MCP client or HTTP client supporting the MCP protocol.

---

## Troubleshooting

### Installation Issues

**"uv: command not found"**
- Close and reopen terminal after installing UV
- Verify: `uv --version`
- Alternative: Use pip instead (`pip install -e .`)

**"make: command not found" (Windows)**
- Use manual commands from Makefile
- Or install Make for Windows via Chocolatey: `choco install make`

**UV sync fails**
- Clear cache: `rm -rf .venv && make uv-install`
- Check Python version: `python --version` (needs 3.10+)

### Claude Desktop Integration

**Claude doesn't see the tools**
1. Verify absolute path in config (no `~`, use full path)
2. Completely restart Claude Desktop (Quit, not just close window)
3. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`
4. Test server manually: `make uv-server`
5. Ensure UV is in PATH (try `which uv` or `where uv`)

**Tools fail with errors**
- Verify all inputs use Field Units (psia, °F, ft, mD)
- Check parameter names match exactly (case-sensitive)
- Run validation: `uv run python test_tools.py`

### Runtime Issues

**Import errors**
```bash
# Reinstall dependencies
make uv-install
# or
uv sync --force
```

**Calculation errors**
- Check units (must be psia, °F, etc.)
- Verify inputs are realistic (e.g., API 10-50, temperatures 60-300°F)
- Some correlations have valid ranges - try different methods
- Check [pyResToolbox docs](https://github.com/mwburgoyne/pyResToolbox) for correlation limits

**Performance issues**
- Array calculations are optimized via numpy
- For large datasets, consider batching requests
- Docker deployment adds minimal overhead

### Getting Help

- Check [INTERESTING_QUERIES.md](INTERESTING_QUERIES.md) for query examples
- Review [examples/](examples/) directory for working code
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup
- Open an [issue](../../issues) for bugs or feature requests

---

## Contributing

Contributions are welcome! This project follows the GPL-3.0 license of the upstream pyResToolbox library.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** (follow code style guidelines)
4. **Test thoroughly** (`uv run python test_tools.py` - all 47 must pass)
5. **Format code** (`uv run black src/ tests/`)
6. **Commit** (`git commit -m 'Add amazing feature'`)
7. **Push** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

### Development Setup

```bash
git clone https://github.com/gabrielserrao/pyrestoolbox-mcp.git
cd pyrestoolbox-mcp
make uv-install
uv run python test_tools.py  # Verify all 47 tools pass
```

### Guidelines

- Use type hints for all function parameters and return values
- Write Google-style docstrings
- Add tests for all new tools
- Follow existing code structure
- Update documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## License

**GNU General Public License v3.0 (GPL-3.0)**

This MCP server is built on [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox), which is licensed under GPL-3.0. This project maintains full compliance with GPL-3.0 license terms.

**Key Points:**
- Free and open source software
- You may use, modify, and distribute under GPL-3.0 terms
- Any modifications must also be released under GPL-3.0
- No warranty provided (see LICENSE for details)
- Commercial use is permitted under GPL-3.0 terms

See [LICENSE](LICENSE) for complete license text.

---

## Project Status

| Aspect | Status | Details |
|--------|--------|---------|
| **Tests** | ![Tests](https://img.shields.io/badge/tests-47%2F47%20passing-brightgreen.svg) | 100% tool coverage |
| **Production** | ✅ Ready | All tools validated |
| **Documentation** | ✅ Complete | README, examples, guides |
| **License** | GPL-3.0 | Matches upstream |
| **Python** | 3.10+ | Type hints throughout |
| **Framework** | FastMCP 2.0+ | Modern MCP implementation |

See [PRODUCTION_READY.md](PRODUCTION_READY.md) for detailed verification results.

### Version History

**v1.0.0** (2024-11-15) - Initial production release
- 47 production-ready tools
- 100% test coverage
- Docker deployment support
- Comprehensive documentation
- GPL-3.0 license compliance

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

## Roadmap

### Planned Features
- [ ] Web UI for HTTP transport with interactive forms
- [ ] Additional workflow examples for common tasks
- [ ] Performance benchmarking suite
- [ ] Extended simulation tools (grid processing, ECLIPSE utilities)
- [ ] Jupyter notebook integration with examples
- [ ] API documentation site (Sphinx/MkDocs)
- [ ] Rate limiting and authentication for HTTP deployments
- [ ] Prometheus metrics export

See [open issues](../../issues) for full list of proposed features and known issues.

### Upstream Integration
We're exploring opportunities to contribute improvements back to [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox), including:
- Standalone `gas_grad2sg` implementation (bug fix)
- Enhanced type hints
- Additional validation utilities

---

## Related Projects

### Core Dependencies
- **[pyResToolbox](https://github.com/mwburgoyne/pyResToolbox)** - Reservoir engineering library by Mark Burgoyne
- **[FastMCP](https://github.com/jlowin/fastmcp)** - Python framework for MCP servers
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP specification by Anthropic

### Similar MCP Servers
- **[mcp-servers](https://github.com/modelcontextprotocol/servers)** - Official MCP server examples
- **[awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)** - Curated list of MCP servers

### Petroleum Engineering Tools
- **[PVTpy](https://github.com/aegis4048/PVTpy)** - PVT calculations in Python
- **[petbox](https://github.com/mwentzWW/petbox)** - Petroleum engineering toolbox

---

## Acknowledgments

This project wouldn't exist without:

- **Mark Burgoyne** - Creator of [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox), the foundation of this MCP server
- **Marvin AI Team** - Developers of [FastMCP](https://github.com/jlowin/fastmcp) framework
- **Anthropic** - For Claude and the [Model Context Protocol](https://modelcontextprotocol.io/) specification
- **The reservoir engineering community** - For developing and refining the correlations implemented in this project

Special thanks to all contributors who help improve this project!

---

## Citation

If you use this MCP server in academic or commercial work, please cite the original pyResToolbox library:

```bibtex
@software{pyrestoolbox,
  author = {Burgoyne, Mark W.},
  title = {pyResToolbox: A Collection of Reservoir Engineering Utilities},
  url = {https://github.com/mwburgoyne/pyResToolbox},
  version = {2.x},
  year = {2024}
}
```

For this MCP server:

```bibtex
@software{pyrestoolbox_mcp,
  author = {Serrao, Gabriel},
  title = {pyResToolbox MCP Server: AI-Powered Reservoir Engineering Calculations},
  url = {https://github.com/gabrielserrao/pyrestoolbox-mcp},
  version = {1.0.0},
  year = {2024},
  note = {Built on pyResToolbox by Mark W. Burgoyne}
}
```

---

## Support

### Getting Help

**For MCP server issues:**
- Check [Troubleshooting](#troubleshooting) section
- Review [examples/](examples/) directory
- Search [existing issues](../../issues)
- Open a [new issue](../../issues/new)

**For calculation accuracy or pyResToolbox features:**
- See [pyResToolbox documentation](https://github.com/mwburgoyne/pyResToolbox)
- Check [pyResToolbox issues](https://github.com/mwburgoyne/pyResToolbox/issues)

**For FastMCP framework:**
- See [FastMCP documentation](https://github.com/jlowin/fastmcp)

**For Model Context Protocol:**
- See [MCP specification](https://modelcontextprotocol.io/)
- Join [MCP Discord](https://discord.gg/anthropic) (if available)

### Community

- **Discussions:** [GitHub Discussions](../../discussions)
- **Issues:** [GitHub Issues](../../issues)
- **Pull Requests:** [Contributing Guide](CONTRIBUTING.md)

---

## Support & Star

<div align="center">

### ⭐ Star This Project

If you find this project useful, please give it a star on GitHub! Stars help others discover this project and motivate continued development.

### ☕ Buy Me a Coffee

Support the development and maintenance of this project:

<a href="https://buymeacoffee.com/gabrielsero" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >
</a>

Your support helps keep this project free and open source for the petroleum engineering community!

### 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=gabrielserrao/pyrestoolbox-mcp&type=Date)](https://star-history.com/#gabrielserrao/pyrestoolbox-mcp&Date)

</div>

---

<div align="center">

---

**Built with ❤️ for the petroleum engineering community**

**Created by [Gabriel Serrao](https://www.linkedin.com/in/gabriel-serrao-seabra/)**

---

[Report Bug](../../issues) · [Request Feature](../../issues) · [Documentation](.) · [Examples](examples/)

[![GitHub Stars](https://img.shields.io/github/stars/gabrielserrao/pyrestoolbox-mcp?style=social)](https://github.com/gabrielserrao/pyrestoolbox-mcp/stargazers)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/gabriel-serrao-seabra/)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-FFDD00?logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/gabrielsero)

</div>
