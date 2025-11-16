"""Simulation tools for FastMCP."""

import numpy as np
import pyrestoolbox.simtools as simtools
from pyrestoolbox.classes import kr_family, kr_table
from fastmcp import FastMCP

from ..models.simtools_models import (
    RelPermTableRequest,
    InfluenceTableRequest,
    RachfordRiceRequest,
    ExtractProblemCellsRequest,
    ZipSimDeckRequest,
)


def register_simtools_tools(mcp: FastMCP) -> None:
    """Register all simulation tools with the MCP server."""

    @mcp.tool()
    def generate_rel_perm_table(request: RelPermTableRequest) -> dict:
        """Generate relative permeability table for reservoir simulation.

        **CRITICAL SIMULATION TOOL** - Creates saturation-dependent relative permeability
        curves for ECLIPSE, Intersect, CMG, or other simulators. Relative permeability
        is essential for multiphase flow simulation and determines fluid mobility.

        **Parameters:**
        - **rows** (int, required): Number of saturation points in table. Must be > 0.
          Typical: 20-50. Example: 25. More rows = smoother curves but larger files.
        - **krtable** (str, required): Table type. Options: "SWOF", "SGOF", "SGWFN".
          Example: "SWOF" for water-oil systems.
        - **krfamily** (str, required): Correlation family. Options: "COR" (Corey), "LET".
          Example: "COR" for simple power-law, "LET" for flexible fitting.
        - **kromax** (float, required): Maximum oil relative permeability (0-1).
          Typical: 0.5-1.0. Example: 1.0.
        - **swc** (float, required): Connate water saturation (0-1). Must be < 1.
          Typical: 0.1-0.3. Example: 0.15.
        - **krwmax** (float, optional): Maximum water rel perm for SWOF (0-1).
          Typical: 0.1-0.5. Example: 0.25.
        - **krgmax** (float, optional): Maximum gas rel perm for SGOF/SGWFN (0-1).
          Typical: 0.5-1.0. Example: 1.0.
        - **sorw** (float, optional): Residual oil saturation to water (0-1).
          Typical: 0.1-0.3. Example: 0.15.
        - **sorg** (float, optional): Residual oil saturation to gas (0-1).
          Typical: 0.05-0.2. Example: 0.1.
        - **sgc** (float, optional): Critical gas saturation (0-1).
          Typical: 0.05-0.15. Example: 0.1.
        - **swcr** (float, optional): Critical water saturation for Corey (0-1).
          Typical: 0.15-0.25. Example: 0.2.
        - **no** (float, optional): Corey exponent for oil (Corey only). Must be > 0.
          Typical: 2.0-4.0. Example: 2.5. Higher = more curved.
        - **nw** (float, optional): Corey exponent for water (Corey only). Must be > 0.
          Typical: 1.5-3.0. Example: 1.5.
        - **ng** (float, optional): Corey exponent for gas (Corey only). Must be > 0.
          Typical: 2.0-3.5. Example: 2.0.
        - **Lo, Eo, To** (float, optional): LET parameters for oil (LET only).
          Typical: Lo=1-3, Eo=1-2, To=1-3. Example: Lo=2.5, Eo=1.25, To=1.75.
        - **Lw, Ew, Tw** (float, optional): LET parameters for water (LET only).
          Typical: Lw=1-3, Ew=1-2, Tw=1-3. Example: Lw=1.5, Ew=1.0, Tw=2.0.
        - **Lg, Eg, Tg** (float, optional): LET parameters for gas (LET only).
          Typical: Lg=1-3, Eg=1-2, Tg=1-3. Example: Lg=1.2, Eg=1.5, Tg=2.0.

        **Correlation Families:**
        - **Corey (1954):** Simple power-law model, fast, widely used.
          Formula: Kr = krmax * ((S - Sc) / (1 - Swc - Sor))^n
          Use for: Quick estimates, standard cases, compatibility.
        - **LET (2005):** Flexible 3-parameter model, better curve fitting.
          Formula: Kr = krmax * (S^L) / (S^L + E * (1-S)^T)
          Use for: History matching, complex curves, accuracy.

        **Table Types:**
        - **SWOF:** Water-Oil (waterflood, aquifer influx). Columns: Sw, Krw, Kro, Pcow.
        - **SGOF:** Gas-Oil (gas cap expansion, gas injection). Columns: Sg, Krg, Krog, Pcog.
        - **SGWFN:** Three-phase gas-water (gas cycling, WAG). Columns: Sg, Krg, Krw, Pcog, Pcow.

        **Saturation Endpoints:**
        - Swc: Connate water (immobile water)
        - Sorw: Residual oil to water (trapped oil after waterflood)
        - Sorg: Residual oil to gas (trapped oil after gas injection)
        - Sgc: Critical gas (minimum gas saturation for flow)

        **Workflow:**
        1. Choose correlation family (Corey or LET)
        2. Select table type (SWOF, SGOF, SGWFN)
        3. Specify saturation endpoints (Swc, Sor, Sgc)
        4. Set maximum rel perms (kromax, krwmax, krgmax)
        5. Define correlation parameters (Corey exponents or LET params)
        6. Generate table with specified number of rows

        **Returns:**
        Dictionary with:
        - **table** (list): List of dicts with saturation and rel perm values
        - **columns** (list): Column names (e.g., ["Sw", "Krw", "Kro", "Pcow"])
        - **rows** (int): Number of rows in table
        - **table_type** (str): Table type (SWOF, SGOF, SGWFN)
        - **correlation** (str): Correlation family (COR, LET)
        - **note** (str): Usage guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Saturation endpoints don't sum correctly (Swc + Sor < 1.0)
        - Using wrong table type for simulation (check simulator requirements)
        - Corey exponents too high (>5) causing unrealistic curves
        - Not specifying required parameters for chosen table type
        - Too few rows (<10) causing poor curve resolution
        - Maximum rel perms > 1.0 (must be dimensionless 0-1)

        **Example Usage (Corey SWOF):**
        ```python
        {
            "rows": 25,
            "krtable": "SWOF",
            "krfamily": "COR",
            "kromax": 1.0,
            "krwmax": 0.25,
            "swc": 0.15,
            "swcr": 0.2,
            "sorw": 0.15,
            "no": 2.5,
            "nw": 1.5
        }
        ```

        **Example Usage (LET SGOF):**
        ```python
        {
            "rows": 25,
            "krtable": "SGOF",
            "krfamily": "LET",
            "kromax": 1.0,
            "krgmax": 1.0,
            "swc": 0.2,
            "sorg": 0.15,
            "sgc": 0.1,
            "Lo": 2.5,
            "Eo": 1.25,
            "To": 1.75,
            "Lg": 1.2,
            "Eg": 1.5,
            "Tg": 2.0
        }
        ```

        **Note:** Relative permeability tables are critical for accurate simulation.
        Always validate endpoints against core data or literature. Use LET for
        history matching when Corey doesn't fit data well. Table format is
        ECLIPSE-compatible and ready for direct inclusion in simulation decks.
        """
        family_enum = getattr(kr_family, request.krfamily)
        table_enum = getattr(kr_table, request.krtable)

        # Build kwargs based on correlation family and table type
        kwargs = {
            "rows": request.rows,
            "krtable": table_enum,
            "krfamily": family_enum,
            "kromax": request.kromax,
            "swc": request.swc,
        }

        # Add table-specific parameters
        if request.krtable == "SWOF":
            if request.krwmax is not None:
                kwargs["krwmax"] = request.krwmax
            if request.sorw is not None:
                kwargs["sorw"] = request.sorw
        elif request.krtable in ["SGOF", "SGWFN"]:
            if request.krgmax is not None:
                kwargs["krgmax"] = request.krgmax
            if request.sorg is not None:
                kwargs["sorg"] = request.sorg
            if request.sgc is not None:
                kwargs["sgc"] = request.sgc

        # Add correlation-specific parameters
        if request.krfamily == "COR":
            # Corey parameters
            if request.no is not None:
                kwargs["no"] = request.no
            if request.nw is not None:
                kwargs["nw"] = request.nw
            if request.ng is not None:
                kwargs["ng"] = request.ng
            if request.swcr is not None:
                kwargs["swcr"] = request.swcr
        elif request.krfamily == "LET":
            # LET parameters - Oil
            if request.Lo is not None:
                kwargs["Lo"] = request.Lo
            if request.Eo is not None:
                kwargs["Eo"] = request.Eo
            if request.To is not None:
                kwargs["To"] = request.To
            # LET parameters - Water
            if request.Lw is not None:
                kwargs["Lw"] = request.Lw
            if request.Ew is not None:
                kwargs["Ew"] = request.Ew
            if request.Tw is not None:
                kwargs["Tw"] = request.Tw
            # LET parameters - Gas
            if request.Lg is not None:
                kwargs["Lg"] = request.Lg
            if request.Eg is not None:
                kwargs["Eg"] = request.Eg
            if request.Tg is not None:
                kwargs["Tg"] = request.Tg

        # Generate table
        df = simtools.rel_perm_table(**kwargs)

        # Convert DataFrame to list of dicts
        table_data = df.to_dict(orient="records")

        return {
            "table": table_data,
            "columns": list(df.columns),
            "rows": len(table_data),
            "table_type": request.krtable,
            "correlation": request.krfamily,
            "note": "Table formatted for ECLIPSE/Intersect simulation input",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def generate_aquifer_influence(request: InfluenceTableRequest) -> dict:
        """Generate Van Everdingen & Hurst aquifer influence functions.

        **CRITICAL AQUIFER MODELING TOOL** - Creates dimensionless aquifer influence
        functions for AQUTAB keyword in ECLIPSE/Intersect. These functions quantify
        water influx from surrounding aquifers into hydrocarbon reservoirs.

        **Parameters:**
        - **res** (float or list, required): Dimensionless aquifer radius (ReD).
          Must be > 1.0. Can be scalar or list. Typical: 5-100. Example: 10.0.
          ReD = re/rw where re = aquifer outer radius, rw = reservoir radius.
        - **start** (float, required): Minimum dimensionless time (tD_min).
          Must be > 0. Typical: 0.01-1.0. Example: 0.1.
        - **end** (float, required): Maximum dimensionless time (tD_max).
          Must be > start. Typical: 10-1000. Example: 100.0.
        - **rows** (int, required): Number of time points in table. Must be > 0.
          Typical: 20-100. Example: 50. More rows = smoother curves.

        **Background:**
        Van Everdingen & Hurst (1949) developed analytical solutions for aquifer influx
        using diffusivity equation. These functions relate:
        - Dimensionless time (tD) = (k × t) / (φ × μ × ct × rw²)
        - Dimensionless pressure (pD) = aquifer response function
        - Dimensionless radius (ReD) = aquifer geometry

        **Influence Function:**
        The influence function pD(tD, ReD) represents the dimensionless pressure response
        at the reservoir-aquifer boundary. It depends on:
        - Aquifer geometry (radial vs linear, finite vs infinite)
        - Boundary conditions (constant rate vs constant pressure)
        - Aquifer properties (permeability, porosity, compressibility)

        **Applications:**
        - **Material Balance:** Quantify aquifer support in material balance analysis
        - **Pressure Maintenance:** Evaluate aquifer pressure support
        - **Water Influx:** Calculate cumulative water influx over time
        - **History Matching:** Match production history with aquifer model
        - **Production Forecasting:** Predict future aquifer influx

        **Integration Method:**
        Uses numerical integration (Gaussian quadrature) of diffusivity equation with
        high-resolution integration (M=8) for accuracy. The solution is computed at
        specified dimensionless time points.

        **Returns:**
        Dictionary with:
        - **dimensionless_time** (list): Dimensionless time values (tD)
        - **dimensionless_pressures** (list): List of pD arrays (one per ReD)
        - **rows** (int): Number of time points
        - **dimensionless_radii** (list): ReD values used
        - **time_range** (dict): Start and end dimensionless times
        - **note** (str): Usage guidance for ECLIPSE
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - ReD < 1.0 (aquifer radius must be > reservoir radius)
        - tD_max < tD_min (end must be > start)
        - Too few rows (<10) causing poor resolution
        - Wrong dimensionless radius (must match aquifer geometry)
        - Confusing dimensionless time with actual time
        - Not accounting for aquifer compressibility

        **Example Usage:**
        ```python
        {
            "res": 10.0,
            "start": 0.1,
            "end": 100.0,
            "rows": 50
        }
        ```
        Result: Table with 50 time points from tD=0.1 to tD=100.0 for ReD=10.0.

        **Note:** AQUTAB keyword is ready for direct inclusion in ECLIPSE DATA file.
        The influence functions are dimensionless and must be scaled using reservoir
        and aquifer properties. For multiple aquifers, generate separate tables for
        each aquifer with different ReD values.
        """
        # Generate influence table
        # influence_tables expects ReDs (list of dimensionless radii)
        ReDs = [request.res] if isinstance(request.res, (int, float)) else request.res
        result = simtools.influence_tables(
            ReDs=ReDs,
            min_td=request.start,
            max_td=request.end,
            n_incr=request.rows,
            M=8,  # Integration parameter
            export=False,
        )

        # influence_tables returns tuple of (tD, list of pD lists)
        # Convert to DataFrame-like structure and convert mpmath types to float
        tD, pD_lists = result
        
        # Convert mpmath types to regular floats
        tD_list = [float(t) for t in tD]
        pD_converted = [
            [float(p) for p in pd_array]
            for pd_array in pD_lists
        ]
        
        return {
            "dimensionless_time": tD_list,
            "dimensionless_pressures": pD_converted,
            "rows": len(tD_list),
            "dimensionless_radii": [float(r) for r in ReDs],
            "time_range": {"start": request.start, "end": request.end},
            "note": "AQUTAB keyword for ECLIPSE/Intersect - use in DATA file",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def rachford_rice_flash(request: RachfordRiceRequest) -> dict:
        """Solve Rachford-Rice equation for vapor-liquid equilibrium.

        **PHASE BEHAVIOR TOOL** - Calculates vapor fraction (beta) and phase compositions
        for two-phase flash at specified pressure and temperature. Essential for
        compositional analysis, separator design, and phase behavior calculations.

        **Parameters:**
        - **zis** (list, required): Overall mole fractions of components (0-1).
          Must sum to 1.0. Length must match Kis. Example: [0.5, 0.3, 0.2] for 3 components.
        - **Kis** (list, required): Equilibrium ratios (K-values) for components.
          Ki = yi/xi where yi = vapor mole fraction, xi = liquid mole fraction.
          Length must match zis. Example: [2.5, 1.8, 0.6]. K > 1 = light component.

        **Rachford-Rice Equation:**
        Σ[zi(Ki - 1) / (1 + β(Ki - 1))] = 0

        Where:
        - zi = overall mole fraction of component i
        - Ki = equilibrium ratio (yi/xi) for component i
        - β = vapor mole fraction (0 to 1)

        **Phase Behavior:**
        - β = 0: All liquid (subcooled)
        - 0 < β < 1: Two-phase (vapor + liquid)
        - β = 1: All vapor (superheated)

        **K-Value Behavior:**
        - K > 1: Component prefers vapor phase (light components)
        - K = 1: Component equally distributed (critical component)
        - K < 1: Component prefers liquid phase (heavy components)
        - K-values depend on pressure, temperature, and composition

        **Solution Method:**
        Iterative Newton-Raphson method with bounds checking (0 ≤ β ≤ 1).
        Converges rapidly for well-posed problems. Typically converges in 3-10 iterations.

        **Applications:**
        - **Gas-Oil Separator Design:** Determine separator conditions for phase split
        - **Phase Envelope:** Calculate bubble/dew points and phase boundaries
        - **Compositional Simulation:** Flash calculations in compositional models
        - **EOS Flash:** Solve equation of state flash calculations
        - **Surface Facility Design:** Design separation trains and processing units
        - **Material Balance:** Phase split in material balance calculations

        **Returns:**
        Dictionary with:
        - **vapor_fraction** (float): Vapor mole fraction β (0-1)
        - **liquid_composition** (list): Liquid phase mole fractions xi
        - **vapor_composition** (list): Vapor phase mole fractions yi
        - **method** (str): "Rachford-Rice (Newton-Raphson)"
        - **note** (str): Interpretation guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Mole fractions don't sum to 1.0 (must normalize)
        - K-values don't match components (length mismatch)
        - K-values at wrong P-T conditions (must match flash conditions)
        - Using weight fractions instead of mole fractions
        - Not accounting for non-hydrocarbon components
        - K-values from wrong correlation/EOS

        **Example Usage:**
        ```python
        {
            "zis": [0.5, 0.3, 0.2],
            "Kis": [2.5, 1.8, 0.6]
        }
        ```
        Result: β ≈ 0.3-0.5 (two-phase), with light components enriched in vapor,
        heavy components enriched in liquid.

        **Note:** Rachford-Rice equation assumes ideal mixing. For real systems,
        K-values must account for non-ideality (activity coefficients, fugacity).
        K-values are typically obtained from EOS (Peng-Robinson, Soave-Redlich-Kwong)
        or correlations (Wilson, Standing). Always ensure K-values match flash conditions.
        """
        # Solve Rachford-Rice
        iteration, xi, yi, beta, err = simtools.rr_solver(
            zi=request.zis,
            ki=request.Kis,
        )

        return {
            "vapor_fraction": float(beta),
            "liquid_composition": [float(x) for x in xi],
            "vapor_composition": [float(y) for y in yi],
            "method": "Rachford-Rice (Newton-Raphson)",
            "inputs": request.model_dump(),
            "note": "Vapor fraction (beta) ranges from 0 (all liquid) to 1 (all vapor)",
        }

    @mcp.tool()
    def extract_eclipse_problem_cells(request: ExtractProblemCellsRequest) -> dict:
        """Extract convergence problem cells from ECLIPSE/Intersect PRT file.

        **SIMULATION DIAGNOSTICS TOOL** - Parse ECLIPSE/Intersect PRT output
        files to extract cells with convergence failures, material balance
        errors, or other simulation problems.

        **What It Does:**
        - Scans ECLIPSE .PRT files for error/warning messages
        - Identifies problem cells by (I, J, K) grid coordinates
        - Extracts timestep and iteration information
        - Reports error types and severity

        **Applications:**
        - **Convergence Debugging:** Find cells causing timestep cuts
        - **Model QC:** Identify grid initialization issues
        - **Performance Tuning:** Locate problematic regions
        - **Numerical Stability:** Track material balance errors

        **Common Problems Detected:**
        - Material balance errors
        - Negative saturations
        - Pressure/temperature out of range
        - Flash calculation failures
        - Linear solver issues
        - Severe saturation changes

        **Workflow:**
        1. Run ECLIPSE/Intersect simulation
        2. Locate the .PRT output file
        3. Use this tool to extract problem cell locations
        4. Investigate problematic cells in pre-processor
        5. Refine initialization or grid properties

        **Output Format:** List of problem cells with timestep, iteration,
        cell coordinates (I,J,K), error type, and severity.

        Args:
            request: Path to PRT file and output options

        Returns:
            Dictionary with list of problem cells and summary statistics
        """
        try:
            # Extract problem cells from PRT file
            results = simtools.ix_extract_problem_cells(
                filename=request.filename,
                silent=request.silent
            )

            if not results:
                return {
                    "problem_cells": [],
                    "total_problems": 0,
                    "message": "No convergence problems detected in PRT file",
                    "file": request.filename,
                    "inputs": request.model_dump(),
                }

            # Process results into structured format
            problem_list = []
            for problem in results:
                problem_list.append({
                    "timestep": problem.get("timestep", "Unknown"),
                    "iteration": problem.get("iteration", "Unknown"),
                    "i": problem.get("i", -1),
                    "j": problem.get("j", -1),
                    "k": problem.get("k", -1),
                    "error_type": problem.get("error_type", "Unknown"),
                    "message": problem.get("message", ""),
                })

            return {
                "problem_cells": problem_list,
                "total_problems": len(problem_list),
                "file": request.filename,
                "method": "ECLIPSE/Intersect PRT file parsing",
                "inputs": request.model_dump(),
                "note": "Investigate problem cells in grid pre-processor to resolve convergence issues",
            }

        except FileNotFoundError:
            return {
                "error": f"PRT file not found: {request.filename}",
                "suggestion": "Verify file path and ensure ECLIPSE/Intersect simulation completed",
                "inputs": request.model_dump(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "file": request.filename,
                "inputs": request.model_dump(),
            }

    @mcp.tool()
    def validate_simulation_deck(request: ZipSimDeckRequest) -> dict:
        """Validate and process ECLIPSE simulation deck with INCLUDE files.

        **DECK MANAGEMENT TOOL** - Recursively process ECLIPSE/Intersect
        simulation decks to find all INCLUDE files, validate references,
        and optionally create a complete archive.

        **What It Does:**
        - Parses main DATA file for INCLUDE keywords
        - Recursively follows INCLUDE chains
        - Validates all referenced files exist
        - Identifies missing or broken references
        - Optionally creates zip archive with all files

        **Applications:**
        - **Deck Validation:** Ensure all files present before submission
        - **Deck Transfer:** Create complete archive for sharing
        - **Version Control:** Bundle all files for archiving
        - **QC Check:** Verify deck completeness before cluster runs

        **Workflow:**
        1. Specify main DATA file(s) to check
        2. Tool recursively finds all INCLUDE files
        3. Validates each file exists
        4. Reports missing files or broken paths
        5. Optionally creates zip with all referenced files

        **INCLUDE File Support:**
        - Absolute paths: /full/path/to/file.inc
        - Relative paths: ../INCLUDE/GRID.GRDECL
        - Same directory: SCHEDULE.INC
        - Nested INCLUDE chains: INCLUDE files that reference other INCLUDE files

        **Output Formats:**
        - Summary of all files found
        - List of missing/broken references
        - Optional: ZIP archive with complete deck

        Args:
            request: List of DATA files, zip option, console output preference

        Returns:
            Dictionary with file inventory, validation results, and optional zip path
        """
        try:
            # Process simulation deck
            results = simtools.zip_check_sim_deck(
                files2scrape=request.files2scrape,
                tozip=request.tozip,
                console_summary=request.console_summary
            )

            # Parse results (format depends on pyrestoolbox implementation)
            if isinstance(results, dict):
                found_files = results.get("found_files", [])
                missing_files = results.get("missing_files", [])
                zip_path = results.get("zip_path", None)
            else:
                # If results is a list of files
                found_files = results if isinstance(results, list) else []
                missing_files = []
                zip_path = None

            return {
                "deck_validation": {
                    "main_files": request.files2scrape,
                    "total_files_found": len(found_files),
                    "total_files_missing": len(missing_files),
                    "status": "VALID" if len(missing_files) == 0 else "INCOMPLETE",
                },
                "found_files": found_files,
                "missing_files": missing_files,
                "zip_archive": zip_path if request.tozip else None,
                "method": "Recursive INCLUDE file parsing",
                "inputs": request.model_dump(),
                "note": "All referenced files must exist for successful simulation run",
            }

        except FileNotFoundError as e:
            return {
                "error": f"Main deck file not found: {e}",
                "suggestion": "Verify paths to DATA files are correct",
                "inputs": request.model_dump(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "inputs": request.model_dump(),
            }
