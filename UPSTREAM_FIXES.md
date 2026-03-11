# Upstream pyResToolbox Issues and Workarounds

This document tracks issues in the upstream [pyResToolbox](https://github.com/mwburgoyne/pyResToolbox) library (v3.0.4) that required workarounds or fixes in the MCP server.

---

## 1. `gas_grad2sg` — Broken `bisect_solve` Internal Function

**Issue:** `pyrestoolbox.gas.gas_grad2sg()` calls an internal `bisect_solve()` function that fails at runtime, making the function unusable.

**Affected versions:** pyResToolbox <= 3.0.4

**Error:** The bisection solver used internally does not converge or raises exceptions for valid inputs.

**Workaround:** A standalone reimplementation using Newton-Raphson iteration is provided in `src/pyrestoolbox_mcp/tools/gas_fixes.py`:

```python
def gas_grad2sg_fixed(grad, p, degf, zmethod, cmethod, co2, h2s, n2, tc, pc, rtol, metric):
    """Newton-Raphson solver replacing broken bisect_solve."""
    ...
```

The MCP tool `gas_sg_from_gradient` uses this fixed implementation instead of the upstream function.

**File:** `src/pyrestoolbox_mcp/tools/gas_fixes.py`

---

## 2. `oil.oil_rs()` — Does Not Accept List/Array Pressure Input

**Issue:** `pyrestoolbox.oil.oil_rs()` accepts only scalar `float` for the `p` parameter, not lists or arrays. Passing a list raises:

```
TypeError: '>=' not supported between instances of 'list' and 'float'
```

**Affected versions:** pyResToolbox <= 3.0.4

**Workaround:** The MCP tool `oil_solution_gor` detects list input and loops over individual pressure values:

```python
if isinstance(request.p, list):
    value = [
        float(oil.oil_rs(api=request.api, degf=request.degf, p=p_val, ...))
        for p_val in request.p
    ]
else:
    value = float(oil.oil_rs(api=request.api, degf=request.degf, p=request.p, ...))
```

**File:** `src/pyrestoolbox_mcp/tools/oil_tools.py` (lines ~148-240)

---

## 3. NumPy/mpmath Object Serialization

**Issue:** Many pyResToolbox functions return `numpy.ndarray`, `numpy.float64`, `numpy.int64`, or `mpmath` objects that are not JSON-serializable. The FastMCP framework requires plain Python types in tool return values.

**Affected functions:** Most functions that return arrays or use numpy internally.

**Workaround:** All tool implementations convert numpy types before returning:

```python
# Simple cases
result.tolist()           # numpy array → list
float(result)             # numpy scalar → float

# Deeply nested cases (e.g., fit_relative_permeability_best)
def _serialize(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]
    return obj
```

**Files:** All tool files in `src/pyrestoolbox_mcp/tools/`

---

## 4. Missing `metric` Parameter in Some Functions

**Issue:** Some pyResToolbox functions documented as supporting metric units did not originally expose the `metric` parameter in earlier versions. With v3.0.4, metric support is generally available but parameter behavior varies by function.

**Affected versions:** pyResToolbox < 3.0.4 (partially resolved in 3.0.4)

**Workaround:** All MCP tool models include `metric: bool = False` and pass it through to upstream functions. The MCP server validates that metric mode works correctly for each tool.

---

## 5. `SoreideWhitson` Class — Attribute Access Patterns

**Issue:** The `pyrestoolbox.brine.SoreideWhitson` class returns VLE results through attribute access patterns that are not well documented. Component-level results (Rs by component, densities, viscosities) require accessing internal arrays and converting to dictionaries.

**Affected versions:** pyResToolbox 3.0.4

**Workaround:** The `soreide_whitson_vle` tool manually extracts and structures the results:

```python
sw = brine.SoreideWhitson(pres=..., temp=..., ppm=..., sg=..., ...)
result = {
    "solution_gor_by_component": {...},
    "solution_gor_total": float(sw.Rs_total),
    "densities": {...},
    "viscosities": {...},
    ...
}
```

**File:** `src/pyrestoolbox_mcp/tools/brine_tools.py`

---

## Recommendations for Upstream

1. **Fix `bisect_solve`** in `gas_grad2sg` — or replace with `scipy.optimize.brentq`
2. **Support array input** in `oil_rs()` — consistent with other PVT functions that accept arrays
3. **Add JSON-serializable return types** — or provide a `.to_dict()` method on result objects
4. **Document `SoreideWhitson` attributes** — especially component-level access patterns
5. **Standardize `metric` parameter** across all public functions
