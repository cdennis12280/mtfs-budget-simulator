"""
Tenant-aware storage utilities with optional encryption at rest.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:  # pragma: no cover
    Fernet = None
    InvalidToken = Exception

import streamlit as st


def persistence_enabled() -> bool:
    return os.getenv("PERSISTENCE_ENABLED", "false").lower() == "true"


def tenant_id() -> str:
    return st.session_state.get("auth_tenant") or os.getenv("DEFAULT_TENANT", "default")


def base_dir() -> Path:
    root = os.getenv("TENANT_DATA_DIR", "data/tenants")
    return Path(root).expanduser().resolve()


def tenant_dir() -> Path:
    path = base_dir() / tenant_id()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _fernet() -> Optional[Fernet]:
    key = os.getenv("FERNET_KEY", "").strip()
    if not key or Fernet is None:
        return None
    try:
        return Fernet(key.encode("utf-8"))
    except Exception:
        return None


def _encrypt(payload: bytes) -> bytes:
    f = _fernet()
    if not f:
        return payload
    return f.encrypt(payload)


def _decrypt(payload: bytes) -> bytes:
    f = _fernet()
    if not f:
        return payload
    try:
        return f.decrypt(payload)
    except InvalidToken:
        return payload


def load_json(name: str, default: Optional[Any] = None) -> Any:
    if not persistence_enabled():
        return default
    path = tenant_dir() / name
    if not path.exists():
        return default
    data = path.read_bytes()
    raw = _decrypt(data)
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return default


def save_json(name: str, data: Any) -> None:
    if not persistence_enabled():
        return
    path = tenant_dir() / name
    raw = json.dumps(data, indent=2).encode("utf-8")
    path.write_bytes(_encrypt(raw))


def prune_list(name: str, keep_last: int = 200) -> None:
    if not persistence_enabled() or keep_last <= 0:
        return
    items = load_json(name, [])
    if not isinstance(items, list):
        return
    if len(items) <= keep_last:
        return
    save_json(name, items[-keep_last:])
