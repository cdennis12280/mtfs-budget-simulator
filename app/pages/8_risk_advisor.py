"""
Risk & Sensitivity-Weighted Scenario Advisor
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
from risk_advisor import (
    load_risk_register,
    normalize_risk_register,
    merge_sensitivity,
    build_stress_table,
    build_contingency_plan,
    adverse_value,
)
from audit_log import get_audit_log
from ui import apply_theme, page_header
from auth import require_auth, require_roles, auth_sidebar

apply_theme()
if not require_auth():
    st.stop()
require_roles({"Admin", "Analyst", "Read-only"})
auth_sidebar()
page_header("Risk and Sensitivity Scenario Advisor", "Link the corporate risk register to model sensitivity and generate stress tests.")
st.markdown("""
<div class="app-callout">
  Keep the risk register aligned to MTFS drivers. Use composite stress for worst-case testing.
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

# Base scenario from session state (or defaults)
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

valid_params = {
    'council_tax_increase_pct', 'business_rates_growth_pct', 'grant_change_pct',
    'fees_charges_growth_pct', 'pay_award_pct', 'general_inflation_pct',
    'asc_demand_growth_pct', 'csc_demand_growth_pct', 'annual_savings_target_pct',
    'use_of_reserves_pct', 'protect_social_care'
}
base_params = {k: v for k, v in base_params.items() if k in valid_params}

calc = MTFSCalculator(base_data)

st.markdown("---")
st.markdown("## Corporate Risk Register")

risk_path = Path(__file__).parent.parent.parent / 'data' / 'risk_register.csv'

if 'risk_register_df' not in st.session_state:
    st.session_state['risk_register_df'] = load_risk_register(risk_path)

risk_df = st.session_state['risk_register_df']

edited = st.data_editor(
    risk_df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        'likelihood': st.column_config.NumberColumn(min_value=0, max_value=5, step=1),
        'impact': st.column_config.NumberColumn(min_value=0, max_value=5, step=1),
        'default_stress_pct': st.column_config.NumberColumn(min_value=0, max_value=50, step=1),
        'direction': st.column_config.SelectboxColumn(options=["increase", "decrease"]),
    },
)

col_apply, col_reset, col_save = st.columns(3)
with col_apply:
    if st.button("Apply edits"):
        st.session_state['risk_register_df'] = normalize_risk_register(edited)
        st.success("Risk register updated for this session.")
with col_reset:
    if st.button("Reset to defaults"):
        st.session_state['risk_register_df'] = load_risk_register(risk_path)
        st.info("Risk register reset to defaults.")
with col_save:
    csv_bytes = normalize_risk_register(edited).to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download risk register (CSV)",
        data=csv_bytes,
        file_name='risk_register.csv',
        mime='text/csv'
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
    help="Used to compute the tornado sensitivity range linked to each risk driver."
)

sens = SensitivityAnalysis(calc, base_data, base_budget_year1)
sensitivity_df = sens.tornado_analysis(base_params, perturbation)
linked = merge_sensitivity(risk_df, sensitivity_df)

st.dataframe(
    linked[[
        'risk_id', 'risk_title', 'driver_label', 'driver_param',
        'likelihood', 'impact', 'risk_score', 'Sensitivity Range (£m)'
    ]].rename(columns={
        'risk_id': 'Risk ID',
        'risk_title': 'Risk',
        'driver_label': 'Driver',
        'driver_param': 'Driver Param',
    }),
    use_container_width=True
)

st.markdown("---")
st.markdown("## Risk-Weighted Stress Tests")

stress_override = st.selectbox(
    "Stress level",
    options=["Use register defaults", "Use risk score scale", "Custom %"],
    index=0
)

custom_stress = None
if stress_override == "Custom %":
    custom_stress = st.slider("Custom stress %", 1, 50, 15, 1)

stress_df = build_stress_table(
    calc,
    base_params,
    linked,
    stress_pct_override=custom_stress if stress_override == "Custom %" else None
)

if stress_override == "Use risk score scale":
    # force default stress to 0 so score-based lookup is used
    linked_for_score = linked.copy()
    linked_for_score['default_stress_pct'] = 0
    stress_df = build_stress_table(calc, base_params, linked_for_score, None)

if stress_df.empty:
    st.info("No stress tests could be generated. Check the risk register driver parameters.")
    st.stop()

st.dataframe(
    stress_df[[
        'Risk ID', 'Risk', 'Driver', 'Direction', 'Risk Score', 'Stress %',
        'Base Value', 'Stressed Value', 'Gap Delta (£m)', 'Weighted Impact'
    ]].style.format({
        'Base Value': '{:.2f}',
        'Stressed Value': '{:.2f}',
        'Gap Delta (£m)': '{:.2f}',
        'Weighted Impact': '{:.2f}',
    }),
    use_container_width=True
)

st.markdown("---")
st.markdown("## Recommended Stress Scenarios")

top_n = st.slider("Number of top risks to stress", 1, min(6, len(stress_df)), 3, 1)

top_df = stress_df.head(top_n)

st.markdown("### Top risks (ranked by weighted impact)")
st.dataframe(
    top_df[[
        'Risk ID', 'Risk', 'Driver', 'Direction', 'Stress %',
        'Base Value', 'Stressed Value', 'Gap Delta (£m)'
    ]].style.format({
        'Base Value': '{:.2f}',
        'Stressed Value': '{:.2f}',
        'Gap Delta (£m)': '{:.2f}',
    }),
    use_container_width=True
)

# Composite stress scenario
composite_params = base_params.copy()
for _, row in top_df.iterrows():
    composite_params[row['Driver Param']] = row['Stressed Value']

composite_proj = calc.project_mtfs(**composite_params)
composite_kpis = calc.calculate_kpis(composite_proj, base_budget_year1)
composite_gap = composite_kpis['total_4_year_gap']
final_reserves = composite_proj.iloc[-1]['Closing_Reserves']

st.markdown("### Composite stress scenario")
st.write(
    f"Applies the top {top_n} stress tests together. "
    f"Cumulative gap: **£{composite_gap:.1f}m**. "
    f"Final reserves: **£{final_reserves:.1f}m**."
)

col_apply_single, col_apply_comp = st.columns(2)

with col_apply_single:
    selected_risk = st.selectbox("Apply single stress", options=stress_df['Risk'].tolist())
    selected_row = stress_df[stress_df['Risk'] == selected_risk].iloc[0]
    if st.button("Apply selected stress to assumptions"):
        key = selected_row['Driver Param']
        old = st.session_state.get(key)
        st.session_state[key] = float(selected_row['Stressed Value'])
        audit = get_audit_log()
        audit.log_entry(
            action='risk_stress_apply',
            user='system',
            key=key,
            old_value=old,
            new_value=st.session_state[key],
            notes=f"Applied risk stress: {selected_row['Risk ID']}"
        )
        st.success(f"Applied stress to {selected_row['Driver']}")

with col_apply_comp:
    if st.button("Apply composite stress to assumptions"):
        audit = get_audit_log()
        for _, row in top_df.iterrows():
            key = row['Driver Param']
            old = st.session_state.get(key)
            st.session_state[key] = float(row['Stressed Value'])
            audit.log_entry(
                action='risk_stress_apply',
                user='system',
                key=key,
                old_value=old,
                new_value=st.session_state[key],
                notes=f"Applied composite stress: {row['Risk ID']}"
            )
        st.success("Composite stress applied to assumptions.")

# Export stress plan
csv = stress_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download stress plan (CSV)",
    data=csv,
    file_name='risk_stress_plan.csv',
    mime='text/csv'
)

st.markdown("---")
st.markdown("## Contingency Planning Guidance")

contingency_df = build_contingency_plan(top_df)

for _, row in contingency_df.iterrows():
    st.markdown(
        f"**{row['Risk']}** ({row['Driver']}) — {row['Recommended Action']}"
    )

st.markdown("---")
st.markdown("### Notes")
st.markdown(
    "- Stress levels can be overridden to match local risk appetite or audit requirements.\n"
    "- Apply single or composite stresses to push changes back into the model sidebar.\n"
    "- Update the risk register as corporate risks change or new drivers emerge."
)
