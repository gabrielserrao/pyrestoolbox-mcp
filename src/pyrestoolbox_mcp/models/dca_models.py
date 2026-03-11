"""Pydantic models for Decline Curve Analysis calculations."""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Union, List, Optional


class FitDeclineRequest(BaseModel):
    """Request model for decline curve fitting to rate vs time data."""

    time: List[float] = Field(
        ..., description="Time array (user-defined units, e.g. months or years)"
    )
    rates: List[float] = Field(..., description="Production rate array (must be > 0)")
    method: Literal["exponential", "harmonic", "hyperbolic", "duong", "best"] = Field(
        "best", description="Decline model to fit. 'best' tries all and returns highest R-squared"
    )
    t_start: Optional[float] = Field(None, description="Start of fitting window (inclusive)")
    t_end: Optional[float] = Field(None, description="End of fitting window (inclusive)")

    @field_validator("rates")
    @classmethod
    def validate_rates(cls, v):
        if not all(r > 0 for r in v):
            raise ValueError("All rate values must be positive")
        return v


class FitDeclineCumRequest(BaseModel):
    """Request model for decline curve fitting to rate vs cumulative data."""

    cumulative_production: List[float] = Field(..., description="Cumulative production array")
    rates: List[float] = Field(..., description="Production rate array (must be > 0)")
    method: Literal["exponential", "harmonic", "hyperbolic", "best"] = Field(
        "best", description="Decline model to fit"
    )
    calendar_time: Optional[List[float]] = Field(
        None, description="Optional calendar time array for uptime calculation"
    )
    np_start: Optional[float] = Field(None, description="Start of fitting window (cumulative)")
    np_end: Optional[float] = Field(None, description="End of fitting window (cumulative)")

    @field_validator("rates")
    @classmethod
    def validate_rates(cls, v):
        if not all(r > 0 for r in v):
            raise ValueError("All rate values must be positive")
        return v


class DeclineForecastRequest(BaseModel):
    """Request model for decline curve forecast generation."""

    qi: float = Field(..., gt=0, description="Initial rate (volume/time)")
    di: float = Field(0.0, ge=0, description="Initial decline rate (1/time). Not used for Duong")
    b: float = Field(0.0, ge=0, le=2, description="Arps b-factor (0=exp, 0<b<1=hyp, 1=harmonic)")
    method: Literal["exponential", "harmonic", "hyperbolic", "duong"] = Field(
        "hyperbolic", description="Decline model type"
    )
    t_end: float = Field(..., gt=0, description="End time for forecast")
    dt: float = Field(1.0, gt=0, description="Time step (default 1.0)")
    q_min: float = Field(0.0, ge=0, description="Economic limit rate (0 = no cutoff)")
    uptime: float = Field(1.0, gt=0, le=1, description="Uptime fraction (0-1)")
    a: Optional[float] = Field(None, description="Duong 'a' parameter (required for Duong)")
    m: Optional[float] = Field(None, description="Duong 'm' parameter (required for Duong)")


class ArpsRateRequest(BaseModel):
    """Request model for Arps decline rate calculation."""

    qi: float = Field(..., gt=0, description="Initial rate (volume/time)")
    di: float = Field(..., gt=0, description="Initial decline rate (1/time)")
    b: float = Field(..., ge=0, le=2, description="Arps b-factor")
    t: Union[float, List[float]] = Field(..., description="Time value(s)")

    @field_validator("t")
    @classmethod
    def validate_time(cls, v):
        if isinstance(v, list):
            if not all(t >= 0 for t in v):
                raise ValueError("All time values must be non-negative")
        elif v < 0:
            raise ValueError("Time must be non-negative")
        return v


class ArpsCumRequest(BaseModel):
    """Request model for Arps cumulative production calculation."""

    qi: float = Field(..., gt=0, description="Initial rate (volume/time)")
    di: float = Field(..., gt=0, description="Initial decline rate (1/time)")
    b: float = Field(..., ge=0, le=2, description="Arps b-factor")
    t: Union[float, List[float]] = Field(..., description="Time value(s)")

    @field_validator("t")
    @classmethod
    def validate_time(cls, v):
        if isinstance(v, list):
            if not all(t >= 0 for t in v):
                raise ValueError("All time values must be non-negative")
        elif v < 0:
            raise ValueError("Time must be non-negative")
        return v


class EURRequest(BaseModel):
    """Request model for estimated ultimate recovery calculation."""

    qi: float = Field(..., gt=0, description="Initial rate")
    di: float = Field(..., gt=0, description="Initial decline rate (1/time)")
    b: float = Field(..., ge=0, le=2, description="Arps b-factor")
    q_min: float = Field(..., gt=0, description="Economic limit rate")


class DuongRateRequest(BaseModel):
    """Request model for Duong decline rate calculation."""

    qi: float = Field(..., gt=0, description="Rate at t=1 (volume/time)")
    a: float = Field(..., gt=0, description="Duong 'a' parameter")
    m: float = Field(..., gt=1, description="Duong 'm' parameter (must be > 1)")
    t: Union[float, List[float]] = Field(..., description="Time value(s) (must be > 0)")

    @field_validator("t")
    @classmethod
    def validate_time(cls, v):
        if isinstance(v, list):
            if not all(t > 0 for t in v):
                raise ValueError("All time values must be positive for Duong model")
        elif v <= 0:
            raise ValueError("Time must be positive for Duong model")
        return v


class FitRatioRequest(BaseModel):
    """Request model for GOR/WOR ratio model fitting."""

    x: List[float] = Field(..., description="Independent variable (cumulative production or time)")
    ratio: List[float] = Field(..., description="Ratio values (e.g. GOR, WOR)")
    method: Literal["linear", "exponential", "power", "logistic", "best"] = Field(
        "best", description="Ratio model to fit"
    )
    domain: Literal["cum", "time"] = Field(
        "cum", description="Domain type: 'cum' (cumulative) or 'time'"
    )


class RatioForecastRequest(BaseModel):
    """Request model for ratio forecast from fitted model."""

    method: Literal["linear", "exponential", "power", "logistic"] = Field(
        ..., description="Ratio model type"
    )
    a: float = Field(..., description="Primary parameter")
    b: float = Field(..., description="Secondary parameter")
    c: float = Field(0.0, description="Tertiary parameter (logistic only)")
    x: Union[float, List[float]] = Field(..., description="Values to evaluate at")
    domain: Literal["cum", "time"] = Field("cum", description="Domain type")
