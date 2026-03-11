"""Pydantic models for Material Balance calculations."""

from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class GasMatbalRequest(BaseModel):
    """Request model for P/Z gas material balance."""

    pressures: List[float] = Field(
        ...,
        description="Reservoir pressures at each survey (psia | barsa). First = initial pressure",
    )
    cumulative_gas: List[float] = Field(
        ...,
        description="Cumulative gas production at each survey (user units — OGIP in same units)",
    )
    temperature: float = Field(..., description="Reservoir temperature (deg F | deg C)")
    gas_sg: float = Field(0.65, ge=0.5, le=2.0, description="Gas specific gravity (air=1)")
    co2: float = Field(0.0, ge=0, le=1, description="CO2 mole fraction")
    h2s: float = Field(0.0, ge=0, le=1, description="H2S mole fraction")
    n2: float = Field(0.0, ge=0, le=1, description="N2 mole fraction")
    h2: float = Field(0.0, ge=0, le=1, description="H2 mole fraction")
    cumulative_water: Optional[List[float]] = Field(
        None, description="Cumulative water production (optional)"
    )
    water_fvf: float = Field(1.0, gt=0, description="Water FVF (rb/stb)")
    water_influx: Optional[List[float]] = Field(
        None, description="Cumulative water influx (optional, for Havlena-Odeh)"
    )
    z_method: Literal["DAK", "HY", "WYW", "BUR"] = Field("DAK", description="Z-factor method")
    c_method: Literal["PMC", "SUT", "BUR"] = Field("PMC", description="Critical properties method")
    metric: bool = Field(False, description="Use metric units (barsa, degC)")


class OilMatbalRequest(BaseModel):
    """Request model for Havlena-Odeh oil material balance."""

    pressures: List[float] = Field(
        ...,
        description="Reservoir pressures at each survey (psia | barsa). First = initial pressure",
    )
    cumulative_oil: List[float] = Field(
        ..., description="Cumulative oil production (STB | sm3) at each pressure step"
    )
    temperature: float = Field(..., description="Reservoir temperature (deg F | deg C)")
    api: float = Field(0.0, ge=0, le=100, description="Stock tank oil API gravity")
    sg_sp: float = Field(0.0, ge=0, le=3, description="Separator gas specific gravity")
    sg_g: float = Field(0.0, ge=0, le=3, description="Weighted average surface gas SG")
    pb: float = Field(0.0, ge=0, description="Bubble point pressure (psia | barsa)")
    rsb: float = Field(0.0, ge=0, description="Solution GOR at Pb (scf/stb | sm3/sm3)")
    producing_gor: Optional[List[float]] = Field(
        None, description="Cumulative producing GOR at each step"
    )
    cumulative_water: Optional[List[float]] = Field(None, description="Cumulative water production")
    water_injection: Optional[List[float]] = Field(None, description="Cumulative water injection")
    gas_injection: Optional[List[float]] = Field(None, description="Cumulative gas injection")
    water_fvf: float = Field(1.0, gt=0, description="Water FVF")
    gas_cap_ratio: float = Field(0.0, ge=0, description="Gas cap ratio m = G*Bgi/(N*Boi)")
    cf: float = Field(0.0, ge=0, description="Formation compressibility (1/psi | 1/bar)")
    sw_i: float = Field(0.0, ge=0, le=1, description="Initial water saturation")
    cw: float = Field(0.0, ge=0, description="Water compressibility (1/psi | 1/bar)")
    rs_method: Literal["VELAR", "STAN", "VALMC"] = Field("VELAR", description="Solution GOR method")
    bo_method: Literal["MCAIN", "STAN"] = Field("MCAIN", description="Oil FVF method")
    z_method: Literal["DAK", "HY", "WYW", "BUR"] = Field("DAK", description="Z-factor method")
    c_method: Literal["PMC", "SUT", "BUR"] = Field("PMC", description="Critical properties method")
    metric: bool = Field(False, description="Use metric units")
