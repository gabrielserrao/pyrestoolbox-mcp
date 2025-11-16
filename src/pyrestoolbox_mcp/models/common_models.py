"""Common Pydantic models shared across modules."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Union, List


class ArrayInput(BaseModel):
    """Base model for array inputs - supports both scalar and array values."""

    @staticmethod
    def to_value(field: Union[float, List[float]]) -> Union[float, List[float]]:
        """Convert input to appropriate type."""
        return field


class MethodResponse(BaseModel):
    """Standard response format with metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "value": 3456.7,
                "method": "VALMC",
                "units": "psia",
                "inputs": {
                    "api": 35.0,
                    "degf": 180.0,
                    "rsb": 800.0,
                    "sg_g": 0.75,
                },
            }
        }
    )

    value: Union[float, List[float], dict] = Field(
        ..., description="Calculated value(s)"
    )
    method: str = Field(..., description="Calculation method used")
    units: str = Field(..., description="Units of the result")
    inputs: dict = Field(..., description="Input parameters used")
