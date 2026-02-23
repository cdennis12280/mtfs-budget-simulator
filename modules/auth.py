"""
Authentication and authorization helpers.
Password-based login with role + tenant support.
"""

from __future__ import annotations

import json
import os
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import streamlit as st


@dataclass
class AuthUser:
    username: str
    role: str
    tenant: str


def _auth_mode() -> str:
    return os.getenv("AUTH_MODE", "disabled").strip().lower()


def _ttl_seconds() -> int:
    try:
        return int(float(os.getenv("AUTH_TTL_MINUTES", "60")) * 60)
    except Exception:
        return 60 * 60


def _load_users() -> Dict[str, Dict[str, str]]:
    """
    Load users from:
    - AUTH_USERS_JSON (JSON string)
    - AUTH_USERS_FILE (path)
    - data/auth_users.json (fallback)
    """
    raw = os.getenv("AUTH_USERS_JSON", "").strip()
    file_path = os.getenv("AUTH_USERS_FILE", "").strip()
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
    default_path = Path(__file__).parent.parent / "data" / "auth_users.json"
    if default_path.exists():
        try:
            return json.loads(default_path.read_text())
        except Exception:
            return {}
    return {}


def _pbkdf2_hash(password: str, salt: str, iterations: int = 120000) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return dk.hex()


def _verify_password(stored: str, password: str) -> bool:
    """
    Supported formats:
    - pbkdf2$iterations$salt$hash
    - plaintext (only if ALLOW_PLAINTEXT_PASSWORDS=true)
    """
    if stored.startswith("pbkdf2$"):
        try:
            _, iterations, salt, digest = stored.split("$", 3)
            calc = _pbkdf2_hash(password, salt, int(iterations))
            return calc == digest
        except Exception:
            return False
    if os.getenv("ALLOW_PLAINTEXT_PASSWORDS", "false").lower() == "true":
        return stored == password
    return False


def _set_auth(user: AuthUser) -> None:
    st.session_state["auth_user"] = user.username
    st.session_state["auth_role"] = user.role
    st.session_state["auth_tenant"] = user.tenant
    st.session_state["auth_last_seen"] = time.time()


def current_user() -> Optional[AuthUser]:
    user = st.session_state.get("auth_user")
    role = st.session_state.get("auth_role")
    tenant = st.session_state.get("auth_tenant")
    if not user or not role or not tenant:
        return None
    return AuthUser(username=user, role=role, tenant=tenant)


def require_auth() -> bool:
    """
    Enforce authentication. Returns True when authenticated, otherwise renders login and returns False.
    """
    if _auth_mode() == "disabled":
        if "auth_user" not in st.session_state:
            _set_auth(AuthUser(username="system", role="Admin", tenant="default"))
        return True

    last_seen = st.session_state.get("auth_last_seen")
    if last_seen and (time.time() - last_seen) < _ttl_seconds():
        st.session_state["auth_last_seen"] = time.time()
        return True

    st.session_state.pop("auth_user", None)
    st.session_state.pop("auth_role", None)
    st.session_state.pop("auth_tenant", None)

    st.markdown("### Sign in")
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if not submitted:
        return False

    users = _load_users()
    record = users.get(username)
    if not record:
        st.error("Invalid credentials.")
        return False
    stored_pw = record.get("password", "")
    if not _verify_password(stored_pw, password):
        st.error("Invalid credentials.")
        return False

    role = record.get("role", "Analyst")
    tenant = record.get("tenant", "default")
    _set_auth(AuthUser(username=username, role=role, tenant=tenant))
    st.success("Signed in.")
    return True


def require_roles(allowed_roles) -> None:
    user = current_user()
    if not user:
        st.stop()
    if user.role not in allowed_roles:
        st.error("You do not have access to this area.")
        st.stop()


def auth_sidebar() -> None:
    user = current_user()
    if not user:
        return
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Access")
        st.caption(f"User: {user.username}")
        st.caption(f"Role: {user.role}")
        st.caption(f"Tenant: {user.tenant}")
        if st.button("Log out"):
            st.session_state.pop("auth_user", None)
            st.session_state.pop("auth_role", None)
            st.session_state.pop("auth_tenant", None)
            st.session_state.pop("auth_last_seen", None)
            st.experimental_rerun()
