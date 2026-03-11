"""Configuration for pyResToolbox MCP Server."""

from typing import Final

# Server Configuration
SERVER_NAME: Final[str] = "pyRestToolbox"
SERVER_VERSION: Final[str] = "2.0.0"
SERVER_DESCRIPTION: Final[str] = (
    "Reservoir Engineering PVT calculations and simulation tools for AI agents. "
    "Supports field (psia, degF) and metric (barsa, degC) unit systems."
)

# Unit System Documentation
UNIT_SYSTEM: Final[dict] = {
    "field": {
        "system": "Field Units (US Oilfield)",
        "pressure": "psia (pounds per square inch absolute)",
        "temperature": "degF (degrees Fahrenheit)",
        "length": "ft (feet)",
        "permeability": "mD (millidarcies)",
        "viscosity": "cP (centipoise)",
        "oil_rate": "STB/day (stock tank barrels per day)",
        "gas_rate": "MSCF/day (thousand standard cubic feet per day)",
        "oil_gravity": "API degrees or specific gravity (dimensionless)",
        "gas_gravity": "specific gravity relative to air (dimensionless)",
        "solution_gor": "scf/stb (standard cubic feet per stock tank barrel)",
        "fvf": "rb/stb (reservoir barrels per stock tank barrel) for oil, rcf/scf for gas",
        "compressibility": "1/psi",
        "density": "lb/cuft (pounds per cubic foot)",
    },
    "metric": {
        "system": "Metric Units (SI Oilfield)",
        "pressure": "barsa (bar absolute)",
        "temperature": "degC (degrees Celsius)",
        "length": "m (meters)",
        "permeability": "mD (millidarcies)",
        "viscosity": "cP (centipoise)",
        "oil_rate": "sm3/day (standard cubic meters per day)",
        "gas_rate": "sm3/day (standard cubic meters per day)",
        "oil_gravity": "API degrees or specific gravity (dimensionless)",
        "gas_gravity": "specific gravity relative to air (dimensionless)",
        "solution_gor": "sm3/sm3 (standard cubic meters per standard cubic meter)",
        "fvf": "rm3/sm3 (reservoir cubic meters per standard cubic meter)",
        "compressibility": "1/bar",
        "density": "kg/m3 (kilograms per cubic meter)",
    },
}

# Available Calculation Methods
CALCULATION_METHODS: Final[dict] = {
    "z_factor": {
        "DAK": "Dranchuk & Abou-Kassem (1975)",
        "HY": "Hall & Yarborough (1973)",
        "WYW": "Wang, Ye & Wu (2021)",
        "BUR": "Burgoyne, Nielsen & Stanko (2025) - Universal EOS-based (SPE-229932-MS)",
    },
    "critical_properties": {
        "PMC": "Piper, McCain & Corredor (1993)",
        "SUT": "Sutton (1985)",
        "BUR": "Burgoyne, Nielsen & Stanko (2025) - Universal correlation (SPE-229932-MS)",
    },
    "bubble_point": {
        "STAN": "Standing (1947)",
        "VALMC": "Valko & McCain (2003) - Recommended",
        "VELAR": "Velarde (1997)",
    },
    "solution_gor": {
        "VELAR": "Velarde (1997)",
        "STAN": "Standing (1947)",
        "VALMC": "Valko & McCain (2003)",
    },
    "oil_fvf": {
        "MCAIN": "McCain et al. (1988) - Recommended",
        "STAN": "Standing (1947)",
    },
    "oil_viscosity": {
        "BR": "Beggs & Robinson (1975)",
    },
    "rel_perm": {
        "COR": "Corey (1954)",
        "LET": "Lomeland, Ebeltoft & Thomas (2005)",
        "JER": "Jerauld (2006)",
    },
    "vlp": {
        "WG": "Woldesemayat-Ghajar - Recommended",
        "HB": "Hagedorn-Brown (1965)",
        "GRAY": "Gray (1978) - Gas wells with condensate",
        "BB": "Beggs & Brill (1973) - General purpose",
    },
    "decline_curve": {
        "EXP": "Exponential decline",
        "HYP": "Hyperbolic decline",
        "HM": "Harmonic decline",
        "MSH": "Modified stretched hyperbolic",
        "SE": "Stretched exponential",
        "DUONG": "Duong (2011) - Tight/shale wells",
    },
    "hydrate_prediction": {
        "TOWLER": "Towler (2005) - Gas hydrate formation temperature",
    },
    "brine": {
        "STANDARD": "Industry standard correlations",
        "CO2_DUAN": "Duan & Sun (2003) CO2-H2O-NaCl model",
        "SW_VLE": "Soreide-Whitson (1992) VLE with hydrocarbon gas",
    },
}

# Physical Constants
CONSTANTS: Final[dict] = {
    "R": 10.732,  # Gas constant (psia·ft³)/(lbmol·°R)
    "psc": 14.7,  # Standard pressure (psia)
    "tsc": 60.0,  # Standard temperature (°F)
    "MW_AIR": 28.97,  # Molecular weight of air (lb/lbmol)
    "psc_metric": 1.01325,  # Standard pressure (barsa)
    "tsc_metric": 15.0,  # Standard temperature (°C)
}
