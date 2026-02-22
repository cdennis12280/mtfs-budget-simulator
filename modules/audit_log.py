"""
Audit Log System
Track all user actions, assumptions, scenario changes, and exports for compliance & governance
"""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

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
    """Manage persistent audit log for all actions"""
    
    def __init__(self, log_file: Path = None):
        if log_file is None:
            log_file = Path.cwd() / '.audit_log.jsonl'
        self.log_file = log_file
        self.ensure_file()
    
    def ensure_file(self):
        """Create empty audit log file if it doesn't exist"""
        if not self.log_file.exists():
            self.log_file.touch()
    
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
        # Append as JSONL (one JSON object per line)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(asdict(entry)) + '\n')
    
    def read_all(self) -> list:
        """Read all audit entries from log file"""
        entries = []
        if not self.log_file.exists():
            return entries
        
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries
    
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
        if self.log_file.exists():
            self.log_file.unlink()
        self.ensure_file()

# Global audit log instance
_audit_log = None

def get_audit_log() -> AuditLog:
    """Get or create the global audit log instance"""
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditLog()
    return _audit_log
