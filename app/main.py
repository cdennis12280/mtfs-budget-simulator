"""
MTFS Budget Gap Simulator - Web Application
Interactive financial planning tool for Section 151 / Corporate Leadership Teams
Built with Streamlit + Pandas + Plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from pathlib import Path
import sys

# Add modules to path
modules_path = Path(__file__).parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from calculations import MTFSCalculator
from scenarios import Scenarios
from rag_rating import RAGRating
from report import generate_pdf_report
from commercial import CommercialProject
from help import get_help, HELP_TEXT
from onboarding import show_first_visit_banner, show_key_terms, show_calculation_flow
from sensitivity import SensitivityAnalysis
from audit_log import get_audit_log
from reserves_policy import ReservesPolicy, ReservesPolicyChecker
from risk_advisor import load_risk_register, build_stress_table
from snapshots import add_snapshot, load_snapshots
from ui import apply_theme, page_header, app_link
from billing import plan_label
from auth import require_auth, require_roles, auth_sidebar


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="MTFS Budget Gap Simulator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply UI theme from settings
apply_theme()

if not require_auth():
    st.stop()
auth_sidebar()
read_only = st.session_state.get("auth_role") == "Read-only"
if read_only:
    st.info("Read-only mode: inputs and save actions are disabled.")
with st.sidebar:
    st.markdown("---")
    st.markdown("### Session Status")
    st.caption(f"Role: {st.session_state.get('auth_role', 'Unknown')}")
    st.caption(f"Plan: {plan_label()}")
    st.caption(
        "Persistence: Enabled"
        if os.getenv("PERSISTENCE_ENABLED", "false").lower() == "true"
        else "Persistence: Session-only"
    )
    if st.button("Reset demo tenant", disabled=not st.session_state.get("demo_mode", False)):
        st.session_state.pop("forecast_snapshots", None)
        st.session_state.pop("audit_log_entries", None)
        st.session_state.pop("saved_scenarios", None)
        if os.getenv("PERSISTENCE_ENABLED", "false").lower() == "true":
            try:
                from storage import save_json
                save_json("snapshots.json", [])
                save_json("audit_log.json", [])
            except Exception:
                pass
        st.success("Demo tenant reset.")

# Remove Streamlit branding overlays and tighten default layout/padding for S151 presentation
st.markdown("""
<style>
    /* Hide Streamlit header, main menu (hamburger) and footer */
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}

    /* Reduce default padding for denser layout */
    .block-container {padding-top: 0.5rem; padding-left: 0.75rem; padding-right: 0.75rem;}
    .stSidebar {padding-top: 0.5rem;}

    /* Topbar */
    .topbar {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 12px 18px;
        box-shadow: var(--shadow);
    }
    .topbar-inner {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap: 16px;
        flex-wrap: wrap;
    }
    .brand-mark {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: color-mix(in srgb, var(--accent) 18%, white);
        border: 1px solid color-mix(in srgb, var(--accent) 35%, transparent);
        display:flex;
        align-items:center;
        justify-content:center;
        font-weight:700;
        color: var(--accent);
        font-size: 13px;
        letter-spacing: 0.06em;
    }
    .brand-title { font-weight: 700; font-size: 18px; }
    .brand-subtitle { font-size: 12px; color: var(--muted); }
    .topbar-nav { display:flex; align-items:center; gap: 8px; flex-wrap: wrap; }
    .nav-link {
        color: var(--accent);
        border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        background: color-mix(in srgb, var(--accent) 10%, white);
    }
    .nav-link:hover { text-decoration: none; filter: brightness(0.98); }
    .role-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        background: color-mix(in srgb, var(--accent) 12%, white);
        border: 1px solid color-mix(in srgb, var(--accent) 35%, transparent);
        color: var(--accent);
    }
    .demo-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        background: rgba(217, 119, 6, 0.12);
        border: 1px solid rgba(217, 119, 6, 0.35);
        color: #b45309;
    }

    .s151-strip {
        margin-top: 14px;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 10px 14px;
        box-shadow: var(--shadow-soft);
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
    }
    .s151-item {
        background: var(--panel-alt);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 8px 10px;
    }
    .s151-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        margin-bottom: 4px;
    }
    .s151-value {
        font-weight: 700;
        font-size: 18px;
    }
    .rag-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(0,0,0,0.06);
        color: white;
    }

    @media (max-width: 900px) {
        .topbar-nav { gap: 6px; }
        .nav-link { padding: 4px 8px; font-size: 11px; }
        .brand-title { font-size: 16px; }
        .brand-mark { width: 32px; height: 32px; font-size: 11px; }
        .s151-strip { grid-template-columns: 1fr; }
    }

    @media (max-width: 640px) {
        .brand-subtitle { display: none; }
    }
</style>
""", unsafe_allow_html=True)

# Custom non-collapsible header (professional site banner)
council_name = st.session_state.get("council_name", "").strip()
header_title = council_name if council_name else "MTFS Budget Gap Simulator"
role_badge = "<span class='role-badge'>Read-Only</span>" if read_only else ""
demo_badge = "<span class='demo-badge'>Demo Mode</span>" if st.session_state.get("demo_mode", False) else ""
st.markdown("""
<div class='topbar'>
    <div class='topbar-inner'>
        <div style='display:flex; align-items:center; gap:12px;'>
            <div class='brand-mark'>MTFS</div>
            <div>
                <div class='brand-title'>{header_title} {role_badge} {demo_badge}</div>
                <div class='brand-subtitle'>Decision-support for Section 151 Officers — v1.0</div>
            </div>
        </div>
        <div class='topbar-nav'>
            <a class='nav-link' href='{dashboard_link}'>Dashboard</a>
            <a class='nav-link' href='{wizard_link}'>Wizard</a>
            <a class='nav-link' href='{inputs_link}'>Inputs</a>
            <a class='nav-link' href='{commercial_link}'>Commercial</a>
            <a class='nav-link' href='{compare_link}'>Compare</a>
            <a class='nav-link' href='{sensitivity_link}'>Sensitivity</a>
            <a class='nav-link' href='{risk_link}'>Risk Advisor</a>
            <a class='nav-link' href='{reports_link}'>Reports</a>
            <a class='nav-link' href='{audit_link}'>Audit</a>
            <a class='nav-link' href='{snapshots_link}'>Snapshots</a>
            <a class='nav-link' href='{settings_link}'>Settings</a>
            <a class='nav-link' href='{user_guide_link}'>User Guide</a>
            <a class='nav-link' href='/'>New Clean Session</a>
        </div>
    </div>
</div>
""".format(
    header_title=header_title,
    role_badge=role_badge,
    demo_badge=demo_badge,
    dashboard_link=app_link("/"),
    wizard_link=app_link("/wizard"),
    inputs_link=app_link("/inputs"),
    commercial_link=app_link("/commercial"),
    compare_link=app_link("/scenarios-compare"),
    sensitivity_link=app_link("/sensitivity-analysis"),
    risk_link=app_link("/risk_advisor"),
    reports_link=app_link("/reports"),
    audit_link=app_link("/audit"),
    snapshots_link=app_link("/snapshots"),
    settings_link=app_link("/settings"),
    user_guide_link=app_link("/user_guide"),
), unsafe_allow_html=True)


# ============================================================================
# LOAD DATA
# ============================================================================

def load_base_data():
    if 'base_data' in st.session_state:
        return st.session_state['base_data'].copy()
    demo_mode = st.session_state.get("demo_mode", False)
    filename = 'demo_financials.csv' if demo_mode else 'base_financials.csv'
    data_path = Path(__file__).parent.parent / 'data' / filename
    return pd.read_csv(data_path)


base_data = load_base_data()
base_budget_year1 = base_data[base_data['Year'] == 'Year_1']['Net_Revenue_Budget'].values[0]

# Initialize audit log
audit = get_audit_log()
# Log app startup/session
if 'session_id' not in st.session_state:
    audit.log_entry(action='session_start', user='system', notes='New session started')
    st.session_state['session_id'] = pd.Timestamp.now().isoformat()

# Show first-visit banner if settings allow
if st.session_state.get('show_onboarding', True):
    show_first_visit_banner()


# ============================================================================
# SIDEBAR: USER INPUT CONTROLS
# ============================================================================

st.sidebar.title("📋 MTFS Assumptions")

with st.sidebar:
    st.markdown("### Funding Assumptions")
    
    council_tax_increase = st.slider(
        "Council Tax Increase (%)",
        min_value=-2.0,
        max_value=5.0,
        value=2.0,
        step=0.5,
        help=get_help('council_tax_increase'),
        disabled=read_only
    )
    
    business_rates_growth = st.slider(
        "Business Rates Growth (%)",
        min_value=-5.0,
        max_value=3.0,
        value=-1.0,
        step=0.5,
        help=get_help('business_rates_growth'),
        disabled=read_only
    )
    
    grant_change = st.slider(
        "Government Grant Change (%)",
        min_value=-10.0,
        max_value=2.0,
        value=-2.0,
        step=0.5,
        help=get_help('grant_change'),
        disabled=read_only
    )
    
    fees_charges_growth = st.slider(
        "Fees & Charges Growth (%)",
        min_value=0.0,
        max_value=6.0,
        value=3.0,
        step=0.5,
        help=get_help('fees_charges_growth'),
        disabled=read_only
    )
    
    st.markdown("### Expenditure Assumptions")
    
    pay_award = st.slider(
        "Pay Award (%)",
        min_value=1.0,
        max_value=8.0,
        value=3.5,
        step=0.5,
        help=get_help('pay_award'),
        disabled=read_only
    )
    
    general_inflation = st.slider(
        "General Inflation (%)",
        min_value=0.5,
        max_value=6.0,
        value=2.0,
        step=0.5,
        help=get_help('general_inflation'),
        disabled=read_only
    )
    
    asc_demand_growth = st.slider(
        "Adult Social Care Demand Growth (%)",
        min_value=-1.0,
        max_value=10.0,
        value=4.0,
        step=0.5,
        help=get_help('asc_demand_growth'),
        disabled=read_only
    )
    
    csc_demand_growth = st.slider(
        "Children's Social Care Demand Growth (%)",
        min_value=-1.0,
        max_value=8.0,
        value=3.0,
        step=0.5,
        help=get_help('csc_demand_growth'),
        disabled=read_only
    )
    
    st.markdown("### Policy Decisions")
    
    savings_target = st.slider(
        "Annual Savings Target (% of budget)",
        min_value=0.0,
        max_value=5.0,
        value=2.0,
        step=0.25,
        help=get_help('savings_target'),
        disabled=read_only
    )
    
    use_of_reserves = st.slider(
        "Use of Reserves (%)",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=10.0,
        help=get_help('use_of_reserves'),
        disabled=read_only
    )
    
    protect_social_care = st.checkbox(
        "🛡️ Protect Social Care Services",
        value=False,
        help=get_help('protect_social_care'),
        disabled=read_only
    )
    
    st.markdown("---")
    
    # Scenario buttons
    st.markdown("### Quick Scenarios")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("📊 Base Case", use_container_width=True, disabled=read_only):
        scenario = Scenarios.get_base_case()
        st.session_state.update({k: v for k, v in scenario.items()})
        st.rerun()
    
    if col2.button("📈 Optimistic", use_container_width=True, disabled=read_only):
        scenario = Scenarios.get_optimistic_case()
        st.session_state.update({k: v for k, v in scenario.items()})
        st.rerun()
    
    if col3.button("📉 Pessimistic", use_container_width=True, disabled=read_only):
        scenario = Scenarios.get_pessimistic_case()
        st.session_state.update({k: v for k, v in scenario.items()})
        st.rerun()

    st.markdown("---")
    st.markdown("### Savings Register")
    savings_register_file = st.file_uploader(
        "Upload Savings Register CSV (optional)",
        type=['csv'],
        disabled=read_only
    )
    if savings_register_file is not None:
        try:
            savings_df = pd.read_csv(savings_register_file)
            st.session_state['savings_register_total'] = savings_df['Amount'].sum()
            st.write(f"Loaded savings register — total: £{st.session_state['savings_register_total']:.2f}m")
        except Exception:
            st.warning("Could not read savings register CSV — expected column 'Amount'")


# ============================================================================
# MAIN CONTENT: RUN CALCULATIONS
# ============================================================================

calculator = MTFSCalculator(base_data)

projection_df = calculator.project_mtfs(
    council_tax_increase_pct=council_tax_increase,
    business_rates_growth_pct=business_rates_growth,
    grant_change_pct=grant_change,
    fees_charges_growth_pct=fees_charges_growth,
    pay_award_pct=pay_award,
    general_inflation_pct=general_inflation,
    asc_demand_growth_pct=asc_demand_growth,
    csc_demand_growth_pct=csc_demand_growth,
    annual_savings_target_pct=savings_target,
    use_of_reserves_pct=use_of_reserves,
    protect_social_care=protect_social_care,
)

# === Phase 2 Feature: Savings Strategy Builder ===
st.sidebar.markdown("---")
st.sidebar.markdown("### Savings Strategy Builder")
s_transformation = st.sidebar.slider(
    "Transformation (% of savings)",
    0.0,
    100.0,
    50.0,
    5.0,
    help=get_help('savings_transformation'),
    disabled=read_only
)
s_income = st.sidebar.slider(
    "Income Generation (% of savings)",
    0.0,
    100.0,
    30.0,
    5.0,
    help=get_help('savings_income'),
    disabled=read_only
)
s_demand = st.sidebar.slider(
    "Demand Management (% of savings)",
    0.0,
    100.0,
    20.0,
    5.0,
    help=get_help('savings_demand'),
    disabled=read_only
)
# normalize if sum != 100
s_total = s_transformation + s_income + s_demand
if s_total == 0:
    s_total = 1.0
s_transformation_pct = s_transformation / s_total
s_income_pct = s_income / s_total
s_demand_pct = s_demand / s_total

# apply savings register if uploaded
savings_register_total = st.session_state.get('savings_register_total', 0.0)

# Apply strategy by adjusting funding/expenditure/demand across projection
proj = projection_df.copy()
proj['Adjusted_Total_Funding'] = proj['Total_Funding']
proj['Adjusted_Projected_Expenditure'] = proj['Projected_Expenditure']

for i, row in proj.iterrows():
    total_sav = row['Annual_Savings'] + (savings_register_total / len(proj) if savings_register_total else 0.0)
    inc = total_sav * s_income_pct
    trans = total_sav * s_transformation_pct
    dem = total_sav * s_demand_pct
    proj.at[i, 'Adjusted_Total_Funding'] = row['Total_Funding'] + inc
    proj.at[i, 'Adjusted_Projected_Expenditure'] = row['Projected_Expenditure'] - trans - dem

# recompute gaps after savings strategy
proj['Annual_Budget_Gap_Strategy'] = proj['Adjusted_Projected_Expenditure'] - proj['Adjusted_Total_Funding']
proj['Cumulative_Gap_Strategy'] = proj['Annual_Budget_Gap_Strategy'].cumsum()
opening_reserves = proj.iloc[0]['Opening_Reserves']
proj['Closing_Reserves_Strategy'] = opening_reserves - proj['Annual_Budget_Gap_Strategy'].cumsum()

# === Council Tax Sensitivity Tool ===
st.sidebar.markdown("---")
st.sidebar.markdown("### Council Tax Sensitivity")
num_households = st.sidebar.number_input(
    "Number of households (for per-household impact)",
    min_value=1,
    value=100000,
    help=get_help('council_tax_per_household'),
    disabled=read_only
)
one_pct_impact = base_budget_year1 * 0.01
per_household = one_pct_impact * 1e6 / num_households if base_budget_year1 > 0 else 0.0
st.sidebar.write(f"1% council tax ≈ £{one_pct_impact:.2f}m total — £{per_household:.2f} per household")

# === Departmental Drill-Down ===
st.sidebar.markdown("---")
st.sidebar.markdown("### Departmental Drill-Down")
dept_file = st.sidebar.file_uploader(
    "Upload departmental budget CSV (optional)",
    type=['csv'],
    disabled=read_only
)
if dept_file is not None:
    try:
        dept_df = pd.read_csv(dept_file)
        st.session_state['dept_df'] = dept_df
    except Exception:
        st.warning("Could not read departmental CSV — expected columns 'Department' and 'Base_Expenditure'")
if 'dept_df' not in st.session_state:
    # default department split
    dept_df = pd.DataFrame({
        'Department': ['Adult Social Care', 'Children Social Care', 'Education', 'Housing', 'Other'],
        'Base_Expenditure': [60.0, 40.0, 30.0, 20.0, 48.0]
    })
else:
    dept_df = st.session_state['dept_df']

# Cascade inflation/pay to departments proportionally
dept_df['Projected_Expenditure'] = dept_df['Base_Expenditure'] * (1 + general_inflation / 100 + pay_award / 100)

# === Stochastic modelling ===
st.sidebar.markdown("---")
st.sidebar.markdown("### Stochastic (Monte Carlo)")
enable_stochastic = st.sidebar.checkbox(
    "Enable stochastic modelling",
    value=False,
    help=get_help('monte_carlo'),
    disabled=read_only
)
stochastic_runs = st.sidebar.number_input(
    "Monte Carlo runs",
    min_value=100,
    max_value=5000,
    value=500,
    step=100,
    disabled=read_only
)
stochastic_std_pct = st.sidebar.slider(
    "Std dev for assumptions (% of value)",
    0.1,
    10.0,
    2.0,
    help=get_help('stochastic_std'),
    disabled=read_only
)

stochastic_results = None
if enable_stochastic:
    samples = []
    for _ in range(int(stochastic_runs)):
        sample = calculator.project_mtfs(
            council_tax_increase_pct=max(0.0, np.random.normal(council_tax_increase, council_tax_increase * stochastic_std_pct / 100)),
            business_rates_growth_pct=np.random.normal(business_rates_growth, abs(business_rates_growth) * stochastic_std_pct / 100),
            grant_change_pct=np.random.normal(grant_change, abs(grant_change) * stochastic_std_pct / 100),
            fees_charges_growth_pct=np.random.normal(fees_charges_growth, fees_charges_growth * stochastic_std_pct / 100),
            pay_award_pct=np.random.normal(pay_award, pay_award * stochastic_std_pct / 100),
            general_inflation_pct=np.random.normal(general_inflation, general_inflation * stochastic_std_pct / 100),
            asc_demand_growth_pct=np.random.normal(asc_demand_growth, asc_demand_growth * stochastic_std_pct / 100),
            csc_demand_growth_pct=np.random.normal(csc_demand_growth, csc_demand_growth * stochastic_std_pct / 100),
            annual_savings_target_pct=max(0.0, np.random.normal(savings_target, savings_target * stochastic_std_pct / 100)),
            use_of_reserves_pct=use_of_reserves,
            protect_social_care=protect_social_care,
        )
        samples.append(sample['Annual_Budget_Gap'].sum())
    stochastic_results = np.array(samples)

# === Stress Test Presets ===
st.sidebar.markdown("---")
st.sidebar.markdown("### Stress Test Presets")

severity = st.sidebar.selectbox(
    "Preset severity",
    options=["Mild", "Moderate", "Severe"],
    index=1,
    disabled=read_only
)

severity_scale = {
    "Mild": 0.5,
    "Moderate": 1.0,
    "Severe": 1.5
}[severity]

stress_presets = {
    "Funding Shock": {
        'grant_change_pct': -3.0,
        'business_rates_growth_pct': -2.0,
        'fees_charges_growth_pct': -2.0,
        'council_tax_increase_pct': -0.5,
    },
    "Demand Surge": {
        'asc_demand_growth_pct': 2.0,
        'csc_demand_growth_pct': 2.0,
        'general_inflation_pct': 0.5,
    },
    "Pay Settlement": {
        'pay_award_pct': 2.0,
    },
}

for preset_name, deltas in stress_presets.items():
    if st.sidebar.button(f"Apply {preset_name}", disabled=read_only):
        for key, delta in deltas.items():
            old_val = st.session_state.get(key)
            if old_val is None:
                old_val = 0.0
            st.session_state[key] = float(old_val) + float(delta) * severity_scale
            audit.log_entry(
                action='stress_preset_apply',
                user='system',
                key=key,
                old_value=old_val,
                new_value=st.session_state[key],
                notes=f"Preset: {preset_name} ({severity})"
            )
        st.sidebar.success(f"{preset_name} applied.")

# === Scenario Bookmarking (Session Only) ===
if st.sidebar.button('Save Current Scenario', disabled=read_only):
    scenario_name = f"Custom {pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
    scenario_data = {
        'name': scenario_name,
        'params': {
            'council_tax_increase_pct': council_tax_increase,
            'business_rates_growth_pct': business_rates_growth,
            'grant_change_pct': grant_change,
            'fees_charges_growth_pct': fees_charges_growth,
            'pay_award_pct': pay_award,
            'general_inflation_pct': general_inflation,
            'asc_demand_growth_pct': asc_demand_growth,
            'csc_demand_growth_pct': csc_demand_growth,
            'annual_savings_target_pct': savings_target,
            'use_of_reserves_pct': use_of_reserves,
            'protect_social_care': protect_social_care,
        }
    }
    saved = st.session_state.get('saved_scenarios', [])
    saved.append(scenario_data)
    st.session_state['saved_scenarios'] = saved
    # Log scenario save to audit
    audit.log_entry(
        action='scenario_save',
        user='system',
        key=scenario_name,
        notes=f'Scenario saved with assumptions: tax={council_tax_increase}%, grant={grant_change}%, pay={pay_award}%'
    )
    st.sidebar.success('Scenario saved')

saved = st.session_state.get('saved_scenarios', [])

if saved:
    chosen = st.sidebar.selectbox(
        'Load saved scenario',
        ['-- none --'] + [s['name'] for s in saved],
        disabled=read_only
    )
    if chosen and chosen != '-- none --':
        sel = next(s for s in saved if s['name'] == chosen)
        params = sel['params']
        # update UI variables in session (non-invasive)
        for k, v in params.items():
            st.session_state[k] = v
        st.sidebar.success(f"Loaded {chosen} — adjust sliders if needed")

    # Optional export of saved scenarios (session only)
    saved_json = json.dumps(saved, indent=2).encode('utf-8')
    st.sidebar.download_button(
        "Download saved scenarios (JSON)",
        data=saved_json,
        file_name="saved_scenarios.json",
        mime="application/json"
    )

kpis = calculator.calculate_kpis(projection_df, base_budget_year1)
sustainability = RAGRating.calculate_sustainability_metrics(
    projection_df, 
    base_budget_year1
)

final_reserves_pct = (projection_df.iloc[-1]['Closing_Reserves'] / base_budget_year1) * 100
rag_rating, rag_reasoning = RAGRating.get_rating(
    projection_df,
    base_budget_year1,
    final_reserves_pct
)

# === Forecast Snapshots (Rolling) ===
snapshot_file = Path(__file__).parent.parent / '.forecast_snapshots.json'
st.sidebar.markdown("---")
st.sidebar.markdown("### Forecast Snapshots")
snapshot_name = st.sidebar.text_input("Snapshot name", value="Rolling Forecast", disabled=read_only)
snapshot_notes = st.sidebar.text_area("Notes", value="", height=80, disabled=read_only)

assumptions_payload = {
    'council_tax_increase_pct': council_tax_increase,
    'business_rates_growth_pct': business_rates_growth,
    'grant_change_pct': grant_change,
    'fees_charges_growth_pct': fees_charges_growth,
    'pay_award_pct': pay_award,
    'general_inflation_pct': general_inflation,
    'asc_demand_growth_pct': asc_demand_growth,
    'csc_demand_growth_pct': csc_demand_growth,
    'annual_savings_target_pct': savings_target,
    'use_of_reserves_pct': use_of_reserves,
    'protect_social_care': protect_social_care,
}

if st.sidebar.button("Save Snapshot", disabled=read_only):
    entry = add_snapshot(
        path=None,
        name=snapshot_name,
        assumptions=assumptions_payload,
        kpis=kpis,
        rag_rating=rag_rating,
        notes=snapshot_notes
    )
    audit.log_entry(
        action='forecast_snapshot_save',
        user='system',
        key=entry.get('snapshot_id', snapshot_name),
        notes=f"Snapshot saved: {snapshot_name} v{entry.get('version', 1)}"
    )
    st.sidebar.success("Snapshot saved.")

snapshots = load_snapshots()
if snapshots:
    options = [
        f"{s.get('name', 'Snapshot')} v{s.get('version', 1)} ({s.get('timestamp', '')[:10]})"
        for s in snapshots
    ]
    selected_idx = st.sidebar.selectbox(
        "Load snapshot",
        ['-- none --'] + options,
        disabled=read_only
    )
    if selected_idx != '-- none --':
        sel = snapshots[options.index(selected_idx)]
        if st.sidebar.button("Apply snapshot assumptions", disabled=read_only):
            for key, val in sel.get('assumptions', {}).items():
                st.session_state[key] = val
            audit.log_entry(
                action='forecast_snapshot_apply',
                user='system',
                key=sel.get('snapshot_id', ''),
                notes=f"Applied snapshot {sel.get('name', '')} v{sel.get('version', 1)}"
            )
            st.sidebar.success("Snapshot applied.")

# === Reserves Policy Check ===
# Load policy from session settings (defaults to standard S151 policy)
reserves_policy = ReservesPolicy(
    min_pct=st.session_state.get('reserves_policy_min', 5.0),
    target_pct=st.session_state.get('reserves_policy_target', 10.0),
    max_pct=st.session_state.get('reserves_policy_max', 25.0),
    policy_name="Council Reserves Policy"
)
policy_checker = ReservesPolicyChecker(reserves_policy)
policy_check = policy_checker.check_forecast(projection_df, base_budget_year1)

# === S151 Persona: Global risk overrides ===
st.sidebar.markdown("---")
st.sidebar.markdown("### S151 Override (Global Risk Parameters)")
override_pwlb = st.sidebar.number_input(
    "Assume PWLB interest rate (%)",
    value=4.5,
    step=0.1,
    help=get_help('pwlb_rate'),
    disabled=read_only
)
override_reserve_floor = st.sidebar.number_input(
    "Reserve floor (£m)",
    value=10.0,
    step=1.0,
    disabled=read_only
)
override_investment_threshold = st.sidebar.slider(
    "Max capital exposure (% of budget) before RED",
    1.0,
    20.0,
    5.0,
    1.0,
    disabled=read_only
)

# Sample commercial projects
projA = CommercialProject(name='Commercial Property A', capital_cost=30.0, annual_income_target=2.0, life_years=40, operating_costs=0.2, capital_receipt=0.0)
projB = CommercialProject(name='District Energy Scheme', capital_cost=20.0, annual_income_target=1.6, life_years=30, operating_costs=0.1, capital_receipt=0.0)
projC = CommercialProject(name='Service Transformation (capital led)', capital_cost=10.0, annual_income_target=0.5, life_years=10, operating_costs=0.05, capital_receipt=2.0)

commercial_projects = [projA, projB, projC]

# Commercial tools moved to a dedicated page for cleaner dashboard
st.markdown("---")

# Opportunity cost simulator
st.markdown("---")
st.markdown("## Opportunity Cost Simulator")
choices = {p.name: p for p in commercial_projects}
choice = st.selectbox('Choose project to compare vs transformation vs do-nothing', ['Do Nothing'] + list(choices.keys()))
if choice != 'Do Nothing':
    sel = choices[choice]
    # calculate 4-year cumulative net benefit
    years = 4
    # assume incomes start Year1 and persist
    benefit = 0.0
    for y in range(years):
        # assume realisation at 80% default unless adjusted above
        rkey = f"real_{commercial_projects.index(sel)}"
        real_pct = st.session_state.get(rkey, 80)
        net = sel.net_return(real_pct, override_pwlb)['net_return']
        benefit += net
    st.write(f"Estimated 4-year cumulative net benefit of {sel.name}: £{benefit:.2f}m")
    # compare to using capital receipt to fund one-off costs
    if sel.capital_receipt > 0:
        st.write(f"Capital receipt available: £{sel.capital_receipt:.2f}m — can fund one-off revenue pressures")
else:
    st.write("No commercial project selected — model uses reserves/savings only")


# ============================================================================
# SECTION 1: STRATEGIC HEADLINE KPIS
# ============================================================================

page_header(
    "MTFS Budget Gap Simulator",
    "Interactive financial planning tool for Section 151 and Corporate Leadership Teams"
)

gap_amount = kpis['total_4_year_gap']
gap_pct = (gap_amount / base_budget_year1 * 100) if base_budget_year1 else 0.0
final_reserves = projection_df.iloc[-1]['Closing_Reserves']
policy_target = st.session_state.get('reserves_policy_target', 10.0)
rag_color_map = {"RED": "#d62728", "AMBER": "#ff7f0e", "GREEN": "#2ca02c"}
rag_color = rag_color_map.get(rag_rating, "#6b7280")

st.markdown(f"""
<div class="s151-strip">
    <div class="s151-item">
        <div class="s151-label">Sustainability RAG</div>
        <div class="s151-value">
            <span class="rag-pill" style="background:{rag_color};">{rag_rating}</span>
        </div>
        <div style="font-size:12px; color:var(--muted); margin-top:4px;">{rag_reasoning}</div>
    </div>
    <div class="s151-item">
        <div class="s151-label">4-Year Funding Gap</div>
        <div class="s151-value">£{gap_amount:.1f}m</div>
        <div style="font-size:12px; color:var(--muted); margin-top:4px;">{gap_pct:.1f}% of Year 1 budget</div>
    </div>
    <div class="s151-item">
        <div class="s151-label">Final Reserves</div>
        <div class="s151-value">£{final_reserves:.1f}m</div>
        <div style="font-size:12px; color:var(--muted); margin-top:4px;">Policy target {policy_target:.1f}%</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-callout">
  <b>Quick Start</b><br/>
  1. Set baseline data in Inputs<br/>
  2. Adjust assumptions on this dashboard<br/>
  3. Save a snapshot and export reports for governance
</div>
""", unsafe_allow_html=True)

# Help & Key Terms
col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
with col_h1:
    if st.button("📖 What is the MTFS?"):
        show_key_terms()
with col_h2:
    if st.button("🔄 How it works"):
        with st.expander("Calculation Flow", expanded=True):
            show_calculation_flow()
with col_h3:
    if st.button("❓ Glossary"):
        show_key_terms()

st.markdown("## Strategic Headlines (4-Year MTFS)")
st.markdown("*Hover over cards for explanations*")
plotly_template = st.session_state.get('plotly_template', 'plotly_white')

# Risk advisor KPI prep
risk_top = None
try:
    risk_path = Path(__file__).parent.parent / 'data' / 'risk_register.csv'
    risk_df = load_risk_register(risk_path)
    base_params = {
        'council_tax_increase_pct': council_tax_increase,
        'business_rates_growth_pct': business_rates_growth,
        'grant_change_pct': grant_change,
        'fees_charges_growth_pct': fees_charges_growth,
        'pay_award_pct': pay_award,
        'general_inflation_pct': general_inflation,
        'asc_demand_growth_pct': asc_demand_growth,
        'csc_demand_growth_pct': csc_demand_growth,
        'annual_savings_target_pct': savings_target,
        'use_of_reserves_pct': use_of_reserves,
        'protect_social_care': protect_social_care,
    }
    stress_df = build_stress_table(calculator, base_params, risk_df)
    if not stress_df.empty:
        risk_top = stress_df.iloc[0]
except Exception:
    risk_top = None

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    gap_amount = kpis['total_4_year_gap']
    gap_color = "red" if gap_amount > 20 else "orange" if gap_amount > 10 else "green"
    st.metric(
        "💰 Cumulative Gap",
        f"£{gap_amount:.1f}m",
        delta=f"{(gap_amount / base_budget_year1 * 100):.1f}% of budget",
        delta_color="inverse",
        help=get_help('cumulative_gap')
    )

with col2:
    if kpis['year_reserves_exhausted']:
        reserves_text = f"Year {kpis['year_reserves_exhausted']}"
        reserves_color = "orange"
    else:
        reserves_text = "✓ Sustainable"
        reserves_color = "green"
    st.metric(
        "📉 Reserves Status",
        reserves_text,
        delta=f"Final: £{projection_df.iloc[-1]['Closing_Reserves']:.1f}m",
        help=get_help('reserves_status')
    )

with col3:
    savings_req = kpis['savings_required_pct']
    st.metric(
        "🎯 Additional Savings Needed",
        f"{savings_req:.1f}%",
        delta="of annual budget",
        delta_color="inverse",
        help=get_help('savings_needed')
    )

with col4:
    rag_color_map = {"RED": "#d62728", "AMBER": "#ff7f0e", "GREEN": "#2ca02c"}
    st.markdown(f"""
    <div style="background-color: {rag_color_map[rag_rating]}; color: white; padding: 15px; border-radius: 5px; text-align: center;">
        <p style="font-size: 14px; margin: 0;">Financial Sustainability</p>
        <p style="font-size: 24px; font-weight: bold; margin: 5px 0;">{rag_rating}</p>
        <p style="font-size: 11px; margin: 0; line-height: 1.3;">{rag_reasoning}</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    # Reserves Policy Compliance
    policy_status = policy_check['by_year'][-1]['status'] if policy_check['by_year'] else 'UNKNOWN'
    policy_color_map = {"RED": "#d62728", "AMBER": "#ff7f0e", "GREEN": "#2ca02c"}
    policy_label = (
        "🔴 Non-Compliant" if policy_status == "RED"
        else "🟡 Below Target" if policy_status == "AMBER"
        else "🟢 Policy Met"
    )
    st.markdown(f"""
    <div style="background-color: {policy_color_map[policy_status]}; color: white; padding: 15px; border-radius: 5px; text-align: center;">
        <p style="font-size: 14px; margin: 0;">Reserves Policy</p>
        <p style="font-size: 18px; font-weight: bold; margin: 5px 0;">{policy_label}</p>
        <p style="font-size: 11px; margin: 0; line-height: 1.3;">Min: {reserves_policy.min_pct}%  |  Target: {reserves_policy.target_pct}%</p>
    </div>
    """, unsafe_allow_html=True)

if risk_top is not None:
    st.markdown("### Risk-Adjusted Highlights")
    rcol1, rcol2 = st.columns(2)
    with rcol1:
        st.metric(
            "⚠️ Top Risk Stress Impact",
            f"£{risk_top['Gap Delta (£m)']:.1f}m",
            delta=f"Stress {risk_top['Stress %']:.0f}%",
            delta_color="inverse",
            help="Largest risk-weighted stress impact on the cumulative gap."
        )
    with rcol2:
        st.metric(
            "🧭 Top Risk Driver",
            f"{risk_top['Risk']}",
            delta=f"{risk_top['Driver']}",
            help="Highest weighted impact (risk score × gap impact)."
        )
    st.markdown(f"[Open Risk Advisor]({app_link('/risk_advisor')})")

st.markdown("---")

# ============================================================================
# SECTION 2: BUDGET GAP TRAJECTORY
# ============================================================================

st.markdown("## Scenario Story: Base vs Pessimistic")
base_proj = projection_df
base_gap = base_proj['Annual_Budget_Gap'].sum()
base_reserves = base_proj.iloc[-1]['Closing_Reserves']

pess = Scenarios.get_pessimistic_case()
pess_proj = calculator.project_mtfs(
    council_tax_increase_pct=pess['council_tax_increase_pct'],
    business_rates_growth_pct=pess['business_rates_growth_pct'],
    grant_change_pct=pess['grant_change_pct'],
    fees_charges_growth_pct=pess['fees_charges_growth_pct'],
    pay_award_pct=pess['pay_award_pct'],
    general_inflation_pct=pess['general_inflation_pct'],
    asc_demand_growth_pct=pess['asc_demand_growth_pct'],
    csc_demand_growth_pct=pess['csc_demand_growth_pct'],
    annual_savings_target_pct=pess['annual_savings_target_pct'],
    use_of_reserves_pct=pess['use_of_reserves_pct'],
    protect_social_care=pess['protect_social_care'],
)
pess_gap = pess_proj['Annual_Budget_Gap'].sum()
pess_reserves = pess_proj.iloc[-1]['Closing_Reserves']
pess_final_reserves_pct = (pess_reserves / base_budget_year1) * 100 if base_budget_year1 else 0
pess_rag, _ = RAGRating.get_rating(pess_proj, base_budget_year1, pess_final_reserves_pct)

story_col1, story_col2, story_col3 = st.columns(3)
with story_col1:
    st.metric("Base gap (£m)", f"{base_gap:.1f}", delta="Current assumptions")
with story_col2:
    st.metric("Pessimistic gap (£m)", f"{pess_gap:.1f}", delta=f"+£{(pess_gap - base_gap):.1f}m vs base")
with story_col3:
    st.metric("Pessimistic RAG", pess_rag, delta=f"Final reserves £{pess_reserves:.1f}m")

st.caption("Use this story to explain downside exposure during leadership briefings.")

st.markdown("## Budget Gap by Year")

# Show baseline and strategy-adjusted gaps
fig_gap = go.Figure()
fig_gap.add_trace(go.Scatter(
    x=projection_df['Year_Number'],
    y=projection_df['Annual_Budget_Gap'],
    mode='lines+markers',
    name='Annual Gap (Base)',
    line=dict(color='#d62728', width=2),
))
fig_gap.add_trace(go.Scatter(
    x=proj['Year_Number'],
    y=proj['Annual_Budget_Gap_Strategy'],
    mode='lines+markers',
    name='Annual Gap (With Savings Strategy)',
    line=dict(color='#2ca02c', width=2),
))
fig_gap.add_trace(go.Scatter(
    x=proj['Year_Number'],
    y=proj['Cumulative_Gap_Strategy'],
    mode='lines',
    name='Cumulative Gap (Strategy)',
    line=dict(color='#ff7f0e', width=2, dash='dash'),
))
fig_gap.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Balanced")
fig_gap.update_layout(
    title="Annual and Cumulative Budget Gap (Base vs Strategy)",
    xaxis_title="Year",
    yaxis_title="Gap (£m)",
    hovermode='x unified',
    height=420,
    template=plotly_template,
)
st.plotly_chart(fig_gap, use_container_width=True)

# ============================================================================
# SECTION 3: RESERVES DEPLETION
# ============================================================================

st.markdown("## Reserves Depletion Profile")

fig_reserves = go.Figure()
fig_reserves.add_trace(go.Bar(
    x=projection_df['Year_Number'],
    y=projection_df['Closing_Reserves'],
    name='Closing Reserves',
    marker=dict(color=projection_df['Closing_Reserves'], colorscale='RdYlGn', 
                cmin=0, cmax=projection_df['Closing_Reserves'].max()),
))
min_threshold = base_budget_year1 * (RAGRating.MIN_RESERVES_PCT / 100)
fig_reserves.add_hline(y=min_threshold, line_dash="dash", line_color="red", 
                       annotation_text=f"Minimum Threshold (£{min_threshold:.1f}m)")
# strategy reserves
fig_reserves.add_trace(go.Scatter(
    x=proj['Year_Number'],
    y=proj['Closing_Reserves_Strategy'],
    mode='lines+markers',
    name='Closing Reserves (Strategy)',
    line=dict(color='#2ca02c', width=2, dash='dash')
))
fig_reserves.update_layout(
    title="Reserves Position (Closing Balance)",
    xaxis_title="Year",
    yaxis_title="Reserves (£m)",
    height=400,
    showlegend=False,
    template=plotly_template,
)
st.plotly_chart(fig_reserves, use_container_width=True)

# === Reserves Policy Compliance Panel ===
st.markdown("## Reserves Policy Compliance")

if policy_check['compliant']:
    st.success(f"✅ {policy_checker.summary_text(policy_check)}")
else:
    st.warning(f"⚠️ {policy_checker.summary_text(policy_check)}")

st.info(f"📋 {policy_checker.recommendation_text(policy_check, base_budget_year1)}")

# Show year-by-year compliance table
compliance_rows = []
for year_check in policy_check['by_year']:
    compliance_rows.append({
        'Year': f"Year {year_check['year']}",
        'Closing Reserves (£m)': f"{year_check['closing_reserves']:.1f}",
        'Reserves (%)': f"{year_check['reserves_pct']:.1f}%",
        'Min Threshold': f"£{year_check['min_threshold']:.1f}m ({reserves_policy.min_pct}%)",
        'Status': year_check['status'],
    })

compliance_df = pd.DataFrame(compliance_rows)
st.dataframe(compliance_df, use_container_width=True, hide_index=True)

# ============================================================================
# SECTION 4: FUNDING VS EXPENDITURE
# ============================================================================

st.markdown("## Funding vs Expenditure Stack")

fig_stack = go.Figure()
fig_stack.add_trace(go.Bar(
    x=projection_df['Year_Number'],
    y=projection_df['Total_Funding'],
    name='Total Funding',
    marker=dict(color='#2ca02c'),
))
fig_stack.add_trace(go.Bar(
    x=projection_df['Year_Number'],
    y=projection_df['Projected_Expenditure'],
    name='Projected Expenditure',
    marker=dict(color='#d62728'),
))
fig_stack.update_layout(
    title="Funding vs Expenditure Comparison",
    xaxis_title="Year",
    yaxis_title="Amount (£m)",
    barmode='group',
    height=400,
    template=plotly_template,
    hovermode='x unified',
)
st.plotly_chart(fig_stack, use_container_width=True)

# ============================================================================
# SECTION 5: SCENARIO COMPARISON
# ============================================================================

st.markdown("## Scenario Comparison")

scenarios_dict = Scenarios.get_all_scenarios()
scenario_results = {}

for scenario_name, scenario_params in scenarios_dict.items():
    scenario_proj = calculator.project_mtfs(
        council_tax_increase_pct=scenario_params['council_tax_increase_pct'],
        business_rates_growth_pct=scenario_params['business_rates_growth_pct'],
        grant_change_pct=scenario_params['grant_change_pct'],
        fees_charges_growth_pct=scenario_params['fees_charges_growth_pct'],
        pay_award_pct=scenario_params['pay_award_pct'],
        general_inflation_pct=scenario_params['general_inflation_pct'],
        asc_demand_growth_pct=scenario_params['asc_demand_growth_pct'],
        csc_demand_growth_pct=scenario_params['csc_demand_growth_pct'],
        annual_savings_target_pct=scenario_params['annual_savings_target_pct'],
        use_of_reserves_pct=scenario_params['use_of_reserves_pct'],
        protect_social_care=scenario_params['protect_social_care'],
    )
    
    scenario_kpis = calculator.calculate_kpis(scenario_proj, base_budget_year1)
    scenario_final_reserves = scenario_proj.iloc[-1]['Closing_Reserves']
    scenario_rag, _ = RAGRating.get_rating(scenario_proj, base_budget_year1,
                                          (scenario_final_reserves / base_budget_year1) * 100)
    
    scenario_results[scenario_name] = {
        'projection': scenario_proj,
        'gap': scenario_kpis['total_4_year_gap'],
        'final_reserves': scenario_final_reserves,
        'rag': scenario_rag,
    }

col1, col2, col3 = st.columns(3)

scenarios_list = list(scenario_results.keys())
colors_map = {"RED": "#d62728", "AMBER": "#ff7f0e", "GREEN": "#2ca02c"}

for idx, scenario_name in enumerate(scenarios_list):
    with [col1, col2, col3][idx]:
        result = scenario_results[scenario_name]
        rag_color = colors_map[result['rag']]
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px; border-left: 4px solid {rag_color};">
            <h4>{scenario_name}</h4>
            <p><strong>4-Year Gap:</strong> £{result['gap']:.1f}m</p>
            <p><strong>Final Reserves:</strong> £{result['final_reserves']:.1f}m</p>
            <p><strong>Rating:</strong> <span style="color: {rag_color}; font-weight: bold;">{result['rag']}</span></p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# SECTION 6: GAP DRIVERS WATERFALL
# ============================================================================

st.markdown("## Budget Gap Drivers (Year 1 Waterfall)")

drivers = calculator.calculate_drivers_waterfall(projection_df, base_budget_year1)

# Sort for waterfall (positive down, negative are pressures)
waterfall_data = {
    'Council Tax Growth': drivers['Council_Tax_Growth'],
    'Business Rates Change': drivers['Business_Rates_Change'],
    'Grant Changes': drivers['Grant_Changes'],
    'Fees Growth': drivers['Fees_Growth'],
    'Pay Pressures': drivers['Pay_Pressures'],
    'Inflation Pressures': drivers['Inflation_Pressures'],
    'Demand Pressures': drivers['Demand_Pressures'],
    'Savings Delivered': drivers['Savings_Delivered'],
}

waterfall_labels = list(waterfall_data.keys())
waterfall_values = list(waterfall_data.values())
waterfall_colors = ['green' if v > 0 else 'red' for v in waterfall_values]

fig_waterfall = go.Figure(go.Waterfall(
    x=waterfall_labels,
    y=waterfall_values,
    connector={'line': {'color': 'rgba(0, 0, 0, 0.3)'}},
    increasing={'marker': {'color': '#2ca02c'}},
    decreasing={'marker': {'color': '#d62728'}},
))

fig_waterfall.update_layout(
    title="Year 1 Budget Gap Components",
    height=400,
    template=plotly_template,
    xaxis_tickangle=-45,
)
st.plotly_chart(fig_waterfall, use_container_width=True)

# ============================================================================
# SECTION 7: DETAILED PROJECTION TABLE
# ============================================================================

st.markdown("## Detailed Year-by-Year Projection")

display_cols = [
    'Year_Number', 'Total_Funding', 'Projected_Expenditure', 
    'Annual_Budget_Gap', 'Cumulative_Gap', 'Closing_Reserves'
]

display_df = projection_df[display_cols].copy()
display_df.columns = ['Year', 'Funding (£m)', 'Expenditure (£m)', 
                      'Annual Gap (£m)', 'Cumulative Gap (£m)', 'Reserves (£m)']

st.dataframe(
    display_df.style.format({
        'Funding (£m)': '{:.1f}',
        'Expenditure (£m)': '{:.1f}',
        'Annual Gap (£m)': '{:.1f}',
        'Cumulative Gap (£m)': '{:.1f}',
        'Reserves (£m)': '{:.1f}',
    }).highlight_null(),
    use_container_width=True,
)

# ============================================================================
# SECTION 8: SUSTAINABILITY METRICS
# ============================================================================

st.markdown("## Financial Sustainability Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Reserves / Budget Ratio (Year 5)",
        f"{sustainability['reserves_to_budget_pct']:.1f}%",
        delta=f"Target: {RAGRating.MIN_RESERVES_PCT}% minimum",
        delta_color="inverse" if sustainability['reserves_to_budget_pct'] < RAGRating.MIN_RESERVES_PCT else "normal"
    )

with col2:
    st.metric(
        "Avg Annual Savings Delivery",
        f"{sustainability['savings_as_pct_budget']:.1f}%",
        delta="of operating budget",
    )

with col3:
    st.metric(
        "Funding Volatility Score",
        f"{sustainability['funding_volatility_score']:.2f}",
        delta="Lower = more stable",
    )

# ============================================================================
# SECTION X: STOCHASTIC & DEPARTMENTAL OUTPUTS + PDF EXPORT
# ============================================================================

if stochastic_results is not None:
    st.markdown("## Stochastic Monte Carlo Results")
    fig_hist = px.histogram(stochastic_results, nbins=40, title='Distribution of 4-year cumulative gap (Monte Carlo)')
    st.plotly_chart(fig_hist, use_container_width=True)
    st.write(f"Mean gap: £{stochastic_results.mean():.2f}m — 5th/50th/95th percentiles: £{np.percentile(stochastic_results,5):.2f}m / £{np.percentile(stochastic_results,50):.2f}m / £{np.percentile(stochastic_results,95):.2f}m")

st.markdown("## Departmental Drill-Down")
st.dataframe(dept_df.style.format({'Base_Expenditure': '{:.1f}', 'Projected_Expenditure': '{:.1f}'}), use_container_width=True)
fig_dept = go.Figure()
fig_dept.add_trace(go.Bar(x=dept_df['Department'], y=dept_df['Projected_Expenditure'], marker_color='#636efa'))
fig_dept.update_layout(title='Projected Expenditure by Department', xaxis_title='Department', yaxis_title='Expenditure (£m)')
st.plotly_chart(fig_dept, use_container_width=True)

# PDF report generation
st.markdown("## Export Report")
if st.button('Generate PDF Report'):
    kpis_for_report = {
        'Cumulative 4-Year Gap (£m)': f"{kpis['total_4_year_gap']:.1f}",
        'Year Reserves Exhausted': kpis['year_reserves_exhausted'] or 'N/A',
        'Savings Required (%)': f"{kpis['savings_required_pct']:.2f}",
        'Council Tax Equivalent (£)': f"{kpis['council_tax_equivalent_impact']:.2f}",
        'RAG Rating': rag_rating,
    }
    out_path = Path.cwd() / 'mtfs_report.pdf'
    try:
        pdf_path = generate_pdf_report(str(out_path), 'MTFS Budget Gap Simulator — Report', kpis_for_report, note=f"Scenario: {st.session_state.get('scenario','Custom')}")
        with open(pdf_path, 'rb') as fh:
            data = fh.read()
        # Log PDF export to audit
        audit.log_entry(
            action='export',
            user='system',
            key='mtfs_report.pdf',
            notes=f'PDF report generated - Gap: £{kpis["total_4_year_gap"]:.1f}m, RAG: {rag_rating}'
        )
        st.download_button('Download PDF', data, file_name='mtfs_report.pdf', mime='application/pdf')
    except Exception as e:
        st.error(f"Failed to generate PDF: {e}")


# ============================================================================
# SECTION 9: GOVERNANCE & AUDITABILITY
# ============================================================================

st.markdown("---")

with st.expander("🔍 Governance & Auditability Panel"):
    st.markdown("""
    ### Data Sources
    - **Base Dataset:** local authority baseline financials (simplified single-council model)
    - **Cost Bases:** Pay, inflation, and demand baselines from budget papers
    - **Assumptions:** User-adjusted via interactive sliders
    
    ### Methodology
    - **Calculation Engine:** Deterministic rule-based (not ML)
    - **Transparency:** All formulas are auditable and linear
    - **Governance:** Matches real MTFS planning processes used in UK public sector
    
    #### Key Formulas
    ```
    Projected Funding = Council Tax + Business Rates + Grants + Fees & Charges
    Projected Expenditure = Base + Pay Impact + Inflation + Demand Pressures - Savings
    Annual Gap = Projected Expenditure - Projected Funding
    Cumulative Gap = Sum of annual gaps
    Closing Reserves = Opening Reserves - Annual Gap
    ```
    
    ### Risk Assessment (RAG Rating Rules)
    - **RED:** Reserves exhausted OR gap >8% budget OR savings >5% capacity
    - **AMBER:** Reserves decline >25% OR gap 5-8% budget
    - **GREEN:** Financial position sustainable
    
    ### Limitations
    - Single-council simplified model (no external market data)
    - Deterministic projections (does not model probability ranges)
    - Assumes linear relationships (demand/cost pressures)
    - Does not include specific service transformation initiatives
    - Reserves held at aggregate level (no department-level detail)
    
    ### Version & Support
    - **Version:** 1.0 (Feb 2026)
    - **Built:** Python + Streamlit
    - **Contact:** Section 151 Officer
    """)

# ============================================================================
# SECTION 10: DECISION-SUPPORT POSITIONING
# ============================================================================

st.markdown("---")

st.markdown("""
### 🎯 How This Tool Supports Section 151 Decision-Making

#### Budget Setting
- **What-if modelling** of funding assumptions (council tax, grants, business rates)
- **Spend pressures** on pay, inflation, and demand (particularly ASC/CSC)
- **Savings validation** — test if planned savings targets are realistic and deliverable

#### Reserves Strategy
- **Depletion profile** — understand when reserves will run out under different scenarios
- **Sustainability check** — ensure minimum reserves are maintained (typically 5-10% of budget)
- **Risk-adjusted drawdown** — model controlled use of reserves vs. service reductions

#### Savings Planning
- **Capacity testing** — can the council achieve X% savings without service cuts being too aggressive?
- **Scenario comparison** — optimistic, base, pessimistic cases to guide strategy
- **RAG rating** — automated sustainability flag to highlight red/amber risks

#### Risk Management
- **Funding volatility** — business rates and grant swings visualized
- **Demand uncertainty** — ASC/CSC cost pressures modelled with growth assumptions
- **Social care protection** — toggle to show cost of protecting adult/children's services
- **Sensitivity analysis** — one-slider changes show full 5-year impact

---

**Use this simulator to:**
1. Build confidence in your MTFS through transparent, auditable assumptions
2. Test strategic options (e.g., "what if we increase council tax by 3% instead of 2%?")
3. Communicate financial sustainability to Members and stakeholders
4. Plan reserves strategy with clear 5-year visibility
5. Support difficult savings decisions with data-driven scenarios
""")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 12px; color: #888;'>MTFS Budget Gap Simulator v1.0 | Feb 2026</p>", 
            unsafe_allow_html=True)
