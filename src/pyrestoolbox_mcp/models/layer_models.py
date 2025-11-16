"""Pydantic models for Layer/Heterogeneity calculations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Union


class LorenzRequest(BaseModel):
    """Request model for Lorenz coefficient calculation."""

    value: float = Field(..., ge=0, le=1, description="Lorenz or beta value")


class FlowFractionRequest(BaseModel):
    """Request model for flow fraction calculations."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "flow_frac": [0.8, 0.15, 0.05],
                "perm_frac": [0.6, 0.3, 0.1],
            }
        }
    )

    flow_frac: List[float] = Field(
        ..., min_length=2, description="Flow fractions per layer"
    )
    perm_frac: List[float] = Field(
        ..., min_length=2, description="Permeability-thickness fractions per layer"
    )

    @field_validator("flow_frac", "perm_frac")
    @classmethod
    def validate_fractions(cls, v):
        """Validate fractions sum to ~1.0."""
        total = sum(v)
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Fractions must sum to 1.0 (got {total})")
        return v


class LayerDistributionRequest(BaseModel):
    """Request model for layer distribution generation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lorenz": 0.7,
                "nlay": 10,
                "normalize": True,
            }
        }
    )

    lorenz: float = Field(
        ..., ge=0, le=1, description="Lorenz coefficient (0=homogeneous, 1=heterogeneous)"
    )
    nlay: int = Field(..., gt=0, le=100, description="Number of layers")
    h: float = Field(1.0, gt=0, description="Total thickness (ft, default=1 for normalized)")
    k_avg: float = Field(
        1.0, gt=0, description="Average permeability (mD, default=1 for normalized)"
    )
    normalize: bool = Field(
        True, description="Normalize output (h and k fractions vs absolute)"
    )
