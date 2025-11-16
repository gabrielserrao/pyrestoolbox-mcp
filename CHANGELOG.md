# Changelog

All notable changes to the pyResToolbox MCP Server will be documented in this file.

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

## [Unreleased]

### Planned
- Additional example workflows
- Performance optimization
- Extended documentation
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

