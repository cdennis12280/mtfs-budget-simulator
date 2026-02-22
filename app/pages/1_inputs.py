import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Inputs — Budget & Line Items")
st.markdown("Upload or edit the authoritative inputs for the MTFS model. Use the table to bulk-edit budgets, expenditures and capital items, then click `Apply to model` to push values into session state.")

upload = st.file_uploader('Upload Inputs CSV (columns: name,type,year,amount,department,notes)', type=['csv'])

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

df = st.session_state.get('inputs_df', make_default_df())

st.markdown('### Editable table')
edited = None
try:
    # prefer built-in data_editor when available
    if hasattr(st, 'data_editor'):
        edited = st.data_editor(df, num_rows='dynamic')
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

if edited is not None:
    st.session_state['inputs_df'] = edited

col1, col2 = st.columns([1,1])
with col1:
    if st.button('Apply to model'):
        inputs = st.session_state.get('inputs_df', df)
        # attempt to derive a sensible base budget (Year_1 budgets)
        try:
            # look for rows marked 'budget' in Year_1
            mask = inputs['type'].astype(str).str.lower() == 'budget'
            yr_mask = inputs['year'].astype(str) == 'Year_1'
            candidate = inputs[mask & yr_mask]
            if candidate.shape[0] > 0:
                base_budget = float(candidate['amount'].sum())
            else:
                # fallback: sum all budget rows
                base_budget = float(inputs[mask]['amount'].sum()) if inputs[mask].shape[0] > 0 else float(inputs['amount'].sum())
            st.session_state['base_budget'] = base_budget
            st.success(f'Applied inputs — set `base_budget` = {base_budget} (units as in CSV, typically £m)')
        except Exception as e:
            st.error('Could not apply inputs to model: ' + str(e))

with col2:
    csv = st.session_state.get('inputs_df', df).to_csv(index=False).encode('utf-8')
    st.download_button('Download inputs CSV', data=csv, file_name='inputs.csv', mime='text/csv')

st.markdown('### Notes')
st.markdown('- Recommended CSV columns: `name,type,year,amount,department,notes`.')
st.markdown('- `type` should be one of `budget`, `expenditure`, or `capital` to aid automatic mapping.')
