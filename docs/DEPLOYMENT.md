# Deployment Guidance

## Recommended Runtime
- Python 3.12
- Streamlit 1.41+

## Production Checklist
1. Set `AUTH_MODE=password` and define users.
2. Enable persistence with `PERSISTENCE_ENABLED=true`.
3. Configure `TENANT_DATA_DIR` to a durable volume.
4. Set `FERNET_KEY` for encryption at rest.
5. Configure plan/subscription data.

## Streamlit Launch
```bash
streamlit run app/main.py --server.headless true --server.port 8501 --server.address 0.0.0.0
```

## Docker (Skeleton)
Create a Dockerfile that:
1. Installs dependencies from `requirements.txt`
2. Copies `app/`, `modules/`, `data/`
3. Exposes port 8501

## Cloud Hosting
Suitable targets:
- Azure App Service (Linux)
- AWS ECS / Fargate
- Streamlit Community/Enterprise Cloud

## Monitoring
At minimum:
- Log collection
- Instance restart alerts
- HTTPS + TLS termination

