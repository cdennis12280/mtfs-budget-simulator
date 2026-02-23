# Authentication & Roles

This app supports password-based authentication with role- and tenant-aware access control.

## Enable Auth
Set the environment variable:
- `AUTH_MODE=password`

By default, auth is disabled to keep local dev friction-free.

## Users File
Provide users via JSON:
- `AUTH_USERS_JSON` (inline JSON string)
- `AUTH_USERS_FILE` (path to JSON file)
- `data/auth_users.json` (auto-loaded if present)

Example file structure:
```json
{
  "s151_officer": {
    "password": "pbkdf2$120000$salt123$<hash>",
    "role": "Admin",
    "tenant": "council-a"
  },
  "analyst": {
    "password": "pbkdf2$120000$salt123$<hash>",
    "role": "Analyst",
    "tenant": "council-a"
  },
  "viewer": {
    "password": "pbkdf2$120000$salt123$<hash>",
    "role": "Read-only",
    "tenant": "council-a"
  }
}
```

Sample `data/auth_users.json` uses password `ChangeMe123!` for all demo users. Update before production.

## Password Hashing
Supported format:
- `pbkdf2$iterations$salt$hash`

Plaintext is disabled by default. To allow plaintext (not recommended):
- `ALLOW_PLAINTEXT_PASSWORDS=true`

## Session TTL
Set:
- `AUTH_TTL_MINUTES=60`

## Roles
Default role mapping:
- `Admin`: full access
- `Analyst`: authoring access
- `Read-only`: view-only pages

Roles are enforced per page in the Streamlit router.
