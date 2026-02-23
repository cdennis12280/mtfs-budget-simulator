# MTFS Budget Gap Simulator — Methodology & Technical Documentation

> Quick links: `docs/QUICK_START.md` for setup/run, `docs/DEPLOYMENT.md` for hosting, `docs/AUTHENTICATION.md` for access control.


## 1. Overview

The **MTFS (Medium-Term Financial Strategy) Budget Gap Simulator** is an interactive financial planning tool designed for UK local authority Section 151 officers and Corporate Leadership Teams. It enables deterministic, transparent modelling of 4–5 year financial sustainability through a range of what-if scenarios.

**Key Features:**
- Real-time calculation of annual and cumulative budget gaps
- Reserves depletion tracking
- Automated risk rating (RED / AMBER / GREEN)
- Predefined scenarios (Base Case, Optimistic, Pessimistic)
- Governance audit trail and methodology transparency

---

## 2. Calculation Engine

### 2.1 Core Projection Logic

For each year Y (1–5), the simulator calculates:

#### **Funding Side (Income)**

```
Total Funding (Y) = 
    Council_Tax_Income(Y) × (1 + council_tax_growth_assumption%)
  + Business_Rates_Income(Y) × (1 + business_rates_growth_assumption%)
  + Core_Grants(Y) × (1 + grant_change_assumption%)
  + Fees_And_Charges(Y) × (1 + fees_charges_growth_assumption%)
```

#### **Expenditure Side (Costs)**

```
Projected_Expenditure(Y) = 
    Base_Expenditure(Y)
  + Pay_Impact(Y)           // Pay_Cost_Base × pay_award_assumption%
  + Inflation_Impact(Y)     // Inflation_Base × general_inflation_assumption%
  + ASC_Demand(Y)           // ASC_Base × asc_growth_assumption%
  + CSC_Demand(Y)           // CSC_Base × csc_growth_assumption%
  - Annual_Savings_Achieved(Y)  // Base_Expenditure × savings_target_assumption%
```

**Social Care Protection Option:**
- If `Protect_Social_Care` toggle is TRUE, ASC and CSC demand impacts are set to zero
- Forces council to fund demand pressures from base budget (increases savings requirement)

#### **Budget Gap**

```
Annual_Budget_Gap(Y) = Projected_Expenditure(Y) - Total_Funding(Y)

Cumulative_Gap = Σ Annual_Budget_Gap(1..Y)
```

#### **Reserves Movement**

```
Closing_Reserves(Y) = Opening_Reserves(Y) - Annual_Budget_Gap(Y)
```

Reserves are consumed at the annual gap rate. If closing reserves go negative, the council is technically insolvent (requires external intervention).

---

### 2.2 Data Inputs

**Base Financial Data (CSV):**
- Years 1–5
- Net_Revenue_Budget
- Council_Tax_Income
- Business_Rates_Income
- Core_Grants
- Fees_And_Charges
- Service_Expenditure (base)
- Opening_Reserves
- Pay_Cost_Base, Inflation_Base, Demand_Base_ASC, Demand_Base_CSC

**User Assumptions (Interactive Sliders):**
| Assumption | Range | Default |
|-----------|-------|---------|
| Council Tax Increase (%) | -2.0 to 5.0 | 2.0 |
| Business Rates Growth (%) | -5.0 to 3.0 | -1.0 |
| Grant Change (%) | -10.0 to 2.0 | -2.0 |
| Fees Growth (%) | 0.0 to 6.0 | 3.0 |
| Pay Award (%) | 1.0 to 8.0 | 3.5 |
| General Inflation (%) | 0.5 to 6.0 | 2.0 |
| ASC Demand Growth (%) | -1.0 to 10.0 | 4.0 |
| CSC Demand Growth (%) | -1.0 to 8.0 | 3.0 |
| Annual Savings Target (%) | 0.0 to 5.0 | 2.0 |
| Use of Reserves (%) | 0.0 to 100.0 | 50.0 |
| Protect Social Care | boolean | False |

---

## 3. Scenarios

### 3.1 Predefined Scenarios

#### **Base Case** (Moderate/Realistic)
- Council Tax: 2.0%
- Business Rates: -1.0%
- Grants: -2.0%
- Pay Award: 3.5%
- General Inflation: 2.0%
- ASC Demand: 4.0%
- CSC Demand: 3.0%
- Savings Target: 2.0%
- Social Care Protection: FALSE

**Justification:** Aligned with recent ONS forecasts, Office for Budget Responsibility guidance, and historical local authority trends.

#### **Optimistic** (Best-Case)
- Council Tax: 3.5%
- Business Rates: 2.0%
- Grants: 0.5%
- Pay Award: 2.5%
- General Inflation: 1.5%
- ASC Demand: 2.0%
- CSC Demand: 1.5%
- Savings Target: 3.0%
- Social Care Protection: FALSE

**Justification:** Strong funding recovery, subdued inflation, demand growth contained, savings exceed target.

#### **Pessimistic** (Stress-Case)
- Council Tax: 1.5%
- Business Rates: -3.0%
- Grants: -5.0%
- Pay Award: 5.0%
- General Inflation: 4.5%
- ASC Demand: 6.5%
- CSC Demand: 5.5%
- Savings Target: 1.0%
- Social Care Protection: TRUE

**Justification:** Severe funding squeeze, high cost inflation, demand surges, savings capacity exhausted, forced to protect social care.

---

## 4. Key Performance Indicators (KPIs)

### 4.1 Headline KPIs (Displayed Top of Screen)

| KPI | Formula | Interpretation |
|-----|---------|-----------------|
| **Cumulative 4-Year Gap** | Σ Annual_Budget_Gap(1..5) | Total deficit funding required over MTFS |
| **Year Reserves Exhausted** | Year where Closing_Reserves ≤ 0 | Sustainability horizon (NULL if never exhausted) |
| **Additional Savings Required** | Cumulative_Gap / (Base_Budget × 4) × 100 | % of annual budget that extra savings could address |
| **Council Tax Equivalent** | 1% of Base_Budget | £ impact of 1 percentage point council tax increase |

### 4.2 Sustainability Indicators

| Metric | Formula | Benchmark (Green) |
|--------|---------|-------------------|
| **Reserves / Budget Ratio** | (Final_Reserves / Base_Budget) × 100 | ≥ 5% |
| **Savings as % of Budget** | (Avg_Annual_Savings / Base_Budget) × 100 | ≤ 5% (deliverable) |
| **Funding Volatility Score** | Std Dev(Annual_Funding_Changes) / Base_Budget | < 2% |

---

## 5. Risk Assessment (RAG Rating)

### 5.1 Automated Rules

#### **RED — High Risk**
One or more of:
- Reserves exhausted during MTFS period (Closing_Reserves < 0 at any year)
- Final reserves < 5% of budget
- Average annual gap > 8% of budget
- Average savings target > 5% of budget (undeliverable)

#### **AMBER — Medium Risk**
One or more of:
- Reserves decline > 25% over 5 years
- Average annual gap 5–8% of budget

#### **GREEN — Manageable Risk**
- All thresholds above are met
- Financial position is sustainable

### 5.2 Rationale

These thresholds are calibrated to:
1. **Government Guidance:** MHCLG good practice on reserve minimums (5–10% of budget)
2. **Historical Experience:** Maximum realistic savings delivery (3–5% per annum)
3. **Prudential Code:** Sustainability metrics for local authority finance

---

## 6. Outputs & Visualizations

### 6.1 Core Charts

#### **Budget Gap Trajectory (Line + Bar)**
- Annual gap (primary axis) vs Cumulative gap (secondary axis)
- Shows inflection points and trend
- Zero line indicates balance

#### **Reserves Depletion Profile (Stacked Bar)**
- Year-by-year closing reserves
- Colour gradient (green → amber → red) as reserves decline
- Minimum threshold line at 5% of budget

#### **Funding vs Expenditure (Grouped Bar)**
- Income sources vs expenditure projections side-by-side
- Visualizes gap directly

#### **Scenario Comparison Cards**
- Side-by-side summary: Gap, Reserves, RAG rating

#### **Gap Drivers Waterfall (Year 1)**
- Breaks down Year 1 gap into components
- Funding increases (green), cost pressures (red), savings (green offset)

---

## 7. Scenario Comparison

When user selects a scenario via button, the app re-runs all calculations with that scenario's assumptions. The results are displayed in cards showing:
- 4-year cumulative gap (£m)
- Year 5 closing reserves (£m)
- RAG rating

This allows rapid comparison of strategic alternatives (e.g., "if we increase council tax to 3.5%, can we protect social care?").

---

## 8. Governance & Auditability

### 8.1 Transparent Methodology
- All formulas are visible in the code and documented
- No hidden algorithms; strictly rule-based
- Assumptions are user-visible and adjustable

### 8.2 Data Sources Section
Lists:
- Base financial dataset source (local authority budget papers)
- Assumption baselines (historical trends, external forecasts)
- Methodology updates (version control)

### 8.3 Audit Trail
- User assumptions are captured in URL (via Streamlit widget state)
- All outputs are reproducible from inputs
- No external data feeds or real-time market data (deterministic)

---

## 9. Technical Stack

### 9.1 Languages & Libraries
- **Python 3.9+**
- **Streamlit** — Application framework (web UI)
- **Pandas** — Data manipulation (CSV read, projections)
- **NumPy** — Numerical calculations
- **Plotly** — Interactive visualizations

### 9.2 Deployment
- **Streamlit Community Cloud** (free tier)
- No authentication required
- Runs in browser (no installation)

### 9.3 Data Storage
- CSV files in `/data/` folder
- No database; all data is versioned in git

---

## 10. Limitations & Future Enhancements

### 10.1 Current Limitations
1. **Single-Council Model** — Simplified baseline (not real-time external market data)
2. **Deterministic** — No probability distributions; point estimates only
3. **Linear Assumptions** — Does not model non-linear relationships (e.g., demand cliff edges)
4. **No Service Detail** — Aggregate budget level (no department-by-department tracking)
5. **Aggregate Reserves** — Does not distinguish between earmarked and general reserves
6. **No Savings Detail** — Savings modelled as % reduction, not specific initiatives

### 10.2 Phase 2 Enhancements (Future)
- **Savings Strategy Builder:** Allocate savings across service transformation, income generation, demand management
- **Council Tax Sensitivity Tool:** Impact calculator (£ per band, per resident)
- **Departmental Drill-Down:** Cascade assumptions to individual service areas
- **Stochastic Modelling:** Probability ranges for each assumption
- **Achievement of Savings Register:** Link to live savings tracker
- **Scenario Bookmarking:** Save and compare custom scenarios
- **PDF Export:** Report generation for Cabinet submissions

---

## 11. Running the Application

### 11.1 Local Development
```bash
cd /app
streamlit run main.py
```

Opens at `http://localhost:8501`

### 11.2 Deployment to Streamlit Cloud
```bash
streamlit run app/main.py --logger.level=debug
```

### 11.3 Environment Variables
- None required (CSV data is local)

---

## 12. Support & Governance

### 12.1 Contact
- **Owner:** Section 151 Officer
- **Issues/Requests:** Contact Finance Business Partnering

### 12.2 Version History
| Version | Date | Notes |
|---------|------|-------|
| 1.0 | Feb 2026 | Initial release |

### 12.3 Testing
- Unit tests on calculation logic (pytest, future)
- Manual regression testing on each scenario
- Sensitivity analysis (vary each slider independently)

---

## APPENDIX A: Formula Reference

### A.1 Year-on-Year Funding Growth

Each funding stream is inflated by the user's assumption percentage:

```python
Adjusted_Value(Y) = Base_Value(Y) × (1 + Growth_Assumption%)
```

*Example:* If Business Rates base is £60m and growth assumption is -1.0%, then:
```
Adjusted_Rates(Y) = 60 × (1 - 0.01) = 59.4m
```

### A.2 Cost Pressures

Each cost base is multiplied by the assumption percentage:

```python
Pressure(Y) = Cost_Base(Y) × Pressure_Assumption%
```

*Example:* If Pay cost base is £145m and pay award is 3.5%, then:
```
Pay_Impact(Y) = 145 × 0.035 = 5.075m
```

### A.3 Savings Target

Applied as a percentage of pre-savings expenditure:

```python
Annual_Savings(Y) = (Base_Expenditure + Total_Pressures) × Savings_Target%
```

---

## APPENDIX B: Test Scenarios

### Test 1: Balanced Budget (Zero Gap)
- Adjust sliders so Annual_Budget_Gap ≈ 0 for Year 1
- Verify Closing_Reserves = Opening_Reserves (flat profile)

### Test 2: Reserves Depletion
- Set savings target to 0%, council tax to 0%, grants to -5%
- Verify reserves decline each year
- Check year of exhaustion calculation

### Test 3: Scenario Switching
- Click "Base Case" button
- Verify all sliders reset to base case values
- Verify charts update instantly

### Test 4: Social Care Protection
- Toggle "Protect Social Care" on/off
- Verify ASC/CSC demand impacts toggle between 0 and assumed value
- Check that other costs remain constant

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Classification:** Public (suitable for Council Members and external stakeholders)
