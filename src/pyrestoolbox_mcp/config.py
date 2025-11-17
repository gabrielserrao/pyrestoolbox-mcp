"""Configuration for pyResToolbox MCP Server."""

from typing import Final

# Server Configuration
SERVER_NAME: Final[str] = "pyRestToolbox"
SERVER_VERSION: Final[str] = "1.0.0"
SERVER_DESCRIPTION: Final[str] = (
    "Reservoir Engineering PVT calculations and simulation tools for AI agents"
)

# Unit System Documentation
UNIT_SYSTEM: Final[dict] = {
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
    },
}

# Physical Constants
CONSTANTS: Final[dict] = {
    "R": 10.732,  # Gas constant (psia·ft³)/(lbmol·°R)
    "psc": 14.7,  # Standard pressure (psia)
    "tsc": 60.0,  # Standard temperature (°F)
    "MW_AIR": 28.97,  # Molecular weight of air (lb/lbmol)
}
