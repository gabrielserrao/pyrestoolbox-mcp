"""Pydantic models for Nodal Analysis / VLP / IPR calculations."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, List, Optional


class WellSegmentModel(BaseModel):
    """Model for a single wellbore segment."""

    md: float = Field(..., gt=0, description="Measured depth of segment (ft | m)")
    id: float = Field(..., gt=0, description="Internal diameter (inches | mm)")
    deviation: float = Field(0.0, ge=0, le=90, description="Deviation from vertical (degrees)")
    roughness: Optional[float] = Field(
        None, description="Pipe roughness (inches | mm). Default 0.0006 in"
    )


class CompletionModel(BaseModel):
    """Model for wellbore completion description."""

    tubing_id: float = Field(0.0, ge=0, description="Tubing ID (inches | mm)")
    tubing_length: float = Field(0.0, ge=0, description="Tubing length (ft | m)")
    wellhead_temp: float = Field(
        ..., description="Tubing head (wellhead) temperature (degF | degC)"
    )
    bht: float = Field(..., description="Bottom hole temperature (degF | degC)")
    roughness: float = Field(0.0006, gt=0, description="Tubing roughness (inches | mm)")
    casing_id: float = Field(0.0, ge=0, description="Casing ID (0 = no casing section)")
    casing_roughness: Optional[float] = Field(
        None, description="Casing roughness (defaults to tubing roughness)"
    )
    segments: Optional[List[WellSegmentModel]] = Field(
        None, description="Multi-segment completion (overrides tubing_id/length)"
    )
    metric: bool = Field(False, description="Use metric units (m, mm)")


class ReservoirModel(BaseModel):
    """Model for reservoir description for IPR calculations."""

    pr: float = Field(..., gt=0, description="Reservoir pressure (psia | barsa)")
    degf: float = Field(..., description="Reservoir temperature (degF | degC)")
    k: float = Field(..., gt=0, description="Permeability (mD)")
    h: float = Field(..., gt=0, description="Net pay thickness (ft | m)")
    re: float = Field(..., gt=0, description="Drainage radius (ft | m)")
    rw: float = Field(..., gt=0, description="Wellbore radius (ft | m)")
    S: float = Field(0.0, description="Skin factor")
    D: float = Field(0.0, ge=0, description="Non-Darcy coefficient (day/Mscf)")
    metric: bool = Field(False, description="Use metric units")


class FBHPRequest(BaseModel):
    """Request model for flowing bottom hole pressure calculation."""

    thp: float = Field(..., gt=0, description="Tubing head pressure (psia | barsa)")
    completion: CompletionModel = Field(..., description="Wellbore completion")
    vlp_method: Literal["HB", "WG", "GRAY", "BB"] = Field(
        "WG", description="VLP correlation: HB (Hagedorn-Brown), WG (Woldesemayat-Ghajar), GRAY, BB (Beggs & Brill)"
    )
    well_type: Literal["gas", "oil"] = Field("gas", description="Well type")
    gas_rate_mmscfd: float = Field(0.0, ge=0, description="Gas rate (MMscf/d | sm3/d)")
    cgr: float = Field(0.0, ge=0, description="Condensate-gas ratio (STB/MMscf)")
    water_rate_bwpd: float = Field(0.0, ge=0, description="Water rate (STB/d | sm3/d)")
    oil_viscosity: float = Field(1.0, gt=0, description="Condensate/oil viscosity (cP)")
    api: float = Field(45.0, gt=0, le=100, description="Condensate/oil API gravity")
    reservoir_pressure: float = Field(0.0, ge=0, description="Reservoir pressure for condensate dropout")
    total_liquid_stbpd: float = Field(0.0, ge=0, description="Total liquid rate for oil wells (STB/d)")
    gor: float = Field(0.0, ge=0, description="Producing GOR for oil wells (scf/stb)")
    water_cut: float = Field(0.0, ge=0, le=1, description="Water cut fraction (0-1)")
    water_sg: float = Field(1.07, gt=0, description="Water specific gravity")
    gas_sg: float = Field(0.65, gt=0, le=3, description="Gas specific gravity")
    injection: bool = Field(False, description="Injection well mode")
    metric: bool = Field(False, description="Use metric units")


class IPRCurveRequest(BaseModel):
    """Request model for IPR curve generation."""

    reservoir: ReservoirModel = Field(..., description="Reservoir description")
    well_type: Literal["gas", "oil", "water"] = Field("gas", description="Well type")
    n_points: int = Field(20, gt=1, le=100, description="Number of pressure points")
    min_pwf: Optional[float] = Field(
        None, description="Minimum flowing BHP (psia | barsa). Default 14.7 psia"
    )
    water_cut: float = Field(0.0, ge=0, le=1, description="Water cut fraction (oil wells)")
    water_sg: float = Field(1.07, gt=0, description="Water specific gravity")
    bo: float = Field(1.2, gt=0, description="Oil FVF if no OilPVT (rb/stb)")
    uo: float = Field(1.0, gt=0, description="Oil viscosity if no OilPVT (cP)")
    gas_sg: float = Field(0.65, gt=0, le=3, description="Gas SG if no GasPVT")
    metric: bool = Field(False, description="Use metric units")


class OutflowCurveRequest(BaseModel):
    """Request model for VLP outflow curve generation."""

    thp: float = Field(..., gt=0, description="Tubing head pressure (psia | barsa)")
    completion: CompletionModel = Field(..., description="Wellbore completion")
    vlp_method: Literal["HB", "WG", "GRAY", "BB"] = Field("WG", description="VLP correlation")
    well_type: Literal["gas", "oil"] = Field("gas", description="Well type")
    rates: Optional[List[float]] = Field(
        None, description="Rates to evaluate (auto-generated if None)"
    )
    n_rates: int = Field(20, gt=1, le=100, description="Number of rate points if rates is None")
    max_rate: Optional[float] = Field(None, description="Maximum rate for auto-generation")
    gas_rate_mmscfd: float = Field(0.0, ge=0, description="Not used directly; rates override")
    cgr: float = Field(0.0, ge=0, description="Condensate-gas ratio")
    water_rate_bwpd: float = Field(0.0, ge=0, description="Water rate")
    oil_viscosity: float = Field(1.0, gt=0, description="Oil viscosity (cP)")
    api: float = Field(45.0, gt=0, le=100, description="API gravity")
    gor: float = Field(0.0, ge=0, description="Producing GOR for oil wells")
    water_cut: float = Field(0.0, ge=0, le=1, description="Water cut fraction")
    water_sg: float = Field(1.07, gt=0, description="Water SG")
    gas_sg: float = Field(0.65, gt=0, le=3, description="Gas SG")
    injection: bool = Field(False, description="Injection mode")
    metric: bool = Field(False, description="Use metric units")


class OperatingPointRequest(BaseModel):
    """Request model for VLP/IPR operating point calculation."""

    thp: float = Field(..., gt=0, description="Tubing head pressure (psia | barsa)")
    completion: CompletionModel = Field(..., description="Wellbore completion")
    reservoir: ReservoirModel = Field(..., description="Reservoir description")
    vlp_method: Literal["HB", "WG", "GRAY", "BB"] = Field("WG", description="VLP correlation")
    well_type: Literal["gas", "oil"] = Field("gas", description="Well type")
    cgr: float = Field(0.0, ge=0, description="Condensate-gas ratio")
    water_rate_bwpd: float = Field(0.0, ge=0, description="Water rate")
    oil_viscosity: float = Field(1.0, gt=0, description="Oil viscosity (cP)")
    api: float = Field(45.0, gt=0, le=100, description="API gravity")
    gor: float = Field(0.0, ge=0, description="Producing GOR")
    water_cut: float = Field(0.0, ge=0, le=1, description="Water cut fraction")
    water_sg: float = Field(1.07, gt=0, description="Water SG")
    gas_sg: float = Field(0.65, gt=0, le=3, description="Gas SG")
    bo: float = Field(1.2, gt=0, description="Oil FVF")
    uo: float = Field(1.0, gt=0, description="Oil viscosity")
    n_points: int = Field(25, gt=1, le=100, description="Number of points for curves")
    metric: bool = Field(False, description="Use metric units")


class VFPProdRequest(BaseModel):
    """Request model for VFPPROD table generation."""

    table_num: int = Field(..., ge=1, description="VFP table number")
    completion: CompletionModel = Field(..., description="Wellbore completion")
    well_type: Literal["gas", "oil"] = Field("gas", description="Well type")
    vlp_method: Literal["HB", "WG", "GRAY", "BB"] = Field("WG", description="VLP correlation")
    flo_rates: Optional[List[float]] = Field(None, description="Flow rates (auto if None)")
    thp_values: Optional[List[float]] = Field(None, description="THP values (auto if None)")
    wfr_values: Optional[List[float]] = Field(None, description="Water fraction values")
    gfr_values: Optional[List[float]] = Field(None, description="Gas fraction values")
    alq_values: Optional[List[float]] = Field(None, description="Artificial lift values")
    gas_sg: float = Field(0.65, gt=0, le=3, description="Gas SG")
    oil_viscosity: float = Field(1.0, gt=0, description="Oil viscosity (cP)")
    api: float = Field(45.0, gt=0, le=100, description="API gravity")
    reservoir_pressure: float = Field(0.0, ge=0, description="Reservoir pressure")
    water_sg: float = Field(1.07, gt=0, description="Water SG")
    datum_depth: float = Field(0.0, ge=0, description="Reference depth (ft | m)")
    metric: bool = Field(False, description="Use metric units")


class VFPInjRequest(BaseModel):
    """Request model for VFPINJ table generation."""

    table_num: int = Field(..., ge=1, description="VFP table number")
    completion: CompletionModel = Field(..., description="Wellbore completion")
    flo_type: Literal["WAT", "GAS", "OIL"] = Field("WAT", description="Flow rate type")
    vlp_method: Literal["HB", "WG", "GRAY", "BB"] = Field("WG", description="VLP correlation")
    flo_rates: Optional[List[float]] = Field(None, description="Flow rates")
    thp_values: Optional[List[float]] = Field(None, description="THP values")
    gas_sg: float = Field(0.65, gt=0, le=3, description="Gas SG")
    water_sg: float = Field(1.07, gt=0, description="Water SG")
    api: float = Field(35.0, gt=0, le=100, description="Oil API gravity")
    datum_depth: float = Field(0.0, ge=0, description="Reference depth (ft | m)")
    metric: bool = Field(False, description="Use metric units")
