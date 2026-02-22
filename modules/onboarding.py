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
        st.info("""
        **👋 Welcome to MTFS Budget Gap Simulator!**
        
        This tool helps Section 151 Officers and Leadership Teams model medium-term budget scenarios and test financial resilience.
        
        **Quick Start:** 1) Review assumptions in the sidebar, 2) Explore the dashboard charts, 3) Try scenarios via the buttons, 
        4) Use `Inputs` page to customize your council's data, 5) Check `Commercial` for investment appraisals.
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
