"""Fixed implementations for pyrestoolbox functions with upstream bugs.

This module provides corrected implementations of pyrestoolbox functions
that have bugs in the original library. These implementations are standalone
and don't rely on the buggy upstream code.
"""

import numpy as np
from pyrestoolbox.constants import R, degF2R, MW_AIR
from pyrestoolbox.classes import z_method, c_method
import pyrestoolbox.gas as gas


def gas_grad2sg_fixed(
    grad: float,
    p: float,
    degf: float,
    zmethod: z_method = z_method.DAK,
    cmethod: c_method = c_method.PMC,
    co2: float = 0,
    h2s: float = 0,
    n2: float = 0,
    tc: float = 0,
    pc: float = 0,
    rtol: float = 1e-7,
) -> float:
    """Returns insitu gas specific gravity consistent with observed gas gradient.
    
    Fixed version of gas_grad2sg that doesn't rely on buggy bisect_solve.
    Uses Newton-Raphson iteration instead of bisection.
    
    Args:
        grad: Observed gas gradient (psi/ft)
        p: Pressure at observation (psia)
        degf: Reservoir Temperature (deg F)
        zmethod: Method for calculating Z-Factor
        cmethod: Method for calculating critical properties
        co2: Molar fraction of CO2
        h2s: Molar fraction of H2S
        n2: Molar fraction of Nitrogen
        tc: Critical gas temperature (deg R)
        pc: Critical gas pressure (psia)
        rtol: Relative solution tolerance
    
    Returns:
        Gas specific gravity (air = 1.0)
    """
    degR = degf + degF2R
    
    def calc_gradient(sg):
        """Calculate gradient for a given gas SG."""
        m = sg * MW_AIR
        zee = gas.gas_z(
            p=p,
            degf=degf,
            sg=sg,
            zmethod=zmethod,
            cmethod=cmethod,
            co2=co2,
            h2s=h2s,
            n2=n2,
            tc=tc,
            pc=pc,
        )
        grad_calc = p * m / (zee * R * degR) / 144
        return grad_calc
    
    # Newton-Raphson iteration
    sg_guess = 0.7  # Initial guess
    max_iter = 50
    
    for i in range(max_iter):
        grad_calc = calc_gradient(sg_guess)
        error = abs((grad - grad_calc) / grad)
        
        if error < rtol:
            return sg_guess
        
        # Numerical derivative
        delta = 0.001
        grad_plus = calc_gradient(sg_guess + delta)
        derivative = (grad_plus - grad_calc) / delta
        
        # Newton-Raphson update
        if abs(derivative) > 1e-10:
            sg_new = sg_guess - (grad_calc - grad) / derivative
            # Keep within reasonable bounds
            sg_new = max(0.55, min(1.75, sg_new))
            sg_guess = sg_new
        else:
            # If derivative is too small, use bisection fallback
            if grad_calc > grad:
                sg_guess *= 0.95
            else:
                sg_guess *= 1.05
    
    # Return best estimate even if not fully converged
    return sg_guess


