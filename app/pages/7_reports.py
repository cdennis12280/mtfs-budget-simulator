"""
Multi-Scenario Statutory Report Generator Page
Generate professional, audit-ready MTFS reports with governance-grade formatting
"""

import streamlit as st
import tempfile
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add modules to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'modules'))

from scenarios import Scenarios
from report import generate_mtfs_statutory_report
from export_bi import generate_excel_export, generate_power_bi_template
from audit_log import get_audit_log
from reserves_policy import ReservesPolicy, ReservesPolicyChecker
from calculations import MTFSCalculator
from sensitivity import SensitivityAnalysis
from risk_advisor import load_risk_register, merge_sensitivity, build_stress_table, SUGGESTED_ACTIONS
from ui import apply_theme, page_header

st.set_page_config(page_title="Reports - MTFS Simulator", layout="wide")

# ===== HEADER =====
apply_theme()
page_header("Statutory Report Generator", "Generate audit-ready MTFS reports and data packs.")
st.markdown("""
<div class="app-callout">
  Include reserves policy and risk summary sections to strengthen governance evidence.
</div>
""", unsafe_allow_html=True)

def get_base_data():
    if 'base_data' in st.session_state:
        return st.session_state['base_data'].copy()
    return pd.read_csv(Path(__file__).parent.parent.parent / 'data' / 'base_financials.csv')

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
    include_risk_advisor = st.checkbox("Include Risk & Sensitivity Advisor Summary", value=True)

# ===== SCENARIO SELECTION =====
st.markdown("#### Scenarios to Include")

# Get base case and saved scenarios (session only)
saved_scenarios = {s['name']: s['params'] for s in st.session_state.get('saved_scenarios', [])}
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
            calc = MTFSCalculator(get_base_data())
            valid_params = {
                'council_tax_increase_pct', 'business_rates_growth_pct', 'grant_change_pct',
                'fees_charges_growth_pct', 'pay_award_pct', 'general_inflation_pct',
                'asc_demand_growth_pct', 'csc_demand_growth_pct', 'annual_savings_target_pct',
                'use_of_reserves_pct', 'protect_social_care'
            }
            filtered_params = {k: v for k, v in scenario_params.items() if k in valid_params}
            scenario_projection = calc.project_mtfs(**filtered_params)
            
            # Calculate KPIs for scenario
            scenario_total_gap = max(0, scenario_projection['Annual_Budget_Gap'].sum())
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

# ===== RISK ADVISOR PREVIEW =====
st.markdown("#### Risk & Sensitivity Advisor Preview")
st.markdown("Top risks ranked by weighted impact (risk score × gap impact).")

risk_preview = None
risk_register_export = None
stress_plan_export = None
try:
    base_data = get_base_data()
    base_budget_year1 = base_data[base_data['Year'] == 'Year_1']['Net_Revenue_Budget'].values[0]

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
    sens = SensitivityAnalysis(calc, base_data, base_budget_year1)
    sensitivity_df = sens.tornado_analysis(base_params, perturbation_pct=10.0)

    risk_path = Path(__file__).parent.parent.parent / 'data' / 'risk_register.csv'
    risk_df = load_risk_register(risk_path)
    risk_df = merge_sensitivity(risk_df, sensitivity_df)

    stress_df = build_stress_table(calc, base_params, risk_df)
    if not stress_df.empty:
        risk_register_export = risk_df
        stress_plan_export = stress_df
        risk_preview = stress_df.head(3).copy()
        risk_preview['Recommended Action'] = risk_preview['Driver Param'].map(
            lambda p: SUGGESTED_ACTIONS.get(p, "Review mitigation and contingency options.")
        )
except Exception:
    risk_preview = None

if risk_preview is None or risk_preview.empty:
    st.info("Risk advisor preview unavailable. Generate forecasts first or check risk register.")
else:
    st.dataframe(
        risk_preview[[
            'Risk ID', 'Risk', 'Driver', 'Stress %', 'Gap Delta (£m)', 'Weighted Impact', 'Recommended Action'
        ]].style.format({
            'Gap Delta (£m)': '{:.2f}',
            'Weighted Impact': '{:.2f}',
        }),
        use_container_width=True
    )

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
            risk_summary = None
            if include_risk_advisor:
                base_data = get_base_data()
                base_budget_year1 = base_data[base_data['Year'] == 'Year_1']['Net_Revenue_Budget'].values[0]

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
                sens = SensitivityAnalysis(calc, base_data, base_budget_year1)
                sensitivity_df = sens.tornado_analysis(base_params, perturbation_pct=10.0)

                risk_path = Path(__file__).parent.parent.parent / 'data' / 'risk_register.csv'
                risk_df = load_risk_register(risk_path)
                risk_df = merge_sensitivity(risk_df, sensitivity_df)

                stress_df = build_stress_table(calc, base_params, risk_df)
                if not stress_df.empty:
                    top_df = stress_df.head(3)
                    risk_summary = []
                    for _, row in top_df.iterrows():
                        action_text = SUGGESTED_ACTIONS.get(
                            row.get('Driver Param', ''),
                            "Review mitigation and contingency options."
                        )
                        risk_summary.append({
                            'risk_title': row.get('Risk', ''),
                            'driver': row.get('Driver', ''),
                            'stress_pct': row.get('Stress %', 0),
                            'gap_delta': row.get('Gap Delta (£m)', 0),
                            'weighted_impact': row.get('Weighted Impact', 0),
                            'recommended_action': action_text,
                        })

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
                reserves_policy=reserves_policy,
                risk_summary=risk_summary
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

# ===== EXCEL/BI EXPORT SECTION =====
st.markdown("---")
st.markdown("#### 📊 DATA EXPORT FOR ANALYSIS & DASHBOARDS")
st.markdown("Export scenario data to Excel for detailed analysis, BI integration, or sharing with stakeholders.")

export_col1, export_col2 = st.columns(2)

with export_col1:
    st.markdown("**Excel Export**")
    st.markdown("""
    Multi-worksheet Excel file with:
    - Metadata & council info
    - Executive summary (scenario comparison)
    - Individual scenario time series
    - Cross-scenario analysis
    - Key financial metrics
    
    **Perfect for:**
    - Sharing with finance teams for detailed review
    - Data analysis in Excel or Python/R
    - Archiving alongside the statutory PDF
    """)
    
    excel_export_btn = st.button("📁 Export to Excel", key="excel_export_btn", use_container_width=True)
    
    if excel_export_btn:
        try:
            with st.spinner("📝 Generating Excel export..."):
                temp_dir = tempfile.gettempdir()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                excel_filename = f"MTFS_Scenarios_{timestamp}.xlsx"
                output_path = os.path.join(temp_dir, excel_filename)
                
                # Generate Excel
                excel_path = generate_excel_export(
                    output_path=output_path,
                    scenarios_data=scenarios_data,
                    council_name=council_name,
                    base_budget=base_budget,
                    risk_register_df=risk_register_export,
                    stress_plan_df=stress_plan_export
                )
                
                # Log export to audit trail
                audit_log = get_audit_log()
                scenario_names_summary = ", ".join(list(scenarios_data.keys())[:3])
                if len(scenarios_data) > 3:
                    scenario_names_summary += f" +{len(scenarios_data)-3} more"
                
                audit_log.log_entry(
                    action='excel_data_export',
                    user=st.session_state.get('user', 'Anonymous'),
                    key='export_type',
                    old_value=None,
                    new_value='Multi-Scenario Excel Export',
                    notes=f"Exported {len(scenarios_data)} scenarios to Excel with {len(scenarios_data.get('Base Case', {}).get('projection', pd.DataFrame()))} rows per scenario"
                )
                
                # Read and offer download
                with open(excel_path, 'rb') as f:
                    excel_bytes = f.read()
                
                st.success("✅ Excel export ready!")
                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_bytes,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                file_size_kb = len(excel_bytes) / 1024
                st.caption(f"📊 File: {excel_filename} | Size: {file_size_kb:.1f} KB")
                
                # Cleanup
                try:
                    os.remove(excel_path)
                except:
                    pass
                
        except Exception as e:
            st.error(f"❌ Failed to generate Excel export: {e}")

with export_col2:
    st.markdown("**Power BI Template**")
    st.markdown("""
    JSON configuration template for Power BI:
    - Sheet mapping & relationships
    - Recommended visuals & charts
    - DAX measure suggestions
    - Deployment guide
    
    **Perfect for:**
    - Setting up BI dashboards
    - Creating executive dashboards
    - Integrating with BI infrastructure
    - Sharing interactive views with leadership
    """)
    
    powerbi_export_btn = st.button("📊 Generate Power BI Template", key="powerbi_export_btn", use_container_width=True)
    
    if powerbi_export_btn:
        try:
            with st.spinner("📝 Generating Power BI template..."):
                temp_dir = tempfile.gettempdir()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pbi_filename = f"MTFS_PowerBI_Template_{timestamp}.json"
                output_path = os.path.join(temp_dir, pbi_filename)
                
                # Generate template
                pbi_path = generate_power_bi_template(
                    output_path=output_path,
                    council_name=council_name
                )
                
                # Log export to audit trail
                audit_log = get_audit_log()
                audit_log.log_entry(
                    action='power_bi_template_export',
                    user=st.session_state.get('user', 'Anonymous'),
                    key='export_type',
                    old_value=None,
                    new_value='Power BI Configuration Template',
                    notes=f"Generated Power BI template for {council_name} with {len(scenarios_data)} scenarios"
                )
                
                # Read and offer download
                with open(pbi_path, 'rb') as f:
                    pbi_bytes = f.read()
                
                st.success("✅ Power BI template ready!")
                st.download_button(
                    label="📥 Download JSON Template",
                    data=pbi_bytes,
                    file_name=pbi_filename,
                    mime="application/json",
                    use_container_width=True
                )
                
                file_size_kb = len(pbi_bytes) / 1024
                st.caption(f"⚙️ File: {pbi_filename} | Size: {file_size_kb:.1f} KB")
                
                # Cleanup
                try:
                    os.remove(pbi_path)
                except:
                    pass
                
        except Exception as e:
            st.error(f"❌ Failed to generate Power BI template: {e}")

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

with st.expander("Excel Export & Power BI Integration", expanded=False):
    st.markdown("""
    **Excel Export Features:**
    - **Metadata Sheet**: Export date, council name, baseline budget, scenarios included
    - **Executive Summary**: High-level comparison of all scenarios (gap, reserves, RAG rating)
    - **Time Series Comparison**: Year-by-year data across all scenarios for detailed analysis
    - **Key Metrics**: Summary financial KPIs by scenario for dashboard creation
    - **Individual Scenario Sheets**: Full projection data for each scenario (for detailed review)
    
    **Recommended Uses:**
    - Share with finance and strategic teams for deeper analysis
    - Create custom pivot tables and charts in Excel
    - Import into Python/R for statistical analysis and scenario weighting
    - Archive alongside statutory PDF for audit compliance
    - Track assumption changes over time (compare exports from different dates)
    
    **Power BI Template:**
    The JSON template includes:
    - **Sheet Mapping**: References to all Excel sheets and their purpose
    - **Data Relationships**: How to link scenarios to time series and metrics
    - **Recommended Visuals**: Pre-designed charts (Gap Trend, Reserves Comparison, etc.)
    - **DAX Measures**: Suggested calculations (Average Gap, Total Reserves, etc.)
    - **Deployment Guide**: Step-by-step instructions for setting up the dashboard
    
    **Setting Up Power BI Dashboard:**
    1. Export the Excel file from this page
    2. Download the Power BI template JSON
    3. Open Power BI Desktop
    4. Create a new report and load the Excel file
    5. Follow the template guide to create sheets, relationships, and visuals
    6. Use the recommended DAX measures for calculations
    7. Publish to Power BI Service for sharing with stakeholders
    8. Set up scheduled refresh if Excel is stored in OneDrive or SharePoint
    
    **BI Best Practices:**
    - Use slicers to filter by scenario, year, or department
    - Color-code RAG ratings for quick visual scanning
    - Create drill-down pages for detailed scenario analysis
    - Add KPI cards showing key metrics (total gap, reserves, savings needed)
    - Track forecast accuracy by comparing actuals against Base Case projection
    - Use Power BI alerts to notify stakeholders when reserves fall below policy threshold
    """)

st.markdown("---")
st.markdown("""
**💡 Tip:** Save this report and compare it against in-year management accounts to track forecast accuracy.
For auditor reviews, print and bind with a cover sheet noting the Council's consideration date.

**Data Export Tip:** Export Excel and Power BI template together. Use Excel for detailed analysis and archiving; 
use Power BI dashboard for governance meetings and executive updates.
""")
