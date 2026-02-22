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
from pathlib import Path
import sys

# Add modules to path
modules_path = Path(__file__).parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from calculations import MTFSCalculator
from scenarios import Scenarios
from rag_rating import RAGRating


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="MTFS Budget Gap Simulator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .red-text { color: #d62728; font-weight: bold; }
    .amber-text { color: #ff7f0e; font-weight: bold; }
    .green-text { color: #2ca02c; font-weight: bold; }
</style>
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
        help="Annual council tax increase assumption"
    )
    
    business_rates_growth = st.slider(
        "Business Rates Growth (%)",
        min_value=-5.0,
        max_value=3.0,
        value=-1.0,
        step=0.5,
        help="Business rates income growth/decline"
    )
    
    grant_change = st.slider(
        "Government Grant Change (%)",
        min_value=-10.0,
        max_value=2.0,
        value=-2.0,
        step=0.5,
        help="Core grant funding change"
    )
    
    fees_charges_growth = st.slider(
        "Fees & Charges Growth (%)",
        min_value=0.0,
        max_value=6.0,
        value=3.0,
        step=0.5,
        help="Growth in fees and charges income"
    )
    
    st.markdown("### Expenditure Assumptions")
    
    pay_award = st.slider(
        "Pay Award (%)",
        min_value=1.0,
        max_value=8.0,
        value=3.5,
        step=0.5,
        help="Annual pay award inflation"
    )
    
    general_inflation = st.slider(
        "General Inflation (%)",
        min_value=0.5,
        max_value=6.0,
        value=2.0,
        step=0.5,
        help="General inflation on non-pay costs"
    )
    
    asc_demand_growth = st.slider(
        "Adult Social Care Demand Growth (%)",
        min_value=-1.0,
        max_value=10.0,
        value=4.0,
        step=0.5,
        help="ASC demand and complexity growth"
    )
    
    csc_demand_growth = st.slider(
        "Children's Social Care Demand Growth (%)",
        min_value=-1.0,
        max_value=8.0,
        value=3.0,
        step=0.5,
        help="CSC demand growth"
    )
    
    st.markdown("### Policy Decisions")
    
    savings_target = st.slider(
        "Annual Savings Target (% of budget)",
        min_value=0.0,
        max_value=5.0,
        value=2.0,
        step=0.25,
        help="Planned savings as % of budget"
    )
    
    use_of_reserves = st.slider(
        "Use of Reserves (%)",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=10.0,
        help="Proportion of gap funded from reserves vs. service cuts"
    )
    
    protect_social_care = st.checkbox(
        "🛡️ Protect Social Care Services",
        value=False,
        help="Suppress demand pressures from planning (cost must be from baseline)"
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


# ============================================================================
# SECTION 1: STRATEGIC HEADLINE KPIS
# ============================================================================

st.title("📊 MTFS Budget Gap Simulator")
st.markdown("**Interactive financial planning tool for Section 151 / Corporate Leadership Teams**")
st.markdown("---")

st.markdown("## Strategic Headlines (4-Year MTFS)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    gap_amount = kpis['total_4_year_gap']
    gap_color = "red" if gap_amount > 20 else "orange" if gap_amount > 10 else "green"
    st.metric(
        "💰 Cumulative Gap",
        f"£{gap_amount:.1f}m",
        delta=f"{(gap_amount / base_budget_year1 * 100):.1f}% of budget",
        delta_color="inverse"
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
        delta=f"Final: £{projection_df.iloc[-1]['Closing_Reserves']:.1f}m"
    )

with col3:
    savings_req = kpis['savings_required_pct']
    st.metric(
        "🎯 Additional Savings Needed",
        f"{savings_req:.1f}%",
        delta="of annual budget",
        delta_color="inverse"
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

fig_gap = go.Figure()
fig_gap.add_trace(go.Scatter(
    x=projection_df['Year_Number'],
    y=projection_df['Annual_Budget_Gap'],
    mode='lines+markers',
    name='Annual Gap',
    line=dict(color='#d62728', width=3),
    marker=dict(size=8),
))
fig_gap.add_trace(go.Scatter(
    x=projection_df['Year_Number'],
    y=projection_df['Cumulative_Gap'],
    mode='lines+markers',
    name='Cumulative Gap',
    line=dict(color='#ff7f0e', width=2, dash='dash'),
    marker=dict(size=6),
))
fig_gap.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Balanced")
fig_gap.update_layout(
    title="Annual and Cumulative Budget Gap",
    xaxis_title="Year",
    yaxis_title="Gap (£m)",
    hovermode='x unified',
    height=400,
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
