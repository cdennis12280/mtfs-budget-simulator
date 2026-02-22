# To Do — S151 Enhancements

## Core App Status
- ✅ Full MTFS simulator with Streamlit + multipage architecture
- ✅ Phase 1: Calculations, scenarios, RAG ratings, visualizations
- ✅ Phase 2: Savings strategies, sensitivity, stochastic, scenario bookmarking, PDF export
- ✅ Phase 3: Commercial model, PWLB auto-lookup, CSV upload/export
- ✅ Phase 4: Inputs page with data editor, theme customization, onboarding, help tooltips
- ✅ Scenario comparison dashboard, sensitivity analysis (tornado charts)

## Next 5 Features (S151 Governance & Compliance)

### 1. ⭐⭐⭐ Audit Trail & Change Log (IN PROGRESS)
- Track timestamp, user, change type, old/new values for all assumption changes + scenario saves + exports
- Display audit log panel on dedicated admin/audit page
- Export audit report as CSV
- Non-negotiable for external auditor compliance and governance sign-off

### 2. Reserves Policy Alignment Tool
- Define council's reserves policy (min %, target %)
- Auto-flag when model forecast breaches policy
- Visual KPI cards showing policy vs. forecast
- Demonstrates S151's statutory duty to set & maintain adequate reserves

### 3. Multi-Scenario Statutory Report Generator
- Export scenarios + assumptions + KPIs into audit-ready PDF
- Professional template with methodology notes, statutory disclaimers, recommendation narrative
- Auditor sign-off page
- Gives councillors a polished, governance-grade artefact

### 4. Excel / Power BI Data Export
- Export scenario data + time series as `.xlsx` with multiple worksheets
- Optional Power BI connector template
- Integrates with council BI/reporting infrastructure

### 5. Risk & Sensitivity-Weighted Scenario Advisor
- Link sensitivity drivers to corporate risk register
- Suggest which scenarios to stress-test + by how much
- Auto-recommend contingency planning based on sensitivity + risk scores
- Elevates tool to strategic risk adviser

## Running the App

```bash
streamlit run app/main.py
```

Server: http://localhost:8501
