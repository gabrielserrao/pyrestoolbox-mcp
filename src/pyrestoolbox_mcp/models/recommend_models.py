"""Pydantic models for Method Recommendation tools."""

from pydantic import BaseModel, Field
from typing import Literal, Optional


class RecommendMethodsRequest(BaseModel):
    """Request model for master method recommendation."""

    gas_sg: float = Field(0.65, ge=0.5, le=2.0, description="Gas specific gravity (air=1)")
    co2: float = Field(0.0, ge=0, le=1, description="CO2 mole fraction")
    h2s: float = Field(0.0, ge=0, le=1, description="H2S mole fraction")
    n2: float = Field(0.0, ge=0, le=1, description="N2 mole fraction")
    h2: float = Field(0.0, ge=0, le=1, description="H2 mole fraction")
    api: Optional[float] = Field(
        None, gt=0, le=100,
        description="Oil API gravity. If provided, includes oil method recommendations"
    )
    deviation: float = Field(
        0.0, ge=0, le=90, description="Max wellbore deviation from vertical (degrees)"
    )
    well_type: Literal["gas", "oil"] = Field("gas", description="Well type")


class RecommendGasMethodsRequest(BaseModel):
    """Request model for gas method recommendation."""

    gas_sg: float = Field(0.65, ge=0.5, le=2.0, description="Gas specific gravity (air=1)")
    co2: float = Field(0.0, ge=0, le=1, description="CO2 mole fraction")
    h2s: float = Field(0.0, ge=0, le=1, description="H2S mole fraction")
    n2: float = Field(0.0, ge=0, le=1, description="N2 mole fraction")
    h2: float = Field(0.0, ge=0, le=1, description="H2 mole fraction")


class RecommendOilMethodsRequest(BaseModel):
    """Request model for oil method recommendation."""

    api: float = Field(35.0, gt=0, le=100, description="Oil API gravity")


class RecommendVLPMethodRequest(BaseModel):
    """Request model for VLP method recommendation."""

    deviation: float = Field(0.0, ge=0, le=90, description="Max deviation from vertical (degrees)")
    well_type: Literal["gas", "oil"] = Field("gas", description="Well type")
