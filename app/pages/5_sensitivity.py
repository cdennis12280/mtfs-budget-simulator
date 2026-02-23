"""
Sensitivity Analysis Dashboard
One-way sensitivity and tornado charts for MTFS assumptions
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add modules to path
modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from calculations import MTFSCalculator
from sensitivity import SensitivityAnalysis
from ui import apply_theme, page_header
from auth import require_auth, require_roles, auth_sidebar

apply_theme()
if not require_auth():
    st.stop()
require_roles({"Admin", "Analyst"})
auth_sidebar()
page_header("Sensitivity Analysis", "Test how robust the MTFS is to changes in key assumptions.")
st.markdown("""
<div class="app-callout">
  Focus on the top drivers first. Use two-way sensitivity to understand compounding risks.
</div>
""", unsafe_allow_html=True)

# Load base data
def load_base_data():
    if 'base_data' in st.session_state:
        return st.session_state['base_data'].copy()
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
    # Filter to only valid project_mtfs parameters
    valid_params = {
        'council_tax_increase_pct', 'business_rates_growth_pct', 'grant_change_pct',
        'fees_charges_growth_pct', 'pay_award_pct', 'general_inflation_pct',
        'asc_demand_growth_pct', 'csc_demand_growth_pct', 'annual_savings_target_pct',
        'use_of_reserves_pct', 'protect_social_care'
    }
    base_params_dict = {k: v for k, v in base_params_dict.items() if k in valid_params}
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
            template=st.session_state.get('plotly_template', 'plotly_white'),
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

        # Two-way sensitivity (top 2 drivers)
        st.markdown("---")
        st.markdown("## Two-Way Sensitivity (Top 2 Drivers)")

        if len(sensitivity_df) >= 2:
            top_two = sensitivity_df.head(2)['Assumption'].tolist()

            label_to_param = {}
            for p in base_params.keys():
                label_to_param[p.replace('_pct', '').replace('_', ' ').title()] = p

            param_y = label_to_param.get(top_two[0])
            param_x = label_to_param.get(top_two[1])

            if param_x and param_y:
                base_val_x = base_params[param_x]
                base_val_y = base_params[param_y]

                def value_grid(base_val):
                    delta = abs(base_val) * (perturbation / 100.0) if base_val != 0 else perturbation / 100.0
                    return np.linspace(base_val - delta, base_val + delta, 5)

                grid_x = value_grid(base_val_x)
                grid_y = value_grid(base_val_y)

                calc = MTFSCalculator(base_data)
                z = []
                for y_val in grid_y:
                    row = []
                    for x_val in grid_x:
                        params = base_params.copy()
                        params[param_x] = float(x_val)
                        params[param_y] = float(y_val)
                        proj = calc.project_mtfs(**params)
                        row.append(proj['Annual_Budget_Gap'].sum())
                    z.append(row)

                heatmap_df = pd.DataFrame(z, index=[f"{v:.2f}" for v in grid_y],
                                          columns=[f"{v:.2f}" for v in grid_x])

                import plotly.graph_objects as go
                fig2 = go.Figure(data=go.Heatmap(
                    z=heatmap_df.values,
                    x=heatmap_df.columns,
                    y=heatmap_df.index,
                    colorscale='RdYlGn_r',
                    colorbar=dict(title='Cumulative Gap (£m)')
                ))
                fig2.update_layout(
                    title=f"Two-Way Sensitivity: {top_two[0]} vs {top_two[1]}",
                    xaxis_title=top_two[1],
                    yaxis_title=top_two[0],
                    height=450,
                    template=st.session_state.get('plotly_template', 'plotly_white'),
                )
                st.plotly_chart(fig2, use_container_width=True)
                st.caption("Grid shows cumulative 4-year gap under paired assumption shifts.")
            else:
                st.info("Unable to map top drivers to parameters for two-way sensitivity.")
        else:
            st.info(\"Need at least two sensitivity drivers to compute two-way analysis.\")
        
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
