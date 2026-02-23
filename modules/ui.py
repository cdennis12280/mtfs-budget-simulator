"""
UI helpers: theme application and page headers.
"""

from __future__ import annotations

import streamlit as st
from session_store import ensure_session, sync_session


def _theme_palette(theme: str, accent: str):
    if theme == "Dark":
        return {
            "bg": "#0f1117",
            "panel": "#161b22",
            "panel_alt": "#1f2633",
            "text": "#e6edf3",
            "muted": "#9aa4b2",
            "border": "#2b3443",
            "accent": accent,
            "success": "#2ca02c",
            "warning": "#ff7f0e",
            "danger": "#d62728",
        }
    if theme == "Print-Friendly":
        return {
            "bg": "#ffffff",
            "panel": "#ffffff",
            "panel_alt": "#f4f4f4",
            "text": "#111111",
            "muted": "#4a4a4a",
            "border": "#c9c9c9",
            "accent": accent,
            "success": "#1a7f37",
            "warning": "#b36b00",
            "danger": "#b00020",
        }
    # Light (default)
    return {
        "bg": "#f3f5f8",
        "panel": "#ffffff",
        "panel_alt": "#f7f9fc",
        "text": "#0b1220",
        "muted": "#5a667a",
        "border": "#dde3ee",
        "accent": accent,
        "success": "#2ca02c",
        "warning": "#ff7f0e",
        "danger": "#d62728",
    }


def apply_theme():
    ensure_session()
    theme = st.session_state.get("theme", "Light")
    if theme not in {"Light", "Dark", "Print-Friendly"}:
        theme = "Light"
    st.session_state["theme"] = theme
    accent = st.session_state.get("council_colour", "#0b3d91")
    palette = _theme_palette(theme, accent)

    st.session_state["plotly_template"] = "plotly_dark" if theme == "Dark" else "plotly_white"

    if theme == "Dark":
        background_style = palette["bg"]
    elif theme == "Print-Friendly":
        background_style = "#ffffff"
    else:
        background_style = "linear-gradient(180deg, #f6f7fb 0%, #eef2f8 100%)"

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {{
  --bg: {palette['bg']};
  --panel: {palette['panel']};
  --panel-alt: {palette['panel_alt']};
  --text: {palette['text']};
  --muted: {palette['muted']};
  --border: {palette['border']};
  --accent: {palette['accent']};
  --success: {palette['success']};
  --warning: {palette['warning']};
  --danger: {palette['danger']};
  --shadow: 0 10px 28px rgba(15, 23, 42, 0.10);
  --shadow-soft: 0 6px 18px rgba(15, 23, 42, 0.08);
  --radius-lg: 14px;
  --radius-md: 10px;
  --radius-sm: 8px;
}}

html, body, [data-testid=\"stAppViewContainer\"] {{
  background: {background_style} !important;
  color: var(--text) !important;
  font-family: "IBM Plex Sans", "Segoe UI", sans-serif !important;
  letter-spacing: 0.01em;
}}

[data-testid=\"stSidebar\"] {{
  background: var(--panel) !important;
  border-right: 1px solid var(--border);
}}

h1, h2, h3, h4, h5, h6 {{
  font-family: "Fraunces", "Georgia", serif !important;
  color: var(--text);
}}

p, label, div, span {{
  color: var(--text);
}}

a {{
  color: var(--accent);
  text-decoration: none;
}}

a:hover {{
  text-decoration: underline;
}}

.app-card {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  box-shadow: var(--shadow);
}}

.app-callout {{
  background: var(--panel-alt);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: var(--radius-md);
  padding: 12px 14px;
}}

.app-section {{
  margin-top: 10px;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}}

.tag {{
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--panel-alt);
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 12px;
}}

/* Layout */
.block-container {{ padding-top: 0.75rem; padding-left: 1.1rem; padding-right: 1.1rem; }}

/* Buttons and inputs */
button, div[data-testid=\"stButton\"] button {{
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
}}

button[kind=\"primary\"] {{
  background: var(--accent) !important;
  border: 1px solid var(--accent) !important;
  color: white !important;
  box-shadow: var(--shadow-soft);
}}

button:focus-visible {{
  outline: 2px solid color-mix(in srgb, var(--accent) 45%, transparent) !important;
  outline-offset: 2px !important;
}}

div[data-testid=\"stMetric\"], div[data-testid=\"stDataFrame\"], div[data-testid=\"stExpander\"] {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 10px 12px;
  box-shadow: var(--shadow-soft);
}}

div[role=\"radiogroup\"], div[role=\"listbox\"], div[data-testid=\"stSelectbox\"], div[data-testid=\"stSlider\"], div[data-testid=\"stNumberInput\"], div[data-testid=\"stTextInput\"], div[data-testid=\"stTextArea\"] {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 6px 8px;
}}

div[data-testid=\"stAlert\"] {{
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
}}

/* Sidebar section headers */
.sidebar .app-section {{
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}}

/* Reduce Streamlit chrome spacing for a calmer layout */
section.main > div {{ padding-bottom: 2rem; }}
</style>
""",
        unsafe_allow_html=True,
    )
    sync_session()


def page_header(title: str, subtitle: str | None = None):
    if subtitle:
        st.markdown(
            f"""
<div class="app-card">
  <div style="font-size:22px; font-weight:700;">{title}</div>
  <div style="color:var(--muted); margin-top:2px;">{subtitle}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
<div class="app-card">
  <div style="font-size:22px; font-weight:700;">{title}</div>
</div>
""",
            unsafe_allow_html=True,
        )


def app_link(path: str) -> str:
    token = st.session_state.get("session_token", "")
    if not path.startswith("/"):
        path = "/" + path
    joiner = "&" if "?" in path else "?"
    return f"{path}{joiner}session={token}" if token else path
