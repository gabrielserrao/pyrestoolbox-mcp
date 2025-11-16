"""Layer heterogeneity calculation tools for FastMCP."""

import numpy as np
import pyrestoolbox.layer as layer
from fastmcp import FastMCP

from ..models.layer_models import (
    LorenzRequest,
    FlowFractionRequest,
    LayerDistributionRequest,
)


def register_layer_tools(mcp: FastMCP) -> None:
    """Register all layer/heterogeneity tools with the MCP server."""

    @mcp.tool()
    def lorenz_to_beta(request: LorenzRequest) -> dict:
        """Convert Lorenz coefficient to Dykstra-Parsons beta parameter.

        **HETEROGENEITY QUANTIFICATION** - Converts between two common measures of
        reservoir heterogeneity. Essential for comparing reservoirs using different
        heterogeneity metrics and for literature data conversion.

        **Parameters:**
        - **value** (float, required): Lorenz coefficient (0-1). Must be 0 ≤ L ≤ 1.
          Typical: 0.2-0.7. Example: 0.5 for moderate heterogeneity.

        **Lorenz Coefficient (L):**
        - Ranges from 0 (homogeneous) to 1 (completely heterogeneous)
        - Based on cumulative flow capacity vs cumulative storage capacity
        - Geometric interpretation: area between Lorenz curve and 45° line
        - L = 2 × area between curve and diagonal
        - Directly measurable from production data (PLT, tracer tests)

        **Dykstra-Parsons Beta (β):**
        - Permeability variation coefficient (dimensionless, 0-1)
        - β = (k50 - k84.1) / k50
        - Based on log-normal permeability distribution
        - Requires permeability data (core, logs)
        - Common in literature and older studies

        **Conversion Relationship:**
        Beta and Lorenz are related through log-normal distribution statistics.
        Higher Lorenz = higher Beta (both indicate more heterogeneity).

        **Typical Ranges:**
        - L < 0.3 (homogeneous): β < 0.5
        - L = 0.3-0.6 (moderate): β = 0.5-0.7
        - L > 0.6 (heterogeneous): β > 0.7

        **Applications:**
        - **Waterflood Sweep Efficiency:** Predict vertical sweep from heterogeneity
        - **Vertical Conformance Analysis:** Evaluate production allocation
        - **Reservoir Characterization:** Compare reservoirs using different metrics
        - **Performance Prediction:** Use beta in Dykstra-Parsons calculations
        - **Literature Conversion:** Convert published beta values to Lorenz

        **Returns:**
        Dictionary with:
        - **beta** (float): Dykstra-Parsons beta coefficient (0-1)
        - **lorenz_coefficient** (float): Input Lorenz coefficient
        - **method** (str): "Lorenz to Dykstra-Parsons conversion"
        - **interpretation** (dict): Heterogeneity level guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Lorenz coefficient outside valid range (must be 0-1)
        - Confusing Lorenz with other heterogeneity measures
        - Using beta from wrong distribution (must be log-normal)
        - Not understanding that conversion is approximate (depends on distribution)

        **Example Usage:**
        ```python
        {
            "value": 0.5
        }
        ```
        Result: β ≈ 0.6-0.7 (moderate to high heterogeneity).

        **Note:** Conversion assumes log-normal permeability distribution. For
        non-log-normal distributions, conversion may be less accurate. Always
        validate against actual permeability data when possible.
        """
        beta = layer.lorenz2b(lorenz=request.value)

        return {
            "beta": float(beta),
            "lorenz_coefficient": request.value,
            "method": "Lorenz to Dykstra-Parsons conversion",
            "interpretation": {
                "lorenz_0": "Homogeneous reservoir",
                "lorenz_1": "Completely heterogeneous",
                "beta_low": "Low variation (<0.5)",
                "beta_high": "High variation (>0.7)",
            },
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def beta_to_lorenz(request: LorenzRequest) -> dict:
        """Convert Dykstra-Parsons beta to Lorenz coefficient.

        **HETEROGENEITY CONVERSION** - Converts beta parameter to Lorenz coefficient.
        Essential for converting literature data and comparing reservoirs using
        different heterogeneity metrics.

        **Parameters:**
        - **value** (float, required): Dykstra-Parsons beta coefficient (0-1).
          Must be 0 ≤ β ≤ 1. Typical: 0.3-0.8. Example: 0.6 for moderate heterogeneity.

        **Dykstra-Parsons Beta (β):**
        - Permeability variation coefficient (dimensionless, 0-1)
        - β = (k50 - k84.1) / k50
        - Based on log-normal permeability distribution
        - Requires permeability data (core, logs)
        - Common in literature and older studies

        **Lorenz Coefficient (L):**
        - Ranges from 0 (homogeneous) to 1 (completely heterogeneous)
        - Based on cumulative flow capacity vs cumulative storage capacity
        - Directly measurable from production data
        - More intuitive for production analysis

        **Typical Ranges:**
        - β < 0.5: Low heterogeneity (L ~ 0.2-0.3)
        - β = 0.5-0.7: Moderate (L ~ 0.3-0.5)
        - β > 0.7: High heterogeneity (L > 0.5)

        **Use Cases:**
        - **Literature Conversion:** Convert published beta values to Lorenz
        - **Reservoir Comparison:** Compare reservoirs using different metrics
        - **Simulation Input:** Convert beta to Lorenz for simulation models
        - **Reservoir Analog Studies:** Use analog beta values with Lorenz-based tools
        - **Historical Data:** Convert old Dykstra-Parsons studies to modern metrics

        **Returns:**
        Dictionary with:
        - **lorenz_coefficient** (float): Lorenz coefficient (0-1)
        - **beta** (float): Input beta coefficient
        - **method** (str): "Dykstra-Parsons to Lorenz conversion"
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Beta coefficient outside valid range (must be 0-1)
        - Confusing beta with other variation coefficients
        - Using beta from wrong distribution (must be log-normal)
        - Not understanding that conversion is approximate (depends on distribution)

        **Example Usage:**
        ```python
        {
            "value": 0.6
        }
        ```
        Result: L ≈ 0.4-0.5 (moderate heterogeneity).

        **Note:** Conversion assumes log-normal permeability distribution. For
        non-log-normal distributions, conversion may be less accurate. Always
        validate against actual production data when possible.
        """
        lorenz = layer.lorenzfromb(B=request.value)

        return {
            "lorenz_coefficient": float(lorenz),
            "beta": request.value,
            "method": "Dykstra-Parsons to Lorenz conversion",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def lorenz_from_flow_fractions(request: FlowFractionRequest) -> dict:
        """Calculate Lorenz coefficient from flow and permeability fractions.

        **LORENZ FROM PRODUCTION DATA** - Computes Lorenz coefficient from layer-by-layer
        flow and permeability data. Essential for analyzing actual production data and
        quantifying vertical conformance from measured production allocation.

        **Parameters:**
        - **flow_frac** (list, required): Flow fractions from each layer (0-1).
          Must sum to 1.0. Length must match perm_frac. Example: [0.1, 0.2, 0.3, 0.4].
        - **perm_frac** (list, required): Permeability-thickness fractions (kh fractions)
          for each layer (0-1). Must sum to 1.0. Length must match flow_frac.
          Example: [0.05, 0.15, 0.25, 0.55].

        **Input Data Sources:**
        - **PLT (Production Logging Tool):** Flow rate per layer from production logs
        - **Tracer Tests:** Flow allocation from tracer response
        - **Production Allocation:** Flow rates from well test analysis
        - **Core Data:** Permeability and thickness from core analysis
        - **Log Data:** Permeability from well logs, thickness from formation tops

        **Lorenz Coefficient Calculation:**
        Constructs Lorenz curve from data:
        1. Sort layers by kh fraction (ascending)
        2. Calculate cumulative kh fraction (x-axis)
        3. Calculate cumulative flow fraction (y-axis)
        4. Calculate area between curve and diagonal (45° line)
        5. L = 2 × area (normalized to 0-1)

        **Interpretation:**
        - L < 0.3: High conformance (flow matches capacity)
        - L = 0.3-0.6: Moderate conformance (some flow imbalance)
        - L ≥ 0.6: Poor conformance (severe flow imbalance)

        **Applications:**
        - **Production Allocation Analysis:** Quantify vertical conformance from PLT data
        - **PLT Interpretation:** Convert PLT flow rates to heterogeneity measure
        - **Tracer Test Analysis:** Evaluate sweep efficiency from tracer response
        - **Vertical Conformance Evaluation:** Assess waterflood performance
        - **History Matching:** Match simulation to measured production allocation
        - **Performance Diagnosis:** Identify layers with poor conformance

        **Returns:**
        Dictionary with:
        - **lorenz_coefficient** (float): Lorenz coefficient (0-1)
        - **number_of_layers** (int): Number of layers analyzed
        - **method** (str): "Lorenz from flow and permeability fractions"
        - **interpretation** (str): Conformance level guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Flow fractions don't sum to 1.0 (must normalize)
        - Perm fractions don't sum to 1.0 (must normalize)
        - Length mismatch between flow_frac and perm_frac
        - Using weight fractions instead of flow fractions
        - Not sorting layers correctly (must sort by kh)
        - Using wrong kh calculation (must be k × h, not just k)

        **Example Usage:**
        ```python
        {
            "flow_frac": [0.1, 0.2, 0.3, 0.4],
            "perm_frac": [0.05, 0.15, 0.25, 0.55]
        }
        ```
        Result: L ≈ 0.4-0.5 (moderate conformance - high-k layers produce more than
        their capacity fraction, low-k layers produce less).

        **Note:** This is the most direct way to calculate Lorenz from actual production
        data. Always ensure fractions sum to 1.0 and layers are correctly matched.
        High L indicates poor vertical conformance (flow imbalance).
        """
        lorenz = layer.lorenz_from_flow_fraction(
            kh_frac=request.flow_frac[0],  # Use first value as kh_frac
            phih_frac=request.perm_frac[0],  # Use first value as phih_frac
        )

        return {
            "lorenz_coefficient": float(lorenz),
            "number_of_layers": len(request.flow_frac),
            "method": "Lorenz from flow and permeability fractions",
            "interpretation": (
                "High conformance (L<0.3)"
                if lorenz < 0.3
                else "Moderate conformance (0.3≤L<0.6)"
                if lorenz < 0.6
                else "Poor conformance (L≥0.6)"
            ),
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def flow_fractions_from_lorenz(request: LorenzRequest) -> dict:
        """Generate flow fractions from Lorenz coefficient.

        **SYNTHETIC FLOW PROFILE** - Creates idealized flow distribution matching a
        specified Lorenz coefficient. Generates a Lorenz curve (cumulative flow vs
        cumulative capacity) that honors the target heterogeneity level.

        **Parameters:**
        - **value** (float, required): Target Lorenz coefficient (0-1). Must be 0 ≤ L ≤ 1.
          Typical: 0.2-0.7. Example: 0.5 for moderate heterogeneity.

        **Lorenz Curve Generation:**
        Creates a curve showing:
        - X-axis: Cumulative storage capacity (kh fraction)
        - Y-axis: Cumulative flow capacity (flow fraction)
        - Curve shape: Determined by Lorenz coefficient
        - Points: 20 points along the curve for visualization

        **Curve Behavior:**
        - L = 0: Straight diagonal line (perfect conformance)
        - L > 0: Curved line below diagonal (flow imbalance)
        - Higher L: More curvature, greater flow imbalance

        **Applications:**
        - **Reservoir Simulation:** Generate layer properties for simulation models
        - **Waterflood Prediction:** Predict sweep efficiency from heterogeneity
        - **Sweep Efficiency Estimation:** Estimate vertical sweep from Lorenz
        - **Sensitivity Analysis:** Test impact of heterogeneity on performance
        - **Conceptual Models:** Create idealized reservoir models for studies
        - **Visualization:** Plot Lorenz curve to visualize heterogeneity

        **Returns:**
        Dictionary with:
        - **cumulative_flow_capacity** (list): Y-axis values (cumulative flow fractions)
        - **cumulative_storage_capacity** (list): X-axis values (cumulative kh fractions)
        - **lorenz_coefficient** (float): Target Lorenz coefficient
        - **method** (str): "Generated Lorenz curve"
        - **note** (str): Visualization guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Lorenz coefficient outside valid range (must be 0-1)
        - Confusing cumulative fractions with incremental fractions
        - Not understanding that curve represents idealized distribution
        - Using curve for non-log-normal distributions (may be inaccurate)

        **Example Usage:**
        ```python
        {
            "value": 0.5
        }
        ```
        Result: Lorenz curve with 20 points showing cumulative flow vs cumulative
        capacity. Curve is below diagonal, indicating flow imbalance (high-k layers
        produce more than their capacity fraction).

        **Note:** This generates an idealized Lorenz curve. For actual reservoirs,
        use `lorenz_from_flow_fractions` with measured production data. The curve
        assumes log-normal permeability distribution. Plot cumulative flow vs
        cumulative storage to visualize heterogeneity.
        """
        # lorenz_2_flow_frac returns a scalar flow fraction, not arrays
        # We need to generate a full curve, so we'll call it multiple times
        phih_values = np.linspace(0, 1, 20)
        flow_values = [layer.lorenz_2_flow_frac(lorenz=request.value, phih_frac=phi) for phi in phih_values]
        
        # Convert to lists
        flow_capacity = flow_values
        storage_capacity = phih_values.tolist()

        return {
            "cumulative_flow_capacity": flow_capacity,
            "cumulative_storage_capacity": storage_capacity,
            "lorenz_coefficient": request.value,
            "method": "Generated Lorenz curve",
            "note": "Plot cumulative flow vs storage to visualize heterogeneity",
            "inputs": request.model_dump(),
        }

    @mcp.tool()
    def generate_layer_distribution(request: LayerDistributionRequest) -> dict:
        """Generate layered permeability distribution from Lorenz coefficient.

        **LAYER PROPERTY GENERATION** - Creates detailed layer-by-layer permeability
        and thickness distribution matching specified heterogeneity. Essential for
        building reservoir simulation models and predicting waterflood performance.

        **Parameters:**
        - **lorenz** (float, required): Lorenz coefficient (0-1). Must be 0 ≤ L ≤ 1.
          Typical: 0.2-0.7. Example: 0.6 for moderate heterogeneity.
        - **nlay** (int, required): Number of layers to generate. Must be > 0.
          Typical: 5-50. Example: 10 for 10-layer model.
        - **k_avg** (float, required): Average permeability in mD. Must be > 0.
          Typical: 10-1000 mD. Example: 100.0 mD.
        - **h** (float, optional, default=100.0): Total thickness in feet.
          Must be > 0. Typical: 50-500 ft. Example: 100.0 ft.

        **Method:**
        Uses Dykstra-Parsons log-normal permeability distribution with correlation
        to Lorenz coefficient to generate realistic layer properties:
        1. Convert Lorenz to beta parameter
        2. Generate log-normal permeability distribution
        3. Sort layers by permeability (ascending)
        4. Assign equal thickness to each layer
        5. Calculate layer statistics

        **Output Properties:**
        For each layer:
        - **Thickness (ft):** Layer thickness (equal for all layers)
        - **Permeability (mD):** Layer permeability (log-normal distribution)
        - **Thickness Fraction:** Fraction of total thickness
        - **kh Fraction:** Fraction of total flow capacity (k × h)

        **Statistics Calculated:**
        - k_min, k_max: Minimum and maximum permeability
        - k_avg, k_median: Average and median permeability
        - k_std: Standard deviation
        - Heterogeneity ratio: k_max / k_min

        **Critical for:**
        - **Reservoir Simulation:** Generate layer properties for simulation models
        - **Waterflood Prediction:** Predict sweep efficiency and recovery
        - **Vertical Sweep Efficiency:** Analyze vertical conformance
        - **Conformance Studies:** Evaluate production allocation
        - **Upscaling:** Create coarse-scale models from fine-scale data
        - **Sensitivity Analysis:** Test impact of heterogeneity on performance

        **Usage Example:**
        For 10-layer simulation model with Lorenz=0.6:
        ```python
        {
            "lorenz": 0.6,
            "nlay": 10,
            "k_avg": 100.0,
            "h": 100.0
        }
        ```
        Result: 10 layers with permeabilities ranging from ~20 mD (low-k) to ~500 mD
        (high-k), each with 10 ft thickness. High-k layers have higher kh fractions.

        **Returns:**
        Dictionary with:
        - **layers** (list): List of dicts with layer properties (thickness, permeability, fractions)
        - **statistics** (dict): Permeability statistics (min, max, avg, median, std, ratio)
        - **total_thickness_ft** (float): Total thickness
        - **average_permeability_md** (float): Average permeability
        - **lorenz_coefficient** (float): Input Lorenz coefficient
        - **number_of_layers** (int): Number of layers
        - **method** (str): "Dykstra-Parsons log-normal distribution"
        - **note** (str): Usage guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Lorenz coefficient outside valid range (must be 0-1)
        - Too few layers (<5) causing poor resolution
        - Too many layers (>50) causing unnecessary complexity
        - Wrong average permeability (must match reservoir average)
        - Not understanding that layers are sorted by permeability
        - Confusing thickness fraction with absolute thickness

        **Example Usage:**
        ```python
        {
            "lorenz": 0.6,
            "nlay": 10,
            "k_avg": 100.0,
            "h": 100.0
        }
        ```
        Result: 10 layers with log-normal permeability distribution, each 10 ft thick.
        Permeability ranges from ~20 mD to ~500 mD, matching Lorenz=0.6 heterogeneity.

        **Note:** This generates idealized layer properties assuming log-normal
        permeability distribution and equal layer thickness. For actual reservoirs,
        use measured core or log data when available. Layer properties are ready
        for direct use in reservoir simulation models.
        """
        # lorenz_2_layers returns np.ndarray of permeabilities, assuming equal thickness
        k_values = layer.lorenz_2_layers(
            lorenz=request.lorenz,
            nlayers=request.nlay,
            k_avg=request.k_avg,
        )
        
        # Assume equal thickness layers
        h_values = np.ones(request.nlay) * request.h / request.nlay
        
        layer_data = []
        for i in range(request.nlay):
            layer_data.append({
                "layer": i + 1,
                "thickness_ft": float(h_values[i]),
                "permeability_md": float(k_values[i]),
                "thickness_fraction": float(h_values[i] / np.sum(h_values)),
                "kh_fraction": float(
                    k_values[i] * h_values[i] / np.sum(k_values * h_values)
                ),
            })

        # Calculate statistics
        statistics = {
            "k_min_md": float(np.min(k_values)),
            "k_max_md": float(np.max(k_values)),
            "k_avg_md": float(np.mean(k_values)),
            "k_median_md": float(np.median(k_values)),
            "k_std_md": float(np.std(k_values)),
            "heterogeneity_ratio": float(np.max(k_values) / np.min(k_values)),
        }

        return {
            "layers": layer_data,
            "statistics": statistics,
            "total_thickness_ft": float(np.sum(h_values)),
            "average_permeability_md": request.k_avg,
            "lorenz_coefficient": request.lorenz,
            "number_of_layers": request.nlay,
            "method": "Dykstra-Parsons log-normal distribution",
            "inputs": request.model_dump(),
            "note": "Use layer properties directly in reservoir simulation models",
        }
