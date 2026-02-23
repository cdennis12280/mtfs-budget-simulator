# MTFS Budget Simulator - Section 151 User Guide

> Quick links: `docs/QUICK_START.md` for setup/run, `docs/DEPLOYMENT.md` for hosting, `docs/AUTHENTICATION.md` for access control.


## Purpose
This guide is for Section 151 Officers and senior finance leaders using the MTFS Budget Gap Simulator to set, test, and document the Council's medium-term financial strategy.

## What This Tool Delivers
- A 5-year MTFS projection with clear gap and reserves trajectories.
- Scenario testing, sensitivity and risk stress testing.
- Governance-grade outputs: statutory report, audit trail, and data exports.
- Policy alignment checks for reserves.

## Core Workflow (Recommended)
1. Set the Council baseline in `Inputs` and `Settings`.
2. Adjust the main assumptions on the dashboard.
3. Review headline KPIs and RAG rating.
4. Stress test and compare scenarios.
5. Save snapshots for governance sign-off.
6. Export statutory report and data packs.

## Page-by-Page Guide

### Dashboard (Main)
Purpose: Single-pane decision view and primary assumptions control.

Key controls
- Funding assumptions: Council tax, business rates, grants, fees.
- Expenditure assumptions: pay award, inflation, ASC/CSC demand.
- Savings and reserves use.
- Stress test presets (Mild/Moderate/Severe).
- Forecast snapshots (save/load with versioning).

Key outputs
- Cumulative 4-year gap, reserves status, savings required.
- Financial sustainability RAG rating.
- Reserves policy compliance indicator.
- Risk-adjusted highlights based on the corporate risk register.

Governance use
- Capture a snapshot before cabinet or committee decisions.
- Use presets to evidence downside testing.

### Inputs
Purpose: Set base data and editing for the financial baseline.

Key actions
- Validate the base data table for Year 1 values.
- Confirm opening reserves and key cost bases.

### Commercial
Purpose: Test commercial options and capital income strategies.

Key actions
- Adjust PWLB rate override and project assumptions.
- Review net return and risk (commercial RAG).

### Scenarios Compare
Purpose: Compare multiple scenarios side by side.

Key actions
- Load saved scenarios and predefined cases.
- Compare gap trajectory and reserves trajectory.
- Export comparison to CSV.

### Sensitivity Analysis
Purpose: Identify which assumptions drive the budget gap.

Key actions
- Run a tornado analysis with a selected perturbation.
- Review top drivers.
- Use the two-way sensitivity heatmap for the top two drivers.

### Risk Advisor
Purpose: Link corporate risk register to financial stress tests.

Key actions
- Edit the corporate risk register in-app.
- Choose stress approach (register defaults, risk score scale, or custom).
- Generate single or composite stress scenarios.
- Apply stresses back to assumptions.

Governance use
- Evidence that risks in the corporate register are quantified in the MTFS.

### Reports
Purpose: Generate audit-ready statutory outputs.

Key actions
- Select scenarios for statutory report.
- Include reserves policy compliance and risk advisor summary.
- Export PDF and Excel/Power BI packs.

### Audit
Purpose: Formal audit log of changes and exports.

Key actions
- Review assumption changes, scenario saves, and exports.
- Export audit log for external review.

### Snapshots
Purpose: Rolling forecast versioning.

Key actions
- Review historical snapshots.
- Restore a prior snapshot for decisions or scrutiny.
- Export snapshot history to CSV.

### Settings
Purpose: Organizational configuration and defaults.

Key actions
- Set reserves policy thresholds.
- Toggle onboarding and UI preferences (theme is dark-only).

## Governance and Assurance

### Audit Trail Expectations
- All changes to assumptions, scenario saves, and exports are logged.
- Use snapshots for key governance gates (budget setting, monitoring updates).

### Risk and Sensitivity Evidence
- Keep the corporate risk register aligned to MTFS drivers.
- Include risk advisor summary in statutory reports.
- Use two-way sensitivity to evidence compounding risks.

### Reserves Policy Compliance
- Confirm policy thresholds with the S151 approved policy.
- Use policy alerts in reports and governance meetings.

## Recommended Evidence Pack (For Cabinet or Audit)
- Statutory PDF report.
- Risk advisor summary and stress plan.
- Snapshot record of the agreed position.
- Audit log excerpt covering key decisions.
- Excel export for reconciliation.

## Operating Standards
- Update base data and risk register at least quarterly.
- Use mild and severe stress presets for budget papers.
- Record a snapshot for each formal decision point.

## Troubleshooting
- If a page is blank, run the main Dashboard first to initialize the session.
- If reports fail, check that base data and scenarios exist.
- If risk advisor is empty, confirm that the risk register has valid driver parameters.

## Data and Storage
- Scenarios are stored in-session only (download JSON to retain).
- Audit entries are session-only (export CSV for retention).
- Forecast snapshots are session-only (export CSV to retain).

## Glossary
- MTFS: Medium Term Financial Strategy.
- RAG: Red Amber Green rating of sustainability.
- ASC/CSC: Adult Social Care / Children Social Care.
- PWLB: Public Works Loan Board.
