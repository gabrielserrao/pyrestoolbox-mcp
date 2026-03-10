"""Decline Curve Analysis tools for FastMCP."""

import numpy as np
import pyrestoolbox.dca as dca
from fastmcp import FastMCP

from ..models.dca_models import (
    FitDeclineRequest,
    FitDeclineCumRequest,
    DeclineForecastRequest,
    ArpsRateRequest,
    ArpsCumRequest,
    EURRequest,
    DuongRateRequest,
    FitRatioRequest,
    RatioForecastRequest,
)


def register_dca_tools(mcp: FastMCP) -> None:
    """Register all decline curve analysis tools with the MCP server."""

    @mcp.tool()
    def fit_decline(request: FitDeclineRequest) -> dict:
        """Fit a decline curve model to production rate vs time data.

        **PRODUCTION ANALYSIS TOOL** - Fits Arps (exponential, harmonic, hyperbolic) and
        Duong decline models to production data. 'best' tries all models and returns
        the one with highest R-squared.

        **Parameters:**
        - **time** (list[float], required): Time array (user-defined units, e.g. months).
        - **rates** (list[float], required): Production rate array. All values must be > 0.
        - **method** (str, optional, default="best"): Model to fit.
          Options: "exponential", "harmonic", "hyperbolic", "duong", "best".
        - **t_start** (float, optional): Start of fitting window (inclusive).
        - **t_end** (float, optional): End of fitting window (inclusive).

        **Returns:** Dictionary with fitted parameters (qi, di, b, a, m), R-squared,
        and the method name.

        **Example:**
        ```json
        {"time": [1,2,3,6,12,18,24,36], "rates": [1000,800,650,400,200,130,90,50], "method": "best"}
        ```
        """
        result = dca.fit_decline(
            t=request.time, q=request.rates, method=request.method,
            t_start=request.t_start, t_end=request.t_end,
        )
        return {
            "method": result.method,
            "qi": float(result.qi),
            "di": float(result.di),
            "b": float(result.b),
            "a": float(result.a) if hasattr(result, 'a') and result.a is not None else None,
            "m": float(result.m) if hasattr(result, 'm') and result.m is not None else None,
            "r_squared": float(result.r_squared),
        }

    @mcp.tool()
    def fit_decline_cumulative(request: FitDeclineCumRequest) -> dict:
        """Fit a decline curve model to rate vs cumulative production data.

        **PRODUCTION ANALYSIS TOOL** - Eliminates time from the Arps equations to fit
        rate as a function of cumulative production. Parameters are compatible with
        time-domain forecasting. Useful when time data is unreliable.

        **Parameters:**
        - **cumulative_production** (list[float], required): Cumulative production array.
        - **rates** (list[float], required): Production rate array (must be > 0).
        - **method** (str, optional, default="best"): "exponential", "harmonic", "hyperbolic", or "best".
        - **calendar_time** (list[float], optional): Calendar time for uptime calculation.
        - **np_start** (float, optional): Start of fitting window (cumulative).
        - **np_end** (float, optional): End of fitting window (cumulative).

        **Returns:** Fitted parameters, R-squared, and method name.
        """
        result = dca.fit_decline_cum(
            Np=request.cumulative_production, q=request.rates,
            method=request.method, t_calendar=request.calendar_time,
            Np_start=request.np_start, Np_end=request.np_end,
        )
        return {
            "method": result.method,
            "qi": float(result.qi),
            "di": float(result.di),
            "b": float(result.b),
            "r_squared": float(result.r_squared),
        }

    @mcp.tool()
    def decline_forecast(request: DeclineForecastRequest) -> dict:
        """Generate a production rate and cumulative forecast from decline parameters.

        **PRODUCTION FORECASTING TOOL** - Creates time-stepped forecasts from fitted
        or assumed decline parameters. Supports economic limit cutoff and uptime factors.

        **Parameters:**
        - **qi** (float, required): Initial rate (volume/time).
        - **di** (float, optional): Initial decline rate (1/time). Not used for Duong.
        - **b** (float, optional): Arps b-factor (0=exp, 0<b<1=hyp, 1=harmonic).
        - **method** (str, optional, default="hyperbolic"): Decline model type.
        - **t_end** (float, required): End time for forecast.
        - **dt** (float, optional, default=1.0): Time step.
        - **q_min** (float, optional, default=0): Economic limit rate. 0 = no cutoff.
        - **uptime** (float, optional, default=1.0): Uptime fraction (0-1).
        - **a** (float, optional): Duong 'a' parameter (required for Duong method).
        - **m** (float, optional): Duong 'm' parameter (required for Duong method).

        **Returns:** Time array, rate array, cumulative array, and EUR.
        """
        # Build DeclineResult-like object
        dr = dca.DeclineResult()
        dr.method = request.method
        dr.qi = request.qi
        dr.di = request.di
        dr.b = request.b
        dr.a = request.a if request.a is not None else 0
        dr.m = request.m if request.m is not None else 0
        dr.r_squared = 0
        dr.uptime_history = None
        dr.uptime_mean = request.uptime

        fc = dca.forecast(
            result=dr, t_end=request.t_end, dt=request.dt,
            q_min=request.q_min, uptime=request.uptime,
        )
        return {
            "time": fc.t.tolist(),
            "rate": fc.q.tolist(),
            "cumulative": fc.Qcum.tolist(),
            "eur": float(fc.eur),
        }

    @mcp.tool()
    def arps_rate(request: ArpsRateRequest) -> dict:
        """Calculate Arps decline rate at specified time(s).

        **DECLINE CURVE TOOL** - Computes production rate using Arps decline equation.
        q(t) = qi / (1 + b*di*t)^(1/b) for hyperbolic decline.

        **Parameters:**
        - **qi** (float, required): Initial rate (volume/time). Must be > 0.
        - **di** (float, required): Initial decline rate (1/time). Must be > 0.
        - **b** (float, required): Arps b-factor (0=exponential, 0<b<1=hyperbolic, 1=harmonic).
        - **t** (float or list, required): Time value(s).

        **Returns:** Rate value(s) at specified time(s).
        """
        t = np.array(request.t) if isinstance(request.t, list) else request.t
        result = dca.arps_rate(qi=request.qi, di=request.di, b=request.b, t=t)
        if isinstance(result, np.ndarray):
            return {"rate": result.tolist(), "units": "same as qi"}
        return {"rate": float(result), "units": "same as qi"}

    @mcp.tool()
    def arps_cumulative(request: ArpsCumRequest) -> dict:
        """Calculate Arps cumulative production at specified time(s).

        **DECLINE CURVE TOOL** - Computes cumulative production from Arps parameters.

        **Parameters:**
        - **qi** (float, required): Initial rate. Must be > 0.
        - **di** (float, required): Initial decline rate. Must be > 0.
        - **b** (float, required): Arps b-factor.
        - **t** (float or list, required): Time value(s).

        **Returns:** Cumulative production at specified time(s).
        """
        t = np.array(request.t) if isinstance(request.t, list) else request.t
        result = dca.arps_cum(qi=request.qi, di=request.di, b=request.b, t=t)
        if isinstance(result, np.ndarray):
            return {"cumulative": result.tolist()}
        return {"cumulative": float(result)}

    @mcp.tool()
    def estimated_ultimate_recovery(request: EURRequest) -> dict:
        """Calculate Estimated Ultimate Recovery (EUR) for Arps decline.

        **RESERVE ESTIMATION TOOL** - Computes cumulative production when rate
        reaches the economic limit. Essential for reserve booking and economics.

        **Parameters:**
        - **qi** (float, required): Initial rate.
        - **di** (float, required): Initial decline rate (1/time).
        - **b** (float, required): Arps b-factor (0-1).
        - **q_min** (float, required): Economic limit rate.

        **Returns:** EUR value in same volume units as qi * time.
        """
        result = dca.eur(qi=request.qi, di=request.di, b=request.b, q_min=request.q_min)
        return {"eur": float(result)}

    @mcp.tool()
    def duong_rate(request: DuongRateRequest) -> dict:
        """Calculate Duong decline rate for unconventional reservoirs.

        **UNCONVENTIONAL DECLINE TOOL** - Duong model for tight oil/shale gas.
        q(t) = qi * t^(-m) * exp(a/(1-m) * (t^(1-m) - 1))

        **Parameters:**
        - **qi** (float, required): Rate at t=1. Must be > 0.
        - **a** (float, required): Duong 'a' parameter. Must be > 0.
        - **m** (float, required): Duong 'm' parameter. Must be > 1.
        - **t** (float or list, required): Time (must be > 0).

        **Returns:** Rate at specified time(s).
        """
        t = np.array(request.t) if isinstance(request.t, list) else request.t
        result = dca.duong_rate(qi=request.qi, a=request.a, m=request.m, t=t)
        if isinstance(result, np.ndarray):
            return {"rate": result.tolist()}
        return {"rate": float(result)}

    @mcp.tool()
    def fit_ratio(request: FitRatioRequest) -> dict:
        """Fit a ratio model (GOR, WOR, CGR) to production data.

        **RATIO ANALYSIS TOOL** - Fits linear, exponential, power, or logistic models
        to secondary phase ratios. 'best' tries all and returns highest R-squared.

        **Parameters:**
        - **x** (list[float], required): Independent variable (cumulative production or time).
        - **ratio** (list[float], required): Ratio values (e.g. GOR, WOR).
        - **method** (str, optional, default="best"): Model type.
          Options: "linear", "exponential", "power", "logistic", "best".
        - **domain** (str, optional, default="cum"): Domain type: "cum" or "time".

        **Returns:** Fitted model type, parameters (a, b, c), R-squared, and domain.
        """
        result = dca.fit_ratio(
            x=request.x, ratio=request.ratio,
            method=request.method, domain=request.domain,
        )
        return {
            "method": result.method,
            "a": float(result.a),
            "b": float(result.b),
            "c": float(result.c) if hasattr(result, 'c') and result.c is not None else 0.0,
            "r_squared": float(result.r_squared),
            "domain": result.domain,
        }

    @mcp.tool()
    def ratio_forecast(request: RatioForecastRequest) -> dict:
        """Evaluate a fitted ratio model at given values.

        **RATIO FORECASTING TOOL** - Uses parameters from fit_ratio to predict
        secondary phase ratios at new cumulative production or time values.

        **Parameters:**
        - **method** (str, required): Ratio model type.
        - **a** (float, required): Primary parameter from fit_ratio.
        - **b** (float, required): Secondary parameter from fit_ratio.
        - **c** (float, optional): Tertiary parameter (logistic only).
        - **x** (float or list, required): Values to evaluate at.
        - **domain** (str, optional, default="cum"): Domain type.

        **Returns:** Predicted ratio values.
        """
        # Build RatioResult-like object
        rr = dca.RatioResult()
        rr.method = request.method
        rr.a = request.a
        rr.b = request.b
        rr.c = request.c
        rr.domain = request.domain
        rr.r_squared = 0

        x = np.array(request.x) if isinstance(request.x, list) else request.x
        result = dca.ratio_forecast(result=rr, x=x)
        if isinstance(result, np.ndarray):
            return {"ratio": result.tolist()}
        return {"ratio": float(result)}
