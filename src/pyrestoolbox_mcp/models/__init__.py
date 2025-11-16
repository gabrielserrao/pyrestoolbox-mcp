"""Pydantic models for request validation."""

from .common_models import MethodResponse, ArrayInput
from .oil_models import (
    BubblePointRequest,
    SolutionGORRequest,
    OilFVFRequest,
    OilViscosityRequest,
    OilDensityRequest,
    OilCompressibilityRequest,
    APIConversionRequest,
    SGConversionRequest,
    BlackOilTableRequest,
    EvolvedGasSGRequest,
    JacobyAromaticitySGRequest,
    TwuPropertiesRequest,
    WeightedAverageGasSGRequest,
    StockTankGORRequest,
    CheckGasSGsRequest,
)
from .gas_models import (
    ZFactorRequest,
    GasFVFRequest,
    GasViscosityRequest,
    GasDensityRequest,
    GasCompressibilityRequest,
    CriticalPropertiesRequest,
    GasPseudopressureRequest,
    GasPressureFromPZRequest,
    GasSGFromGradientRequest,
    GasWaterContentRequest,
    GasSGFromCompositionRequest,
)
from .library_models import (
    ComponentPropertiesRequest,
)
from .layer_models import (
    LorenzRequest,
    FlowFractionRequest,
    LayerDistributionRequest,
)
from .brine_models import (
    BrinePropertiesRequest,
    CO2BrineMixtureRequest,
)
from .simtools_models import (
    RelPermTableRequest,
    InfluenceTableRequest,
    RachfordRiceRequest,
    ExtractProblemCellsRequest,
    ZipSimDeckRequest,
)
from .inflow_models import (
    OilRateRadialRequest,
    OilRateLinearRequest,
    GasRateRadialRequest,
    GasRateLinearRequest,
)

__all__ = [
    "MethodResponse",
    "ArrayInput",
    "BubblePointRequest",
    "SolutionGORRequest",
    "OilFVFRequest",
    "OilViscosityRequest",
    "OilDensityRequest",
    "OilCompressibilityRequest",
    "APIConversionRequest",
    "SGConversionRequest",
    "BlackOilTableRequest",
    "EvolvedGasSGRequest",
    "JacobyAromaticitySGRequest",
    "TwuPropertiesRequest",
    "WeightedAverageGasSGRequest",
    "StockTankGORRequest",
    "CheckGasSGsRequest",
    "ZFactorRequest",
    "GasFVFRequest",
    "GasViscosityRequest",
    "GasDensityRequest",
    "GasCompressibilityRequest",
    "CriticalPropertiesRequest",
    "GasPseudopressureRequest",
    "GasPressureFromPZRequest",
    "GasSGFromGradientRequest",
    "GasWaterContentRequest",
    "GasSGFromCompositionRequest",
    "RelPermTableRequest",
    "InfluenceTableRequest",
    "RachfordRiceRequest",
    "ExtractProblemCellsRequest",
    "ZipSimDeckRequest",
    "BrinePropertiesRequest",
    "CO2BrineMixtureRequest",
    "LorenzRequest",
    "FlowFractionRequest",
    "LayerDistributionRequest",
    "ComponentPropertiesRequest",
    "OilRateRadialRequest",
    "OilRateLinearRequest",
    "GasRateRadialRequest",
    "GasRateLinearRequest",
]
