"""
Guided Wizard for Section 151 MTFS workflow.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from ui import apply_theme, page_header
from snapshots import add_snapshot
from audit_log import get_audit_log
from calculations import MTFSCalculator
import plotly.graph_objects as go

apply_theme()
page_header("MTFS Guided Wizard", "A step-by-step flow for Section 151 budget setting and reporting.")

st.markdown("""
<div class="app-callout">
  Follow the steps in order. Each step applies changes to your session and can be revisited.
</div>
""", unsafe_allow_html=True)

steps = [
    "1. Council Profile",
    "2. Baseline Inputs",
    "3. Core Assumptions",
    "4. Risk Stressing",
    "5. Governance Snapshot",
    "6. Export & Report",
]

step = st.radio("Wizard step", options=steps, horizontal=True)

def get_base_data():
    if 'base_data' in st.session_state:
        return st.session_state['base_data'].copy()
    return pd.read_csv(Path(__file__).parent.parent.parent / 'data' / 'base_financials.csv')

def build_params():
    return {
        'council_tax_increase_pct': st.session_state.get('council_tax_increase_pct', 2.0),
        'business_rates_growth_pct': st.session_state.get('business_rates_growth_pct', -1.0),
        'grant_change_pct': st.session_state.get('grant_change_pct', -2.0),
        'fees_charges_growth_pct': st.session_state.get('fees_charges_growth_pct', 3.0),
        'pay_award_pct': st.session_state.get('pay_award_pct', 3.5),
        'general_inflation_pct': st.session_state.get('general_inflation_pct', 2.0),
        'asc_demand_growth_pct': st.session_state.get('asc_demand_growth_pct', 4.0),
        'csc_demand_growth_pct': st.session_state.get('csc_demand_growth_pct', 3.0),
        'annual_savings_target_pct': st.session_state.get('annual_savings_target_pct', 2.0),
        'use_of_reserves_pct': st.session_state.get('use_of_reserves_pct', 50.0),
        'protect_social_care': st.session_state.get('protect_social_care', False),
    }

def live_kpis():
    base_data = get_base_data()
    base_budget_year1 = base_data[base_data['Year'] == 'Year_1']['Net_Revenue_Budget'].values[0]
    calc = MTFSCalculator(base_data)
    proj = calc.project_mtfs(**build_params())
    kpis = calc.calculate_kpis(proj, base_budget_year1)
    st.session_state['kpis'] = kpis
    return proj, kpis

def live_charts(proj):
    template = st.session_state.get('plotly_template', 'plotly_dark')
    fig_gap = go.Figure()
    fig_gap.add_trace(go.Scatter(
        x=proj['Year_Number'],
        y=proj['Annual_Budget_Gap'],
        mode='lines+markers',
        name='Annual Gap',
        line=dict(width=3)
    ))
    fig_gap.add_hline(y=0, line_dash="dash", line_color="#6ee7b7")
    fig_gap.update_layout(
        title="Annual Budget Gap",
        xaxis_title="Year",
        yaxis_title="Gap (£m)",
        height=280,
        template=template,
        margin=dict(l=10, r=10, t=40, b=10),
    )

    fig_res = go.Figure()
    fig_res.add_trace(go.Scatter(
        x=proj['Year_Number'],
        y=proj['Closing_Reserves'],
        mode='lines+markers',
        name='Closing Reserves',
        line=dict(width=3)
    ))
    fig_res.update_layout(
        title="Closing Reserves",
        xaxis_title="Year",
        yaxis_title="Reserves (£m)",
        height=280,
        template=template,
        margin=dict(l=10, r=10, t=40, b=10),
    )

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_gap, use_container_width=True)
    with c2:
        st.plotly_chart(fig_res, use_container_width=True)

# Step 1: Council profile
if step == "1. Council Profile":
    st.markdown("### Council Profile")
    council_name = st.text_input(
        "Council name",
        value=st.session_state.get('council_name', 'Example Council')
    )
    council_colour = st.color_picker(
        "Primary brand color",
        value=st.session_state.get('council_colour', '#0b3d91')
    )
    st.session_state['council_name'] = council_name
    st.session_state['council_colour'] = council_colour

    st.info("Dark theme is enforced for all users.")

    st.markdown("Next: go to `2. Baseline Inputs`.")
    proj, kpis = live_kpis()
    st.markdown("### Live Impact")
    st.write(f"Cumulative gap: £{kpis['total_4_year_gap']:.1f}m")
    live_charts(proj)

# Step 2: Baseline inputs
if step == "2. Baseline Inputs":
    st.markdown("### Baseline Inputs")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['base_budget'] = st.number_input(
            "Year 1 net revenue budget (£m)",
            min_value=0.0,
            value=float(st.session_state.get('base_budget', 250.0)),
            step=1.0
        )
        st.session_state['opening_reserves'] = st.number_input(
            "Opening reserves (£m)",
            min_value=0.0,
            value=float(st.session_state.get('opening_reserves', 40.0)),
            step=1.0
        )
    with col2:
        st.markdown("Need detailed line items?")
        st.markdown("[Go to Inputs page](/inputs)")

    st.info("Values apply immediately. Update detailed line items in Inputs if needed.")

    # Reflect baseline into in-session base_data for model use
    try:
        base_data = get_base_data()
        base_data.loc[base_data['Year'] == 'Year_1', 'Net_Revenue_Budget'] = float(st.session_state['base_budget'])
        base_data.loc[base_data['Year'] == 'Year_1', 'Opening_Reserves'] = float(st.session_state['opening_reserves'])
        st.session_state['base_data'] = base_data
    except Exception:
        pass

    proj, kpis = live_kpis()
    st.markdown("### Live Impact")
    st.write(f"Cumulative gap: £{kpis['total_4_year_gap']:.1f}m")
    live_charts(proj)

# Step 3: Assumptions
if step == "3. Core Assumptions":
    st.markdown("### Core Assumptions")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state['council_tax_increase_pct'] = st.slider(
            "Council tax increase (%)",
            0.0, 5.0, float(st.session_state.get('council_tax_increase_pct', 2.0)), 0.1
        )
        st.session_state['business_rates_growth_pct'] = st.slider(
            "Business rates growth (%)",
            -5.0, 5.0, float(st.session_state.get('business_rates_growth_pct', -1.0)), 0.1
        )
        st.session_state['grant_change_pct'] = st.slider(
            "Grant change (%)",
            -10.0, 5.0, float(st.session_state.get('grant_change_pct', -2.0)), 0.1
        )
    with col2:
        st.session_state['pay_award_pct'] = st.slider(
            "Pay award (%)",
            0.0, 8.0, float(st.session_state.get('pay_award_pct', 3.5)), 0.1
        )
        st.session_state['general_inflation_pct'] = st.slider(
            "General inflation (%)",
            0.0, 8.0, float(st.session_state.get('general_inflation_pct', 2.0)), 0.1
        )
        st.session_state['annual_savings_target_pct'] = st.slider(
            "Annual savings target (%)",
            0.0, 6.0, float(st.session_state.get('annual_savings_target_pct', 2.0)), 0.1
        )
    with col3:
        st.session_state['asc_demand_growth_pct'] = st.slider(
            "ASC demand growth (%)",
            0.0, 10.0, float(st.session_state.get('asc_demand_growth_pct', 4.0)), 0.1
        )
        st.session_state['csc_demand_growth_pct'] = st.slider(
            "CSC demand growth (%)",
            0.0, 10.0, float(st.session_state.get('csc_demand_growth_pct', 3.0)), 0.1
        )
        st.session_state['use_of_reserves_pct'] = st.slider(
            "Use of reserves (% of gap)",
            0.0, 100.0, float(st.session_state.get('use_of_reserves_pct', 50.0)), 1.0
        )

    st.info("These values apply immediately. See live impact below.")

    proj, kpis = live_kpis()
    st.markdown("### Live Impact")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Cumulative Gap (£m)", f"{kpis['total_4_year_gap']:.1f}")
    with c2:
        st.metric("Savings Required (%)", f"{kpis['savings_required_pct']:.2f}")
    with c3:
        reserves_end = proj.iloc[-1]['Closing_Reserves']
        st.metric("Final Reserves (£m)", f"{reserves_end:.1f}")
    live_charts(proj)

    st.markdown("[Go to Dashboard](/)")

# Step 4: Risk stressing
if step == "4. Risk Stressing":
    st.markdown("### Risk Stressing")
    st.markdown("Use the Risk Advisor for targeted stress tests and composite scenarios.")
    st.markdown("[Open Risk Advisor](/risk_advisor)")
    st.markdown("You can also apply presets on the Dashboard sidebar.")
    proj, kpis = live_kpis()
    st.markdown("### Current Position")
    st.write(f"Cumulative gap: £{kpis['total_4_year_gap']:.1f}m")
    live_charts(proj)
    st.markdown("[Open Dashboard](/)")

# Step 5: Governance snapshot
if step == "5. Governance Snapshot":
    st.markdown("### Governance Snapshot")
    snapshot_name = st.text_input("Snapshot name", value="Budget Setting - Draft")
    snapshot_notes = st.text_area("Notes", value="", height=100)
    if st.button("Save snapshot"):
        assumptions = {
            'council_tax_increase_pct': st.session_state.get('council_tax_increase_pct', 2.0),
            'business_rates_growth_pct': st.session_state.get('business_rates_growth_pct', -1.0),
            'grant_change_pct': st.session_state.get('grant_change_pct', -2.0),
            'fees_charges_growth_pct': st.session_state.get('fees_charges_growth_pct', 3.0),
            'pay_award_pct': st.session_state.get('pay_award_pct', 3.5),
            'general_inflation_pct': st.session_state.get('general_inflation_pct', 2.0),
            'asc_demand_growth_pct': st.session_state.get('asc_demand_growth_pct', 4.0),
            'csc_demand_growth_pct': st.session_state.get('csc_demand_growth_pct', 3.0),
            'annual_savings_target_pct': st.session_state.get('annual_savings_target_pct', 2.0),
            'use_of_reserves_pct': st.session_state.get('use_of_reserves_pct', 50.0),
            'protect_social_care': st.session_state.get('protect_social_care', False),
        }
        kpis = st.session_state.get('kpis', {})
        rag = st.session_state.get('rag_rating', 'AMBER')
        entry = add_snapshot(
            path=Path(__file__).parent.parent.parent / '.forecast_snapshots.json',
            name=snapshot_name,
            assumptions=assumptions,
            kpis=kpis,
            rag_rating=rag,
            notes=snapshot_notes
        )
        get_audit_log().log_entry(
            action='forecast_snapshot_save',
            user='system',
            key=entry.get('snapshot_id', snapshot_name),
            notes=f"Snapshot saved from wizard: {snapshot_name} v{entry.get('version', 1)}"
        )
        st.success("Snapshot saved.")

    proj, kpis = live_kpis()
    st.markdown("### Live Impact")
    st.write(f"Cumulative gap: £{kpis['total_4_year_gap']:.1f}m")
    live_charts(proj)

# Step 6: Exports
if step == "6. Export & Report":
    st.markdown("### Export and Report")
    st.markdown("Generate statutory reports and data packs for governance.")
    st.markdown("[Open Reports page](/reports)")
    st.markdown("For audit trails and evidence, export logs from the Audit page.")
    st.markdown("[Open Audit page](/audit)")
