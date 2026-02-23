"""
Billing plan utilities and feature gating.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

import streamlit as st


DEFAULT_PLANS = {
    "community": {"features": ["view"], "label": "Community"},
    "governance": {"features": ["view", "exports", "audit"], "label": "Governance"},
    "enterprise": {"features": ["view", "exports", "audit", "sso", "multi_tenant"], "label": "Enterprise"},
}


def _load_plans() -> Dict[str, Dict[str, List[str]]]:
    raw = os.getenv("BILLING_PLANS_JSON", "").strip()
    file_path = os.getenv("BILLING_PLANS_FILE", "").strip()
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return DEFAULT_PLANS
    if file_path:
        try:
            return json.loads(Path(file_path).read_text())
        except Exception:
            return DEFAULT_PLANS
    default_path = Path(__file__).parent.parent / "data" / "billing_plans.json"
    if default_path.exists():
        try:
            return json.loads(default_path.read_text())
        except Exception:
            return DEFAULT_PLANS
    return DEFAULT_PLANS


def _load_subscriptions() -> Dict[str, str]:
    raw = os.getenv("BILLING_SUBSCRIPTIONS_JSON", "").strip()
    file_path = os.getenv("BILLING_SUBSCRIPTIONS_FILE", "").strip()
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return {}
    if file_path:
        try:
            return json.loads(Path(file_path).read_text())
        except Exception:
            return {}
    default_path = Path(__file__).parent.parent / "data" / "billing_subscriptions.json"
    if default_path.exists():
        try:
            return json.loads(default_path.read_text())
        except Exception:
            return {}
    return {}


def get_plan(tenant: str) -> Dict[str, List[str]]:
    plans = _load_plans()
    subs = _load_subscriptions()
    plan_key = subs.get(tenant, os.getenv("DEFAULT_PLAN", "governance"))
    return plans.get(plan_key, DEFAULT_PLANS["governance"])


def has_feature(feature: str) -> bool:
    tenant = st.session_state.get("auth_tenant", "default")
    plan = get_plan(tenant)
    return feature in plan.get("features", [])


def plan_label() -> str:
    tenant = st.session_state.get("auth_tenant", "default")
    plan = get_plan(tenant)
    return plan.get("label", "Governance")
