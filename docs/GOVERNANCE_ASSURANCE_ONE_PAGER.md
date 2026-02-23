# Governance Assurance One‑Pager

> Quick links: `docs/QUICK_START.md` for setup/run, `docs/DEPLOYMENT.md` for hosting, `docs/AUTHENTICATION.md` for access control.


## Purpose
Provide an at‑a‑glance summary of governance controls for Section 151 sign‑off.

## Access & Roles
- Role‑based access: Admin / Analyst / Read‑only.
- Session timeout: configurable with `AUTH_TTL_MINUTES`.
- Passwords hashed (PBKDF2); plaintext disabled by default.

## Audit & Evidence
- Audit trail for key model changes and exports.
- Snapshot history for decision checkpoints.
- Exportable audit log for governance packs.

## Data Protection
- Optional tenant‑scoped persistence (`data/tenants/<tenant>`).
- Encryption at rest with `FERNET_KEY`.
- Retention limits (audit + snapshots).

## Operational Controls
- Export gating by plan.
- Demo mode clearly marked and resettable.
- Deployment guidance documented.

