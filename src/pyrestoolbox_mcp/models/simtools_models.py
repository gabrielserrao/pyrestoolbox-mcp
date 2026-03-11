"""Pydantic models for Simulation Tools calculations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, List, Optional


class RelPermTableRequest(BaseModel):
    """Request model for relative permeability table generation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rows": 25,
                "krtable": "SWOF",
                "krfamily": "LET",
                "kromax": 1.0,
                "krwmax": 0.25,
                "swc": 0.15,
                "sorw": 0.15,
                "Lo": 2.5,
                "Eo": 1.25,
                "To": 1.75,
                "Lw": 2.0,
                "Ew": 1.5,
                "Tw": 2.0,
            }
        }
    )

    rows: int = Field(25, gt=0, le=100, description="Number of table rows")
    krtable: Literal["SWOF", "SGOF", "SGWFN"] = Field(
        "SWOF", description="Table type (SWOF, SGOF, SGWFN)"
    )
    krfamily: Literal["COR", "LET"] = Field("LET", description="Correlation family (Corey or LET)")

    # Max rel perms
    kromax: float = Field(1.0, ge=0, le=1, description="Max oil rel perm")
    krwmax: Optional[float] = Field(None, ge=0, le=1, description="Max water rel perm (SWOF)")
    krgmax: Optional[float] = Field(None, ge=0, le=1, description="Max gas rel perm (SGOF/SGWFN)")

    # Saturations
    swc: float = Field(0.0, ge=0, le=1, description="Connate water saturation")
    swcr: Optional[float] = Field(None, ge=0, le=1, description="Critical water sat (Corey)")
    sorg: Optional[float] = Field(None, ge=0, le=1, description="Residual oil to gas")
    sorw: Optional[float] = Field(None, ge=0, le=1, description="Residual oil to water")
    sgc: Optional[float] = Field(None, ge=0, le=1, description="Critical gas saturation")

    # Corey exponents
    no: Optional[float] = Field(None, gt=0, description="Oil Corey exponent")
    nw: Optional[float] = Field(None, gt=0, description="Water Corey exponent")
    ng: Optional[float] = Field(None, gt=0, description="Gas Corey exponent")

    # LET parameters - Oil
    Lo: Optional[float] = Field(None, gt=0, description="Oil L parameter (LET)")
    Eo: Optional[float] = Field(None, gt=0, description="Oil E parameter (LET)")
    To: Optional[float] = Field(None, gt=0, description="Oil T parameter (LET)")

    # LET parameters - Water
    Lw: Optional[float] = Field(None, gt=0, description="Water L parameter (LET)")
    Ew: Optional[float] = Field(None, gt=0, description="Water E parameter (LET)")
    Tw: Optional[float] = Field(None, gt=0, description="Water T parameter (LET)")

    # LET parameters - Gas
    Lg: Optional[float] = Field(None, gt=0, description="Gas L parameter (LET)")
    Eg: Optional[float] = Field(None, gt=0, description="Gas E parameter (LET)")
    Tg: Optional[float] = Field(None, gt=0, description="Gas T parameter (LET)")


class InfluenceTableRequest(BaseModel):
    """Request model for Van Everdingen & Hurst aquifer influence tables."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start": 0.01,
                "end": 1000.0,
                "rows": 25,
                "res": 10,
                "aqunum": 1,
                "infl": "pot",
                "ei": True,
            }
        }
    )

    start: float = Field(0.01, gt=0, description="Starting dimensionless time")
    end: float = Field(1000.0, gt=0, description="Ending dimensionless time")
    rows: int = Field(25, gt=0, le=200, description="Number of table rows")
    res: int = Field(10, gt=1, le=50, description="Resolution for integration")
    aqunum: int = Field(1, ge=1, le=10, description="Aquifer number for ECLIPSE")
    infl: Literal["pot", "press"] = Field(
        "pot", description="Influence function type (pot or press)"
    )
    ei: bool = Field(True, description="Use exponential integral")
    piston: bool = Field(False, description="Piston-like aquifer")
    td_scale: Optional[float] = Field(None, gt=0, description="Time dimension scaling")


class RachfordRiceRequest(BaseModel):
    """Request model for Rachford-Rice flash calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "zis": [0.5, 0.3, 0.2],
                "Kis": [1.5, 0.9, 0.3],
            }
        }
    )

    zis: List[float] = Field(..., min_length=2, description="Overall mole fractions")
    Kis: List[float] = Field(..., min_length=2, description="K-values (yi/xi)")

    @field_validator("zis", "Kis")
    @classmethod
    def validate_composition(cls, v):
        """Validate composition arrays."""
        if not all(val >= 0 for val in v):
            raise ValueError("All values must be non-negative")
        return v

    @field_validator("zis")
    @classmethod
    def validate_sum(cls, v):
        """Validate sum of mole fractions."""
        total = sum(v)
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Mole fractions must sum to 1.0 (got {total})")
        return v


class ExtractProblemCellsRequest(BaseModel):
    """Request model for ECLIPSE problem cell extraction."""

    filename: str = Field(..., description="Path to ECLIPSE/Intersect PRT file")
    silent: bool = Field(True, description="Suppress console output")


class ZipSimDeckRequest(BaseModel):
    """Request model for simulation deck file checking."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "files2scrape": ["CASE.DATA"],
                "tozip": False,
                "console_summary": True,
            }
        }
    )

    files2scrape: List[str] = Field(
        ..., min_length=1, description="List of deck files to process (e.g., ['CASE.DATA'])"
    )
    tozip: bool = Field(False, description="Create zip archive of all referenced files")
    console_summary: bool = Field(True, description="Print summary to console")


class BlackOilTableRequest2(BaseModel):
    """Request model for make_bot_og black oil table generation."""

    pi: float = Field(..., gt=0, description="Initial pressure (psia | barsa)")
    api: float = Field(..., gt=0, le=100, description="Oil API gravity")
    degf: float = Field(..., description="Temperature (deg F | deg C)")
    sg_g: float = Field(..., gt=0, le=3, description="Gas specific gravity")
    pmax: float = Field(..., gt=0, description="Maximum pressure (psia | barsa)")
    pb: float = Field(0.0, ge=0, description="Bubble point (0 = calculate)")
    rsb: float = Field(0.0, ge=0, description="Solution GOR at Pb")
    pmin: float = Field(25.0, gt=0, description="Minimum pressure")
    nrows: int = Field(20, gt=0, le=200, description="Number of rows")
    wt: float = Field(0.0, ge=0, le=30, description="Brine salinity (wt%)")
    ch4_sat: float = Field(0.0, ge=0, le=1, description="Methane saturation (0-1)")
    export: bool = Field(False, description="Write PVTO/PVDG/PVDO files")
    pvto: bool = Field(False, description="Generate PVTO format (vs PVDO)")
    vis_frac: float = Field(1.0, gt=0, description="Viscosity scaling factor")
    metric: bool = Field(False, description="Use metric units")


class PVTWTableRequest(BaseModel):
    """Request model for PVTW table generation."""

    pi: float = Field(..., gt=0, description="Reference pressure (psia | barsa)")
    degf: float = Field(..., description="Temperature (deg F | deg C)")
    wt: float = Field(0.0, ge=0, le=30, description="Salt wt% (0-100)")
    ch4_sat: float = Field(0.0, ge=0, le=1, description="Methane saturation (0-1)")
    pmin: float = Field(500.0, gt=0, description="Minimum pressure")
    pmax: float = Field(10000.0, gt=0, description="Maximum pressure")
    nrows: int = Field(20, gt=0, le=200, description="Number of rows")
    export: bool = Field(False, description="Write PVTW.INC file")
    metric: bool = Field(False, description="Use metric units")


class FitRelPermRequest(BaseModel):
    """Request model for relative permeability curve fitting."""

    sw: List[float] = Field(..., description="Saturation values")
    kr: List[float] = Field(..., description="Measured relative permeability values")
    krfamily: Literal["COR", "LET", "JER"] = Field(
        "COR", description="Model: COR (Corey), LET, JER (Jerauld)"
    )
    krmax: float = Field(1.0, gt=0, le=1, description="Maximum kr endpoint")
    sw_min: float = Field(0.0, ge=0, le=1, description="Minimum saturation endpoint")
    sw_max: float = Field(1.0, ge=0, le=1, description="Maximum saturation endpoint")


class FitRelPermBestRequest(BaseModel):
    """Request model for best-fit relative permeability model selection."""

    sw: List[float] = Field(..., description="Saturation values")
    kr: List[float] = Field(..., description="Measured relative permeability values")
    krmax: float = Field(1.0, gt=0, le=1, description="Maximum kr endpoint")
    sw_min: float = Field(0.0, ge=0, le=1, description="Minimum saturation endpoint")
    sw_max: float = Field(1.0, ge=0, le=1, description="Maximum saturation endpoint")


class JerauldRequest(BaseModel):
    """Request model for Jerauld relative permeability evaluation."""

    s: List[float] = Field(..., min_length=2, description="Normalized saturation values (0-1)")
    a: float = Field(..., description="Jerauld 'a' parameter")
    b: float = Field(..., description="Jerauld 'b' parameter")


class IsLETPhysicalRequest(BaseModel):
    """Request model for LET physical validity check."""

    s: List[float] = Field(..., min_length=2, description="Normalized saturation values (0-1)")
    L: float = Field(..., gt=0, description="LET L parameter")
    E: float = Field(..., gt=0, description="LET E parameter")
    T: float = Field(..., gt=0, description="LET T parameter")
