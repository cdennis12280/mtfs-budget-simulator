# Governance Assurance Note (2 pages)

> Quick links: `docs/QUICK_START.md` for setup/run, `docs/DEPLOYMENT.md` for hosting, `docs/AUTHENTICATION.md` for access control.


## Purpose
This note summarises governance, security, and evidence controls for the MTFS Budget Gap Simulator.

## Access Control
- Role-based access: `Admin`, `Analyst`, `Read-only`.
- Session timeouts enforced via `AUTH_TTL_MINUTES`.
- Passwords hashed (PBKDF2); plaintext disabled by default.

## Audit & Evidence
- All scenario changes, exports, and snapshots are recorded.
- Audit log export available for governance review.
- Snapshots preserve assumptions and KPI context at decision points.

## Data Protection
- Optional persistence scoped by tenant (`data/tenants/<tenant>`).
- Encryption at rest available via `FERNET_KEY`.
- Retention limits: audit (1000 entries), snapshots (200 entries).

## Operational Controls
- Export gating by plan (e.g., governance/enterprise).
- Demo mode clearly marked; reset available for clean walkthroughs.
- Deployment guidance and environment controls documented.

## Residual Risks
- External data dependency: PWLB rate lookup (if enabled).
- Requires hosting environment to enforce HTTPS and backups.
- Assumes secure storage of environment variables and keys.

