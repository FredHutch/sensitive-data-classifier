# Deployment (Docker Compose) Quick Start

This directory provides a minimal containerized deployment option.

Prereqs
- Docker and Docker Compose v2

Steps
- cd deployment
- cp app.env .env  # or edit app.env and reference via env_file
- docker compose up --build -d
- Access http://localhost/

Notes
- TLS: terminate at a load balancer or add a certbot container to nginx.
- Secrets: do not commit secrets; use environment variables or a secrets manager.
- For production, tune gunicorn and consider external PostgreSQL/Redis.
