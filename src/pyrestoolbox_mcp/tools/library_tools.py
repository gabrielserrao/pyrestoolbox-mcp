"""Component library access tools for FastMCP."""

from fastmcp import FastMCP
from pyrestoolbox.library import component_library

from ..models.library_models import ComponentPropertiesRequest


def register_library_tools(mcp: FastMCP) -> None:
    """Register all component library tools with the MCP server."""

    @mcp.tool()
    def get_component_properties(request: ComponentPropertiesRequest) -> dict:
        """Get critical properties for hydrocarbon components from database.

        **COMPONENT DATABASE** - Access to comprehensive database of critical properties
        for standard hydrocarbon components and common non-hydrocarbons. Essential for
        compositional analysis, EOS calculations, and phase behavior modeling.

        **Parameters:**
        - **component** (str, required): Component name. Case-insensitive.
          Examples: "methane", "C1", "ethane", "C2", "propane", "C3", "n-butane", "nC4",
          "i-butane", "iC4", "benzene", "toluene", "N2", "CO2", "H2S", "H2O".
        - **eos** (str, optional, default="PR79"): Equation of State model.
          Options: "PR79", "PR77", "SRK", "RK". PR79 recommended.

        **Available Components:**
        - **Light Ends:** Methane (C1), Ethane (C2), Propane (C3), Butane (C4), Pentane (C5)
        - **Normal Paraffins:** n-C4 through n-C45 (n-butane to n-pentatetracontane)
        - **Branched Alkanes:** iC4 (isobutane), iC5 (isopentane), neoC5 (neopentane)
        - **Aromatics:** Benzene (C6H6), Toluene (C7H8), Xylenes (C8H10)
        - **Naphthenes:** Cyclopentane, Cyclohexane
        - **Non-Hydrocarbons:** N2 (nitrogen), CO2 (carbon dioxide), H2S (hydrogen sulfide), H2O (water)

        **Properties Returned:**
        - **MW:** Molecular weight in lb/lbmol. Example: 16.04 for methane.
        - **Tc:** Critical temperature in °R. Example: 343.0 for methane.
        - **Pc:** Critical pressure in psia. Example: 667.8 for methane.
        - **Zc:** Critical compressibility factor (dimensionless). Example: 0.286 for methane.
        - **Omega:** Acentric factor ω (dimensionless). Example: 0.011 for methane.
        - **Vcritical:** Critical volume in cuft/lbmol. Example: 1.59 for methane.
        - **Tb:** Normal boiling point in °R. Example: 201.6 for methane.
        - **SG:** Specific gravity (dimensionless, relative to water). Example: 0.554 for methane.

        **EOS Models:**
        - **PR79** (Peng-Robinson 1979): **RECOMMENDED**. Most widely used, best accuracy.
          Use for: Most applications, hydrocarbon systems, gas processing.
        - **PR77** (Peng-Robinson 1977): Original version. Use for: Compatibility, older models.
        - **SRK** (Soave-Redlich-Kwong 1972): Alternative EOS. Use for: Specific applications, comparison.
        - **RK** (Redlich-Kwong 1949): Older EOS. Use for: Historical compatibility, simple systems.

        **Critical Properties Usage:**
        Critical properties are essential for:
        - EOS phase behavior calculations (PR, SRK, RK)
        - Flash calculations (bubble point, dew point)
        - Phase envelope generation
        - Compressibility factor calculations
        - Vapor-liquid equilibrium

        **Applications:**
        - **Compositional Simulation:** Input component properties for compositional models
        - **EOS Phase Behavior:** Calculate phase envelopes and phase boundaries
        - **Flash Calculations:** Solve vapor-liquid equilibrium problems
        - **PVT Modeling:** Build compositional PVT models
        - **Gas Processing Design:** Design separation and processing facilities
        - **Material Balance:** Compositional material balance calculations

        **Source:**
        Industry-standard component database with properties from:
        - NIST (National Institute of Standards and Technology)
        - API (American Petroleum Institute) data
        - EOS calibrations and literature values

        **Returns:**
        Dictionary with:
        - **component** (str): Component name
        - **eos_model** (str): EOS model used
        - **properties** (dict): All critical properties (MW, Tc, Pc, Zc, Omega, Vcritical, Tb, SG)
        - **method** (str): "Component database lookup"
        - **note** (str): Usage guidance
        - **inputs** (dict): Echo of input parameters

        **Common Mistakes:**
        - Component name misspelled (check spelling, try common aliases like "C1" for methane)
        - Wrong EOS model (use PR79 unless specific requirement)
        - Case sensitivity (component names are case-insensitive, but use standard capitalization)
        - Component not in database (check available components list)
        - Using properties from wrong EOS (properties are EOS-specific)

        **Example Usage:**
        ```python
        {
            "component": "methane",
            "eos": "PR79"
        }
        ```
        Result: Returns all critical properties for methane calibrated for PR79 EOS.

        **Note:** Component properties are EOS-specific. Always use properties from the
        same EOS model throughout your calculations. PR79 is recommended for most applications.
        For components not in database, use external sources or estimate from correlations.
        """
        try:
            # Initialize component library
            lib = component_library()

            # Get component properties
            props = lib.get_component(request.component, eos=request.eos)

            return {
                "component": request.component,
                "eos_model": request.eos,
                "properties": {
                    "molecular_weight_lb_lbmol": float(props["MW"]),
                    "critical_temperature_degR": float(props["Tc"]),
                    "critical_pressure_psia": float(props["Pc"]),
                    "critical_compressibility": float(props["Zc"]),
                    "acentric_factor": float(props["Omega"]),
                    "critical_volume_cuft_lbmol": float(props["Vcrit"]),
                    "boiling_point_degR": float(props["Tb"]),
                    "specific_gravity": float(props["SG"]),
                },
                "method": "Component database lookup",
                "note": "Properties calibrated for specified EOS model",
                "inputs": request.model_dump(),
            }
        except KeyError:
            return {
                "error": f"Component '{request.component}' not found in database",
                "suggestion": "Try common names like 'Methane', 'C1', 'Ethane', 'C2', etc.",
                "available_note": "Database includes C1-C45 plus common non-hydrocarbons",
                "inputs": request.model_dump(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "inputs": request.model_dump(),
            }
