# SKILLS.md — Realtime Disasters Monitoring

**Project Context for Climate Risk, Insurance & Financial Materiality Work**

This document provides the strategic, scientific, and financial context needed to work effectively on this dashboard and related climate-finance tooling.

---

## 1. Project Mission

Build production-grade, open-data-driven tools that help **insurance**, **finance**, and **risk teams** quantify the real-world impact of climate and geophysical hazards using publicly available government and scientific data.

Current focus areas:
- Acute physical risks (earthquakes, tropical cyclones, floods)
- Emerging / systemic risks (space weather / geomagnetic storms)
- Financial translation via insurance claims and exposure data (FEMA NFIP)

---

## 2. Climate Research Approaches Relevant to This Project

### 2.1 Physical Risk Assessment
- **Acute risks**: Sudden events (hurricanes, floods, earthquakes, wildfires, space weather events)
- **Chronic risks**: Longer-term shifts (sea level rise, changing precipitation patterns)

This project primarily focuses on **acute physical risks** using event-level data.

### 2.2 Key Scientific Data Sources & Their Role
| Domain              | Primary Sources in this project          | Typical Use Case                          |
|---------------------|------------------------------------------|-------------------------------------------|
| Seismology          | USGS                                     | Earthquake shaking, tsunami risk          |
| Meteorology         | NOAA NHC / JTWC                          | Tropical cyclone intensity & tracks       |
| Space Weather       | NOAA SWPC + NASA/JPL CNEOS               | Geomagnetic storms, satellite drag, GIC   |
| Flood Insurance     | FEMA OpenFEMA (NFIP Claims & Policies)   | Direct financial loss translation         |

### 2.3 Why Combine These Sources?
Climate scientists and catastrophe modelers rarely rely on a single dataset. Combining:
- Hazard intensity (USGS, NOAA)
- Exposure (location, value)
- Vulnerability (building codes, insurance penetration)
- Loss data (FEMA claims)

...gives a much more defensible view of **financial materiality** than hazard data alone.

---

## 3. Financial Materiality & Climate Risk

### 3.1 What "Financial Materiality" Means Here
A climate or geophysical event is **financially material** when it has the potential to significantly affect:
- Insurer loss ratios and reserves
- Bank loan portfolios (mortgages, commercial real estate)
- Asset valuations (especially real assets and infrastructure)
- Regulatory capital requirements

### 3.2 How Different Actors Manage This

#### Insurance Companies
- Use **catastrophe (CAT) models** (RMS, Verisk, Karen Clark) for pricing and reinsurance.
- Supplement models with **actual claims data** (FEMA NFIP is one of the few large public loss datasets in the US).
- Track **loss development** after major events (e.g., Hurricane Ian, California wildfires).
- Space weather is an emerging "silent" risk for satellite fleets and power utilities.

#### Banks & Asset Managers
- Conduct **climate stress testing** (NGFS scenarios, ECB/EBA climate risk exercises).
- Map physical risk to collateral (mortgages in flood zones, wildfire-prone areas).
- Increasing disclosure requirements under ISSB, CSRD, and SEC climate rules.

#### Climate Scientists & Catastrophe Modelers
- Focus on **hazard + vulnerability + exposure** framework.
- Spend significant effort on **uncertainty quantification** and **non-stationarity** (climate change is making historical data less representative).
- Public datasets like FEMA + USGS are used for model validation and "ground truthing".

#### Regulators & Supervisors
- Want to understand **systemic risk** (e.g., simultaneous losses across many insurers after a major hurricane or a severe geomagnetic storm affecting the grid).

---

## 4. Data Philosophy of This Project

**"Open data first, then enrich"**

- We deliberately start with fully public, no-cost APIs and datasets (USGS, NOAA, FEMA OpenFEMA, NASA/JPL).
- This makes the tool accessible to smaller insurers, NGOs, researchers, and emerging market teams that cannot afford commercial CAT models.
- The trade-off is that commercial models have much richer vulnerability curves and stochastic event sets. Our job is to make the **public data as actionable as possible**.

Key principles:
- Always show **source + timestamp**
- Clearly communicate **limitations** (e.g., NFIP only covers flood, not wind or wildfire)
- Provide **interpretation guidance** (not just raw numbers)

---

## 5. UI/UX & Product Guidelines

When adding features or improving the dashboard:

- **Every number needs context** — raw loss figures mean little without comparison to historical averages or exposure base.
- **Progressive disclosure** — start with high-level KPIs and maps, allow users to drill into methodology.
- **"So what?" test** — every visualization should help answer: "Why should an insurer, banker, or risk manager care?"
- **Graceful degradation** — external APIs fail. Never let the whole app crash (we already have patterns for this with Kp and NFIP).
- **Educational tone** — many users are not climate scientists. Good explanations increase trust and adoption.

Recommended patterns:
- Use expanders for methodology
- Clear "Data last updated" indicators
- Consistent color scales (Reds for losses, Blues for cyclones, etc.)
- Mobile-responsive layouts

---

## 6. Development & Engineering Standards (Production Style)

This repository aims to be treated like internal tooling at an insurance or climate-risk company:

- **Testing**: All data fetchers and transformation functions should have unit tests (especially around edge cases like empty API responses).
- **Documentation**: Major data sources and financial interpretation logic live in `docs/` or `SKILLS.md`.
- **Observability**: Functions log clear errors and return empty/safe defaults instead of crashing.
- **Reproducibility**: Prefer pinned dependencies and clear environment setup.
- **Security**: Never commit secrets. All data sources used here are public.

---

## 7. Emerging & Compound Risks (Future Scope)

Areas the project is well positioned to expand into:
- Compound events (hurricane + flooding + power outage)
- Space weather impacts on critical infrastructure and insurance (satellite, aviation, power)
- Wildfire and severe convective storm data integration
- Forward-looking climate-adjusted hazard layers

---

## 8. How to Contribute Effectively

1. When adding a new data source, document:
   - What physical/financial risk it addresses
   - Strengths and known biases
   - How it should be interpreted by non-experts

2. When building visualizations, always ask:
   - Does this help an underwriter, portfolio manager, or regulator make a better decision?

3. When handling "no data" states, provide helpful guidance instead of leaving users confused.

---

**Last updated**: 2026-05 (after major improvements to Kp handling and NFIP claims aggregation)

This document should be treated as living context for anyone (human or AI) working on the project.
