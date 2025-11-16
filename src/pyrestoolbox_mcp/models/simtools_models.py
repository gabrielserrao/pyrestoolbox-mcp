"""Pydantic models for Simulation Tools calculations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Union, List, Optional


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
        "SWOF", description="Table type (SWOF, SGOF, SGWFN)")
    krfamily: Literal["COR", "LET"] = Field(
        "LET", description="Correlation family (Corey or LET)")

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
        "pot", description="Influence function type (pot or press)")
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

    files2scrape: List[str] = Field(..., min_length=1, description="List of deck files to process (e.g., ['CASE.DATA'])")
    tozip: bool = Field(False, description="Create zip archive of all referenced files")
    console_summary: bool = Field(True, description="Print summary to console")
