"""
Commercial tools page (multipage)
CSV uploader + paged detailed view for commercial projects
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import io
import json
import sys

# ensure modules path
sys.path.insert(0, str(Path(__file__).parents[2] / 'modules'))
from commercial import CommercialProject
from rag_rating import RAGRating
from pwlb import get_latest_pwlb_rate
from ui import apply_theme, page_header
from auth import require_auth, require_roles, auth_sidebar

st.set_page_config(page_title="Commercial Tools", layout="wide")

apply_theme()
if not require_auth():
    st.stop()
require_roles({"Admin", "Analyst", "Read-only"})
auth_sidebar()
read_only = st.session_state.get("auth_role") == "Read-only"
if read_only:
    st.info("Read-only mode: inputs are disabled.")
page_header(
    "Commercial Projects - Portfolio Analysis",
    "Upload a CSV or use the sample portfolio. Expected columns: name, capital_cost, annual_income_target, life_years, operating_costs, capital_receipt."
)
st.markdown("""
<div class="app-callout">
  Use this page to test PWLB assumptions and see commercial RAG ratings before committing capital.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2,1])
with col2:
    st.download_button(
        'Download sample CSV',
        data='name,capital_cost,annual_income_target,life_years,operating_costs,capital_receipt\nProperty A,30,2,40,0.2,0\nDistrict Energy,20,1.6,30,0.1,0\nTransformation,10,0.5,10,0.05,2',
        file_name='sample_commercial.csv'
    )

auto_pwlb = get_latest_pwlb_rate()
st.write(f"Auto PWLB rate: {auto_pwlb if auto_pwlb is not None else 'N/A'}% (refreshable)")
if st.button('Refresh PWLB Rate', disabled=read_only):
    auto_pwlb = get_latest_pwlb_rate()
    st.write(f"Refreshed PWLB rate: {auto_pwlb if auto_pwlb is not None else 'N/A'}%")

upload = st.file_uploader('Upload commercial projects CSV', type=['csv'], disabled=read_only)

if upload is not None:
    try:
        df = pd.read_csv(upload)
    except Exception as e:
        st.error('Could not read CSV: '+str(e))
        st.stop()
else:
    # default sample
    df = pd.DataFrame([
        {'name':'Commercial Property A','capital_cost':30.0,'annual_income_target':2.0,'life_years':40,'operating_costs':0.2,'capital_receipt':0.0},
        {'name':'District Energy Scheme','capital_cost':20.0,'annual_income_target':1.6,'life_years':30,'operating_costs':0.1,'capital_receipt':0.0},
        {'name':'Service Transformation','capital_cost':10.0,'annual_income_target':0.5,'life_years':10,'operating_costs':0.05,'capital_receipt':2.0},
    ])

# Simple pagination
page_size = st.selectbox('Rows per page', [5,10,20], index=0, disabled=read_only)
total = len(df)
pages = (total + page_size - 1) // page_size
page = st.number_input('Page', min_value=1, max_value=max(1,pages), value=1, disabled=read_only)
start = (page-1)*page_size
end = start + page_size

st.markdown(f"Showing {start+1}-{min(end,total)} of {total} projects")
st.dataframe(df.iloc[start:end].reset_index(drop=True))

st.markdown('---')
st.header('Project Details')
for idx, row in df.iterrows():
    if idx < start or idx >= end:
        continue
    with st.expander(f"{row['name']} (capital £{row['capital_cost']}m)"):
        proj = CommercialProject(
            name=row['name'],
            capital_cost=float(row.get('capital_cost',0.0)),
            annual_income_target=float(row.get('annual_income_target',0.0)),
            life_years=int(row.get('life_years',25)),
            operating_costs=float(row.get('operating_costs',0.0)),
            capital_receipt=float(row.get('capital_receipt',0.0)),
        )
        pwlb_default = auto_pwlb if auto_pwlb is not None else 4.5
        pwlb = st.number_input(
            f'PWLB rate for {proj.name} (%)',
            value=float(pwlb_default),
            key=f'pwlb_{idx}',
            disabled=read_only
        )
        real = st.slider(
            f'Income realisation % ({proj.name})',
            50,
            100,
            80,
            key=f'realproj_{idx}',
            disabled=read_only
        )
        summary = proj.net_return(real, pwlb)
        st.write(f"Projected income: £{summary['income']:.2f}m")
        st.write(f"Annual debt service: £{summary['debt_service']:.2f}m")
        st.write(f"Operating costs: £{summary['operating_costs']:.2f}m")
        st.write(f"Net return: £{summary['net_return']:.2f}m — ROI {summary['roi_pct']:.2f}% — Spread {summary['spread_pct']:.2f}%")
        rag, reason = RAGRating.commercial_rag(proj, base_budget=st.session_state.get('base_budget', 250.0), pwlb_rate_pct=pwlb)
        st.markdown(f"**RAG:** {rag} — {reason}")

    # build export rows
rows = []
for _, r in df.iterrows():
    p = CommercialProject(name=r['name'], capital_cost=float(r.get('capital_cost',0)), annual_income_target=float(r.get('annual_income_target',0)), life_years=int(r.get('life_years',25)), operating_costs=float(r.get('operating_costs',0)), capital_receipt=float(r.get('capital_receipt',0)))
    # default analysis at 80% realisation using auto pwlb if present
    pw = auto_pwlb if auto_pwlb is not None else 4.5
    summ = p.net_return(80, pw)
    rag, reason = RAGRating.commercial_rag(p, base_budget=st.session_state.get('base_budget',250.0), pwlb_rate_pct=pw)
    rows.append({
        'name': p.name,
        'capital_cost': p.capital_cost,
        'annual_income_80pct': summ['income'],
        'debt_service': summ['debt_service'],
        'net_return_80pct': summ['net_return'],
        'roi_pct': summ['roi_pct'],
        'spread_pct': summ['spread_pct'],
        'RAG': rag,
        'RAG_reason': reason,
    })

export_df = pd.DataFrame(rows)
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button('Export portfolio RAG CSV', data=csv, file_name='commercial_portfolio_rag.csv', mime='text/csv')
