# MTFS Budget Gap Simulator

## Overview

**Interactive financial planning tool for UK local authority Section 151 officers and Corporate Leadership Teams.**

This web application enables transparent, deterministic modelling of 4–5 year financial sustainability, with what-if scenario analysis and automated risk ratings (RED / AMBER / GREEN).

### Key Capabilities

✅ **Real-time MTFS Projection**
- Projects annual and cumulative budget gaps over 5 years
- Models funding sources (council tax, business rates, grants, fees)
- Calculates cost pressures (pay, inflation, demand)

✅ **Reserves Strategy**
- Tracks reserves depletion profile
- Identifies year when reserves are exhausted
- Tests reserve-use strategies

✅ **Scenario Modelling**
- Pre-built scenarios: Base Case, Optimistic, Pessimistic
- Custom what-if analysis via interactive sliders
- Side-by-side scenario comparison

✅ **Risk Assessment**
- Automated RED / AMBER / GREEN sustainability rating
- Financial resilience indicators (reserves ratio, savings capacity)
- Funding volatility analysis

✅ **Decision Support**
- Budget gap waterfall (drivers analysis)
- Savings requirement calculation
- Council tax equivalent impact

✅ **Governance**
- Transparent, auditable formulas
- Full methodology documentation
- Deterministic (rule-based, not ML)

---

## Quick Start

### 1. Install Dependencies

```bash
cd /workspaces/mtfs-budget-simulator
pip install -r requirements.txt
```

### 2. Run Locally

```bash
streamlit run app/main.py
```

Opens at: `http://localhost:8501`

### 3. Use the App

- **Left Sidebar:** Adjust funding and spending assumptions with sliders
- **Main Panel:** View MTFS projections, charts, and scenarios
- **Buttons:** Quick-load predefined scenarios (Base Case, Optimistic, Pessimistic)
- **Expander:** View governance, methodology, and limitations

---

## Documentation
- Docs index: `docs/README.md`

## Project Structure

```
├── app/
│   └── main.py                 # Streamlit web application
├── modules/
│   ├── calculations.py         # Core MTFS calculation engine
│   ├── scenarios.py            # Predefined scenarios
│   └── rag_rating.py           # Risk assessment rules
├── data/
│   └── base_financials.csv     # Base financial data (5 years)
├── docs/
│   └── methodology.md          # Full technical documentation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Features

### User Inputs (Interactive Sliders)

**Funding Assumptions:**
- Council Tax Increase (%)
- Business Rates Growth (%)
- Grant Change (%)
- Fees & Charges Growth (%)

**Expenditure Assumptions:**
- Pay Award (%)
- General Inflation (%)
- ASC Demand Growth (%)
- CSC Demand Growth (%)

**Policy Decisions:**
- Annual Savings Target (% of budget)
- Use of Reserves (%)
- Protect Social Care (toggle)

### Outputs (Visualizations & Metrics)

1. **Headline KPIs**
   - Cumulative 4-year gap (£m)
   - Year reserves exhausted
   - Savings required to balance
   - Financial sustainability rating (RAG)

2. **Charts**
   - Budget gap trajectory (annual + cumulative)
   - Reserves depletion profile
   - Funding vs expenditure comparison
   - Gap drivers waterfall

3. **Scenario Analysis**
   - Base Case, Optimistic, Pessimistic side-by-side
   - Custom scenario comparison

4. **Detailed Tables**
   - Year-by-year projection data
   - All input assumptions visible

5. **Governance Panel**
   - Data sources and methodology
   - Limitations and risk factors
   - RAG rating rules
   - Version information

---

## Calculation Logic

### Core Formula

**For each year:**

```
Total Funding = Council Tax + Business Rates + Grants + Fees & Charges

Projected Expenditure = Base + Pay Impact + Inflation + Demand - Savings

Annual Gap = Projected Expenditure - Total Funding

Cumulative Gap = Sum of annual gaps

Closing Reserves = Opening Reserves - Annual Gap
```

All figures are adjusted by the user's assumption percentages.

**Social Care Protection:** If enabled, ASC/CSC demand impacts are zeroed (forcing council to fund from base).

---

## Risk Assessment (RAG Rating)

### GREEN (Sustainable)
- Reserves ≥ 5% of budget
- Annual gap < 8% of budget
- Savings deliverable (< 5% of budget)

### AMBER (Medium Risk)
- Reserves declining > 25% over MTFS
- Gap 5–8% of budget

### RED (High Risk)
- Reserves exhausted or < 5% of budget
- Gap > 8% of budget
- Savings undeliverable (> 5% of budget)

---

## Scenarios

### Base Case (Realistic)
- Council Tax: 2% growth
- Business Rates: -1% decline
- Grants: -2% decline
- Pay Award: 3.5%
- Inflation: 2%
- Savings Target: 2% of budget
- Social Care Protection: NO

### Optimistic (Best-Case)
- Council Tax: 3.5% growth
- Business Rates: 2% growth
- Grants: 0.5% growth
- Pay Award: 2.5%
- Inflation: 1.5%
- Savings Target: 3% of budget
- Social Care Protection: NO

### Pessimistic (Stress-Case)
- Council Tax: 1.5% growth
- Business Rates: -3% decline
- Grants: -5% decline
- Pay Award: 5%
- Inflation: 4.5%
- Savings Target: 1% of budget
- Social Care Protection: YES (protected from cuts)

---

## Deployment

### Streamlit Community Cloud (Free)

1. Push to GitHub
2. Connect repo to Streamlit Cloud
3. Select `app/main.py` as entrypoint
4. Deploy

**URL Format:**
```
https://[username]-[repo-name]-[branch].streamlit.app
```

---

## Technical Stack

- **Language:** Python 3.9+
- **Web Framework:** Streamlit 1.28+
- **Data:** Pandas, NumPy
- **Visualization:** Plotly
- **Deployment:** Streamlit Community Cloud (free)
- **Storage:** CSV files (versioned in git)

---

## Documentation

- **Full Methodology:** See [docs/methodology.md](docs/methodology.md)
- **Formulas & Thresholds:** Detailed in methodology
- **Testing Guide:** Included in docs

---

## Use Cases

### Section 151 Officer
- Develop realistic MTFS
- Test reserve strategy
- Prepare Cabinet papers
- Q&A against challenge from Members

### Finance Business Partner
- Explain budget challenges to service directors
- Model impact of policy decisions (e.g., social care protection)
- Build savings case with evidence

### Corporate Director
- Understand sustainability position
- Sense-check financial assumptions
- Support strategic options appraisal

### Council Members
- Simple, understandable view of finances
- Scenario comparison (optimistic vs pessimistic)
- See impact of council tax decisions

---

## Limitations & Future Work

### Current Limitations
- Single simplified council model (not real-time data)
- Deterministic (no probability ranges)
- Aggregate budget level (no departmental drill-down)
- Savings modelled as % of budget (not specific initiatives)

### Phase 2 Enhancements (Roadmap)
- Savings strategy builder (allocate across initiatives)
- Council tax sensitivity tool
- Departmental cascading
- Stochastic modelling (probability ranges)
- PDF report generation
- Scenario bookmarking
- Link to live savings register

---

## Support

- **Owner:** Section 151 Officer
- **Questions/Issues:** Contact Finance Team
- **Version:** 1.0 (Feb 2026)

---

## License

Internal use only — UK Local Government Finance

---

## About

Built with Python + Streamlit to support transparent, auditable financial planning aligned to:
- MHCLG Good Practice Guidance
- Prudential Code for Capital Finance
- CIPFA MTFS Best Practice

**No external market data, logins, or authentication required.**
