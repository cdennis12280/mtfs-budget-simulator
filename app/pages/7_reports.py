"""
Multi-Scenario Statutory Report Generator Page
Generate professional, audit-ready MTFS reports with governance-grade formatting
"""

import streamlit as st
import tempfile
import os
from datetime import datetime
from pathlib import Path

# Add modules to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'modules'))

from calculation import project_mtfs
from scenarios import get_saved_scenarios, load_scenario_params
from report import generate_mtfs_statutory_report
from audit_log import get_audit_log
from reserves_policy import ReservesPolicy, ReservesPolicyChecker

st.set_page_config(page_title="Reports - MTFS Simulator", layout="wide")

# ===== HEADER =====
st.markdown("### 📊 STATUTORY REPORT GENERATOR")
st.markdown("Generate professional, audit-ready MTFS reports with multi-scenario comparisons and governance notes.")

# ===== SAFETY CHECKS =====
if 'projection_df' not in st.session_state or st.session_state.projection_df.empty:
    st.info("📌 Run the **Main Dashboard** first to generate forecast data.")
    st.stop()

# ===== LOAD SESSION STATE =====
base_budget = st.session_state.get('base_budget', 250)
base_closure = st.session_state.get('base_closure', 0)
projection_df = st.session_state.projection_df
kpis = st.session_state.kpis
council_name = st.session_state.get('council_name', 'Example Council')
base_case_rag = st.session_state.get('rag_rating', 'AMBER')

# ===== REPORT CONFIGURATION =====
st.markdown("#### Report Configuration")

col1, col2 = st.columns(2)

with col1:
    report_title = st.text_input("Report Title", value="Multi-Year Financial Strategy (MTFS) 2024-2029")
    report_date = st.date_input("Report Date", value=datetime.now())
    council_name = st.text_input("Council Name", value=council_name)

with col2:
    st.markdown("")  # spacing
    st.markdown("")
    include_reserves_policy = st.checkbox("Include Reserves Policy Compliance Section", value=True)
    include_assumptions = st.checkbox("Include Detailed Assumptions", value=True)

# ===== SCENARIO SELECTION =====
st.markdown("#### Scenarios to Include")

# Get base case and saved scenarios
saved_scenarios = get_saved_scenarios()
scenario_names = ['Base Case'] + list(saved_scenarios.keys())

# Multi-select for scenarios
selected_scenarios = st.multiselect(
    "Select scenarios to include in report:",
    scenario_names,
    default=['Base Case'],
    help="The Base Case will always be included. Select any saved scenarios here."
)

if 'Base Case' not in selected_scenarios:
    selected_scenarios = ['Base Case'] + selected_scenarios

# ===== BUILD SCENARIOS DATA =====
scenarios_data = {}

# Base case
scenarios_data['Base Case'] = {
    'projection': projection_df,
    'kpis': kpis,
    'rag': base_case_rag
}

# Additional scenarios
for scenario_name in selected_scenarios[1:]:
    if scenario_name in saved_scenarios:
        scenario_params = saved_scenarios[scenario_name]
        try:
            # Recall the scenario assumptions
            scenario_projection = project_mtfs(
                initial_budget=base_budget,
                **{k: v for k, v in scenario_params.items() if k not in ['name', 'timestamp']}
            )
            
            # Calculate KPIs for scenario
            scenario_total_gap = max(0, scenario_projection['Budget_Gap'].sum())
            scenario_closing_reserves = scenario_projection.iloc[-1]['Closing_Reserves']
            scenario_savings_pct = (scenario_total_gap / base_budget) * 100
            
            # Simple RAG for scenario
            if scenario_total_gap > (base_budget * 0.05):
                scenario_rag = 'RED'
            elif scenario_total_gap > (base_budget * 0.02):
                scenario_rag = 'AMBER'
            else:
                scenario_rag = 'GREEN'
            
            scenarios_data[scenario_name] = {
                'projection': scenario_projection,
                'kpis': {
                    'total_4_year_gap': scenario_total_gap,
                    'savings_required_pct': scenario_savings_pct,
                    'closing_reserves': scenario_closing_reserves
                },
                'rag': scenario_rag
            }
        except Exception as e:
            st.warning(f"⚠️ Could not load scenario '{scenario_name}': {e}")

# ===== PREVIEW REPORT DATA =====
st.markdown("#### Report Preview")

preview_col1, preview_col2, preview_col3 = st.columns(3)

with preview_col1:
    st.metric("Scenarios to Include", len(scenarios_data))

with preview_col2:
    base_kpis = scenarios_data['Base Case']['kpis']
    st.metric("Base Case Gap", f"£{base_kpis.get('total_4_year_gap', 0):.1f}m")

with preview_col3:
    st.metric("Closing Reserves (Y5)", f"£{scenarios_data['Base Case']['projection'].iloc[-1]['Closing_Reserves']:.1f}m")

# Show scenario details table
st.markdown("**Scenario Details**")
scenario_summary = []
for s_name, s_data in scenarios_data.items():
    scenario_summary.append({
        'Scenario': s_name,
        'Gap (£m)': f"{s_data['kpis'].get('total_4_year_gap', 0):.1f}",
        'RAG': s_data['rag'],
        'Closing Reserves': f"£{s_data['projection'].iloc[-1]['Closing_Reserves']:.1f}m"
    })

st.dataframe(scenario_summary, use_container_width=True, hide_index=True)

# ===== GENERATE REPORT BUTTON =====
st.markdown("#### Generate Report")

col1, col2 = st.columns([3, 1])

with col1:
    generate_btn = st.button("📄 Generate Statutory Report", use_container_width=True, type="primary")

with col2:
    st.markdown("")  # spacing

if generate_btn:
    try:
        with st.spinner("📝 Generating statutory report..."):
            # Create temp file for PDF
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"MTFS_Report_{timestamp}.pdf"
            output_path = os.path.join(temp_dir, pdf_filename)
            
            # Load reserves policy if needed
            reserves_policy = None
            if include_reserves_policy:
                min_pct = st.session_state.get('min_reserves_pct', 5)
                target_pct = st.session_state.get('target_reserves_pct', 10)
                max_pct = st.session_state.get('max_reserves_pct', 25)
                reserves_policy = ReservesPolicy(
                    min_pct=min_pct,
                    target_pct=target_pct,
                    max_pct=max_pct,
                    policy_name="Standard S151 Thresholds"
                )
            
            # Generate PDF
            pdf_path = generate_mtfs_statutory_report(
                output_path=output_path,
                council_name=council_name,
                report_date=str(report_date),
                scenarios_data=scenarios_data,
                base_budget=base_budget,
                reserves_policy=reserves_policy
            )
            
            # Log export to audit trail
            audit_log = get_audit_log()
            scenario_names_summary = ", ".join(list(scenarios_data.keys())[:3])
            if len(scenarios_data) > 3:
                scenario_names_summary += f" +{len(scenarios_data)-3} more"
            
            audit_log.log_entry(
                action='statutory_report_export',
                user=st.session_state.get('user', 'Anonymous'),
                key='report_type',
                old_value=None,
                new_value='Multi-Scenario Statutory Report',
                notes=f"Generated statutory report with scenarios: {scenario_names_summary}; Includes reserves policy: {include_reserves_policy}"
            )
            
            # Read PDF and offer download
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            st.success("✅ Report generated successfully!")
            
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )
            
            # Show file info
            file_size_kb = len(pdf_bytes) / 1024
            st.info(f"📋 Report File: {pdf_filename} | Size: {file_size_kb:.1f} KB")
            
            # Cleanup
            try:
                os.remove(pdf_path)
            except:
                pass
            
    except Exception as e:
        st.error(f"❌ Failed to generate report: {e}")
        import traceback
        st.code(traceback.format_exc(), language='python')

# ===== REPORT GUIDANCE =====
st.markdown("---")
st.markdown("#### 📖 Report Contents")

with st.expander("Report Structure & Contents", expanded=False):
    st.markdown("""
    **Page 1: Cover Page**
    - Report title and date
    - Statutory disclaimer
    - Compliance statement (Local Government Act 1992, CIPFA Code, etc.)
    
    **Page 2: Executive Summary**
    - Headline financial position
    - Key findings and metrics
    - Scenario overview
    - Strategic recommendations
    
    **Page 3: Scenario Comparison Table**
    - Side-by-side comparison of all scenarios
    - 4-year cumulative gap, savings %, reserves, RAG rating
    
    **Page 4: Key Assumptions**
    - Funding assumptions (Council Tax, Business Rates, Grants, Fees)
    - Expenditure assumptions (Pay, Inflation, Demand growth)
    - Policy decisions and strategy notes
    
    **Page 5: Reserves Policy Compliance** (if enabled)
    - Policy thresholds (min, target, max)
    - Compliance with current policy
    - Year-by-year forecast vs. thresholds
    
    **Page 6: Methodology & Governance**
    - Financial modeling approach
    - RAG rating definitions
    - Statutory compliance statement
    
    **Page 7: Sign-Off & Approval**
    - Section 151 Officer sign-off box
    - External Auditor review checklist
    - Document classification
    
    **Features:**
    - ✅ Professional governance-grade formatting
    - ✅ Multi-scenario comparison
    - ✅ Reserves policy alignment
    - ✅ Statutory compliance disclaimers
    - ✅ Auditor sign-off page
    - ✅ Audit trail logged
    """)

with st.expander("Using the Report for Governance", expanded=False):
    st.markdown("""
    **Cabinet/Council Agendas:**
    - Share this report with elected members to support budget-setting decisions
    - The multi-scenario view helps illustrate risks and opportunities
    
    **External Audit:**
    - Share with your external auditors as evidence of MTFS planning
    - The statutory disclaimers and methodology notes support audit compliance
    - The sign-off page provides audit milestones
    
    **Strategic Planning:**
    - Use scenario comparisons to stress-test key assumptions
    - The reserves policy section demonstrates compliance with statutory duties
    - Revisit and re-run quarterly or when major assumptions change
    
    **Performance Reporting:**
    - Track actual outturn against the Base Case projection
    - Identify which key assumptions proved accurate/inaccurate
    - Update strategy mid-year if significant variances emerge
    """)

st.markdown("---")
st.markdown("""
**💡 Tip:** Save this report and compare it against in-year management accounts to track forecast accuracy.
For auditor reviews, print and bind with a cover sheet noting the Council's consideration date.
""")
