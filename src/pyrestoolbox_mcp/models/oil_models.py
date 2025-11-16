"""Pydantic models for Oil PVT calculations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Union, List, Optional
import numpy as np


class BubblePointRequest(BaseModel):
    """Request model for bubble point pressure calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "api": 35.0,
                "degf": 180.0,
                "rsb": 800.0,
                "sg_g": 0.75,
                "method": "VALMC",
            }
        }
    )

    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    rsb: float = Field(
        ..., ge=0, description="Solution GOR at bubble point (scf/stb)"
    )
    sg_g: float = Field(
        0.0, ge=0, le=3, description="Gas specific gravity (air=1, dimensionless)"
    )
    method: Literal["STAN", "VALMC", "VELAR"] = Field(
        "VALMC", description="Calculation method (VALMC recommended)"
    )


class SolutionGORRequest(BaseModel):
    """Request model for solution gas-oil ratio calculation."""

    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    p: Union[float, List[float]] = Field(
        ..., description="Pressure (psia) - scalar or array"
    )
    sg_g: float = Field(
        0.0, ge=0, le=3, description="Gas specific gravity (air=1, dimensionless)"
    )
    pb: float = Field(0.0, ge=0, description="Bubble point pressure (psia)")
    rsb: float = Field(
        0.0, ge=0, description="Solution GOR at bubble point (scf/stb)"
    )
    method: Literal["VELAR", "STAN", "VALMC"] = Field(
        "VELAR", description="Calculation method"
    )

    @field_validator("p")
    @classmethod
    def validate_pressure(cls, v):
        """Validate pressure values."""
        if isinstance(v, list):
            if not all(p > 0 for p in v):
                raise ValueError("All pressure values must be positive")
        else:
            if v <= 0:
                raise ValueError("Pressure must be positive")
        return v


class OilFVFRequest(BaseModel):
    """Request model for oil formation volume factor calculation."""

    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    p: Union[float, List[float]] = Field(
        ..., description="Pressure (psia) - scalar or array"
    )
    sg_g: float = Field(
        0.0, ge=0, le=3, description="Gas specific gravity (air=1, dimensionless)"
    )
    pb: float = Field(0.0, ge=0, description="Bubble point pressure (psia)")
    rs: Union[float, List[float]] = Field(
        0.0, description="Solution GOR (scf/stb) - scalar or array"
    )
    rsb: float = Field(
        0.0, ge=0, description="Solution GOR at bubble point (scf/stb)"
    )
    method: Literal["MCAIN", "STAN"] = Field(
        "MCAIN", description="Calculation method (MCAIN recommended)"
    )

    @field_validator("p", "rs")
    @classmethod
    def validate_arrays(cls, v):
        """Validate array inputs."""
        if isinstance(v, list):
            if not all(val >= 0 for val in v):
                raise ValueError("All values must be non-negative")
        else:
            if v < 0:
                raise ValueError("Value must be non-negative")
        return v


class OilViscosityRequest(BaseModel):
    """Request model for oil viscosity calculation."""

    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    p: Union[float, List[float]] = Field(
        ..., description="Pressure (psia) - scalar or array"
    )
    pb: float = Field(0.0, ge=0, description="Bubble point pressure (psia)")
    rs: Union[float, List[float]] = Field(
        0.0, description="Solution GOR (scf/stb) - scalar or array"
    )
    rsb: float = Field(
        0.0, ge=0, description="Solution GOR at bubble point (scf/stb)"
    )
    method: Literal["BR"] = Field("BR", description="Calculation method")

    @field_validator("p", "rs")
    @classmethod
    def validate_arrays(cls, v):
        """Validate array inputs."""
        if isinstance(v, list):
            if not all(val >= 0 for val in v):
                raise ValueError("All values must be non-negative")
        else:
            if v < 0:
                raise ValueError("Value must be non-negative")
        return v


class OilDensityRequest(BaseModel):
    """Request model for oil density calculation."""

    p: Union[float, List[float]] = Field(
        ..., description="Pressure (psia) - scalar or array"
    )
    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    rs: Union[float, List[float]] = Field(
        ..., description="Solution GOR (scf/stb) - scalar or array"
    )
    sg_g: float = Field(
        ..., ge=0, le=3, description="Gas specific gravity (air=1, dimensionless)"
    )
    bo: Union[float, List[float]] = Field(
        ..., description="Oil FVF (rb/stb) - scalar or array"
    )

    @field_validator("p", "rs", "bo")
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


class OilCompressibilityRequest(BaseModel):
    """Request model for oil compressibility calculation."""

    p: Union[float, List[float]] = Field(
        ..., description="Pressure (psia) - scalar or array"
    )
    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)"
    )
    pb: float = Field(..., ge=0, description="Bubble point pressure (psia)")
    sg_g: float = Field(
        ..., ge=0, le=3, description="Gas specific gravity (air=1, dimensionless)"
    )
    rs: Union[float, List[float]] = Field(
        ..., description="Solution GOR (scf/stb) - scalar or array"
    )
    rsb: float = Field(
        0.0, ge=0, description="Solution GOR at bubble point (scf/stb)"
    )

    @field_validator("p", "rs")
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


class APIConversionRequest(BaseModel):
    """Request model for API to SG conversion."""

    api: Union[float, List[float]] = Field(
        ..., description="API gravity (degrees) - scalar or array"
    )

    @field_validator("api")
    @classmethod
    def validate_api(cls, v):
        """Validate API values."""
        if isinstance(v, list):
            if not all(val > 0 and val <= 100 for val in v):
                raise ValueError("API gravity must be between 0 and 100")
        else:
            if v <= 0 or v > 100:
                raise ValueError("API gravity must be between 0 and 100")
        return v


class SGConversionRequest(BaseModel):
    """Request model for SG to API conversion."""

    sg: Union[float, List[float]] = Field(
        ..., description="Specific gravity - scalar or array"
    )

    @field_validator("sg")
    @classmethod
    def validate_sg(cls, v):
        """Validate SG values."""
        if isinstance(v, list):
            if not all(val > 0 and val < 1.5 for val in v):
                raise ValueError("Oil SG must be between 0 and 1.5")
        else:
            if v <= 0 or v >= 1.5:
                raise ValueError("Oil SG must be between 0 and 1.5")
        return v


class BlackOilTableRequest(BaseModel):
    """Request model for black oil table generation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pi": 4000.0,
                "api": 38.0,
                "degf": 175.0,
                "sg_g": 0.68,
                "pmax": 5000.0,
                "pb": 3900.0,
                "rsb": 2300.0,
                "nrows": 50,
            }
        }
    )

    pi: float = Field(..., gt=0, description="Initial reservoir pressure (psia)")
    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    sg_g: float = Field(
        ..., ge=0, le=3, description="Gas specific gravity (air=1, dimensionless)")
    pmax: float = Field(
        0.0, ge=0, description="Maximum pressure for table (psia, 0=auto)")
    pb: float = Field(0.0, ge=0, description="Bubble point pressure (psia, 0=calculate)")
    rsb: float = Field(
        0.0, ge=0, description="Solution GOR at bubble point (scf/stb, 0=calculate)")
    nrows: int = Field(50, gt=0, le=200, description="Number of table rows")
    export: bool = Field(False, description="Export ECLIPSE-compatible files")
    pb_method: Literal["STAN", "VALMC", "VELAR"] = Field(
        "VALMC", description="Bubble point calculation method")
    rs_method: Literal["VELAR", "STAN", "VALMC"] = Field(
        "VELAR", description="Solution GOR method")
    bo_method: Literal["MCAIN", "STAN"] = Field(
        "MCAIN", description="Oil FVF method")
    uo_method: Literal["BR"] = Field("BR", description="Oil viscosity method")


class EvolvedGasSGRequest(BaseModel):
    """Request model for evolved gas specific gravity calculation."""

    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")
    degf: float = Field(
        ..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    sg_g: float = Field(
        ..., ge=0, le=3, description="Separator gas specific gravity")
    p: Union[float, List[float]] = Field(
        ..., description="Pressure (psia) - scalar or array")
    psep: float = Field(100.0, gt=0, description="Separator pressure (psia)")

    @field_validator("p")
    @classmethod
    def validate_pressure(cls, v):
        if isinstance(v, list):
            if not all(p > 0 for p in v):
                raise ValueError("All pressure values must be positive")
        else:
            if v <= 0:
                raise ValueError("Pressure must be positive")
        return v


class JacobyAromaticitySGRequest(BaseModel):
    """Request model for Jacoby aromaticity to SG calculation."""

    mw: Union[float, List[float]] = Field(
        ..., gt=0, description="Molecular weight (lb/lbmol) - scalar or array"
    )
    ja: Union[float, List[float]] = Field(
        ..., ge=0, le=1, description="Jacoby aromaticity factor (0=paraffinic, 1=aromatic)"
    )


class TwuPropertiesRequest(BaseModel):
    """Request model for Twu critical properties calculation."""

    mw: Union[float, List[float]] = Field(
        ..., gt=0, description="Molecular weight (lb/lbmol) - scalar or array"
    )
    sg: Union[float, List[float]] = Field(
        ..., gt=0, description="Specific gravity - scalar or array"
    )
    tb: Optional[Union[float, List[float]]] = Field(
        None, description="Boiling point (degR) - optional"
    )
    damp: float = Field(
        0.0, ge=0, le=1, description="Damping factor (0-1)"
    )


class WeightedAverageGasSGRequest(BaseModel):
    """Request model for weighted average gas SG calculation."""

    sg_sp: float = Field(..., gt=0, description="Separator gas specific gravity")
    rsp: float = Field(..., ge=0, description="Separator GOR (scf/stb)")
    sg_st: float = Field(..., gt=0, description="Stock tank gas specific gravity")
    rst: float = Field(..., ge=0, description="Stock tank GOR (scf/stb)")


class StockTankGORRequest(BaseModel):
    """Request model for stock tank incremental GOR calculation."""

    psp: float = Field(..., gt=0, description="Separator pressure (psia)")
    degf_sp: float = Field(
        ..., gt=-460, lt=1000, description="Separator temperature (degF)"
    )
    api: float = Field(..., gt=0, le=100, description="Oil API gravity (degrees)")


class CheckGasSGsRequest(BaseModel):
    """Request model for gas gravity validation/imputation."""

    sg_g: Optional[float] = Field(None, description="Weighted average gas SG (optional)")
    sg_sp: Optional[float] = Field(None, description="Separator gas SG (optional)")
    rst: float = Field(..., ge=0, description="Stock tank GOR (scf/stb)")
    rsp: float = Field(..., ge=0, description="Separator GOR (scf/stb)")
    sg_st: float = Field(..., gt=0, description="Stock tank gas SG")
