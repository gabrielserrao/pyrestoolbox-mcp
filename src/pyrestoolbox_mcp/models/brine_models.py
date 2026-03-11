"""Pydantic models for Brine calculations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Union, List


class BrinePropertiesRequest(BaseModel):
    """Request model for brine properties calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "p": 3000.0,
                "degf": 150.0,
                "wt": 10.0,
                "ch4": 0.0,
                "co2": 0.02,
            }
        }
    )

    p: Union[float, List[float]] = Field(..., description="Pressure (psia) - scalar or array")
    degf: Union[float, List[float]] = Field(
        ..., description="Temperature (degrees Fahrenheit) - scalar or array"
    )
    wt: float = Field(..., ge=0, le=30, description="Brine salinity (weight percent NaCl)")
    ch4: float = Field(0.0, ge=0, description="Dissolved CH4 mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0, description="Dissolved CO2 mole fraction (dimensionless)")
    metric: bool = Field(False, description="Use metric units (barsa, degC)")

    @field_validator("p", "degf")
    @classmethod
    def validate_arrays(cls, v):
        """Validate array inputs."""
        if isinstance(v, list):
            if not all(val > 0 for val in v):
                raise ValueError("All values must be positive")
        else:
            if v <= 0:
                raise ValueError("Value must be positive")
        return v


class CO2BrineMixtureRequest(BaseModel):
    """Request model for CO2-brine mutual solubility calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pres": 3000.0,
                "temp": 150.0,
                "ppm": 50000.0,
                "metric": False,
                "cw_sat": 0.0,
            }
        }
    )

    pres: float = Field(
        ..., gt=0, description="Pressure (psia if metric=False, bar if metric=True)"
    )
    temp: float = Field(
        ..., gt=0, description="Temperature (degF if metric=False, degC if metric=True)"
    )
    ppm: float = Field(..., ge=0, description="Brine salinity (ppm)")
    metric: bool = Field(False, description="Use metric units (True) or field units (False)")
    cw_sat: float = Field(
        0.0, ge=0, description="Cw at saturation pressure (1/psi or 1/bar) - 0 for auto-calculate"
    )


class SoreideWhitsonRequest(BaseModel):
    """Request model for Soreide-Whitson VLE brine calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pres": 3000.0,
                "temp": 180.0,
                "ppm": 50000,
                "sg": 0.65,
                "metric": False,
            }
        }
    )

    pres: float = Field(..., gt=0, description="Pressure (psia | barsa)")
    temp: float = Field(..., description="Temperature (degF | degC)")
    ppm: float = Field(0.0, ge=0, description="Brine salinity (ppm NaCl)")
    y_CO2: float = Field(0.0, ge=0, le=1, description="CO2 mole fraction in gas")
    y_H2S: float = Field(0.0, ge=0, le=1, description="H2S mole fraction in gas")
    y_N2: float = Field(0.0, ge=0, le=1, description="N2 mole fraction in gas")
    y_H2: float = Field(0.0, ge=0, le=1, description="H2 mole fraction in gas")
    sg: float = Field(0.65, gt=0, le=3, description="Gas specific gravity (air=1)")
    metric: bool = Field(False, description="Use metric units")
    cw_sat: bool = Field(False, description="Calculate saturated compressibility")
