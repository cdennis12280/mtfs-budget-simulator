"""
Sensitivity Analysis Dashboard
One-way sensitivity and tornado charts for MTFS assumptions
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add modules to path
modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from calculations import MTFSCalculator
from sensitivity import SensitivityAnalysis

st.title("🎯 Sensitivity Analysis")
st.markdown("Test how robust the MTFS is to changes in key assumptions using tornado analysis.")

# Load base data
@st.cache_data
def load_base_data():
    data_path = Path(__file__).parent.parent.parent / 'data' / 'base_financials.csv'
    return pd.read_csv(data_path)

base_data = load_base_data()
base_budget_year1 = base_data[base_data['Year'] == 'Year_1']['Net_Revenue_Budget'].values[0]

st.markdown("---")

# Base scenario from sidebar (or defaults)
base_params = {
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

# Control panel
col1, col2 = st.columns([2, 1])

with col1:
    perturbation = st.slider(
        "Assumption Change (±%)",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        help="How much to vary each assumption (e.g., ±10% = if pay is 3.5%, test 3.15% and 3.85%)."
    )

with col2:
    run_analysis = st.button("🔄 Run Sensitivity Analysis")

st.markdown("---")

# Run sensitivity (with caching for performance)
@st.cache_data
def run_sensitivity(base_params_tuple, perturbation_pct):
    """Run sensitivity analysis. Use tuple for hashing."""
    base_params_dict = dict(base_params_tuple)
    calc = MTFSCalculator(base_data)
    sens = SensitivityAnalysis(calc, base_data, base_budget_year1)
    return sens.tornado_analysis(base_params_dict, perturbation_pct)

# Cache key
params_tuple = tuple(sorted(base_params.items()))

if run_analysis or st.session_state.get('sensitivity_run', False):
    st.session_state['sensitivity_run'] = True
    
    with st.spinner("Computing sensitivity analysis..."):
        sensitivity_df = run_sensitivity(params_tuple, perturbation)
        
        st.markdown("## Tornado Chart: Impact on 4-Year Cumulative Gap")
        st.markdown(f"Shows impact of ±{perturbation}% change in each assumption on the total budget gap.")
        
        # Custom tornado visualization (simple horizontal bar chart)
        fig_data = sensitivity_df.copy()
        fig_data['Center'] = (fig_data['Low Impact (£m)'] + fig_data['High Impact (£m)']) / 2
        
        import plotly.graph_objects as go
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=fig_data['Assumption'],
            x=fig_data['Low Impact (£m)'],
            name='Low (Favourable)',
            orientation='h',
            marker=dict(color='#2ca02c'),
            text=fig_data['Low Impact (£m)'].round(1),
            textposition='auto',
        ))
        
        fig.add_trace(go.Bar(
            y=fig_data['Assumption'],
            x=fig_data['High Impact (£m)'],
            name='High (Unfavourable)',
            orientation='h',
            marker=dict(color='#d62728'),
            text=fig_data['High Impact (£m)'].round(1),
            textposition='auto',
        ))
        
        fig.update_layout(
            title=f"Sensitivity Tornado: Impact on Cumulative Gap (±{perturbation}% change)",
            xaxis_title="Impact on Gap (£m) — Green = Improves, Red = Worsens",
            yaxis_title="Assumption",
            barmode='relative',
            height=500,
            hovermode='closest',
            template='plotly_white',
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Table view
        st.markdown("## Sensitivity Details")
        st.dataframe(
            sensitivity_df.style.format({
                'Low Impact (£m)': '{:.2f}',
                'High Impact (£m)': '{:.2f}',
                'Range (£m)': '{:.2f}',
            }),
            use_container_width=True
        )
        
        # Interpretation
        st.markdown("---")
        st.markdown("## Interpretation")
        
        top_driver = sensitivity_df.iloc[0]
        st.markdown(f"""
        ### Key Insight
        
        The **{top_driver['Assumption']}** is the most sensitive driver of the budget gap.
        
        A ±{perturbation}% change in this assumption changes the 4-year gap by **£{top_driver['Range (£m)']:.2f}m**.
        
        This means focusing on managing **{top_driver['Assumption'].lower()}** will have the biggest impact on financial resilience.
        
        ### Top 3 Drivers (by sensitivity):
        """)
        
        for idx, row in sensitivity_df.head(3).iterrows():
            st.write(f"{idx+1}. **{row['Assumption']}** — Range: £{row['Range (£m)']:.2f}m")

else:
    st.info("Click 'Run Sensitivity Analysis' to generate the tornado chart.")

st.markdown("---")

st.markdown("""
### How to Use This Tool

1. **Base Scenario**: The analysis uses your current sidebar assumptions as the baseline.
2. **Sensitivity Scale**: Adjust the ±% slider to test different scales of assumption change (±5% = narrow, ±20% = wide).
3. **Interpretation**: Looker at the chart from **left (favourable)** to **right (unfavourable)**.
4. **Action**: Focus savings efforts on the top 3 drivers—these will have the most impact.

### Example
- If **Pay Award** is the top driver and ranges from -£5m to +£8m on the gap,
  then a 1% difference in pay strategy can shift the gap by ~£1.3m over 4 years.
""")
