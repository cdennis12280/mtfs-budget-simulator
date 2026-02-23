# Security & Compliance

This document outlines the minimum governance controls expected for S151 use.

## Access Control
- Enforce `AUTH_MODE=password`.
- Use PBKDF2-hashed passwords (no plaintext).
- Use `AUTH_TTL_MINUTES` to enforce session expiry.
- Assign `Admin/Analyst/Read-only` roles with least privilege.

## Data Protection (UK GDPR)
- Classify data (inputs, exports, audit logs).
- Maintain a retention policy (set in storage pruning).
- Provide data deletion workflow by tenant.
- Avoid storing personal data in model inputs.

## Audit & Logging
- Audit log is enabled in-session by default.
- Enable persistence for statutory audit retention.
- Export logs for governance review.

## Encryption at Rest
- Set `FERNET_KEY` to encrypt tenant JSON storage.
- Store keys securely (KMS or vault).

## Vulnerability Management
- Run dependency scans on `requirements.txt`.
- Keep Streamlit and core libs patched.
- Pen-test before production.

## Operational Controls
- Backups for tenant data store.
- Disaster recovery runbook.
- Incident response contact list.

