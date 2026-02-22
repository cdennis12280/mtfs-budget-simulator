"""
Forecast snapshot utilities.
Store rolling versions of assumptions and KPIs for auditability.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


def load_snapshots(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    if st is not None:
        return st.session_state.get('forecast_snapshots', [])
    if path is None or not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def save_snapshots(path: Optional[Path], snapshots: List[Dict[str, Any]]) -> None:
    if st is not None:
        st.session_state['forecast_snapshots'] = snapshots
        return
    if path is None:
        return
    path.write_text(json.dumps(snapshots, indent=2))


def add_snapshot(path: Optional[Path], name: str, assumptions: Dict[str, Any], kpis: Dict[str, Any],
                 rag_rating: str, notes: str = "", keep_last: int = 50) -> Dict[str, Any]:
    snapshots = load_snapshots(path)
    version = 1 + max([s.get('version', 0) for s in snapshots if s.get('name') == name] or [0])
    entry = {
        'snapshot_id': f"{name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'name': name,
        'version': version,
        'timestamp': datetime.now().isoformat(),
        'assumptions': assumptions,
        'kpis': kpis,
        'rag': rag_rating,
        'notes': notes,
    }
    snapshots.append(entry)
    # rolling retention
    if keep_last > 0 and len(snapshots) > keep_last:
        snapshots = snapshots[-keep_last:]
    save_snapshots(path, snapshots)
    return entry
