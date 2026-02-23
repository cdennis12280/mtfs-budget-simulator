# Quick Start

> Quick links: `docs/QUICK_START.md` for setup/run, `docs/DEPLOYMENT.md` for hosting, `docs/AUTHENTICATION.md` for access control.


## Local Run (No Auth)
```bash
streamlit run app/main.py
```

## Local Run (Auth + Persistence)
```bash
export AUTH_MODE=password
export AUTH_USERS_FILE=./data/auth_users.json
export AUTH_TTL_MINUTES=60
export PERSISTENCE_ENABLED=true
export TENANT_DATA_DIR=./data/tenants
export FERNET_KEY="<set-a-key>"
export BILLING_PLANS_FILE=./data/billing_plans.json
export BILLING_SUBSCRIPTIONS_FILE=./data/billing_subscriptions.json
streamlit run app/main.py
```

## Demo Users
Default demo users are in `data/auth_users.json`. The demo password is `ChangeMe123!`.

## First Steps in the App
1. Open `Inputs` and confirm baseline values.
2. Adjust assumptions on the Dashboard sidebar.
3. Save a snapshot at each checkpoint.
4. Use `Reports` to export statutory PDFs and Excel packs.

## Demo Mode
Enable demo mode in `Settings` to load a curated dataset for walkthroughs.
