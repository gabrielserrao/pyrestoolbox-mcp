"""Sensitivity Analysis tools for FastMCP."""

import numpy as np
import pyrestoolbox as rtb
import pyrestoolbox.sensitivity as sensitivity
from fastmcp import FastMCP

from ..models.sensitivity_models import SweepRequest, TornadoRequest


def _resolve_function(module_name: str, func_name: str):
    """Resolve a pyrestoolbox function from module and function names."""
    module = getattr(rtb, module_name, None)
    if module is None:
        raise ValueError(f"Unknown module: {module_name}. Valid modules: gas, oil, brine, simtools, layer, library, nodal, matbal, dca")
    func = getattr(module, func_name, None)
    if func is None:
        raise ValueError(f"Unknown function: {func_name} in module {module_name}")
    return func


def _serialize_result(val):
    """Serialize a result value for JSON output."""
    # Handle NumPy scalar types by converting to native Python float
    if isinstance(val, (np.floating, np.integer)):
        return float(val)
    # Convert NumPy arrays to lists
    if isinstance(val, np.ndarray):
        return val.tolist()
    # Primitive JSON types can be returned as-is
    if isinstance(val, (int, float, bool, str)) or val is None:
        return val
    # Preserve structure for mappings by recursively serializing values
    if isinstance(val, dict):
        return {k: _serialize_result(v) for k, v in val.items()}
    # Preserve structure for sequences by recursively serializing items
    if isinstance(val, (list, tuple)):
        return [_serialize_result(v) for v in val]
    # Fallback: stringify any other unsupported type
    return str(val)


def register_sensitivity_tools(mcp: FastMCP) -> None:
    """Register all sensitivity analysis tools with the MCP server."""

    @mcp.tool()
    def parameter_sweep(request: SweepRequest) -> dict:
        """Sweep a single parameter across a range of values for any pyResToolbox function.

        **SENSITIVITY ANALYSIS TOOL** - Evaluates a function at each value of a varied
        parameter while keeping all other parameters at their base values. Useful for
        understanding parameter sensitivity and generating cross-plots.

        **Parameters:**
        - **function_module** (str, required): Module name (e.g. "gas", "oil", "brine").
        - **function_name** (str, required): Function name (e.g. "gas_z", "oil_pbub").
        - **base_parameters** (dict, required): Base keyword arguments for the function.
        - **vary_parameter** (str, required): Name of the parameter to vary.
        - **vary_values** (list[float], required): Values to sweep through.
        - **result_key** (str, optional): Key/attribute to extract from each result.

        **Returns:** Parameter name, values swept, and results at each value.

        **Example:**
        ```json
        {
          "function_module": "gas",
          "function_name": "gas_z",
          "base_parameters": {"p": 3000, "degf": 200, "sg": 0.7},
          "vary_parameter": "sg",
          "vary_values": [0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
        }
        ```
        """
        func = _resolve_function(request.function_module, request.function_name)
        result = sensitivity.sweep(
            func=func, base_kwargs=request.base_parameters,
            vary_param=request.vary_parameter, vary_values=request.vary_values,
            result_key=request.result_key,
        )
        return {
            "parameter": result.param,
            "values": result.values,
            "results": [_serialize_result(r) for r in result.results],
        }

    @mcp.tool()
    def tornado_sensitivity(request: TornadoRequest) -> dict:
        """Compute tornado-chart sensitivities for multiple parameters.

        **SENSITIVITY ANALYSIS TOOL** - Evaluates a function at low and high values
        of each parameter to determine which parameters have the most impact on results.
        Entries are sorted by decreasing sensitivity (largest swing first).

        **Parameters:**
        - **function_module** (str, required): Module name.
        - **function_name** (str, required): Function name.
        - **base_parameters** (dict, required): Base keyword arguments.
        - **ranges** (dict, required): Parameter ranges as {param: [low, high]}.
        - **result_key** (str, optional): Key to extract scalar from result.

        **Returns:** Base result and per-parameter sensitivities sorted by impact.

        **Example:**
        ```json
        {
          "function_module": "oil",
          "function_name": "oil_pbub",
          "base_parameters": {"api": 35, "degf": 200, "rsb": 800, "sg_sp": 0.75},
          "ranges": {"api": [25, 45], "degf": [150, 250], "rsb": [400, 1200], "sg_sp": [0.65, 0.85]}
        }
        ```
        """
        func = _resolve_function(request.function_module, request.function_name)
        ranges_tuples = {k: tuple(v) for k, v in request.ranges.items()}
        result = sensitivity.tornado(
            func=func, base_kwargs=request.base_parameters,
            ranges=ranges_tuples, result_key=request.result_key,
        )
        entries = []
        for entry in result.entries:
            entries.append({
                "parameter": entry.param,
                "low_value": _serialize_result(entry.low_value),
                "high_value": _serialize_result(entry.high_value),
                "low_result": _serialize_result(entry.low_result),
                "high_result": _serialize_result(entry.high_result),
            })
        return {
            "base_result": _serialize_result(result.base_result),
            "entries": entries,
        }
