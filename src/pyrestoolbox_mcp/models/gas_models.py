"""Pydantic models for Gas PVT calculations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Union, List, Optional


class ZFactorRequest(BaseModel):
    """Request model for gas Z-factor calculation."""

    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    p: Union[float, List[float]] = Field(..., description="Pressure (psia) - scalar or array")
    h2s: float = Field(0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)")
    n2: float = Field(0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)")
    method: Literal["DAK", "HY", "WYW", "BUR"] = Field(
        "DAK", description="Calculation method (DAK recommended)"
    )
    metric: bool = Field(False, description="Use metric units (barsa, degC)")

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


class CriticalPropertiesRequest(BaseModel):
    """Request model for critical properties calculation."""

    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    h2s: float = Field(0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)")
    n2: float = Field(0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)")
    method: Literal["PMC", "SUT", "BUR"] = Field(
        "PMC", description="Calculation method (PMC recommended)"
    )
    metric: bool = Field(False, description="Use metric units (barsa, degC)")


class GasFVFRequest(BaseModel):
    """Request model for gas formation volume factor calculation."""

    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    p: Union[float, List[float]] = Field(..., description="Pressure (psia) - scalar or array")
    h2s: float = Field(0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)")
    n2: float = Field(0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)")
    zmethod: Literal["DAK", "HY", "WYW", "BUR"] = Field(
        "DAK", description="Z-factor calculation method"
    )
    metric: bool = Field(False, description="Use metric units (barsa, degC)")

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


class GasViscosityRequest(BaseModel):
    """Request model for gas viscosity calculation."""

    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    p: Union[float, List[float]] = Field(..., description="Pressure (psia) - scalar or array")
    h2s: float = Field(0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)")
    n2: float = Field(0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)")
    zmethod: Literal["DAK", "HY", "WYW", "BUR"] = Field(
        "DAK", description="Z-factor calculation method"
    )
    metric: bool = Field(False, description="Use metric units (barsa, degC)")

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


class GasDensityRequest(BaseModel):
    """Request model for gas density calculation."""

    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    p: Union[float, List[float]] = Field(..., description="Pressure (psia) - scalar or array")
    h2s: float = Field(0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)")
    n2: float = Field(0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)")
    zmethod: Literal["DAK", "HY", "WYW", "BUR"] = Field(
        "DAK", description="Z-factor calculation method"
    )
    metric: bool = Field(False, description="Use metric units (barsa, degC)")

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


class GasCompressibilityRequest(BaseModel):
    """Request model for gas compressibility calculation."""

    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    p: Union[float, List[float]] = Field(..., description="Pressure (psia) - scalar or array")
    h2s: float = Field(0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)")
    n2: float = Field(0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)")
    zmethod: Literal["DAK", "HY", "WYW", "BUR"] = Field(
        "DAK", description="Z-factor calculation method"
    )
    metric: bool = Field(False, description="Use metric units (barsa, degC)")

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


class GasPseudopressureRequest(BaseModel):
    """Request model for gas pseudopressure calculation."""

    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    p1: Union[float, List[float]] = Field(
        ..., description="Initial pressure (psia) - scalar or array"
    )
    p2: Union[float, List[float]] = Field(
        ..., description="Final pressure (psia) - scalar or array"
    )
    h2s: float = Field(0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)")
    n2: float = Field(0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)")
    zmethod: Literal["DAK", "HY", "WYW", "BUR"] = Field(
        "DAK", description="Z-factor calculation method"
    )
    metric: bool = Field(False, description="Use metric units (barsa, degC)")


class GasPressureFromPZRequest(BaseModel):
    """Request model for pressure from P/Z calculation."""

    pz: Union[float, List[float]] = Field(..., description="P/Z value (psia) - scalar or array")
    sg: float = Field(
        ..., ge=0.5, le=2.0, description="Gas specific gravity (air=1, dimensionless)"
    )
    degf: float = Field(..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    h2s: float = Field(0.0, ge=0.0, le=1.0, description="H2S mole fraction (dimensionless)")
    co2: float = Field(0.0, ge=0.0, le=1.0, description="CO2 mole fraction (dimensionless)")
    n2: float = Field(0.0, ge=0.0, le=1.0, description="N2 mole fraction (dimensionless)")
    zmethod: Literal["DAK", "HY", "WYW", "BUR"] = Field(
        "DAK", description="Z-factor calculation method"
    )
    metric: bool = Field(False, description="Use metric units (barsa, degC)")


class GasSGFromGradientRequest(BaseModel):
    """Request model for gas SG from pressure gradient."""

    grad: Union[float, List[float]] = Field(
        ..., description="Pressure gradient (psi/ft) - scalar or array"
    )
    degf: float = Field(..., gt=-460, lt=1000, description="Temperature (degrees Fahrenheit)")
    p: float = Field(..., gt=0, description="Pressure (psia)")
    metric: bool = Field(False, description="Use metric units (barsa, degC)")


class GasWaterContentRequest(BaseModel):
    """Request model for gas water content calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "p": 1000.0,
                "degf": 100.0,
            }
        }
    )

    p: Union[float, List[float]] = Field(..., description="Pressure (psia) - scalar or array")
    degf: Union[float, List[float]] = Field(
        ..., description="Temperature (degrees Fahrenheit) - scalar or array"
    )

    @field_validator("p", "degf")
    @classmethod
    def validate_positive(cls, v):
        if isinstance(v, list):
            if not all(val > 0 for val in v):
                raise ValueError("All values must be positive")
        else:
            if v <= 0:
                raise ValueError("Value must be positive")
        return v

    metric: bool = Field(False, description="Use metric units (barsa, degC)")


class GasSGFromCompositionRequest(BaseModel):
    """Request model for gas SG from composition calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "hc_mw": 20.5,
                "co2": 0.05,
                "h2s": 0.01,
                "n2": 0.02,
                "h2": 0.0,
            }
        }
    )

    hc_mw: float = Field(..., gt=0, description="Hydrocarbon molecular weight (lb/lbmol)")
    co2: float = Field(0.0, ge=0, le=1, description="CO2 mole fraction")
    h2s: float = Field(0.0, ge=0, le=1, description="H2S mole fraction")
    n2: float = Field(0.0, ge=0, le=1, description="N2 mole fraction")
    h2: float = Field(0.0, ge=0, le=1, description="H2 mole fraction")
    metric: bool = Field(False, description="Use metric units (barsa, degC)")


class GasHydrateRequest(BaseModel):
    """Request model for gas hydrate prediction."""

    p: float = Field(..., gt=0, description="Operating pressure (psia | barsa)")
    degf: float = Field(..., description="Operating temperature (deg F | deg C)")
    sg: float = Field(..., ge=0.5, le=2.0, description="Gas specific gravity (air=1)")
    method: str = Field("TOWLER", description="Hydrate prediction method")
    inhibitor_type: Optional[str] = Field(
        None, description="Inhibitor type: MEOH, MEG, DEG, TEG, or None"
    )
    inhibitor_wt_pct: float = Field(0.0, ge=0, le=100, description="Inhibitor weight percent")
    co2: float = Field(0.0, ge=0, le=1, description="CO2 mole fraction")
    h2s: float = Field(0.0, ge=0, le=1, description="H2S mole fraction")
    n2: float = Field(0.0, ge=0, le=1, description="N2 mole fraction")
    h2: float = Field(0.0, ge=0, le=1, description="H2 mole fraction")
    p_res: Optional[float] = Field(None, gt=0, description="Reservoir pressure for water balance")
    degf_res: Optional[float] = Field(None, description="Reservoir temperature for water balance")
    metric: bool = Field(False, description="Use metric units (barsa, degC)")


class GasFWSSGRequest(BaseModel):
    """Request model for free-water-saturated gas SG calculation."""

    sg_g: float = Field(..., gt=0, le=3, description="Separator gas SG (relative to air)")
    cgr: float = Field(..., ge=0, description="Condensate-gas ratio (stb/MMscf | sm3/sm3)")
    api_st: float = Field(..., gt=0, le=100, description="Stock tank liquid API gravity")
    metric: bool = Field(False, description="Use metric units")


class GasDmpRequest(BaseModel):
    """Request model for delta-pseudopressure calculation."""

    p1: float = Field(..., gt=0, description="Starting (lower) pressure (psia | barsa)")
    p2: float = Field(..., gt=0, description="Ending (upper) pressure (psia | barsa)")
    degf: float = Field(..., description="Temperature (deg F | deg C)")
    sg: float = Field(..., ge=0.5, le=2.0, description="Gas specific gravity (air=1)")
    h2s: float = Field(0.0, ge=0, le=1, description="H2S mole fraction")
    co2: float = Field(0.0, ge=0, le=1, description="CO2 mole fraction")
    n2: float = Field(0.0, ge=0, le=1, description="N2 mole fraction")
    h2: float = Field(0.0, ge=0, le=1, description="H2 mole fraction")
    zmethod: Literal["DAK", "HY", "WYW", "BUR"] = Field("DAK", description="Z-factor method")
    cmethod: Literal["PMC", "SUT", "BUR"] = Field("PMC", description="Critical properties method")
    metric: bool = Field(False, description="Use metric units")


class GasPVTRequest(BaseModel):
    """Request model for GasPVT object creation and evaluation."""

    sg: float = Field(0.75, ge=0.5, le=2.0, description="Gas specific gravity (air=1)")
    co2: float = Field(0.0, ge=0, le=1, description="CO2 mole fraction")
    h2s: float = Field(0.0, ge=0, le=1, description="H2S mole fraction")
    n2: float = Field(0.0, ge=0, le=1, description="N2 mole fraction")
    h2: float = Field(0.0, ge=0, le=1, description="H2 mole fraction")
    zmethod: Literal["DAK", "HY", "WYW", "BUR"] = Field("DAK", description="Z-factor method")
    cmethod: Literal["PMC", "SUT", "BUR"] = Field("PMC", description="Critical properties method")
    pressures: List[float] = Field(..., description="Pressures to evaluate (psia | barsa)")
    temperature: float = Field(..., description="Temperature (deg F | deg C)")
    metric: bool = Field(False, description="Use metric units")

    @field_validator("pressures")
    @classmethod
    def validate_pressures(cls, v):
        if not all(p > 0 for p in v):
            raise ValueError("All pressure values must be positive")
        return v
