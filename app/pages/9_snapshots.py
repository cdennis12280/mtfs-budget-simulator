"""
Forecast Snapshots Admin
Review, export, and restore rolling forecast snapshots.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add modules to path
modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from snapshots import load_snapshots
from audit_log import get_audit_log
from ui import apply_theme, page_header
from auth import require_auth, require_roles, auth_sidebar

apply_theme()
if not require_auth():
    st.stop()
require_roles({"Admin", "Analyst", "Read-only"})
auth_sidebar()
read_only = st.session_state.get("auth_role") == "Read-only"
if read_only:
    st.info("Read-only mode: restore actions are disabled.")
page_header("Forecast Snapshots", "Review rolling forecast snapshots, export history, or restore assumptions.")
st.markdown("""
<div class="app-callout">
  Capture snapshots at each governance checkpoint for a clear decision trail.
</div>
""", unsafe_allow_html=True)

snapshots = load_snapshots()

if not snapshots:
    st.info("No snapshots found. Save a snapshot from the main dashboard.")
    st.stop()

df = pd.DataFrame(snapshots)

st.markdown("## Snapshot History")
st.dataframe(
    df[[
        'snapshot_id', 'name', 'version', 'timestamp', 'rag', 'notes'
    ]].sort_values('timestamp', ascending=False),
    use_container_width=True
)

st.markdown("---")
st.markdown("## Filter & Inspect")

names = sorted(df['name'].unique().tolist())
sel_name = st.selectbox("Filter by name", options=['All'] + names, disabled=read_only)
filtered = df if sel_name == 'All' else df[df['name'] == sel_name]

latest_only = st.checkbox("Show latest version per name", value=False, disabled=read_only)
if latest_only and not filtered.empty:
    filtered = filtered.sort_values('timestamp').groupby('name').tail(1)

st.dataframe(
    filtered[['snapshot_id', 'name', 'version', 'timestamp', 'rag', 'notes']],
    use_container_width=True
)

st.markdown("---")
st.markdown("## Restore Assumptions")

options = filtered.sort_values('timestamp', ascending=False)['snapshot_id'].tolist()
selected = st.selectbox("Select snapshot to restore", options=options, disabled=read_only)

selected_row = filtered[filtered['snapshot_id'] == selected].iloc[0]
assumptions = selected_row.get('assumptions', {})

with st.expander("View assumptions", expanded=False):
    st.json(assumptions)

if st.button("Apply snapshot assumptions to session", disabled=read_only):
    for key, val in assumptions.items():
        st.session_state[key] = val
    audit = get_audit_log()
    audit.log_entry(
        action='forecast_snapshot_apply',
        user='system',
        key=selected_row.get('snapshot_id', ''),
        notes=f"Applied snapshot from admin page: {selected_row.get('name', '')} v{selected_row.get('version', 1)}"
    )
    st.success("Snapshot applied to session.")

st.markdown("---")
st.markdown("## Export")

csv_bytes = df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download snapshot history (CSV)",
    data=csv_bytes,
    file_name='forecast_snapshots.csv',
    mime='text/csv'
)
