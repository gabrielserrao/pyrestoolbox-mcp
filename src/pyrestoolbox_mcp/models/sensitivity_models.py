"""Pydantic models for Sensitivity Analysis tools."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SweepRequest(BaseModel):
    """Request model for single-parameter sweep."""

    function_module: str = Field(..., description="Module name (e.g. 'gas', 'oil', 'simtools')")
    function_name: str = Field(..., description="Function name (e.g. 'gas_z', 'oil_pbub')")
    base_parameters: Dict[str, Any] = Field(
        ..., description="Base keyword arguments for the function"
    )
    vary_parameter: str = Field(..., description="Name of the parameter to vary")
    vary_values: List[float] = Field(..., description="Values to sweep through")
    result_key: Optional[str] = Field(None, description="Key/attribute to extract from each result")


class TornadoRequest(BaseModel):
    """Request model for tornado sensitivity analysis."""

    function_module: str = Field(..., description="Module name (e.g. 'gas', 'oil')")
    function_name: str = Field(..., description="Function name (e.g. 'oil_pbub')")
    base_parameters: Dict[str, Any] = Field(
        ..., description="Base keyword arguments for the function"
    )
    ranges: Dict[str, List[float]] = Field(
        ..., description="Parameter ranges as {param_name: [low, high]}"
    )
    result_key: Optional[str] = Field(
        None, description="Key/attribute to extract scalar from each result"
    )
