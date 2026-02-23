import streamlit as st
import pandas as pd
from pathlib import Path
import sys

modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from ui import apply_theme, page_header
from auth import require_auth, require_roles, auth_sidebar

apply_theme()
if not require_auth():
    st.stop()
require_roles({"Admin", "Analyst", "Read-only"})
auth_sidebar()
read_only = st.session_state.get("auth_role") == "Read-only"
if read_only:
    st.info("Read-only mode: input editing is disabled.")
page_header(
    "Inputs - Budget and Line Items",
    "Upload or edit the authoritative inputs for the MTFS model."
)
st.markdown("""
<div class="app-callout">
  <b>Session-only:</b> Use the table to bulk-edit inputs, then click
  <code>Apply to model</code> to update calculations for this session. Export CSV to retain changes.
</div>
""", unsafe_allow_html=True)

upload = st.file_uploader(
    'Upload Inputs CSV (columns: name,type,year,amount,department,notes)',
    type=['csv'],
    disabled=read_only
)

def make_default_df():
    return pd.DataFrame([
        {'name': 'Base Net Revenue', 'type': 'budget', 'year': 'Year_1', 'amount': 250.0, 'department': 'Corporate', 'notes': ''},
        {'name': 'Adult Social Care', 'type': 'expenditure', 'year': 'Year_1', 'amount': 60.0, 'department': 'Adult Social Care', 'notes': ''},
        {'name': 'Children Social Care', 'type': 'expenditure', 'year': 'Year_1', 'amount': 40.0, 'department': 'Children Social Care', 'notes': ''},
        {'name': 'Capital Programme Sample', 'type': 'capital', 'year': 'Year_1', 'amount': 30.0, 'department': 'Capital', 'notes': 'Example project'},
    ])

if upload is not None:
    try:
        df = pd.read_csv(upload)
        st.session_state['inputs_df'] = df
        st.success('Inputs CSV loaded')
    except Exception as e:
        st.error('Could not read CSV: ' + str(e))

# Prefill from base_financials.csv when no upload and not already set
if 'inputs_df' not in st.session_state and upload is None:
    try:
        demo_mode = st.session_state.get("demo_mode", False)
        filename = 'demo_financials.csv' if demo_mode else 'base_financials.csv'
        data_path = Path(__file__).parent.parent / 'data' / filename
        if data_path.exists():
            base = pd.read_csv(data_path)
            y1 = base[base['Year'] == 'Year_1'].iloc[0]
            rows = [
                {'name': 'Base Net Revenue', 'type': 'budget', 'year': 'Year_1', 'amount': float(y1.get('Net_Revenue_Budget', 0.0)), 'department': 'Corporate', 'notes': 'prefill from base_financials.csv'},
                {'name': 'Council Tax Income', 'type': 'budget', 'year': 'Year_1', 'amount': float(y1.get('Council_Tax_Income', 0.0)), 'department': 'Corporate', 'notes': ''},
                {'name': 'Business Rates Income', 'type': 'budget', 'year': 'Year_1', 'amount': float(y1.get('Business_Rates_Income', 0.0)), 'department': 'Corporate', 'notes': ''},
                {'name': 'Core Grants', 'type': 'budget', 'year': 'Year_1', 'amount': float(y1.get('Core_Grants', 0.0)), 'department': 'Corporate', 'notes': ''},
                {'name': 'Fees And Charges', 'type': 'budget', 'year': 'Year_1', 'amount': float(y1.get('Fees_And_Charges', 0.0)), 'department': 'Corporate', 'notes': ''},
                {'name': 'Service Expenditure', 'type': 'expenditure', 'year': 'Year_1', 'amount': float(y1.get('Service_Expenditure', 0.0)), 'department': 'All Services', 'notes': ''},
                {'name': 'Opening Reserves', 'type': 'budget', 'year': 'Year_1', 'amount': float(y1.get('Opening_Reserves', 0.0)), 'department': 'Corporate', 'notes': ''},
                {'name': 'Adult Social Care', 'type': 'expenditure', 'year': 'Year_1', 'amount': float(y1.get('Demand_Base_ASC', 0.0)), 'department': 'Adult Social Care', 'notes': ''},
                {'name': 'Children Social Care', 'type': 'expenditure', 'year': 'Year_1', 'amount': float(y1.get('Demand_Base_CSC', 0.0)), 'department': 'Children Social Care', 'notes': ''},
                {'name': 'Pay Cost Base', 'type': 'expenditure', 'year': 'Year_1', 'amount': float(y1.get('Pay_Cost_Base', 0.0)), 'department': 'Corporate', 'notes': ''},
                {'name': 'Savings Plan', 'type': 'budget', 'year': 'Year_1', 'amount': float(y1.get('Savings_Plan', 0.0)), 'department': 'Corporate', 'notes': ''},
            ]
            st.session_state['inputs_df'] = pd.DataFrame(rows)
    except Exception:
        # if prefill fails, fall back to defaults
        st.session_state['inputs_df'] = make_default_df()

df = st.session_state.get('inputs_df', make_default_df())

st.markdown('### Editable table')
edited = None
try:
    # prefer built-in data_editor when available
    if hasattr(st, 'data_editor'):
        edited = st.data_editor(df, num_rows='dynamic', disabled=read_only)
    else:
        # try st_aggrid fallback if installed
        from st_aggrid import AgGrid, GridOptionsBuilder
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(editable=True)
        grid_options = gb.build()
        grid_response = AgGrid(df, gridOptions=grid_options, fit_columns_on_grid_load=True)
        edited = pd.DataFrame(grid_response['data'])
except Exception:
    st.warning('Editable grid not available — showing read-only table. You can still upload/download CSVs.')
    st.dataframe(df)

if edited is not None and not read_only:
    st.session_state['inputs_df'] = edited
    # Auto-apply edits to in-session model
    try:
        data_path = Path(__file__).parent.parent.parent / 'data' / 'base_financials.csv'
        base_data = st.session_state.get('base_data')
        if base_data is None:
            base_data = pd.read_csv(data_path)

        name_to_col = {
            'base net revenue': 'Net_Revenue_Budget',
            'net revenue budget': 'Net_Revenue_Budget',
            'council tax income': 'Council_Tax_Income',
            'business rates income': 'Business_Rates_Income',
            'core grants': 'Core_Grants',
            'fees and charges': 'Fees_And_Charges',
            'fees & charges': 'Fees_And_Charges',
            'service expenditure': 'Service_Expenditure',
            'opening reserves': 'Opening_Reserves',
            'pay cost base': 'Pay_Cost_Base',
            'inflation base': 'Inflation_Base',
            'adult social care': 'Demand_Base_ASC',
            'children social care': 'Demand_Base_CSC',
            'savings plan': 'Savings_Plan',
        }

        def normalize_year(value):
            text = str(value).strip().lower().replace(" ", "").replace("-", "_")
            if text in {"year1", "year_1", "y1", "1"}:
                return "Year_1"
            if text in {"year2", "year_2", "y2", "2"}:
                return "Year_2"
            if text in {"year3", "year_3", "y3", "3"}:
                return "Year_3"
            if text in {"year4", "year_4", "y4", "4"}:
                return "Year_4"
            if text in {"year5", "year_5", "y5", "5"}:
                return "Year_5"
            return str(value)

        for _, row in edited.iterrows():
            name = str(row.get('name', '')).strip().lower()
            year = normalize_year(row.get('year', ''))
            amount = row.get('amount', None)
            if name in name_to_col and year in base_data['Year'].values and amount is not None:
                col = name_to_col[name]
                base_data.loc[base_data['Year'] == year, col] = float(amount)

        st.session_state['base_data'] = base_data
        y1 = base_data[base_data['Year'] == 'Year_1'].iloc[0]
        st.session_state['base_budget'] = float(y1.get('Net_Revenue_Budget', 0.0))
        st.session_state['opening_reserves'] = float(y1.get('Opening_Reserves', 0.0))
    except Exception:
        pass

col1, col2 = st.columns([1,1])
with col1:
    if st.button('Apply to model', disabled=read_only):
        inputs = st.session_state.get('inputs_df', df)
        # Map inputs into in-session base_data (no disk writes)
        try:
            data_path = Path(__file__).parent.parent.parent / 'data' / 'base_financials.csv'
            base_data = st.session_state.get('base_data')
            if base_data is None:
                base_data = pd.read_csv(data_path)

            name_to_col = {
                'base net revenue': 'Net_Revenue_Budget',
                'net revenue budget': 'Net_Revenue_Budget',
                'council tax income': 'Council_Tax_Income',
                'business rates income': 'Business_Rates_Income',
                'core grants': 'Core_Grants',
                'fees and charges': 'Fees_And_Charges',
                'fees & charges': 'Fees_And_Charges',
                'service expenditure': 'Service_Expenditure',
                'opening reserves': 'Opening_Reserves',
                'pay cost base': 'Pay_Cost_Base',
                'inflation base': 'Inflation_Base',
                'adult social care': 'Demand_Base_ASC',
                'children social care': 'Demand_Base_CSC',
                'savings plan': 'Savings_Plan',
            }

            def normalize_year(value):
                text = str(value).strip().lower().replace(" ", "").replace("-", "_")
                if text in {"year1", "year_1", "y1", "1"}:
                    return "Year_1"
                if text in {"year2", "year_2", "y2", "2"}:
                    return "Year_2"
                if text in {"year3", "year_3", "y3", "3"}:
                    return "Year_3"
                if text in {"year4", "year_4", "y4", "4"}:
                    return "Year_4"
                if text in {"year5", "year_5", "y5", "5"}:
                    return "Year_5"
                return str(value)

            updated = 0
            for _, row in inputs.iterrows():
                name = str(row.get('name', '')).strip().lower()
                year = normalize_year(row.get('year', ''))
                amount = row.get('amount', None)
                if name in name_to_col and year in base_data['Year'].values and amount is not None:
                    col = name_to_col[name]
                    base_data.loc[base_data['Year'] == year, col] = float(amount)
                    updated += 1

            st.session_state['base_data'] = base_data

            # update key session values from Year_1
            y1 = base_data[base_data['Year'] == 'Year_1'].iloc[0]
            st.session_state['base_budget'] = float(y1.get('Net_Revenue_Budget', 0.0))
            st.session_state['opening_reserves'] = float(y1.get('Opening_Reserves', 0.0))

            st.success(f'Applied inputs to in-session model. Updated {updated} fields.')
        except Exception as e:
            st.error('Could not apply inputs to model: ' + str(e))

with col2:
    csv = st.session_state.get('inputs_df', df).to_csv(index=False).encode('utf-8')
    st.download_button('Download inputs CSV', data=csv, file_name='inputs.csv', mime='text/csv')

st.markdown('### Notes')
st.markdown('- Recommended CSV columns: `name,type,year,amount,department,notes`.')
st.markdown('- `type` should be one of `budget`, `expenditure`, or `capital` to aid automatic mapping.')
