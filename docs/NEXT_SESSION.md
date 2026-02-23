# Next Session Checklist

## Quick Context
- Dark theme is enforced across the app.
- Session-only storage: no disk writes, export-only persistence.
- Session token sharing across tabs is implemented via `app_link()`.
- Wizard is live and includes KPIs + charts.

## Current Status
- App deploy builds with Python 3.13.
- `requirements.txt` pinned for Python 3.13 compatibility.
- Risk Advisor + Snapshots + Reports + Inputs are working in session-only mode.

## Top Priorities (Next Session)
1. Authentication + role-based access (Admin, Analyst, Read-only).
2. Add “new clean session” link to header (not just dashboard).
3. Add persistent banner: “Session-only mode; export to retain.”
4. Link S151 User Guide in header or Settings page.
5. Extend input-to-model mapping if more line items appear.

## Known Links & Helpers
- `modules/ui.py`: `app_link()` helper appends session token.
- `modules/session_store.py`: in-memory TTL session sharing.
- `app/pages/0_wizard.py`: guided flow + live charts.

## Deploy Notes
- Streamlit Cloud uses Python 3.13.
- Ensure dependencies remain 3.13 compatible.

