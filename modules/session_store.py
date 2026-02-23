"""
In-memory session store for sharing state across tabs via URL token.
Session-only, TTL-based, no disk writes.
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Dict, Any

import streamlit as st

_STORE: Dict[str, Dict[str, Any]] = {}

DEFAULT_KEYS = [
    "base_data",
    "inputs_df",
    "base_budget",
    "opening_reserves",
    "council_name",
    "council_colour",
    "theme",
    "saved_scenarios",
    "risk_register_df",
    "forecast_snapshots",
    "kpis",
    "rag_rating",
    "reserves_policy_min",
    "reserves_policy_target",
    "reserves_policy_max",
    "show_tooltips",
    "show_onboarding",
    "auto_expand_expanders",
    "auth_user",
    "auth_role",
    "auth_tenant",
    "auth_last_seen",
]


def _ttl_seconds() -> int:
    try:
        return int(float(os.getenv("SESSION_TTL_HOURS", "8")) * 3600)
    except Exception:
        return 8 * 3600


def _clone_value(val: Any) -> Any:
    if hasattr(val, "copy"):
        try:
            return val.copy()
        except Exception:
            return val
    return val


def _prune():
    now = time.time()
    ttl = _ttl_seconds()
    expired = [k for k, v in _STORE.items() if now - v.get("ts", now) > ttl]
    for k in expired:
        _STORE.pop(k, None)


def ensure_session():
    _prune()
    token = st.session_state.get("session_token")
    if not token:
        token = st.query_params.get("session")
        if not token:
            token = uuid.uuid4().hex[:12]
        st.session_state["session_token"] = token
        st.query_params["session"] = token

    if not st.session_state.get("session_hydrated"):
        record = _STORE.get(token)
        if record:
            data = record.get("data", {})
            for key, value in data.items():
                st.session_state[key] = _clone_value(value)
        st.session_state["session_hydrated"] = True


def sync_session(keys=None):
    _prune()
    token = st.session_state.get("session_token")
    if not token:
        return
    keys = keys or DEFAULT_KEYS
    data = {k: _clone_value(st.session_state.get(k)) for k in keys if k in st.session_state}
    _STORE[token] = {"ts": time.time(), "data": data}
