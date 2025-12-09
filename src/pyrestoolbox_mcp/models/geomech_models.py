"""Pydantic models for Geomechanics calculations."""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, Union, List, Optional
import numpy as np


class VerticalStressRequest(BaseModel):
    """Request model for vertical stress (overburden) calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "depth": 10000.0,
                "water_depth": 0.0,
                "avg_density": 144.0,
                "water_density": 64.0,
            }
        }
    )

    depth: float = Field(..., gt=0, description="True vertical depth below surface (ft)")
    water_depth: float = Field(
        0.0, ge=0, description="Water depth for offshore wells (ft)"
    )
    avg_density: float = Field(
        144.0, gt=0, le=300, description="Average bulk density of overburden (lb/ft³)"
    )
    water_density: float = Field(
        64.0, gt=0, le=100, description="Water density (lb/ft³) - fresh=62.4, seawater=64.0"
    )


class PorePressureEatonRequest(BaseModel):
    """Request model for pore pressure calculation using Eaton's method."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "depth": 10000.0,
                "observed_value": 100.0,
                "normal_value": 70.0,
                "overburden_psi": 10400.0,
                "eaton_exponent": 3.0,
                "method": "sonic",
            }
        }
    )

    depth: float = Field(..., gt=0, description="True vertical depth (ft)")
    observed_value: float = Field(
        ..., gt=0, description="Observed sonic (μs/ft) or resistivity (ohm-m)"
    )
    normal_value: float = Field(
        ..., gt=0, description="Normal compaction trend value at this depth"
    )
    overburden_psi: float = Field(..., gt=0, description="Overburden stress at depth (psi)")
    eaton_exponent: float = Field(
        3.0, gt=0, le=5, description="Eaton exponent (3.0 for sonic, 1.2 for resistivity)"
    )
    method: Literal["sonic", "resistivity"] = Field(
        "sonic", description="Method type"
    )


class EffectiveStressRequest(BaseModel):
    """Request model for effective stress calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_stress": 10400.0,
                "pore_pressure": 4680.0,
                "biot_coefficient": 1.0,
            }
        }
    )

    total_stress: Union[float, List[float]] = Field(
        ..., description="Total stress (psi) - scalar or array"
    )
    pore_pressure: Union[float, List[float]] = Field(
        ..., description="Formation pore pressure (psi) - scalar or array"
    )
    biot_coefficient: float = Field(
        1.0, gt=0, le=1, description="Biot's coefficient (0.6-1.0 for most rocks)"
    )


class HorizontalStressRequest(BaseModel):
    """Request model for horizontal stress calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vertical_stress": 10400.0,
                "pore_pressure": 4680.0,
                "poisson_ratio": 0.25,
                "tectonic_factor": 0.0,
                "biot_coefficient": 1.0,
            }
        }
    )

    vertical_stress: float = Field(..., gt=0, description="Total vertical stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    poisson_ratio: float = Field(
        ..., gt=0, lt=0.5, description="Poisson's ratio (0.15-0.40 typical)"
    )
    tectonic_factor: float = Field(
        0.0, ge=0, le=1, description="Tectonic stress multiplier (0=passive, 0.5=strike-slip, 1.0=reverse)"
    )
    biot_coefficient: float = Field(
        1.0, gt=0, le=1, description="Biot's coefficient"
    )


class ElasticModuliRequest(BaseModel):
    """Request model for elastic moduli conversion (provide any 2)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "youngs_modulus": 1000000.0,
                "poisson_ratio": 0.25,
            }
        }
    )

    youngs_modulus: Optional[float] = Field(None, gt=0, description="Young's modulus E (psi)")
    bulk_modulus: Optional[float] = Field(None, gt=0, description="Bulk modulus K (psi)")
    shear_modulus: Optional[float] = Field(None, gt=0, description="Shear modulus G (psi)")
    poisson_ratio: Optional[float] = Field(None, gt=-1, lt=0.5, description="Poisson's ratio ν")
    lame_parameter: Optional[float] = Field(None, description="Lamé's first parameter λ (psi)")

    @field_validator("poisson_ratio")
    @classmethod
    def validate_poisson(cls, v):
        """Validate Poisson's ratio for physical bounds."""
        if v is not None and (v < 0 or v >= 0.5):
            raise ValueError("Poisson's ratio must be between 0 and 0.5 for stable materials")
        return v


class RockStrengthRequest(BaseModel):
    """Request model for rock strength calculation using Mohr-Coulomb."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cohesion": 500.0,
                "friction_angle": 30.0,
                "effective_stress_min": 2000.0,
            }
        }
    )

    cohesion: float = Field(..., ge=0, description="Rock cohesion (psi)")
    friction_angle: float = Field(
        ..., gt=0, lt=90, description="Internal friction angle (degrees, 20-40° typical)"
    )
    effective_stress_min: float = Field(
        ..., ge=0, description="Minimum effective principal stress (psi)"
    )


class DynamicToStaticRequest(BaseModel):
    """Request model for dynamic to static moduli conversion."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dynamic_youngs": 1500000.0,
                "dynamic_poisson": 0.20,
                "correlation": "eissa_kazi",
                "lithology": "sandstone",
            }
        }
    )

    dynamic_youngs: Optional[float] = Field(None, gt=0, description="Dynamic Young's modulus (psi)")
    dynamic_poisson: Optional[float] = Field(None, gt=0, lt=0.5, description="Dynamic Poisson's ratio")
    correlation: Literal["eissa_kazi", "plona_cook", "linear"] = Field(
        "eissa_kazi", description="Correlation method"
    )
    lithology: Literal["sandstone", "shale", "carbonate"] = Field(
        "sandstone", description="Rock lithology"
    )


class BreakoutWidthRequest(BaseModel):
    """Request model for borehole breakout width calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_h_max": 8500.0,
                "sigma_h_min": 6500.0,
                "pore_pressure": 4680.0,
                "mud_weight": 9.0,
                "wellbore_azimuth": 45.0,
                "ucs": 3000.0,
                "friction_angle": 30.0,
            }
        }
    )

    sigma_h_max: float = Field(..., gt=0, description="Maximum horizontal stress (psi)")
    sigma_h_min: float = Field(..., gt=0, description="Minimum horizontal stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    mud_weight: float = Field(..., gt=0, description="Drilling fluid density (ppg)")
    wellbore_azimuth: float = Field(
        ..., ge=0, le=360, description="Well azimuth (degrees, 0-360)"
    )
    ucs: float = Field(..., gt=0, description="Unconfined compressive strength (psi)")
    friction_angle: float = Field(
        ..., gt=0, lt=90, description="Internal friction angle (degrees)"
    )


class FractureGradientRequest(BaseModel):
    """Request model for fracture gradient calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "depth": 10000.0,
                "vertical_stress": 10400.0,
                "pore_pressure": 4680.0,
                "poisson_ratio": 0.25,
                "method": "eaton",
            }
        }
    )

    depth: float = Field(..., gt=0, description="True vertical depth (ft)")
    sigma_h_min: Optional[float] = Field(None, gt=0, description="Minimum horizontal stress (psi) if known")
    vertical_stress: float = Field(..., gt=0, description="Overburden stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    poisson_ratio: float = Field(
        0.25, gt=0, lt=0.5, description="Poisson's ratio for estimation methods"
    )
    method: Literal["hubbert_willis", "eaton", "matthews_kelly"] = Field(
        "eaton", description="Calculation method"
    )


class MudWeightWindowRequest(BaseModel):
    """Request model for safe mud weight window calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pore_pressure": 4680.0,
                "fracture_pressure": 7800.0,
                "depth": 10000.0,
                "safety_margin_overbalance": 0.5,
                "safety_margin_fracture": 0.5,
            }
        }
    )

    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    fracture_pressure: float = Field(..., gt=0, description="Formation fracture pressure (psi)")
    depth: float = Field(..., gt=0, description="True vertical depth (ft)")
    collapse_pressure: Optional[float] = Field(None, gt=0, description="Collapse pressure for stability (psi)")
    safety_margin_overbalance: float = Field(
        0.5, ge=0, description="Overbalance safety margin (ppg)"
    )
    safety_margin_fracture: float = Field(
        0.5, ge=0, description="Fracture safety margin (ppg)"
    )


class CriticalMudWeightRequest(BaseModel):
    """Request model for critical mud weight to prevent collapse."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_h_max": 8500.0,
                "sigma_h_min": 6500.0,
                "pore_pressure": 4680.0,
                "cohesion": 500.0,
                "friction_angle": 30.0,
                "wellbore_azimuth": 45.0,
                "wellbore_inclination": 0.0,
                "depth": 10000.0,
            }
        }
    )

    sigma_h_max: float = Field(..., gt=0, description="Maximum horizontal stress (psi)")
    sigma_h_min: float = Field(..., gt=0, description="Minimum horizontal stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    cohesion: float = Field(..., ge=0, description="Rock cohesion (psi)")
    friction_angle: float = Field(..., gt=0, lt=90, description="Internal friction angle (degrees)")
    wellbore_azimuth: float = Field(
        ..., ge=0, le=360, description="Well azimuth (degrees)"
    )
    wellbore_inclination: float = Field(
        0.0, ge=0, le=90, description="Well deviation from vertical (degrees)"
    )
    depth: float = Field(..., gt=0, description="True vertical depth (ft)")


class ReservoirCompactionRequest(BaseModel):
    """Request model for reservoir compaction calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pressure_drop": 1000.0,
                "reservoir_thickness": 100.0,
                "youngs_modulus": 500000.0,
                "poisson_ratio": 0.25,
                "biot_coefficient": 1.0,
            }
        }
    )

    pressure_drop: float = Field(..., gt=0, description="Reservoir pressure depletion (psi)")
    reservoir_thickness: float = Field(..., gt=0, description="Net pay thickness (ft)")
    pore_compressibility: Optional[float] = Field(
        None, gt=0, description="Pore compressibility (1/psi) if known"
    )
    bulk_compressibility: Optional[float] = Field(
        None, gt=0, description="Bulk compressibility (1/psi) if known"
    )
    youngs_modulus: float = Field(..., gt=0, description="Static Young's modulus (psi)")
    poisson_ratio: float = Field(..., gt=0, lt=0.5, description="Poisson's ratio")
    biot_coefficient: float = Field(
        1.0, gt=0, le=1, description="Biot coefficient"
    )


class PoreCompressibilityRequest(BaseModel):
    """Request model for pore volume compressibility calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "porosity": 0.20,
                "youngs_modulus": 500000.0,
                "poisson_ratio": 0.25,
                "grain_compressibility": 3e-7,
            }
        }
    )

    bulk_compressibility: Optional[float] = Field(
        None, gt=0, description="Rock bulk compressibility (1/psi)"
    )
    grain_compressibility: float = Field(
        3e-7, gt=0, description="Grain compressibility (1/psi, default 3e-7)"
    )
    porosity: float = Field(..., gt=0, lt=1, description="Formation porosity (fraction 0-1)")
    youngs_modulus: Optional[float] = Field(None, gt=0, description="Young's modulus for calculating Cb (psi)")
    poisson_ratio: Optional[float] = Field(None, gt=0, lt=0.5, description="Poisson's ratio for calculating Cb")


class LeakOffPressureRequest(BaseModel):
    """Request model for leak-off test analysis."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "leak_off_pressure": 2500.0,
                "mud_weight": 9.0,
                "test_depth": 10000.0,
                "pore_pressure": 4680.0,
                "test_type": "LOT",
            }
        }
    )

    leak_off_pressure: float = Field(..., gt=0, description="LOT pressure at surface (psi)")
    mud_weight: float = Field(..., gt=0, description="Mud weight during test (ppg)")
    test_depth: float = Field(..., gt=0, description="True vertical depth of test (ft)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure at test depth (psi)")
    test_type: Literal["LOT", "FIT"] = Field(
        "LOT", description="Test type - LOT (leak-off) or FIT (integrity test)"
    )


class FractureWidthRequest(BaseModel):
    """Request model for hydraulic fracture width calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "net_pressure": 500.0,
                "fracture_height": 100.0,
                "fracture_half_length": 500.0,
                "youngs_modulus": 1000000.0,
                "poisson_ratio": 0.25,
                "model": "PKN",
            }
        }
    )

    net_pressure: float = Field(..., gt=0, description="Net treating pressure (psi) = Pfrac - σh_min")
    fracture_height: float = Field(..., gt=0, description="Fracture height (ft), typically ≈ pay thickness")
    fracture_half_length: float = Field(..., gt=0, description="Fracture half-length (ft), one wing")
    youngs_modulus: float = Field(..., gt=0, description="Formation Young's modulus (psi)")
    poisson_ratio: float = Field(..., gt=0, lt=0.5, description="Poisson's ratio")
    model: Literal["PKN", "KGD"] = Field("PKN", description="Fracture model")


# ============================================================================
# NEW ADVANCED GEOMECHANICS MODELS
# ============================================================================


class StressPolygonRequest(BaseModel):
    """Request model for stress polygon analysis (allowable stress states)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vertical_stress": 10000.0,
                "pore_pressure": 4500.0,
                "friction_coefficient": 0.6,
                "sigma_h_min": 6500.0,
                "sigma_h_max": 8500.0,
            }
        }
    )

    vertical_stress: float = Field(..., gt=0, description="Vertical stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Pore pressure (psi)")
    friction_coefficient: float = Field(
        0.6, gt=0, lt=1.5, description="Fault friction coefficient (0.6-0.85 typical)"
    )
    sigma_h_min: Optional[float] = Field(None, gt=0, description="Actual min horizontal stress to plot (psi)")
    sigma_h_max: Optional[float] = Field(None, gt=0, description="Actual max horizontal stress to plot (psi)")


class SandProductionRequest(BaseModel):
    """Request model for sand production prediction (critical drawdown/velocity)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_h_max": 8500.0,
                "sigma_h_min": 6500.0,
                "pore_pressure": 4500.0,
                "ucs": 3000.0,
                "cohesion": 500.0,
                "friction_angle": 30.0,
                "wellbore_radius": 0.354,
                "perforation_depth": 0.5,
                "permeability": 100.0,
                "porosity": 0.20,
            }
        }
    )

    sigma_h_max: float = Field(..., gt=0, description="Maximum horizontal stress (psi)")
    sigma_h_min: float = Field(..., gt=0, description="Minimum horizontal stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    ucs: float = Field(..., gt=0, description="Unconfined compressive strength (psi)")
    cohesion: float = Field(..., ge=0, description="Rock cohesion (psi)")
    friction_angle: float = Field(..., gt=0, lt=90, description="Internal friction angle (degrees)")
    wellbore_radius: float = Field(0.354, gt=0, description="Wellbore radius (ft) - default 8.5 inch hole")
    perforation_depth: float = Field(0.5, gt=0, description="Perforation tunnel depth (ft)")
    permeability: float = Field(..., gt=0, description="Formation permeability (mD)")
    porosity: float = Field(..., gt=0, lt=1, description="Formation porosity (fraction)")


class FaultStabilityRequest(BaseModel):
    """Request model for fault stability analysis (Coulomb failure stress)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_1": 10000.0,
                "sigma_3": 6000.0,
                "pore_pressure": 4500.0,
                "fault_strike": 45.0,
                "fault_dip": 60.0,
                "sigma_1_azimuth": 0.0,
                "friction_coefficient": 0.6,
                "cohesion": 0.0,
            }
        }
    )

    sigma_1: float = Field(..., gt=0, description="Maximum principal stress (psi)")
    sigma_3: float = Field(..., gt=0, description="Minimum principal stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Pore pressure (psi)")
    fault_strike: float = Field(..., ge=0, le=360, description="Fault strike azimuth (degrees)")
    fault_dip: float = Field(..., gt=0, le=90, description="Fault dip angle (degrees from horizontal)")
    sigma_1_azimuth: float = Field(0.0, ge=0, le=360, description="σ1 azimuth (degrees from North)")
    friction_coefficient: float = Field(0.6, gt=0, lt=1.5, description="Fault friction coefficient")
    cohesion: float = Field(0.0, ge=0, description="Fault cohesion (psi) - typically 0 for reactivation")


class DeviatedWellStressRequest(BaseModel):
    """Request model for stress transformation to deviated wellbore."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_v": 10000.0,
                "sigma_h_max": 8500.0,
                "sigma_h_min": 6500.0,
                "sigma_h_max_azimuth": 45.0,
                "well_azimuth": 90.0,
                "well_inclination": 60.0,
                "pore_pressure": 4500.0,
                "mud_weight": 10.0,
                "depth": 10000.0,
            }
        }
    )

    sigma_v: float = Field(..., gt=0, description="Vertical stress (psi)")
    sigma_h_max: float = Field(..., gt=0, description="Maximum horizontal stress (psi)")
    sigma_h_min: float = Field(..., gt=0, description="Minimum horizontal stress (psi)")
    sigma_h_max_azimuth: float = Field(..., ge=0, le=360, description="σH_max azimuth from North (degrees)")
    well_azimuth: float = Field(..., ge=0, le=360, description="Well azimuth from North (degrees)")
    well_inclination: float = Field(..., ge=0, le=90, description="Well inclination from vertical (degrees)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    mud_weight: float = Field(..., gt=0, description="Drilling fluid density (ppg)")
    depth: float = Field(..., gt=0, description="True vertical depth (ft)")


class TensileFailureRequest(BaseModel):
    """Request model for tensile failure and breakdown pressure prediction."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_h_max": 8500.0,
                "sigma_h_min": 6500.0,
                "pore_pressure": 4500.0,
                "tensile_strength": 500.0,
                "thermal_stress": 0.0,
            }
        }
    )

    sigma_h_max: float = Field(..., gt=0, description="Maximum horizontal stress (psi)")
    sigma_h_min: float = Field(..., gt=0, description="Minimum horizontal stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    tensile_strength: float = Field(0.0, ge=0, description="Rock tensile strength (psi) - often ~UCS/10")
    thermal_stress: float = Field(0.0, description="Thermal stress contribution (psi) - negative for cooling")


class ShearFailureCriteriaRequest(BaseModel):
    """Request model for multiple shear failure criteria comparison."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_1": 10000.0,
                "sigma_2": 7500.0,
                "sigma_3": 5000.0,
                "ucs": 8000.0,
                "cohesion": 1500.0,
                "friction_angle": 30.0,
                "criteria": ["mohr_coulomb", "drucker_prager", "mogi_coulomb"],
            }
        }
    )

    sigma_1: float = Field(..., description="Maximum principal stress (psi)")
    sigma_2: float = Field(..., description="Intermediate principal stress (psi)")
    sigma_3: float = Field(..., ge=0, description="Minimum principal stress (psi)")
    ucs: float = Field(..., gt=0, description="Unconfined compressive strength (psi)")
    cohesion: float = Field(..., ge=0, description="Rock cohesion (psi)")
    friction_angle: float = Field(..., gt=0, lt=90, description="Internal friction angle (degrees)")
    criteria: List[Literal["mohr_coulomb", "drucker_prager", "mogi_coulomb", "modified_lade", "modified_wiebols"]] = Field(
        ["mohr_coulomb", "drucker_prager", "mogi_coulomb"],
        description="List of failure criteria to evaluate"
    )


class BreakoutStressInversionRequest(BaseModel):
    """Request model for stress estimation from observed breakout width."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "breakout_width": 60.0,
                "sigma_v": 10000.0,
                "pore_pressure": 4500.0,
                "mud_weight": 10.0,
                "ucs": 5000.0,
                "friction_angle": 30.0,
                "depth": 10000.0,
            }
        }
    )

    breakout_width: float = Field(..., gt=0, lt=180, description="Observed breakout angular width (degrees)")
    sigma_v: float = Field(..., gt=0, description="Vertical stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    mud_weight: float = Field(..., gt=0, description="Drilling fluid density during observation (ppg)")
    ucs: float = Field(..., gt=0, description="Unconfined compressive strength (psi)")
    friction_angle: float = Field(..., gt=0, lt=90, description="Internal friction angle (degrees)")
    depth: float = Field(..., gt=0, description="True vertical depth (ft)")


class BreakdownPressureRequest(BaseModel):
    """Request model for formation breakdown pressure calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_h_max": 8500.0,
                "sigma_h_min": 6500.0,
                "pore_pressure": 4500.0,
                "tensile_strength": 500.0,
                "poroelastic_constant": 0.0,
            }
        }
    )

    sigma_h_max: float = Field(..., gt=0, description="Maximum horizontal stress (psi)")
    sigma_h_min: float = Field(..., gt=0, description="Minimum horizontal stress (psi)")
    pore_pressure: float = Field(..., gt=0, description="Formation pore pressure (psi)")
    tensile_strength: float = Field(0.0, ge=0, description="Rock tensile strength (psi)")
    poroelastic_constant: float = Field(
        0.0, ge=0, le=1.0,
        description="Poroelastic constant η = α(1-2ν)/(1-ν), typically 0-0.5"
    )


class StressPathRequest(BaseModel):
    """Request model for stress path analysis during depletion/injection."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "initial_pore_pressure": 5000.0,
                "final_pore_pressure": 3000.0,
                "vertical_stress": 10000.0,
                "initial_sigma_h": 7000.0,
                "poisson_ratio": 0.25,
                "biot_coefficient": 1.0,
                "stress_path_coefficient": 0.67,
            }
        }
    )

    initial_pore_pressure: float = Field(..., gt=0, description="Initial formation pore pressure (psi)")
    final_pore_pressure: float = Field(..., gt=0, description="Final formation pore pressure (psi)")
    vertical_stress: float = Field(..., gt=0, description="Vertical stress - assumed constant (psi)")
    initial_sigma_h: float = Field(..., gt=0, description="Initial horizontal stress (psi)")
    poisson_ratio: float = Field(..., gt=0, lt=0.5, description="Poisson's ratio")
    biot_coefficient: float = Field(1.0, gt=0, le=1, description="Biot coefficient")
    stress_path_coefficient: Optional[float] = Field(
        None, gt=0, lt=1,
        description="Stress path coefficient γ = Δσh/ΔPp. If not provided, calculated from ν"
    )


class ThermalStressRequest(BaseModel):
    """Request model for thermal stress effects calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "temperature_change": -50.0,
                "youngs_modulus": 1000000.0,
                "poisson_ratio": 0.25,
                "thermal_expansion_coefficient": 6e-6,
                "biot_coefficient": 1.0,
            }
        }
    )

    temperature_change: float = Field(
        ..., description="Temperature change (degF) - negative for cooling, positive for heating"
    )
    youngs_modulus: float = Field(..., gt=0, description="Young's modulus (psi)")
    poisson_ratio: float = Field(..., gt=0, lt=0.5, description="Poisson's ratio")
    thermal_expansion_coefficient: float = Field(
        6e-6, gt=0, description="Linear thermal expansion coefficient (1/degF) - typical 5-8e-6"
    )
    biot_coefficient: float = Field(1.0, gt=0, le=1, description="Biot coefficient")


class UCSFromLogsRequest(BaseModel):
    """Request model for UCS estimation from well logs."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sonic_dt": 70.0,
                "porosity": 0.15,
                "youngs_modulus": 2000000.0,
                "lithology": "sandstone",
                "correlation": "mcnally",
            }
        }
    )

    sonic_dt: Optional[float] = Field(None, gt=0, description="Sonic transit time (μs/ft)")
    porosity: Optional[float] = Field(None, gt=0, lt=1, description="Porosity (fraction)")
    youngs_modulus: Optional[float] = Field(None, gt=0, description="Young's modulus (psi)")
    lithology: Literal["sandstone", "shale", "carbonate", "general"] = Field(
        "sandstone", description="Rock lithology for correlation selection"
    )
    correlation: Literal["mcnally", "horsrud", "chang", "lal", "vernik"] = Field(
        "mcnally", description="UCS correlation to use"
    )


class CriticalDrawdownRequest(BaseModel):
    """Request model for critical drawdown pressure calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sigma_h_max": 8500.0,
                "sigma_h_min": 6500.0,
                "reservoir_pressure": 5000.0,
                "ucs": 3000.0,
                "cohesion": 500.0,
                "friction_angle": 30.0,
                "wellbore_radius": 0.354,
            }
        }
    )

    sigma_h_max: float = Field(..., gt=0, description="Maximum horizontal stress (psi)")
    sigma_h_min: float = Field(..., gt=0, description="Minimum horizontal stress (psi)")
    reservoir_pressure: float = Field(..., gt=0, description="Initial reservoir pressure (psi)")
    ucs: float = Field(..., gt=0, description="Unconfined compressive strength (psi)")
    cohesion: float = Field(..., ge=0, description="Rock cohesion (psi)")
    friction_angle: float = Field(..., gt=0, lt=90, description="Internal friction angle (degrees)")
    wellbore_radius: float = Field(0.354, gt=0, description="Wellbore radius (ft)")
