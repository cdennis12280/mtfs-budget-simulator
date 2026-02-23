"""
Council Profile Setup Wizard
First-run configuration for council identity and baseline inputs.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from ui import apply_theme, page_header, app_link
from auth import require_auth, require_roles, auth_sidebar

apply_theme()
if not require_auth():
    st.stop()
require_roles({"Admin", "Analyst", "Read-only"})
auth_sidebar()
read_only = st.session_state.get("auth_role") == "Read-only"
if read_only:
    st.info("Read-only mode: setup inputs are disabled.")

page_header("Council Profile Setup", "Configure identity, baseline budgets, and reserves policy.")

st.markdown("""
<div class="app-callout">
  Complete these steps once per council to make dashboards and reports board-ready.
</div>
""", unsafe_allow_html=True)

def load_base_data():
    if 'base_data' in st.session_state:
        return st.session_state['base_data'].copy()
    demo_mode = st.session_state.get("demo_mode", False)
    filename = 'demo_financials.csv' if demo_mode else 'base_financials.csv'
    return pd.read_csv(Path(__file__).parent.parent.parent / 'data' / filename)

step = st.radio(
    "Setup Step",
    options=[
        "1. Council Identity",
        "2. Baseline Budget",
        "3. Reserves Policy",
        "4. Finish",
    ],
    horizontal=True,
)

if step == "1. Council Identity":
    st.markdown("### Council Identity")
    council_name = st.text_input(
        "Council name",
        value=st.session_state.get('council_name', 'Example Council'),
        disabled=read_only
    )
    council_colour = st.color_picker(
        "Primary brand color",
        value=st.session_state.get('council_colour', '#0b3d91'),
        disabled=read_only
    )
    if not read_only:
        st.session_state['council_name'] = council_name
        st.session_state['council_colour'] = council_colour
    st.markdown("Next: go to `2. Baseline Budget`.")

if step == "2. Baseline Budget":
    st.markdown("### Baseline Budget")
    base_data = load_base_data()
    y1 = base_data[base_data['Year'] == 'Year_1'].iloc[0]

    base_budget = st.number_input(
        "Year 1 net revenue budget (£m)",
        min_value=0.0,
        value=float(st.session_state.get('base_budget', y1.get('Net_Revenue_Budget', 250.0))),
        step=1.0,
        disabled=read_only
    )
    opening_reserves = st.number_input(
        "Opening reserves (£m)",
        min_value=0.0,
        value=float(st.session_state.get('opening_reserves', y1.get('Opening_Reserves', 25.0))),
        step=1.0,
        disabled=read_only
    )
    if not read_only:
        base_data.loc[base_data['Year'] == 'Year_1', 'Net_Revenue_Budget'] = float(base_budget)
        base_data.loc[base_data['Year'] == 'Year_1', 'Opening_Reserves'] = float(opening_reserves)
        st.session_state['base_data'] = base_data
        st.session_state['base_budget'] = float(base_budget)
        st.session_state['opening_reserves'] = float(opening_reserves)
    st.markdown("Next: go to `3. Reserves Policy`.")

if step == "3. Reserves Policy":
    st.markdown("### Reserves Policy")
    st.markdown("Set the policy thresholds used across dashboards and reports.")
    col1, col2, col3 = st.columns(3)
    with col1:
        min_reserves = st.slider(
            "Minimum reserves (%)",
            min_value=0.0,
            max_value=20.0,
            value=st.session_state.get('reserves_policy_min', 5.0),
            step=0.5,
            disabled=read_only
        )
    with col2:
        target_reserves = st.slider(
            "Target reserves (%)",
            min_value=0.0,
            max_value=30.0,
            value=st.session_state.get('reserves_policy_target', 10.0),
            step=0.5,
            disabled=read_only
        )
    with col3:
        max_reserves = st.slider(
            "Maximum reserves (%)",
            min_value=0.0,
            max_value=50.0,
            value=st.session_state.get('reserves_policy_max', 25.0),
            step=1.0,
            disabled=read_only
        )
    if not read_only:
        st.session_state['reserves_policy_min'] = min_reserves
        st.session_state['reserves_policy_target'] = target_reserves
        st.session_state['reserves_policy_max'] = max_reserves
    st.markdown("Next: go to `4. Finish`.")

if step == "4. Finish":
    st.markdown("### Finish Setup")
    st.markdown("Confirm setup completion to remove the first-run prompt.")
    if st.button("✅ Mark setup complete", disabled=read_only):
        st.session_state["profile_setup_complete"] = True
        st.success("Council profile setup completed.")
    st.markdown(f"[Open Dashboard]({app_link('/')})")
