# pyResToolbox MCP Examples

This directory contains comprehensive examples demonstrating how to use the pyResToolbox MCP server for various reservoir engineering calculations.

## Examples Overview

### Basic Examples

- **basic_usage.py** - Simple examples of basic PVT calculations including bubble point, Z-factor, solution GOR, and oil production rate calculations.

- **pvt_workflow.py** - Complete PVT analysis workflow demonstrating bubble point determination, PVT property calculations at multiple pressures, and IPR generation.

### Advanced Examples

- **gas_properties_workflow.py** - Comprehensive gas PVT property calculations including Z-factor, viscosity, density, compressibility, and formation volume factor at multiple pressures. Also compares different Z-factor correlation methods.

- **gas_well_analysis.py** - Complete gas well performance analysis including IPR generation, Z-factor method comparison, linear flow analysis, and sensitivity to gas composition.

- **brine_properties_example.py** - Brine property calculations for various salinities, dissolved gas conditions, and pressure/temperature effects. Demonstrates methane-saturated and CO2-saturated brine calculations.

- **relative_permeability_tables.py** - Generation of relative permeability tables for reservoir simulation using Corey and LET correlations. Includes SWOF, SGOF, and SGWFN table types.

- **well_performance_analysis.py** - Comprehensive well performance analysis including IPR generation, sensitivity analysis (permeability, skin), radial vs linear flow comparison, and Vogel IPR for below bubble point conditions.

- **reservoir_heterogeneity.py** - Reservoir heterogeneity analysis including Lorenz coefficient calculations, beta parameter conversions, layer property generation, and flow fraction analysis.

- **component_library_example.py** - Access to the component library database for critical properties of hydrocarbon components. Demonstrates queries for light hydrocarbons, aromatics, non-hydrocarbons, and heavy components.

- **rachford_rice_flash.py** - Vapor-liquid equilibrium calculations using the Rachford-Rice equation. Includes binary systems, multi-component systems, near-critical conditions, and separator flash calculations.

- **black_oil_table_generation.py** - Generation of comprehensive black oil tables for reservoir simulation. Note: This example uses direct pyrestoolbox calls as `make_bot_og` may not be available as an MCP tool.

## Running Examples

All examples use the FastMCP InMemoryTransport for testing.

### Prerequisites

First, ensure you have `uv` installed. If not, install it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or using pip:
```bash
pip install uv
```

### Setup

Navigate to the project root and set up the environment with `uv`:

```bash
cd pyrestoolbox-mcp
make uv-install
# Or manually:
uv venv
uv sync
```

### Running Examples

#### Option 1: Using Makefile (Easiest)

From the project root:

```bash
# Run all examples
make uv-examples

# Run a specific example
make uv-example EXAMPLE=basic_usage.py
make uv-example EXAMPLE=gas_properties_workflow.py
```

#### Option 2: Using the run script

```bash
cd pyrestoolbox-mcp
./examples/run_examples.sh
```

#### Option 3: Using uv run directly

Activate the virtual environment and run examples:

```bash
# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run examples
cd examples
uv run python basic_usage.py
uv run python gas_properties_workflow.py
uv run python well_performance_analysis.py
```

Or use `uv run` directly without activating the venv:

```bash
cd pyrestoolbox-mcp/examples
uv run python basic_usage.py
uv run python gas_properties_workflow.py
uv run python well_performance_analysis.py
```

#### Option 4: Manual loop

You can run all examples in sequence:

```bash
cd pyrestoolbox-mcp/examples
for example in *.py; do
    if [ "$example" != "__init__.py" ]; then
        echo "Running $example..."
        uv run python "$example"
        echo ""
    fi
done
```

## Example Structure

Each example follows a similar structure:

1. **Setup** - Import required modules and create MCP client
2. **Input Parameters** - Define reservoir and fluid properties
3. **Calculations** - Call MCP tools to perform calculations
4. **Results Display** - Format and display results in tables

## Key Concepts Demonstrated

### PVT Calculations
- Oil bubble point pressure (Standing, Valko-McCain, Velarde)
- Solution gas-oil ratio (Rs)
- Formation volume factors (Bo, Bg)
- Viscosity calculations
- Density and compressibility

### Inflow Performance
- Radial flow (vertical wells)
- Linear flow (horizontal wells)
- IPR curve generation
- Sensitivity analysis

### Simulation Support
- Relative permeability tables (Corey, LET)
- Aquifer influence functions
- Black oil table generation

### Reservoir Analysis
- Heterogeneity quantification (Lorenz coefficient)
- Layer property generation
- Flow fraction analysis

### Phase Behavior
- Rachford-Rice flash calculations
- Vapor-liquid equilibrium
- Separator design

## Notes

- All examples use field units (psia, degF, ft, mD, STB/day, MSCF/day)
- Examples demonstrate both scalar and array inputs where applicable
- Error handling is minimal for clarity; production code should include proper error handling
- Some examples may require direct pyrestoolbox imports for functions not yet exposed via MCP tools

