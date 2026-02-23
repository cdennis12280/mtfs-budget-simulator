"""
Onboarding & Guided Walkthrough
First-visit experience for new users
"""

import streamlit as st

def show_first_visit_banner():
    """Show a banner on first visit offering a guided walkthrough."""
    if st.session_state.get('onboarding_dismissed', False):
        return
    
    col1, col2 = st.columns([10, 1])
    with col1:
        role = st.session_state.get("auth_role", "User")
        role_hint = {
            "Admin": "As Admin, you can set policy thresholds, manage inputs, and export governance reports.",
            "Analyst": "As Analyst, focus on assumptions, sensitivities, and scenario evidence for leadership.",
            "Read-only": "Read-only mode: review dashboards, reports, and evidence without changing assumptions.",
        }.get(role, "Use the dashboard to review the current MTFS position.")
        setup_pending = not st.session_state.get("profile_setup_complete", False)
        setup_line = (
            "Complete the Council Profile setup before presenting to leadership."
            if setup_pending
            else "Council Profile setup is complete."
        )
        st.info("""
        **👋 Welcome to MTFS Budget Gap Simulator!**
        
        This tool helps Section 151 Officers and Leadership Teams model medium-term budget scenarios and test financial resilience.
        
        **First-run checklist:**
        - Review baseline data in `Inputs`
        - Confirm reserves policy in `Settings`
        - Adjust assumptions in the dashboard sidebar
        - Save a governance snapshot
        - Export a statutory PDF from `Reports`
        
        **Role guidance:** {role_hint}
        
        **Setup status:** {setup_line}
        **Open setup wizard:** `/council_profile`
        """)
    with col2:
        if st.button('✕', help="Dismiss this banner"):
            st.session_state['onboarding_dismissed'] = True
            st.rerun()

def show_calculation_flow():
    """Render a simple text-based calculation flow diagram."""
    st.markdown("""
    ### How the Model Works
    
    ```
    Base Data (Inputs page)
         ↓
    Funding Projections (apply growth rates)
    + Expenditure Pressures (pay, inflation, demand)
         ↓
    Annual Budget Gap = Expenditure − Funding
         ↓
    Use Reserves? → either Drawdown or Service Cuts
         ↓
    Final Reserves Position → RAG Rating→ RED / AMBER / GREEN
    ```
    
    **Each scenario adjusts parameters → recalculates → updates all charts in real-time.**
    """)

def show_key_terms():
    """Display a modal-style key terms glossary."""
    with st.expander("📖 Key Terms & Definitions"):
        st.markdown("""
        - **MTFS**: Multi-Year Financial Strategy (typically 4–5 years).
        - **Budget Gap**: Annual shortfall between planned expenditure and available funding.
        - **Reserves**: Unspent funds from prior years (financial buffer).
        - **Council Tax**: Local property tax levied by councils (main revenue source).
        - **Business Rates**: Tax on business properties (shared with government).
        - **Core Grants**: Government funding (declining trend in recent years).
        - **RAG Rating**: Red (unsustainable) / Amber (at-risk) / Green (sustainable).
        - **Savings Programme**: Planned cost reductions to close the gap.
        - **Commercial Income**: Revenue from business ventures, investments, or partnerships.
        """)

def render_onboarding_help():
    """Render a help panel for the current page."""
    with st.sidebar:
        st.markdown("---")
        if st.button("❓ Help & Tutorial"):
            st.session_state['show_help'] = not st.session_state.get('show_help', False)
        
        if st.session_state.get('show_help', False):
            st.markdown("### Tips for This Page")
            st.markdown("""
            - **Adjust sliders** to test different scenarios in real-time.
            - **Save scenarios** to compare them later.
            - **Export PDF** for reporting and external distribution.
            - **Hover over charts** for drill-down data.
            """)
