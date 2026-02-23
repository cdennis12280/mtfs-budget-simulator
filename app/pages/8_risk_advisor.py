"""
Risk & Sensitivity-Weighted Scenario Advisor
"""

from __future__ import annotations

import html
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Add modules to path
modules_path = Path(__file__).parent.parent.parent / "modules"
sys.path.insert(0, str(modules_path))

from audit_log import get_audit_log
from auth import current_user, require_auth, require_roles, auth_sidebar
from calculations import MTFSCalculator
from risk_advisor import (
    adverse_value,
    build_contingency_plan,
    build_stress_table,
    load_risk_register,
    merge_sensitivity,
    normalize_risk_register,
)
from sensitivity import SensitivityAnalysis
from ui import apply_theme, page_header


apply_theme()
if not require_auth():
    st.stop()
require_roles({"Admin", "Analyst", "Read-only"})


risk_path = Path(__file__).parent.parent.parent / "data" / "risk_register.csv"

_, toggle_col = st.columns([4, 1], vertical_alignment="center")
with toggle_col:
    st.caption("View Mode")
    show_mockup = st.toggle("Premium mockup", value=True)


def render_mockup() -> None:
    user = current_user()
    username = user.username if user else "Analyst"
    tenant = user.tenant if user else "Default"
    role = user.role if user else "Analyst"

    risk_df = load_risk_register(risk_path)

    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #0a0f1c;
  --bg-2: #0d111c;
  --surface: #111827;
  --surface-2: #1e293b;
  --surface-3: rgba(30, 41, 59, 0.55);
  --border: rgba(148, 163, 184, 0.16);
  --border-soft: rgba(148, 163, 184, 0.08);
  --text: #e2e8f0;
  --muted: #94a3b8;
  --muted-2: #cbd5f5;
  --accent: #6366f1;
  --accent-soft: rgba(99, 102, 241, 0.25);
  --danger: #e11d48;
  --warning: #d97706;
  --success: #10b981;
  --shadow-1: 0 24px 50px rgba(2, 6, 23, 0.45);
  --shadow-2: 0 10px 28px rgba(2, 6, 23, 0.32);
  --glow: 0 0 0 1px rgba(99, 102, 241, 0.25), 0 0 28px rgba(99, 102, 241, 0.22);
  --radius-xl: 22px;
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 10px;
}

html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 10% -10%, rgba(99, 102, 241, 0.18), transparent 60%),
              radial-gradient(900px 500px at 90% -20%, rgba(14, 165, 233, 0.12), transparent 55%),
              linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%) !important;
  color: var(--text) !important;
  font-family: "Inter Tight", "SF Pro Display", "Segoe UI", sans-serif !important;
  letter-spacing: 0.01em;
}

#MainMenu, header, footer {visibility: hidden !important;}

.block-container {
  padding-top: 1.2rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
  max-width: 1400px;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.95) 0%, rgba(15, 23, 42, 0.96) 100%) !important;
  border-right: 1px solid var(--border);
  box-shadow: 10px 0 40px rgba(2, 6, 23, 0.35);
}

[data-testid="stSidebarNav"] {display: none !important;}

.premium-sidebar {
  padding: 0.5rem 0.2rem 2rem 0.2rem;
}

.brand-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  margin: 0.6rem 0.6rem 1.6rem 0.6rem;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-soft);
  box-shadow: var(--shadow-2);
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: rgba(99, 102, 241, 0.18);
  border: 1px solid rgba(99, 102, 241, 0.45);
  color: var(--muted-2);
  font-weight: 700;
}

.brand-text strong {
  font-size: 15px;
  display: block;
  color: var(--text);
}

.brand-text span {
  font-size: 12px;
  color: var(--muted);
}

.nav-group {
  padding: 0 0.6rem;
  margin-bottom: 1.2rem;
}

.nav-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: rgba(148, 163, 184, 0.6);
  margin: 0.9rem 0.7rem 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin: 6px 0;
  border-radius: 12px;
  color: var(--muted);
  text-decoration: none;
  font-size: 14px;
  position: relative;
}

.nav-item .nav-icon {
  width: 16px;
  height: 16px;
  border-radius: 6px;
  background: rgba(148, 163, 184, 0.2);
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.nav-item.active {
  color: var(--text);
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.35);
  box-shadow: var(--glow);
}

.nav-item.active::before {
  content: "";
  position: absolute;
  left: -2px;
  width: 3px;
  height: 65%;
  border-radius: 4px;
  background: var(--accent);
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.6);
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 26px;
  border-radius: var(--radius-xl);
  background: linear-gradient(140deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.75));
  border: 1px solid var(--border);
  box-shadow: var(--shadow-1);
  backdrop-filter: blur(18px);
}

.header-title {
  font-size: 30px;
  font-weight: 700;
  color: var(--text);
}

.header-subtitle {
  margin-top: 6px;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  max-width: 620px;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border-soft);
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: rgba(148, 163, 184, 0.15);
  border: 1px solid rgba(148, 163, 184, 0.25);
  font-weight: 600;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-meta span:first-child {
  font-size: 13px;
  color: var(--text);
  font-weight: 600;
}

.user-meta span:last-child {
  font-size: 12px;
  color: var(--muted);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--border-soft);
  background: rgba(15, 23, 42, 0.7);
  display: grid;
  place-items: center;
}

.callout {
  margin-top: 18px;
  padding: 16px 20px;
  border-radius: var(--radius-lg);
  border: 1px solid rgba(99, 102, 241, 0.35);
  background: rgba(30, 41, 59, 0.7);
  box-shadow: var(--shadow-2);
  color: var(--muted-2);
  backdrop-filter: blur(14px);
}

.section-title {
  margin: 26px 0 14px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
}

.table-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  background: rgba(15, 23, 42, 0.75);
  box-shadow: var(--shadow-1);
  padding: 16px;
  backdrop-filter: blur(18px);
}

.risk-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 10px;
  font-size: 14px;
}

.risk-table thead th {
  text-align: left;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.65);
  padding: 6px 12px;
}

.risk-table tbody tr {
  background: rgba(30, 41, 59, 0.55);
  border-radius: 14px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.risk-table tbody tr:hover {
  background: rgba(30, 41, 59, 0.85);
  box-shadow: 0 12px 26px rgba(2, 6, 23, 0.35);
  transform: translateY(-2px);
}

.risk-table tbody td {
  padding: 12px;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

.risk-table tbody tr td:first-child {
  border-left: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 12px 0 0 12px;
  font-size: 12px;
  color: var(--muted);
  font-weight: 600;
}

.risk-table tbody tr td:last-child {
  border-right: 1px solid rgba(148, 163, 184, 0.08);
  border-radius: 0 12px 12px 0;
}

.risk-title strong {
  display: block;
  color: var(--text);
  font-weight: 600;
}

.risk-title span {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
  display: block;
}

.param-code {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.7);
  background: rgba(15, 23, 42, 0.6);
  padding: 4px 8px;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.15);
}

.direction {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.direction.up { color: #a5b4fc; }
.direction.down { color: var(--warning); }

.pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 34px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.pill-1 { background: rgba(16, 185, 129, 0.15); color: #86efac; }
.pill-2 { background: rgba(34, 197, 94, 0.12); color: #86efac; }
.pill-3 { background: rgba(148, 163, 184, 0.16); color: #cbd5f5; }
.pill-4 { background: rgba(217, 119, 6, 0.18); color: #fbbf24; }
.pill-5 { background: rgba(225, 29, 72, 0.18); color: #fda4af; }

.stress-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stress-value {
  font-weight: 600;
  color: var(--text);
}

.stress-bar {
  width: 120px;
  height: 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.18);
  overflow: hidden;
}

.stress-bar span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.7), rgba(165, 180, 252, 0.7));
}

.table-actions {
  margin-top: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.action-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 16px;
  border-radius: 12px;
  font-weight: 600;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.btn-primary {
  background: var(--accent);
  color: #0a0f1c;
  box-shadow: var(--shadow-2);
}

.btn-primary:hover {
  filter: brightness(1.05);
  transform: translateY(-1px);
}

.btn-outline {
  background: transparent;
  border-color: rgba(148, 163, 184, 0.3);
  color: var(--text);
}

.btn-outline:hover {
  border-color: rgba(148, 163, 184, 0.6);
  box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.2);
}

.btn-ghost {
  background: rgba(15, 23, 42, 0.7);
  border-color: rgba(148, 163, 184, 0.2);
  color: var(--muted);
}
</style>
""",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            """
<div class="premium-sidebar">
  <div class="brand-badge">
    <div class="brand-mark">MTFS</div>
    <div class="brand-text">
      <strong>Treasury Studio</strong>
      <span>Risk & Sensitivity Suite</span>
    </div>
  </div>
  <div class="nav-group">
    <div class="nav-title">Primary</div>
    <div class="nav-item"><span class="nav-icon"></span>Main</div>
    <div class="nav-item"><span class="nav-icon"></span>Council Profile</div>
    <div class="nav-item"><span class="nav-icon"></span>Wizard</div>
    <div class="nav-item"><span class="nav-icon"></span>Inputs</div>
    <div class="nav-item"><span class="nav-icon"></span>Commercial</div>
    <div class="nav-item"><span class="nav-icon"></span>Settings</div>
  </div>
  <div class="nav-group">
    <div class="nav-title">Risk Engine</div>
    <div class="nav-item"><span class="nav-icon"></span>Scenarios Compare</div>
    <div class="nav-item"><span class="nav-icon"></span>Sensitivity</div>
    <div class="nav-item"><span class="nav-icon"></span>Audit</div>
    <div class="nav-item"><span class="nav-icon"></span>Reports</div>
    <div class="nav-item active"><span class="nav-icon"></span>Risk Adviser</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    rows = []
    for _, row in risk_df.iterrows():
        direction = row["direction"]
        arrow = "↑" if direction == "increase" else "↓"
        direction_class = "up" if direction == "increase" else "down"
        direction_label = "Increase" if direction == "increase" else "Decrease"
        likelihood = int(row["likelihood"])
        impact = int(row["impact"])
        stress = float(row["default_stress_pct"])
        stress_width = max(0, min(100, int(stress * 2)))

        rows.append(
            f"""
<tr>
  <td>{html.escape(str(row['risk_id']))}</td>
  <td class="risk-title">
    <strong>{html.escape(str(row['risk_title']))}</strong>
    <span>{html.escape(str(row['driver_label']))}</span>
  </td>
  <td><span class="param-code">{html.escape(str(row['driver_param']))}</span></td>
  <td><span class="direction {direction_class}">{arrow} {direction_label}</span></td>
  <td><span class="pill pill-{likelihood}">{likelihood}</span></td>
  <td><span class="pill pill-{impact}">{impact}</span></td>
  <td>
    <div class="stress-wrap">
      <span class="stress-value">{int(stress)}%</span>
      <div class="stress-bar"><span style="width:{stress_width}%"></span></div>
    </div>
  </td>
</tr>
"""
        )

    header_html = f"""
<div class="dashboard-header">
  <div>
    <div class="header-title">Risk and Sensitivity Scenario Advisor</div>
    <div class="header-subtitle">Institutional-grade linkage between corporate risk registers and MTFS model drivers for composite worst-case stress testing.</div>
  </div>
  <div class="header-actions">
    <div class="header-user">
      <div class="avatar">{html.escape(username[:2].upper())}</div>
      <div class="user-meta">
        <span>{html.escape(username)} · {html.escape(role)}</span>
        <span>{html.escape(tenant)} Treasury Tenant</span>
      </div>
    </div>
    <div class="icon-btn">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"></path>
        <path d="M12 7v5l3 3"></path>
      </svg>
    </div>
    <div class="icon-btn">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8a6 6 0 0 0-12 0v4"></path>
        <path d="M6 16v2a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-2"></path>
      </svg>
    </div>
    <div class="icon-btn">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10 16l4-4-4-4"></path>
        <path d="M14 12H3"></path>
        <path d="M21 12a9 9 0 1 1-9-9"></path>
      </svg>
    </div>
  </div>
</div>
"""

    callout_html = """
<div class="callout">
  Keep the risk register aligned to MTFS drivers. Use composite stress for worst-case testing.
</div>
"""

    table_html = f"""
<div class="section-title">Corporate Risk Register</div>
<div class="table-card">
  <table class="risk-table">
    <thead>
      <tr>
        <th>Risk ID</th>
        <th>Risk</th>
        <th>Driver Param</th>
        <th>Direction</th>
        <th>Likelihood</th>
        <th>Impact</th>
        <th>Default Stress</th>
      </tr>
    </thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
  <div class="table-actions">
    <div class="action-group">
      <button class="btn btn-primary">Add Risk</button>
      <button class="btn btn-outline">Edit Selected</button>
      <button class="btn btn-ghost">Apply Stress</button>
    </div>
    <div class="action-group">
      <button class="btn btn-outline">Download CSV</button>
      <button class="btn btn-ghost">Audit Trail</button>
    </div>
  </div>
</div>
"""

    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown(callout_html, unsafe_allow_html=True)
    st.markdown(table_html, unsafe_allow_html=True)
    st.markdown("<div style=\"height:32px\"></div>", unsafe_allow_html=True)


def render_live() -> None:
    auth_sidebar()
    read_only = st.session_state.get("auth_role") == "Read-only"
    if read_only:
        st.info("Read-only mode: edits and stress applications are disabled.")

    page_header(
        "Risk and Sensitivity Scenario Advisor",
        "Link the corporate risk register to model sensitivity and generate stress tests.",
    )
    st.markdown(
        """
<div class="app-callout">
  Keep the risk register aligned to MTFS drivers. Use composite stress for worst-case testing.
</div>
""",
        unsafe_allow_html=True,
    )

    def load_base_data():
        if "base_data" in st.session_state:
            return st.session_state["base_data"].copy()
        data_path = Path(__file__).parent.parent.parent / "data" / "base_financials.csv"
        return pd.read_csv(data_path)

    base_data = load_base_data()
    base_budget_year1 = base_data[base_data["Year"] == "Year_1"]["Net_Revenue_Budget"].values[0]

    base_params = {
        "council_tax_increase_pct": st.session_state.get("council_tax_increase_pct", 2.0),
        "business_rates_growth_pct": st.session_state.get("business_rates_growth_pct", -1.0),
        "grant_change_pct": st.session_state.get("grant_change_pct", -2.0),
        "fees_charges_growth_pct": st.session_state.get("fees_charges_growth_pct", 3.0),
        "pay_award_pct": st.session_state.get("pay_award_pct", 3.5),
        "general_inflation_pct": st.session_state.get("general_inflation_pct", 2.0),
        "asc_demand_growth_pct": st.session_state.get("asc_demand_growth_pct", 4.0),
        "csc_demand_growth_pct": st.session_state.get("csc_demand_growth_pct", 3.0),
        "annual_savings_target_pct": st.session_state.get("annual_savings_target_pct", 2.0),
        "use_of_reserves_pct": st.session_state.get("use_of_reserves_pct", 50.0),
        "protect_social_care": st.session_state.get("protect_social_care", False),
    }

    valid_params = {
        "council_tax_increase_pct",
        "business_rates_growth_pct",
        "grant_change_pct",
        "fees_charges_growth_pct",
        "pay_award_pct",
        "general_inflation_pct",
        "asc_demand_growth_pct",
        "csc_demand_growth_pct",
        "annual_savings_target_pct",
        "use_of_reserves_pct",
        "protect_social_care",
    }
    base_params = {k: v for k, v in base_params.items() if k in valid_params}

    calc = MTFSCalculator(base_data)

    st.markdown("---")
    st.markdown("## Corporate Risk Register")

    if "risk_register_df" not in st.session_state:
        st.session_state["risk_register_df"] = load_risk_register(risk_path)

    risk_df = st.session_state["risk_register_df"]

    edited = st.data_editor(
        risk_df,
        use_container_width=True,
        num_rows="dynamic",
        disabled=read_only,
        column_config={
            "likelihood": st.column_config.NumberColumn(min_value=0, max_value=5, step=1),
            "impact": st.column_config.NumberColumn(min_value=0, max_value=5, step=1),
            "default_stress_pct": st.column_config.NumberColumn(min_value=0, max_value=50, step=1),
            "direction": st.column_config.SelectboxColumn(options=["increase", "decrease"]),
        },
    )

    col_apply, col_reset, col_save = st.columns(3)
    with col_apply:
        if st.button("Apply edits", disabled=read_only):
            st.session_state["risk_register_df"] = normalize_risk_register(edited)
            st.success("Risk register updated for this session.")
    with col_reset:
        if st.button("Reset to defaults", disabled=read_only):
            st.session_state["risk_register_df"] = load_risk_register(risk_path)
            st.info("Risk register reset to defaults.")
    with col_save:
        csv_bytes = normalize_risk_register(edited).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download risk register (CSV)",
            data=csv_bytes,
            file_name="risk_register.csv",
            mime="text/csv",
        )

    risk_df = normalize_risk_register(edited)

    st.markdown("---")
    st.markdown("## Sensitivity Linkage")

    perturbation = st.slider(
        "Sensitivity perturbation (±%)",
        min_value=1,
        max_value=30,
        value=10,
        step=1,
        help="Used to compute the tornado sensitivity range linked to each risk driver.",
        disabled=read_only,
    )

    sens = SensitivityAnalysis(calc, base_data, base_budget_year1)
    sensitivity_df = sens.tornado_analysis(base_params, perturbation)
    linked = merge_sensitivity(risk_df, sensitivity_df)

    st.dataframe(
        linked[
            [
                "risk_id",
                "risk_title",
                "driver_label",
                "driver_param",
                "likelihood",
                "impact",
                "risk_score",
                "Sensitivity Range (£m)",
            ]
        ].rename(
            columns={
                "risk_id": "Risk ID",
                "risk_title": "Risk",
                "driver_label": "Driver",
                "driver_param": "Driver Param",
            }
        ),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("## Risk-Weighted Stress Tests")

    stress_override = st.selectbox(
        "Stress level",
        options=["Use register defaults", "Use risk score scale", "Custom %"],
        index=0,
        disabled=read_only,
    )

    custom_stress = None
    if stress_override == "Custom %":
        custom_stress = st.slider("Custom stress %", 1, 50, 15, 1, disabled=read_only)

    stress_df = build_stress_table(
        calc,
        base_params,
        linked,
        stress_pct_override=custom_stress if stress_override == "Custom %" else None,
    )

    if stress_override == "Use risk score scale":
        linked_for_score = linked.copy()
        linked_for_score["default_stress_pct"] = 0
        stress_df = build_stress_table(calc, base_params, linked_for_score, None)

    if stress_df.empty:
        st.info("No stress tests could be generated. Check the risk register driver parameters.")
        st.stop()

    st.dataframe(
        stress_df[
            [
                "Risk ID",
                "Risk",
                "Driver",
                "Direction",
                "Risk Score",
                "Stress %",
                "Base Value",
                "Stressed Value",
                "Gap Delta (£m)",
                "Weighted Impact",
            ]
        ].style.format(
            {
                "Base Value": "{:.2f}",
                "Stressed Value": "{:.2f}",
                "Gap Delta (£m)": "{:.2f}",
                "Weighted Impact": "{:.2f}",
            }
        ),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("## Recommended Stress Scenarios")

    top_n = st.slider("Number of top risks to stress", 1, min(6, len(stress_df)), 3, 1, disabled=read_only)

    top_df = stress_df.head(top_n)

    st.markdown("### Top risks (ranked by weighted impact)")
    st.dataframe(
        top_df[
            [
                "Risk ID",
                "Risk",
                "Driver",
                "Direction",
                "Stress %",
                "Base Value",
                "Stressed Value",
                "Gap Delta (£m)",
            ]
        ].style.format(
            {
                "Base Value": "{:.2f}",
                "Stressed Value": "{:.2f}",
                "Gap Delta (£m)": "{:.2f}",
            }
        ),
        use_container_width=True,
    )

    composite_params = base_params.copy()
    for _, row in top_df.iterrows():
        composite_params[row["Driver Param"]] = row["Stressed Value"]

    composite_proj = calc.project_mtfs(**composite_params)
    composite_kpis = calc.calculate_kpis(composite_proj, base_budget_year1)
    composite_gap = composite_kpis["total_4_year_gap"]
    final_reserves = composite_proj.iloc[-1]["Closing_Reserves"]

    st.markdown("### Composite stress scenario")
    st.write(
        f"Applies the top {top_n} stress tests together. "
        f"Cumulative gap: **£{composite_gap:.1f}m**. "
        f"Final reserves: **£{final_reserves:.1f}m**."
    )

    col_apply_single, col_apply_comp = st.columns(2)

    with col_apply_single:
        selected_risk = st.selectbox("Apply single stress", options=stress_df["Risk"].tolist(), disabled=read_only)
        selected_row = stress_df[stress_df["Risk"] == selected_risk].iloc[0]
        if st.button("Apply selected stress to assumptions", disabled=read_only):
            key = selected_row["Driver Param"]
            old = st.session_state.get(key)
            st.session_state[key] = float(selected_row["Stressed Value"])
            audit = get_audit_log()
            audit.log_entry(
                action="risk_stress_apply",
                user="system",
                key=key,
                old_value=old,
                new_value=st.session_state[key],
                notes=f"Applied risk stress: {selected_row['Risk ID']}",
            )
            st.success(f"Applied stress to {selected_row['Driver']}")

    with col_apply_comp:
        if st.button("Apply composite stress to assumptions", disabled=read_only):
            audit = get_audit_log()
            for _, row in top_df.iterrows():
                key = row["Driver Param"]
                old = st.session_state.get(key)
                st.session_state[key] = float(row["Stressed Value"])
                audit.log_entry(
                    action="risk_stress_apply",
                    user="system",
                    key=key,
                    old_value=old,
                    new_value=st.session_state[key],
                    notes=f"Applied composite stress: {row['Risk ID']}",
                )
            st.success("Composite stress applied to assumptions.")

    csv = stress_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download stress plan (CSV)",
        data=csv,
        file_name="risk_stress_plan.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.markdown("## Contingency Planning Guidance")

    contingency_df = build_contingency_plan(top_df)

    for _, row in contingency_df.iterrows():
        st.markdown(f"**{row['Risk']}** ({row['Driver']}) — {row['Recommended Action']}")

    st.markdown("---")
    st.markdown("### Notes")
    st.markdown(
        "- Stress levels can be overridden to match local risk appetite or audit requirements.\n"
        "- Apply single or composite stresses to push changes back into the model sidebar.\n"
        "- Update the risk register as corporate risks change or new drivers emerge."
    )


if show_mockup:
    render_mockup()
else:
    render_live()
