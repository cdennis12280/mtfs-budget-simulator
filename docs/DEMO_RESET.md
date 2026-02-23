# Hosted Demo Reset Flow

> Quick links: `docs/QUICK_START.md` for setup/run, `docs/DEPLOYMENT.md` for hosting, `docs/AUTHENTICATION.md` for access control.


## Goal
Provide a repeatable demo reset for a hosted environment (no manual cleanup).

## Recommended Approach
1. Use a dedicated `demo` tenant in production.
2. Enable `PERSISTENCE_ENABLED=true` with tenant storage.
3. Add a reset endpoint or admin-only action that:
   - Clears `audit_log.json`
   - Clears `snapshots.json`
   - Clears `saved_scenarios`
   - Reinitializes `base_data` from `data/demo_financials.csv`

## Minimal Implementation (Manual)
If you do not have an API layer yet:
1. Log in as Admin.
2. Use the **Reset demo tenant** button (Dashboard sidebar).
3. Toggle Demo Mode off/on in Settings to refresh base data.

## Production Automation
- Add a scheduled job (nightly) to clear demo tenant state.
- Provide a short “Reset Demo” URL with admin auth for on-demand reset.

