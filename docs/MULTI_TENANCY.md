# Multi-Tenancy & Data Isolation

> Quick links: `docs/QUICK_START.md` for setup/run, `docs/DEPLOYMENT.md` for hosting, `docs/AUTHENTICATION.md` for access control.


Multi-tenancy is implemented as per-tenant storage namespaces.

## Enable Persistence
Persistence is disabled by default to preserve the current session-only behavior.

To enable:
- `PERSISTENCE_ENABLED=true`
- `TENANT_DATA_DIR=data/tenants`

When enabled, audit logs and snapshots are stored under:
```
data/tenants/<tenant_id>/
  audit_log.json
  snapshots.json
```

## Tenant Resolution
Tenant is sourced from:
1. Auth session (`auth_tenant`)
2. `DEFAULT_TENANT` (env var)

## Encryption at Rest
If `FERNET_KEY` is provided, JSON data is encrypted before disk write.
Generate a key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Set:
- `FERNET_KEY=<generated-key>`

## Retention
Built-in pruning keeps:
- Audit log: last 1000 entries
- Snapshots: last 200 entries

Adjust retention in `modules/audit_log.py` and `modules/snapshots.py` if needed.

