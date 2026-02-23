# Billing & Subscription Gating

> Quick links: `docs/QUICK_START.md` for setup/run, `docs/DEPLOYMENT.md` for hosting, `docs/AUTHENTICATION.md` for access control.


Billing is modeled as a plan + feature flags per tenant. This provides governance control without blocking development.

## Plans
Default plans:
- `community`: view-only
- `governance`: view + exports + audit
- `enterprise`: view + exports + audit + sso + multi-tenant

Override via:
- `BILLING_PLANS_JSON` (inline JSON)
- `BILLING_PLANS_FILE` (path)
- `data/billing_plans.json`

Example:
```json
{
  "governance": { "label": "Governance", "features": ["view", "exports", "audit"] },
  "enterprise": { "label": "Enterprise", "features": ["view", "exports", "audit", "sso", "multi_tenant"] }
}
```

## Subscriptions
Per-tenant mapping:
- `BILLING_SUBSCRIPTIONS_JSON`
- `BILLING_SUBSCRIPTIONS_FILE`
- `data/billing_subscriptions.json`

Example:
```json
{
  "council-a": "governance",
  "council-b": "enterprise"
}
```

## Feature Gates
Current gates:
- `exports`: disables report + Excel/Power BI export actions.

Add more gates as required by plan/feature strategy.

