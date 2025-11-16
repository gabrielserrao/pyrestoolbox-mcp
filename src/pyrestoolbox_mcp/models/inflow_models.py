"""Pydantic models for Inflow Performance calculations."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Union, List, Optional


class OilRateRadialRequest(BaseModel):
    """Request model for radial oil inflow performance calculation."""

    pi: float = Field(..., gt=0, description="Initial reservoir pressure (psia)")
    pb: float = Field(..., ge=0, description="Bubble point pressure (psia)")
    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    sg_g: float = Field(
        ..., ge=0, le=3, description="Gas specific gravity (air=1, dimensionless)"
    )
    psd: Union[float, List[float]] = Field(
        ..., description="Sandface pressure (psia) - scalar or array"
    )
    h: float = Field(..., gt=0, description="Net pay thickness (ft)")
    k: float = Field(..., gt=0, description="Permeability (mD)")
    s: float = Field(0.0, description="Skin factor (dimensionless)")
    re: float = Field(..., gt=0, description="Drainage radius (ft)")
    rw: float = Field(..., gt=0, description="Wellbore radius (ft)")
    rsb: float = Field(
        0.0, ge=0, description="Solution GOR at bubble point (scf/stb)"
    )
    vogel: bool = Field(
        False, description="Use Vogel IPR for reservoir pressure below bubble point"
    )

    @field_validator("psd")
    @classmethod
    def validate_pressure(cls, v):
        """Validate pressure values."""
        if isinstance(v, list):
            if not all(p > 0 for p in v):
                raise ValueError("All sandface pressure values must be positive")
        else:
            if v <= 0:
                raise ValueError("Sandface pressure must be positive")
        return v

    @field_validator("rw")
    @classmethod
    def validate_rw(cls, v, info):
        """Validate wellbore radius is less than drainage radius."""
        if "re" in info.data and v >= info.data["re"]:
            raise ValueError("Wellbore radius must be less than drainage radius")
        return v


class OilRateLinearRequest(BaseModel):
    """Request model for linear oil inflow performance calculation."""

    pi: float = Field(..., gt=0, description="Initial reservoir pressure (psia)")
    pb: float = Field(..., ge=0, description="Bubble point pressure (psia)")
    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    sg_g: float = Field(
        ..., ge=0, le=3, description="Gas specific gravity (air=1, dimensionless)"
    )
    psd: Union[float, List[float]] = Field(
        ..., description="Sandface pressure (psia) - scalar or array"
    )
    h: float = Field(..., gt=0, description="Net pay thickness (ft)")
    k: float = Field(..., gt=0, description="Permeability (mD)")
    area: float = Field(..., gt=0, description="Drainage area (sq ft)")
    length: float = Field(..., gt=0, description="Well length (ft)")
    rsb: float = Field(
        0.0, ge=0, description="Solution GOR at bubble point (scf/stb)"
    )

    @field_validator("psd")
    @classmethod
    def validate_pressure(cls, v):
        """Validate pressure values."""
        if isinstance(v, list):
            if not all(p > 0 for p in v):
                raise ValueError("All sandface pressure values must be positive")
        else:
            if v <= 0:
                raise ValueError("Sandface pressure must be positive")
        return v


class GasRateRadialRequest(BaseModel):
    """Request model for radial gas inflow performance calculation."""

    pi: float = Field(..., gt=0, description="Initial reservoir pressure (psia)")
    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    psd: Union[float, List[float]] = Field(
        ..., description="Sandface pressure (psia) - scalar or array"
    )
    h: float = Field(..., gt=0, description="Net pay thickness (ft)")
    k: float = Field(..., gt=0, description="Permeability (mD)")
    s: float = Field(0.0, description="Skin factor (dimensionless)")
    re: float = Field(..., gt=0, description="Drainage radius (ft)")
    rw: float = Field(..., gt=0, description="Wellbore radius (ft)")
    h2s: float = Field(
        0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)"
    )
    co2: float = Field(
        0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)"
    )
    n2: float = Field(
        0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)"
    )

    @field_validator("psd")
    @classmethod
    def validate_pressure(cls, v):
        """Validate pressure values."""
        if isinstance(v, list):
            if not all(p > 0 for p in v):
                raise ValueError("All sandface pressure values must be positive")
        else:
            if v <= 0:
                raise ValueError("Sandface pressure must be positive")
        return v

    @field_validator("rw")
    @classmethod
    def validate_rw(cls, v, info):
        """Validate wellbore radius is less than drainage radius."""
        if "re" in info.data and v >= info.data["re"]:
            raise ValueError("Wellbore radius must be less than drainage radius")
        return v


class GasRateLinearRequest(BaseModel):
    """Request model for linear gas inflow performance calculation."""

    pi: float = Field(..., gt=0, description="Initial reservoir pressure (psia)")
    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    psd: Union[float, List[float]] = Field(
        ..., description="Sandface pressure (psia) - scalar or array"
    )
    h: float = Field(..., gt=0, description="Net pay thickness (ft)")
    k: float = Field(..., gt=0, description="Permeability (mD)")
    area: float = Field(..., gt=0, description="Drainage area (sq ft)")
    length: float = Field(..., gt=0, description="Well length (ft)")
    h2s: float = Field(
        0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)"
    )
    co2: float = Field(
        0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)"
    )
    n2: float = Field(
        0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)"
    )

    @field_validator("psd")
    @classmethod
    def validate_pressure(cls, v):
        """Validate pressure values."""
        if isinstance(v, list):
            if not all(p > 0 for p in v):
                raise ValueError("All sandface pressure values must be positive")
        else:
            if v <= 0:
                raise ValueError("Sandface pressure must be positive")
        return v
