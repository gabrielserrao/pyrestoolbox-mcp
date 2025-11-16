"""Pydantic models for Component Library access."""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class ComponentPropertiesRequest(BaseModel):
    """Request model for component critical properties lookup."""

    component: str = Field(
        ..., description="Component name (e.g., 'Methane', 'C1', 'Ethane', 'C2')"
    )
    eos: Literal["PR79", "PR77", "SRK", "RK"] = Field(
        "PR79", description="Equation of State model"
    )
