"""
Audit Log Dashboard
View, filter, and export audit trail for compliance and governance
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add modules to path
modules_path = Path(__file__).parent.parent.parent / 'modules'
sys.path.insert(0, str(modules_path))

from audit_log import get_audit_log
from ui import apply_theme, page_header

apply_theme()
page_header("Audit Log and Compliance", "View and export audit trail of all actions, assumption changes, and exports.")
st.markdown("""
<div class="app-callout">
  Use filters to build an evidence pack for external audit or committee scrutiny.
</div>
""", unsafe_allow_html=True)

audit_log = get_audit_log()

# === Load all entries ===
all_entries = audit_log.read_all()

if not all_entries:
    st.info("No audit log entries yet. Entries will be recorded as you use the tool.")
    st.stop()

# Convert to DataFrame for easier filtering and display
df = pd.DataFrame(all_entries)
df['timestamp'] = pd.to_datetime(df['timestamp'])

st.markdown("---")

# === Filter Controls ===
col1, col2, col3 = st.columns(3)

with col1:
    action_filter = st.multiselect(
        "Filter by Action",
        options=sorted(df['action'].unique()),
        default=sorted(df['action'].unique()),
        help="Show entries for selected action types"
    )

with col2:
    user_filter = st.multiselect(
        "Filter by User",
        options=sorted(df['user'].unique()),
        default=sorted(df['user'].unique()),
        help="Show entries created by selected users"
    )

with col3:
    date_range = st.date_input(
        "Date Range",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        help="Filter by date range"
    )

# Apply filters
filtered_df = df[
    (df['action'].isin(action_filter)) &
    (df['user'].isin(user_filter)) &
    (df['timestamp'].dt.date >= date_range[0]) &
    (df['timestamp'].dt.date <= date_range[1])
]

st.markdown("---")

# === Summary Stats ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Entries", len(all_entries))

with col2:
    st.metric("Shown Entries", len(filtered_df))

with col3:
    if len(filtered_df) > 0:
        st.metric("Date Range", f"{filtered_df['timestamp'].min().strftime('%Y-%m-%d')} to {filtered_df['timestamp'].max().strftime('%Y-%m-%d')}")
    else:
        st.metric("Date Range", "No data")

with col4:
    st.metric("Unique Users", df['user'].nunique())

st.markdown("---")

# === Detailed Log Table ===
st.markdown("## Audit Log Entries")

display_df = filtered_df.copy()
display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
display_df = display_df.sort_values('timestamp', ascending=False)

st.dataframe(
    display_df[['timestamp', 'action', 'user', 'key', 'old_value', 'new_value', 'notes']],
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# === Summary by Action Type ===
st.markdown("## Activity Summary by Action Type")

summary = filtered_df.groupby('action').size().reset_index(name='count')
summary = summary.sort_values('count', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    st.bar_chart(summary.set_index('action')['count'])

with col2:
    st.dataframe(summary, use_container_width=True, hide_index=True)

st.markdown("---")

# === Exports ===
st.markdown("## Export & Compliance Reports")

col1, col2, col3 = st.columns(3)

with col1:
    # Export filtered log as CSV
    csv_data = filtered_df.copy()
    csv_data['timestamp'] = csv_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    csv = csv_data.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        "📥 Export Filtered Log (CSV)",
        data=csv,
        file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime='text/csv',
        help="Download filtered audit log entries as CSV"
    )

with col2:
    # Export full log
    full_csv = audit_log.export_csv().encode('utf-8')
    st.download_button(
        "📥 Export Full Log (CSV)",
        data=full_csv,
        file_name=f"audit_log_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime='text/csv',
        help="Download complete audit log (all entries)"
    )

with col3:
    if st.button("⚠️ Clear Log (Irreversible)"):
        if st.checkbox("Confirm: I want to clear the audit log"):
            audit_log.clear()
            st.success("Audit log cleared.")
            st.rerun()

st.markdown("---")

# === Compliance Notes ===
st.markdown("""
### Audit Log Compliance

This audit log records all actions taken in the MTFS Budget Gap Simulator:

- **Assumption Changes**: When budget, expenditure, or policy assumptions are modified
- **Scenario Saves**: When scenarios are bookmarked for later comparison
- **Exports**: When reports, CSVs, or PDFs are downloaded
- **Settings Changes**: When branding or preferences are updated
- **Model Runs**: When scenarios are calculated

**Governance Benefits:**
- 📊 Demonstrates probity and due process for budget setting
- 🔍 Provides trail for external auditor review
- 📋 Supports S151 statutory duty to document financial planning
- 🛡️ Non-repudiation: actions are timestamped and attributed to users

**Data Retention:**
- Audit logs are session-only and not stored on the server
- Export regularly as CSV for secure archival

**Export Recommendations:**
- Export full log quarterly and securely store
- Include audit report in Cabinet/Council agendas alongside MTFS
- Provide to external auditors upon request
""")
