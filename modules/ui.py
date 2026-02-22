"""
UI helpers: theme application and page headers.
"""

from __future__ import annotations

import streamlit as st


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
    theme = "Dark"
    st.session_state["theme"] = "Dark"
    accent = st.session_state.get("council_colour", "#0b3d91")
    palette = _theme_palette(theme, accent)

    st.session_state["plotly_template"] = "plotly_dark" if theme == "Dark" else "plotly_white"

    st.markdown(
        f"""
<style>
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
  --shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}}

html, body, [data-testid=\"stAppViewContainer\"] {{
  background: var(--bg) !important;
  color: var(--text) !important;
}}

[data-testid=\"stSidebar\"] {{
  background: var(--panel) !important;
  border-right: 1px solid var(--border);
}}

h1, h2, h3, h4, h5, h6, p, label, div {{
  color: var(--text);
}}

a {{
  color: var(--accent);
}}

.app-card {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  box-shadow: var(--shadow);
}}

.app-callout {{
  background: var(--panel-alt);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: 8px;
  padding: 10px 12px;
}}

.app-section {{
  margin-top: 8px;
  margin-bottom: 4px;
  font-weight: 700;
}}

.tag {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--panel-alt);
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 12px;
}}

/* Improve widget spacing */
.block-container {{ padding-top: 0.75rem; padding-left: 1rem; padding-right: 1rem; }}

/* Buttons and inputs */
button[kind=\"primary\"] {{
  background: var(--accent) !important;
  border: 1px solid var(--accent) !important;
  color: white !important;
  border-radius: 8px !important;
}}

div[data-testid=\"stMetric\"] {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  box-shadow: var(--shadow);
}}

div[data-testid=\"stDataFrame\"] {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 6px;
  box-shadow: var(--shadow);
}}

div[role=\"radiogroup\"], div[role=\"listbox\"], div[data-testid=\"stSelectbox\"], div[data-testid=\"stSlider\"] {{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 6px 8px;
}}

/* Sidebar section headers */
.sidebar .app-section {{
  font-size: 13px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}}

</style>
""",
        unsafe_allow_html=True,
    )


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
