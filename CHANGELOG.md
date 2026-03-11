# Changelog


The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-15

### Added
- Initial production release of pyResToolbox MCP Server
- 47 fully functional reservoir engineering tools:
  - 17 Oil PVT calculation tools
  - 11 Gas PVT calculation tools
  - 4 Inflow performance tools
  - 3 Simulation tools (relative permeability, aquifer, flash)
  - 2 Brine property calculation tools
  - 5 Layer heterogeneity tools
  - 1 Component library tool
  - 4 Configuration resources
- FastMCP framework integration for Model Context Protocol
- Comprehensive Pydantic validation models
- Docker and docker-compose deployment support
- UV package manager configuration for fast installs
- Complete test suite with 100% tool coverage
- GPL-3.0 license compliance
- Claude Desktop integration guide

### Fixed
- Standalone implementation of `gas_grad2sg` (upstream bug fix)
- Corrected 25+ parameter name mismatches with pyrestoolbox library
- Fixed oil inflow tools to auto-calculate PVT properties
- Proper array/scalar handling across all tools
- Type conversion for mpmath, numpy, and pandas objects
- Warning suppression for pkg_resources deprecation

### Documentation
- Comprehensive README with quickstart, examples, and troubleshooting
- QUICKSTART guide for new users
- TEST_RESULTS with complete coverage report
- PRODUCTION_READY deployment guide
- CONTRIBUTING guidelines
- DOCKER deployment documentation
- Example scripts (basic_usage.py verified working)

### Infrastructure
- Makefile with uv-install, uv-test, uv-server commands
- Automated testing with test_tools.py (47/47 passing)
- Docker multi-stage build optimized for production
- .gitignore for clean repository
- .dockerignore for efficient builds

### Dependencies
- pyRestoolbox >=2.1.4 (core calculations)
- FastMCP >=2.0.0 (MCP framework)
- Pydantic >=2.0.0 (validation)
- NumPy >=1.24.0 (numerical operations)
- Pandas >=2.0.0 (data tables)

## [2.0.0] - 2026-03-11

### Added — New Tool Modules (61 new tools)

**Decline Curve Analysis (9 tools)**
- `fit_decline` — Fit Arps decline parameters to rate vs time data
- `fit_decline_cumulative` — Fit decline parameters from cumulative production data
- `decline_forecast` — Generate rate forecast from decline parameters
- `arps_rate` — Calculate Arps decline rate at a given time
- `arps_cumulative` — Calculate cumulative production from Arps decline
- `estimated_ultimate_recovery` — Calculate EUR from decline parameters
- `duong_rate` — Duong decline model for tight/unconventional wells
- `fit_ratio` — Fit production ratio (WOR, GOR, WGR) trends
- `ratio_forecast` — Forecast production ratios

**Material Balance (2 tools)**
- `gas_material_balance` — P/Z gas material balance for OGIP estimation with Cole plot diagnostics
- `oil_material_balance` — Havlena-Odeh oil material balance for OOIP estimation

**Nodal Analysis / VLP (6 tools)**
- `flowing_bhp` — Calculate flowing bottom hole pressure (HB, WG, GRAY, BB correlations)
- `ipr_curve` — Generate inflow performance relationship curves
- `outflow_curve` — Generate VLP outflow curves
- `operating_point` — Find VLP/IPR operating point intersection
- `generate_vfp_prod_table` — Generate VFPPROD tables for reservoir simulators
- `generate_vfp_inj_table` — Generate VFPINJ tables for reservoir simulators

**Method Recommendation (4 tools)**
- `recommend_methods` — General method recommendation based on fluid/conditions
- `recommend_gas_methods` — Recommend gas PVT correlation methods
- `recommend_oil_methods` — Recommend oil PVT correlation methods
- `recommend_vlp_method` — Recommend VLP correlation for well conditions

**Sensitivity Analysis (2 tools)**
- `parameter_sweep` — Run parameter sweeps across any tool
- `tornado_sensitivity` — Generate tornado sensitivity analysis

**Geomechanics & Wellbore Stability (27 tools — now registered in server)**
- `geomech_vertical_stress` — Overburden stress from depth and density
- `geomech_pore_pressure_eaton` — Pore pressure from Eaton's method (sonic/resistivity)
- `geomech_effective_stress` — Terzaghi/Biot effective stress
- `geomech_horizontal_stress` — Poroelastic horizontal stress model
- `geomech_elastic_moduli_conversion` — E, K, G, λ, ν conversions
- `geomech_rock_strength_mohr_coulomb` — Mohr-Coulomb failure criterion
- `geomech_dynamic_to_static_moduli` — Dynamic to static moduli conversion
- `geomech_breakout_width` — Borehole breakout width calculation
- `geomech_fracture_gradient` — Fracture gradient estimation (Eaton, Hubbert-Willis)
- `geomech_safe_mud_weight_window` — Safe mud weight window (kick to lost circulation)
- `geomech_critical_mud_weight_collapse` — Critical mud weight for collapse prevention
- `geomech_reservoir_compaction` — Uniaxial strain compaction and subsidence
- `geomech_pore_compressibility` — Pore and bulk compressibility from elastic moduli
- `geomech_leak_off_pressure` — LOT/FIT analysis for minimum horizontal stress
- `geomech_hydraulic_fracture_width` — PKN and KGD fracture width models
- `geomech_stress_polygon` — Frictional equilibrium stress polygon constraints
- `geomech_sand_production` — Sand production risk assessment
- `geomech_fault_stability` — Coulomb failure stress and slip tendency
- `geomech_deviated_well_stress` — Stress at deviated/horizontal wellbores
- `geomech_tensile_failure` — Tensile failure and breakdown pressure
- `geomech_shear_failure_criteria` — Multiple failure criteria comparison (MC, DP, Mogi)
- `geomech_breakout_stress_inversion` — Stress inversion from breakout observations
- `geomech_breakdown_pressure` — Hydraulic fracturing initiation pressure
- `geomech_stress_path` — Stress path during depletion/injection
- `geomech_thermal_stress` — Temperature-induced stress changes
- `geomech_ucs_from_logs` — UCS estimation from logs (McNally, Horsrud, Chang, Vernik)
- `geomech_critical_drawdown` — Critical drawdown for sand production prediction

### Added — New Tools in Existing Modules

**Oil PVT (2 new tools, 19 total)**
- `oil_harmonize_pvt` — Harmonize PVT properties for consistency
- `create_oil_pvt` — Create OilPVT object for multi-property access

**Gas PVT (4 new tools, 15 total)**
- `gas_hydrate_prediction` — Predict gas hydrate formation conditions
- `gas_fws_sg` — Free-water-saturated gas specific gravity
- `gas_delta_pseudopressure` — Delta pseudopressure calculation
- `create_gas_pvt` — Create GasPVT object for multi-property access

**Simulation (8 new tools, 11 total)**
- `generate_black_oil_table_og` — Oil-gas black oil table generation
- `generate_pvtw_table` — PVTW water properties table
- `fit_relative_permeability` — Fit Corey/LET to relative permeability data
- `fit_relative_permeability_best` — Auto-select best relative permeability fit
- `evaluate_jerauld` — Evaluate Jerauld relative permeability correlation
- `check_let_physical` — Validate LET parameters for physical consistency
- `generate_rel_perm_corey_oil` — Generate Corey oil rel perm curves
- `generate_rel_perm_let_oil` — Generate LET oil rel perm curves

**Brine (1 new tool, 3 total)**
- `soreide_whitson_vle` — Soreide-Whitson VLE brine-gas equilibrium calculation

### Added — Metric Unit Support

- All Oil PVT tools now support `metric: bool` parameter (barsa, °C)
- All Gas PVT tools now support `metric: bool` parameter
- Brine properties support metric units
- DCA, Material Balance, Nodal Analysis, and Simulation tools support metric units
- Config module updated with metric constants and dual unit documentation

### Fixed

**Upstream pyResToolbox Workarounds**
- `gas_grad2sg` — Reimplemented with Newton-Raphson solver (upstream `bisect_solve` broken)
- `oil_rs` — Added list input handling (upstream only accepts scalar float)
- NumPy/mpmath serialization — Recursive `_serialize()` for deeply nested numpy arrays
- SoreideWhitson attribute extraction — Structured result extraction from VLE object

**Test Suite**
- Migrated all tests to FastMCP 3.x client pattern (`{"request": {...}}` nesting)
- Fixed `result.data` access pattern (FastMCP 3.x returns `CallToolResult` objects)
- Fixed DCA test parameter name mismatches (`t_life`→`q_min`, `t`→`time`, `q`→`rates`)
- Fixed recommend test key assertions (`z_method`→`zmethod`)
- Rewrote geomechanics tests from direct function calls to MCP client calls (21 tests)
- Registered geomech_tools in server.py (was missing from tool registration)

**Bug Fixes**
- Fixed `fit_relative_permeability_best` output validation error from nested numpy arrays
- Fixed `oil_solution_gor` TypeError when passing list of pressures
- Added `metric` parameter to `gas_grad2sg_fixed` standalone implementation

### Changed

- Upgraded pyResToolbox dependency from >=2.1.4 to >=3.0.4
- Upgraded FastMCP dependency from >=2.0.0 to >=3.0.0
- Server version bumped from 1.0.0 to 2.0.0
- Total tool count: 47 → 108
- Total test count: 8 → 52
- Config updated with new calculation method categories (vlp, decline_curve, hydrate_prediction, brine)

### Documentation

- Created UPSTREAM_FIXES.md documenting all pyResToolbox workarounds
- Updated README.md with 108 tools, new modules, dual unit support, updated architecture
- Updated CHANGELOG.md with comprehensive v2.0.0 entry
- Updated LaTeX formula reference with DCA, Material Balance, Nodal Analysis sections

## [Unreleased]

### Planned
- Additional example workflows
- Performance optimization
- Web UI for HTTP transport
- Prometheus metrics export
- Rate limiting and authentication options

---

## Release Notes

### Version 1.0.0 - Production Release

This is the first production-ready release of the pyResToolbox MCP Server. All 47 tools have been validated and are working correctly. The server is GPL-3.0 licensed, matching the original pyResToolbox library.

**Highlights:**
- 100% test coverage - all 47 tools passing
- Standalone implementation fixes for upstream bugs
- Full Docker deployment support
- UV package manager for 10-100x faster installs
- Ready for Claude Desktop integration
- Comprehensive documentation

**For Users:**
```bash
# Quick start
cd pyrestoolbox-mcp
make uv-install
uv run python test_tools.py  # Verify
make uv-server               # Run
```

**For Contributors:**
See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

