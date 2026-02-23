# To Do — S151 Enhancements

## Core App Status
- ✅ Full MTFS simulator with Streamlit + multipage architecture
- ✅ Phase 1: Calculations, scenarios, RAG ratings, visualizations
- ✅ Phase 2: Savings strategies, sensitivity, stochastic, scenario bookmarking, PDF export
- ✅ Phase 3: Commercial model, PWLB auto-lookup, CSV upload/export
- ✅ Phase 4: Inputs page with data editor, theme customization, onboarding, help tooltips
- ✅ Scenario comparison dashboard, sensitivity analysis (tornado charts)
- ✅ Dark theme only (enforced)
- ✅ Wizard workflow (live KPIs + live charts)
- ✅ Risk & sensitivity advisor page
- ✅ Session-only storage (no disk writes; export-only)
- ✅ Snapshot admin page + CSV export
- ✅ Risk register CSV default + downloads
- ✅ Two-way sensitivity heatmap
- ✅ Session token sharing across tabs

## Next 5 Features (S151 Governance & Compliance)

### 1. ✅ Audit Trail & Change Log (COMPLETED)
- Track timestamp, user, change type, old/new values for all assumption changes + scenario saves + exports
- Display audit log panel on dedicated admin/audit page
- Export audit report as CSV
- Non-negotiable for external auditor compliance and governance sign-off

### 2. ✅ Reserves Policy Alignment Tool (COMPLETED)
- Define council's reserves policy (min %, target %)
- Auto-flag when model forecast breaches policy
- Visual KPI cards showing policy vs. forecast
- Demonstrates S151's statutory duty to set & maintain adequate reserves

### 3. ✅ Multi-Scenario Statutory Report Generator (COMPLETED)
- Export scenarios + assumptions + KPIs into audit-ready PDF
- Professional template with methodology notes, statutory disclaimers, recommendation narrative
- Auditor sign-off page
- Gives councillors a polished, governance-grade artefact
- Integration: app/pages/7_reports.py dashboard with multi-scenario selector
- Audit logging for all statutory report exports

### 4. ✅ Excel / Power BI Data Export (COMPLETED)
- Export scenario data + time series as `.xlsx` with multiple worksheets
- Optional Power BI connector template
- Integrates with council BI/reporting infrastructure
- Integration: app/pages/7_reports.py with side-by-side Excel and Power BI export options
- Audit logging for all data exports
- Excel includes: Metadata, Executive Summary, Time Series, Key Metrics, Individual Scenarios
- Power BI template includes: Sheet mapping, relationships, recommended visuals, DAX measures, deployment guide

### 5. Risk & Sensitivity-Weighted Scenario Advisor
- Link sensitivity drivers to corporate risk register
- Suggest which scenarios to stress-test + by how much
- Auto-recommend contingency planning based on sensitivity + risk scores
- Elevates tool to strategic risk adviser
- ✅ Implemented with Risk Advisor page + stress tests + composite scenario

## Hosted Access (SaaS Readiness) — NEXT

### 6. Authentication & Access Control (Pending)
- Password-protected login for Section 151 users
- Role-based access (Admin, Finance Analyst, Read-only)
- Session timeout + MFA option

### 7. Multi-Tenant Data Storage (Pending)
- Separate council workspaces and data isolation
- Encrypted storage for uploaded files and exports
- Data retention policy and deletion workflows

### 8. Billing & Subscription Management (Pending)
- Paid access tiers for councils
- Stripe or equivalent billing integration
- License management and usage limits

### 9. Hosting & Deployment (Pending)
- Production hosting (e.g., Streamlit Cloud, Azure, AWS, or Docker)
- HTTPS, custom domain, and monitoring
- Backups and disaster recovery

### 10. Security & Compliance (Pending)
- GDPR / UK data protection alignment
- Audit logging retention and export
- Pen-test readiness and vulnerability scanning

## Immediate Next Tasks (Suggested)
1. Add authentication (login + roles) with session TTL and logout.
2. Centralize app_link usage on all pages and add “New clean session” to header.
3. Add a banner noting session-only mode and export reminders.
4. Add link to Section 151 user guide from header or settings.
5. Add input‑to‑model mapping for additional line items (if needed).

## Critical (Pitch Readiness)
1. Record a 3–5 minute walkthrough video using `docs/WALKTHROUGH_VIDEO.md`.

## Deferred (Later)
- Deploy a stable demo environment (hosted instance with auth, persistence, and data reset).

## Running the App

```bash
streamlit run app/main.py
```

Server: http://localhost:8501
