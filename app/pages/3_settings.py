"""
Settings & Theme Customization
User preferences for the MTFS Budget Gap Simulator
"""

import streamlit as st

st.title("⚙️ Settings & Preferences")

st.markdown("Customize your experience with the MTFS Budget Gap Simulator.")

# Theme Selection
st.markdown("## Theme")
theme = st.radio(
    "Select display theme:",
    options=['Light', 'Dark', 'Print-Friendly'],
    help="Light = default; Dark = easier on eyes; Print-Friendly = optimized for PDF export."
)
st.session_state['theme'] = theme

if theme == 'Dark':
    st.info("🌙 Dark theme enabled. Charts and text optimized for low-light viewing.")
elif theme == 'Print-Friendly':
    st.info("🖨️ Print-Friendly theme enabled. High contrast, no background colors.")

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

st.markdown("---")

if st.button("✅ Save All Settings"):
    st.success("Settings saved to your session. These preferences will persist during your session.")

st.markdown("---")

st.markdown("## About")
st.markdown("""
**MTFS Budget Gap Simulator** v1.0

A decision-support tool for Section 151 Officers and Corporate Leadership Teams.

Built with Streamlit, Pandas, Plotly, and ReportLab.

For support or feedback, contact your ICT/Finance team.
""")
