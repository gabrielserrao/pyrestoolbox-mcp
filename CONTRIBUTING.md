# Contributing to pyResToolbox MCP Server

Thank you for your interest in contributing to the pyResToolbox MCP Server!

## Code of Conduct

This project adheres to the principles of open source collaboration. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](../../issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, UV version)

### Suggesting Enhancements

1. Check existing issues and discussions
2. Create an issue describing:
   - The enhancement and its benefits
   - Use cases
   - Potential implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly:**
   ```bash
   uv run python test_tools.py  # All 47 tools must pass
   uv run python test_server.py
   uv run python examples/basic_usage.py
   ```
5. **Follow code style:**
   ```bash
   uv run black src/ tests/
   uv run ruff check src/ tests/
   ```
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/pyrestoolbox-mcp.git
cd pyrestoolbox-mcp

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project
make uv-install

# Run tests
uv run python test_tools.py
uv run pytest
```

## Code Guidelines

### Python Style
- Use type hints for all function parameters and return values
- Follow PEP 8 style guide
- Use Black for code formatting
- Use Ruff for linting

### Docstrings
- Use Google-style docstrings
- Include parameter descriptions
- Provide usage examples
- Document return values

### Testing
- Write tests for all new tools
- Ensure existing tests pass
- Add to `test_tools.py` for integration testing

## Adding New Tools

1. **Define Pydantic model** in `src/pyrestoolbox_mcp/models/`
2. **Implement tool function** in appropriate `src/pyrestoolbox_mcp/tools/` file
3. **Register tool** in the register function
4. **Add tests** in `test_tools.py`
5. **Update documentation** in README.md

Example:

```python
# In models/oil_models.py
class NewCalculationRequest(BaseModel):
    param1: float = Field(..., description="Parameter 1")
    param2: float = Field(..., description="Parameter 2")

# In tools/oil_tools.py
@mcp.tool()
def new_calculation(request: NewCalculationRequest) -> dict:
    \"\"\"Calculate something new.\"\"\"
    result = oil.some_function(
        param1=request.param1,
        param2=request.param2,
    )
    return {
        "value": float(result),
        "method": "Method name",
        "units": "units",
        "inputs": request.model_dump(),
    }

# In test_tools.py
("new_calculation", {"request": {"param1": 1.0, "param2": 2.0}}),
```

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0 (GPL-3.0), the same license as the original [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox) library.

## Questions?

Feel free to open an issue for any questions about contributing!

## Acknowledgments

This project builds on the excellent [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox) library by Mark Burgoyne. Please also consider contributing to the upstream project!

