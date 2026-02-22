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


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="MTFS Budget Gap Simulator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Remove Streamlit branding overlays and tighten default layout/padding for S151 presentation
st.markdown("""
<style>
    /* Metric box styling */
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .red-text { color: #d62728; font-weight: bold; }
    .amber-text { color: #ff7f0e; font-weight: bold; }
    .green-text { color: #2ca02c; font-weight: bold; }

    /* Hide Streamlit header, main menu (hamburger) and footer */
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}

    /* Reduce default padding for denser layout */
    .block-container {padding-top: 0.5rem; padding-left: 0.75rem; padding-right: 0.75rem;}
    .stSidebar {padding-top: 0.5rem;}

    /* Ensure download buttons and panels still visible */
    .stDownloadButton, .stButton {z-index: 9999}
</style>
""", unsafe_allow_html=True)

# Custom non-collapsible header (professional site banner)
st.markdown("""
<div style='background:#0b3d91; padding:10px 16px; color: white; border-radius:6px;'>
    <div style='display:flex; align-items:center; justify-content:space-between;'>
        <div style='display:flex; align-items:center;'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/3/3f/Placeholder_view_vector.svg' style='height:36px; margin-right:12px; filter: invert(1);'/>
            <div>
                <div style='font-weight:700; font-size:18px;'>MTFS Budget Gap Simulator</div>
                <div style='font-size:12px; opacity:0.85;'>Decision-support for Section 151 Officers — v1.0</div>
            </div>
        </div>
        <div style='font-size:13px; opacity:0.95;'>
            <a href='/' style='color:#ffd966; margin-right:12px;'>Dashboard</a>
            <a href='/inputs' style='color:#ffd966; margin-right:12px;'>Inputs</a>
            <a href='/commercial' style='color:#ffd966; margin-right:12px;'>Commercial</a>
            <a href='/scenarios-compare' style='color:#ffd966; margin-right:12px;'>Compare</a>
            <a href='/sensitivity-analysis' style='color:#ffd966; margin-right:12px;'>Sensitivity</a>
            <a href='/settings' style='color:#ffd966;'>Settings</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data
def load_base_data():
    data_path = Path(__file__).parent.parent / 'data' / 'base_financials.csv'
    return pd.read_csv(data_path)


base_data = load_base_data()
base_budget_year1 = base_data[base_data['Year'] == 'Year_1']['Net_Revenue_Budget'].values[0]

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
        help=get_help('council_tax_increase')
    )
    
    business_rates_growth = st.slider(
        "Business Rates Growth (%)",
        min_value=-5.0,
        max_value=3.0,
        value=-1.0,
        step=0.5,
        help=get_help('business_rates_growth')
    )
    
    grant_change = st.slider(
        "Government Grant Change (%)",
        min_value=-10.0,
        max_value=2.0,
        value=-2.0,
        step=0.5,
        help=get_help('grant_change')
    )
    
    fees_charges_growth = st.slider(
        "Fees & Charges Growth (%)",
        min_value=0.0,
        max_value=6.0,
        value=3.0,
        step=0.5,
        help=get_help('fees_charges_growth')
    )
    
    st.markdown("### Expenditure Assumptions")
    
    pay_award = st.slider(
        "Pay Award (%)",
        min_value=1.0,
        max_value=8.0,
        value=3.5,
        step=0.5,
        help=get_help('pay_award')
    )
    
    general_inflation = st.slider(
        "General Inflation (%)",
        min_value=0.5,
        max_value=6.0,
        value=2.0,
        step=0.5,
        help=get_help('general_inflation')
    )
    
    asc_demand_growth = st.slider(
        "Adult Social Care Demand Growth (%)",
        min_value=-1.0,
        max_value=10.0,
        value=4.0,
        step=0.5,
        help=get_help('asc_demand_growth')
    )
    
    csc_demand_growth = st.slider(
        "Children's Social Care Demand Growth (%)",
        min_value=-1.0,
        max_value=8.0,
        value=3.0,
        step=0.5,
        help=get_help('csc_demand_growth')
    )
    
    st.markdown("### Policy Decisions")
    
    savings_target = st.slider(
        "Annual Savings Target (% of budget)",
        min_value=0.0,
        max_value=5.0,
        value=2.0,
        step=0.25,
        help=get_help('savings_target')
    )
    
    use_of_reserves = st.slider(
        "Use of Reserves (%)",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=10.0,
        help=get_help('use_of_reserves')
    )
    
    protect_social_care = st.checkbox(
        "🛡️ Protect Social Care Services",
        value=False,
        help=get_help('protect_social_care')
    )
    
    st.markdown("---")
    
    # Scenario buttons
    st.markdown("### Quick Scenarios")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("📊 Base Case", use_container_width=True):
        scenario = Scenarios.get_base_case()
        st.session_state.update({k: v for k, v in scenario.items()})
        st.rerun()
    
    if col2.button("📈 Optimistic", use_container_width=True):
        scenario = Scenarios.get_optimistic_case()
        st.session_state.update({k: v for k, v in scenario.items()})
        st.rerun()
    
    if col3.button("📉 Pessimistic", use_container_width=True):
        scenario = Scenarios.get_pessimistic_case()
        st.session_state.update({k: v for k, v in scenario.items()})
        st.rerun()

    st.markdown("---")
    st.markdown("### Savings Register")
    savings_register_file = st.file_uploader("Upload Savings Register CSV (optional)", type=['csv'])
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
s_transformation = st.sidebar.slider("Transformation (% of savings)", 0.0, 100.0, 50.0, 5.0, help=get_help('savings_transformation'))
s_income = st.sidebar.slider("Income Generation (% of savings)", 0.0, 100.0, 30.0, 5.0, help=get_help('savings_income'))
s_demand = st.sidebar.slider("Demand Management (% of savings)", 0.0, 100.0, 20.0, 5.0, help=get_help('savings_demand'))
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
num_households = st.sidebar.number_input("Number of households (for per-household impact)", min_value=1, value=100000, help=get_help('council_tax_per_household'))
one_pct_impact = base_budget_year1 * 0.01
per_household = one_pct_impact * 1e6 / num_households if base_budget_year1 > 0 else 0.0
st.sidebar.write(f"1% council tax ≈ £{one_pct_impact:.2f}m total — £{per_household:.2f} per household")

# === Departmental Drill-Down ===
st.sidebar.markdown("---")
st.sidebar.markdown("### Departmental Drill-Down")
dept_file = st.sidebar.file_uploader("Upload departmental budget CSV (optional)", type=['csv'])
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
enable_stochastic = st.sidebar.checkbox("Enable stochastic modelling", value=False, help=get_help('monte_carlo'))
stochastic_runs = st.sidebar.number_input("Monte Carlo runs", min_value=100, max_value=5000, value=500, step=100)
stochastic_std_pct = st.sidebar.slider("Std dev for assumptions (% of value)", 0.1, 10.0, 2.0, help=get_help('stochastic_std'))

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

# === Scenario Bookmarking ===
bookmark_file = Path(__file__).parent.parent / '.saved_scenarios.json'
if st.sidebar.button('Save Current Scenario'):
    scenario_data = {
        'name': f"Custom {pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
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
    saved = []
    if bookmark_file.exists():
        try:
            saved = json.loads(bookmark_file.read_text())
        except Exception:
            saved = []
    saved.append(scenario_data)
    bookmark_file.write_text(json.dumps(saved, indent=2))
    st.sidebar.success('Scenario saved')

if bookmark_file.exists():
    try:
        saved = json.loads(bookmark_file.read_text())
    except Exception:
        saved = []
else:
    saved = []

if saved:
    chosen = st.sidebar.selectbox('Load saved scenario', ['-- none --'] + [s['name'] for s in saved])
    if chosen and chosen != '-- none --':
        sel = next(s for s in saved if s['name'] == chosen)
        params = sel['params']
        # update UI variables in session (non-invasive)
        for k, v in params.items():
            st.session_state[k] = v
        st.sidebar.success(f"Loaded {chosen} — adjust sliders if needed")

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

# === S151 Persona: Global risk overrides ===
st.sidebar.markdown("---")
st.sidebar.markdown("### S151 Override (Global Risk Parameters)")
override_pwlb = st.sidebar.number_input("Assume PWLB interest rate (%)", value=4.5, step=0.1, help=get_help('pwlb_rate'))
override_reserve_floor = st.sidebar.number_input("Reserve floor (£m)", value=10.0, step=1.0)
override_investment_threshold = st.sidebar.slider("Max capital exposure (% of budget) before RED", 1.0, 20.0, 5.0, 1.0)

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

st.title("📊 MTFS Budget Gap Simulator")
st.markdown("**Interactive financial planning tool for Section 151 / Corporate Leadership Teams**")
st.markdown("---")

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

col1, col2, col3, col4 = st.columns(4)

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

st.markdown("---")

# ============================================================================
# SECTION 2: BUDGET GAP TRAJECTORY
# ============================================================================

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
    template='plotly_white',
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
    template='plotly_white',
)
st.plotly_chart(fig_reserves, use_container_width=True)

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
    template='plotly_white',
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
    template='plotly_white',
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
