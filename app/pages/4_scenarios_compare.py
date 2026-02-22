"""
Scenario Comparison Dashboard
Compare multiple saved scenarios side-by-side
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import json
import sys

# Add modules to path
modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from calculations import MTFSCalculator
from scenarios import Scenarios
from rag_rating import RAGRating

st.title("📊 Scenario Comparison")
st.markdown("Compare multiple scenarios side-by-side to inform decision-making.")

# Load base data
@st.cache_data
def load_base_data():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'base_financials.csv'
    return pd.read_csv(data_path)

base_data = load_base_data()
base_budget_year1 = base_data[base_data['Year'] == 'Year_1']['Net_Revenue_Budget'].values[0]

# Load saved scenarios
bookmark_file = Path(__file__).parent.parent.parent / '.saved_scenarios.json'
saved_scenarios = []
if bookmark_file.exists():
    try:
        saved_scenarios = json.loads(bookmark_file.read_text())
    except Exception:
        saved_scenarios = []

# Add predefined scenarios
predefined = Scenarios.get_all_scenarios()
for name, params in predefined.items():
    saved_scenarios.append({
        'name': f"{name} (predefined)",
        'params': params
    })

if not saved_scenarios:
    st.warning("No scenarios available. Save a scenario from the main Dashboard first, or use predefined scenarios.")
    st.stop()

# Multi-select scenarios to compare
scenario_names = [s['name'] for s in saved_scenarios]
selected = st.multiselect(
    'Select scenarios to compare (up to 4)',
    options=scenario_names,
    default=scenario_names[:min(3, len(scenario_names))],
    max_selections=4
)

if not selected:
    st.info("Select at least one scenario to compare.")
    st.stop()

# Run selected scenarios
calculator = MTFSCalculator(base_data)
comparison_data = {}

for scenario_name in selected:
    s = next((s for s in saved_scenarios if s['name'] == scenario_name), None)
    if not s:
        continue
    
    params = s['params']
    # Filter params to only include valid project_mtfs arguments
    valid_params = {
        'council_tax_increase_pct', 'business_rates_growth_pct', 'grant_change_pct',
        'fees_charges_growth_pct', 'pay_award_pct', 'general_inflation_pct',
        'asc_demand_growth_pct', 'csc_demand_growth_pct', 'annual_savings_target_pct',
        'use_of_reserves_pct', 'protect_social_care'
    }
    filtered_params = {k: v for k, v in params.items() if k in valid_params}
    proj = calculator.project_mtfs(**filtered_params)
    kpis = calculator.calculate_kpis(proj, base_budget_year1)
    final_reserves = proj.iloc[-1]['Closing_Reserves']
    rag, _ = RAGRating.get_rating(proj, base_budget_year1, (final_reserves / base_budget_year1) * 100)
    
    comparison_data[scenario_name] = {
        'projection': proj,
        'kpis': kpis,
        'rag': rag,
        'final_reserves': final_reserves,
    }

st.markdown("---")

# KPI Comparison Cards
st.markdown("## Key Metrics")
cols = st.columns(len(comparison_data))

for col, (scenario_name, data) in zip(cols, comparison_data.items()):
    with col:
        kpis = data['kpis']
        rag = data['rag']
        rag_colors = {"RED": "#d62728", "AMBER": "#ff7f0e", "GREEN": "#2ca02c"}
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px; border-left: 4px solid {rag_colors[rag]};">
            <h5>{scenario_name}</h5>
            <p><strong>Gap:</strong> £{kpis['total_4_year_gap']:.1f}m</p>
            <p><strong>Reserve:</strong> £{data['final_reserves']:.1f}m</p>
            <p><strong>Rating:</strong> <span style="color: {rag_colors[rag]}; font-weight: bold;">{rag}</span></p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Gap Comparison Chart
st.markdown("## Cumulative Gap Trajectory")
fig_gap = go.Figure()

for scenario_name, data in comparison_data.items():
    proj = data['projection']
    fig_gap.add_trace(go.Scatter(
        x=proj['Year_Number'],
        y=proj['Cumulative_Gap'],
        mode='lines+markers',
        name=scenario_name,
        line=dict(width=3),
    ))

fig_gap.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Balanced")
fig_gap.update_layout(
    title="Cumulative 4-Year Budget Gap by Scenario",
    xaxis_title="Year",
    yaxis_title="Cumulative Gap (£m)",
    hovermode='x unified',
    height=450,
    template='plotly_white',
)
st.plotly_chart(fig_gap, use_container_width=True)

# Reserves Comparison Chart
st.markdown("## Reserves Position Over Time")
fig_res = go.Figure()

for scenario_name, data in comparison_data.items():
    proj = data['projection']
    fig_res.add_trace(go.Scatter(
        x=proj['Year_Number'],
        y=proj['Closing_Reserves'],
        mode='lines+markers',
        name=scenario_name,
        line=dict(width=3),
        fill='tozeroy' if len(comparison_data) <= 2 else None,
    ))

min_threshold = base_budget_year1 * (RAGRating.MIN_RESERVES_PCT / 100)
fig_res.add_hline(y=min_threshold, line_dash="dash", line_color="red",
                   annotation_text=f"Min Threshold (£{min_threshold:.1f}m)")

fig_res.update_layout(
    title="Closing Reserves by Scenario",
    xaxis_title="Year",
    yaxis_title="Reserves (£m)",
    hovermode='x unified',
    height=450,
    template='plotly_white',
)
st.plotly_chart(fig_res, use_container_width=True)

# Detailed Comparison Table
st.markdown("## Detailed Comparison Table")
comp_rows = []
for scenario_name, data in comparison_data.items():
    kpis = data['kpis']
    comp_rows.append({
        'Scenario': scenario_name,
        'Total Gap (£m)': f"{kpis['total_4_year_gap']:.1f}",
        'Gap % of Budget': f"{(kpis['total_4_year_gap'] / base_budget_year1 * 100):.1f}%",
        'Final Reserves (£m)': f"{data['final_reserves']:.1f}",
        'Reserves % of Budget': f"{(data['final_reserves'] / base_budget_year1 * 100):.1f}%",
        'Savings Needed': f"{kpis['savings_required_pct']:.2f}%",
        'RAG Rating': data['rag'],
    })

comp_df = pd.DataFrame(comp_rows)
st.dataframe(comp_df, use_container_width=True)

st.markdown("---")

# Export comparison
if st.button("💾 Export Comparison (CSV)"):
    csv = comp_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download comparison CSV",
        data=csv,
        file_name='scenario_comparison.csv',
        mime='text/csv'
    )
