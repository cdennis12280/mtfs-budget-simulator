"""
Audit Log System
Track all user actions, assumptions, scenario changes, and exports for compliance & governance
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None

@dataclass
class AuditEntry:
    """Single audit log entry"""
    timestamp: str  # ISO 8601 format
    action: str    # 'assumption_change', 'scenario_save', 'export', 'settings_change', 'model_run'
    user: str      # username or 'system'
    key: str       # parameter name or asset name
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    notes: str = ""

class AuditLog:
    """Manage audit log for all actions (session-only by default)."""

    def __init__(self):
        self._entries = []
    
    def log_entry(self, action: str, user: str = "system", key: str = "", 
                  old_value: Optional[Any] = None, new_value: Optional[Any] = None, 
                  notes: str = ""):
        """Write a new audit entry to the log file (append mode)"""
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            user=user,
            key=key,
            old_value=old_value,
            new_value=new_value,
            notes=notes
        )
        entry_dict = asdict(entry)
        if st is not None:
            if 'audit_log_entries' not in st.session_state:
                st.session_state['audit_log_entries'] = []
            st.session_state['audit_log_entries'].append(entry_dict)
        else:
            self._entries.append(entry_dict)
    
    def read_all(self) -> list:
        """Read all audit entries from log file"""
        if st is not None:
            return st.session_state.get('audit_log_entries', [])
        return self._entries
    
    def read_recent(self, n: int = 100) -> list:
        """Read the most recent N entries"""
        all_entries = self.read_all()
        return all_entries[-n:] if n > 0 else []
    
    def filter_by_action(self, action: str) -> list:
        """Filter entries by action type"""
        return [e for e in self.read_all() if e['action'] == action]
    
    def filter_by_date(self, start_date: str, end_date: str) -> list:
        """Filter entries by date range (ISO 8601 format)"""
        entries = self.read_all()
        return [e for e in entries if start_date <= e['timestamp'] <= end_date]
    
    def export_csv(self) -> str:
        """Export audit log as CSV"""
        import csv
        from io import StringIO
        
        entries = self.read_all()
        if not entries:
            return ""
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['timestamp', 'action', 'user', 'key', 'old_value', 'new_value', 'notes'])
        writer.writeheader()
        writer.writerows(entries)
        return output.getvalue()
    
    def clear(self):
        """Clear all audit log entries (destructive, use cautiously)"""
        if st is not None:
            st.session_state['audit_log_entries'] = []
        else:
            self._entries = []

# Global audit log instance
_audit_log = None

def get_audit_log() -> AuditLog:
    """Get or create the global audit log instance"""
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditLog()
    return _audit_log
