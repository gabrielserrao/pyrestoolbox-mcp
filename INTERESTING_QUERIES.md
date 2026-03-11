# Interesting Queries for Claude

A curated collection of interesting and practical queries you can ask Claude when using the pyResToolbox MCP server.

## Quick PVT Checks

```
"What's the bubble point pressure for a 35 API oil at 180F with 800 scf/stb GOR and 0.75 gas gravity?"

"Calculate Z-factor for a gas with SG 0.7 at 3500 psia and 180F"

"What's the oil formation volume factor at 3000 psia for 38 API oil at 175F?"
```

## Correlation Comparisons

```
"Compare bubble point predictions from Standing, Valko-McCain, and Velarde for 35 API oil at 180F with GOR 800"

"How do DAK, Hall-Yarborough, and WYW Z-factor methods compare at 3500 psia and 180F?"

"Compare Corey vs LET relative permeability curves with the same endpoints"
```

## Well Performance Studies

```
"Generate an IPR curve for a well with Pi=4000 psia, Pb=3500 psia, 38 API oil at 175F, 75ft pay, 150mD perm, skin -2"

"How does skin factor affect production? Compare rates for skin -5, 0, +5, and +10"

"What production rate can I expect at 2000 psia flowing pressure?"
```

## Simulation Preparation

```
"Generate a SWOF table using Corey correlation with Swc=0.15, Sorw=0.15, no=2.5, nw=1.5"

"Create aquifer influence functions for dimensionless radius 10"

"Generate a complete black oil PVT table from 500 to 5000 psia for 38 API oil"
```

## Geomechanics Analysis

```
"Calculate vertical stress at 10000 ft with average bulk density 2.4 g/cc"

"What's the safe mud weight window at 12000 ft depth?"

"Estimate fracture gradient at 8000 ft with Poisson ratio 0.25"
```

## Decline Curve Analysis

```
"Forecast production for the next 5 years using Arps hyperbolic decline with qi=1000, Di=0.1, b=1.2"

"What's the EUR for this well?"

"Fit a Duong decline model to my tight oil well data"
```

## Material Balance

```
"Estimate OGIP from P/Z data: pressures [4000, 3500, 3000, 2500] and cumulative production [0, 50, 120, 210] MMscf"

"Run a Havlena-Odeh oil material balance analysis"
```

## Brine & CO2 Sequestration

```
"Calculate brine properties at 3000 psia and 175F with 5% NaCl salinity"

"What's the CO2-brine mutual solubility at sequestration conditions: 3000 psia, 180F, 50000 ppm salinity?"
```

## Reservoir Heterogeneity

```
"Convert Lorenz coefficient 0.5 to Dykstra-Parsons beta parameter"

"Generate a 10-layer permeability distribution for Lorenz=0.6 and average k=100 mD"
```

## Multi-Step Workflows

```
"Complete reservoir analysis: calculate bubble point, generate PVT table, create IPR curve, and analyze performance for 38 API oil at 175F with Pi=4000 psia"

"Design a completion: calculate optimal flowing pressure, generate IPR, compare different skin factors"

"Evaluate a gas reservoir: calculate critical properties, generate IPR, compare Z-factor methods"
```

## Tips

1. **Be specific** - include API gravity, temperature, pressure, and other relevant parameters
2. **Specify methods** - mention which correlation you want (VALMC, DAK, Corey, LET, etc.)
3. **Include units** - always specify units (psia, degF, mD, ft)
4. **Ask for comparisons** - Claude can compare methods and scenarios side by side
5. **Request tables** - ask for tabulated results when you need multiple values
6. **Chain queries** - build on previous answers for complex workflows
