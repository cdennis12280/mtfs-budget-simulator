"""
Settings & Theme Customization
User preferences for the MTFS Budget Gap Simulator
"""

import streamlit as st
import sys
from pathlib import Path

# Add modules to path
modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from reserves_policy import ReservesPolicy
from audit_log import get_audit_log
from ui import apply_theme, page_header
from billing import plan_label
from storage import persistence_enabled, save_json
from auth import require_auth, require_roles, auth_sidebar

if "theme" not in st.session_state:
    st.session_state["theme"] = "Light"
apply_theme()
if not require_auth():
    st.stop()
require_roles({"Admin"})
auth_sidebar()
page_header("Settings and Preferences", "Customize your experience with the MTFS Budget Gap Simulator.")
st.markdown("""
<div class="app-callout">
  Theme and branding changes apply immediately across all pages.
</div>
""", unsafe_allow_html=True)

# Theme Selection
st.markdown("## Theme")
theme_options = ["Light", "Dark", "Print-Friendly"]
theme = st.selectbox(
    "Theme",
    options=theme_options,
    index=theme_options.index(st.session_state.get("theme", "Light")),
    help="Light is optimized for board papers; Dark is best for low-light rooms; Print-Friendly is minimal."
)
st.session_state["theme"] = theme

# Demo Mode
st.markdown("## Demo Mode")
demo_mode = st.checkbox(
    "Enable demo dataset",
    value=st.session_state.get("demo_mode", False),
    help="Loads a curated, council-like dataset for demos. Clears in-session inputs."
)
if demo_mode != st.session_state.get("demo_mode", False):
    st.session_state["demo_mode"] = demo_mode
    st.session_state.pop("base_data", None)
    st.session_state.pop("inputs_df", None)
    st.session_state.pop("base_budget", None)
    st.session_state.pop("opening_reserves", None)

if st.button("Reset demo data", disabled=not st.session_state.get("demo_mode", False)):
    st.session_state.pop("base_data", None)
    st.session_state.pop("inputs_df", None)
    st.session_state.pop("base_budget", None)
    st.session_state.pop("opening_reserves", None)
    st.success("Demo data reset for this session.")

if st.button("Reset demo tenant (snapshots + audit)", disabled=not st.session_state.get("demo_mode", False)):
    st.session_state.pop("forecast_snapshots", None)
    st.session_state.pop("audit_log_entries", None)
    st.session_state.pop("saved_scenarios", None)
    if persistence_enabled():
        save_json("snapshots.json", [])
        save_json("audit_log.json", [])
    st.success("Demo tenant reset: snapshots and audit log cleared.")

# Billing Status
st.markdown("## Billing")
st.info(f"Plan: {plan_label()}")

# Council Branding
st.markdown("## Council Branding (Optional)")

council_name = st.text_input(
    "Council Name",
    value=st.session_state.get('council_name', 'Example Council'),
    help="Display name for your organisation."
)
st.session_state['council_name'] = council_name

council_colour = st.color_picker(
    "Primary Brand Colour",
    value=st.session_state.get('council_colour', '#0b3d91'),
    help="Used in headers and highlights."
)
st.session_state['council_colour'] = council_colour

# Reserves Policy Configuration
st.markdown("## Reserves Policy (S151 Governance)")
st.markdown("Define your council's reserves policy thresholds for financial resilience monitoring.")

col1, col2, col3 = st.columns(3)

with col1:
    min_reserves = st.slider(
        "Minimum Reserves (%)",
        min_value=0.0,
        max_value=20.0,
        value=st.session_state.get('reserves_policy_min', 5.0),
        step=0.5,
        help="Minimum reserves as % of net revenue budget. Typical range 5-10%."
    )
    st.session_state['reserves_policy_min'] = min_reserves

with col2:
    target_reserves = st.slider(
        "Target Reserves (%)",
        min_value=0.0,
        max_value=30.0,
        value=st.session_state.get('reserves_policy_target', 10.0),
        step=0.5,
        help="Target reserves as % of net revenue budget. Typical range 10-15%."
    )
    st.session_state['reserves_policy_target'] = target_reserves

with col3:
    max_reserves = st.slider(
        "Maximum Reserves (%)",
        min_value=0.0,
        max_value=50.0,
        value=st.session_state.get('reserves_policy_max', 25.0),
        step=1.0,
        help="Maximum reserves as % of net revenue budget. Prevents over-accumulation."
    )
    st.session_state['reserves_policy_max'] = max_reserves

st.info(f"""
**Policy Summary:**
- 🔴 **RED**: Reserves below {min_reserves}% of budget (non-compliant)
- 🟡 **AMBER**: Reserves below target {target_reserves}% (below ideal) or above max {max_reserves}% (over-funded)
- 🟢 **GREEN**: Reserves in target range ({min_reserves}% to {target_reserves}%)
""")

# Currency & Units
st.markdown("## Units & Format")

currency_unit = st.selectbox(
    "Currency Unit",
    options=['£m (millions)', '£k (thousands)', '£'],
    index=0,
    help="Scale for all financial figures in the app."
)
st.session_state['currency_unit'] = currency_unit

decimal_places = st.slider(
    "Decimal Places",
    min_value=0,
    max_value=3,
    value=1,
    help="Number of decimal places in financial outputs."
)
st.session_state['decimal_places'] = decimal_places

# Display Preferences
st.markdown("## Display Preferences")

show_tooltips = st.checkbox(
    "Show help tooltips and info icons",
    value=st.session_state.get('show_tooltips', True)
)
st.session_state['show_tooltips'] = show_tooltips

show_onboarding = st.checkbox(
    "Show welcome banner on Dashboard",
    value=st.session_state.get('show_onboarding', True)
)
st.session_state['show_onboarding'] = show_onboarding

auto_expand_expanders = st.checkbox(
    "Auto-expand collapsible sections",
    value=st.session_state.get('auto_expand_expanders', False),
    help="If enabled, all expanders open by default."
)
st.session_state['auto_expand_expanders'] = auto_expand_expanders

st.markdown("---")

# Export Preferences
st.markdown("## Export & Reporting")

include_methodology = st.checkbox(
    "Include methodology notes in PDF exports",
    value=st.session_state.get('include_methodology', True)
)
st.session_state['include_methodology'] = include_methodology

include_assumptions = st.checkbox(
    "Include all assumptions in PDF",
    value=st.session_state.get('include_assumptions', True)
)
st.session_state['include_assumptions'] = include_assumptions

st.markdown("## Governance Narrative")
risk_appetite_statement = st.text_area(
    "Risk Appetite Statement (PDFs)",
    value=st.session_state.get(
        "risk_appetite_statement",
        "The Council maintains a low-to-moderate risk appetite for recurrent funding gaps "
        "and expects all scenarios to protect minimum reserves thresholds."
    ),
    height=90
)
st.session_state["risk_appetite_statement"] = risk_appetite_statement

management_summary = st.text_area(
    "Management Summary (PDFs)",
    value=st.session_state.get(
        "management_summary",
        "This report provides a clear, decision-ready view of the medium-term funding gap, "
        "reserves trajectory, and actions required to maintain financial sustainability."
    ),
    height=110
)
st.session_state["management_summary"] = management_summary

st.markdown("---")

if st.button("✅ Save All Settings"):
    audit = get_audit_log()
    # Log reserves policy changes
    audit.log_entry(
        action='settings_change',
        user='system',
        key='reserves_policy',
        new_value=f"min={min_reserves}%, target={target_reserves}%, max={max_reserves}%",
        notes='Reserves policy thresholds updated via Settings page'
    )
    st.success("Settings saved to your session. These preferences will persist during your session.")

st.markdown("---")

st.markdown("## About")
st.markdown("""
**MTFS Budget Gap Simulator** v1.0

A decision-support tool for Section 151 Officers and Corporate Leadership Teams.

Built with Streamlit, Pandas, Plotly, and ReportLab.

For support or feedback, contact your ICT/Finance team.
""")
