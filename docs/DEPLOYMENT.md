# Deployment Guide

## Local development
- python3 -m venv venv && source venv/bin/activate
- pip install -r requirements.txt
- export FLASK_APP=app.py
- flask run

## Production (Ubuntu)
- Create system user and directories.
- python3 -m venv /opt/phi/venv && source /opt/phi/venv/bin/activate
- pip install -r requirements.txt
- Configure gunicorn systemd service to run app:app
- Configure nginx reverse proxy with TLS
- Set environment variables (UMLS_API_KEY if used), SECRET_KEY

## Security
- Process PHI locally only.
- Rotate secrets, limit network egress, apply OS hardening.
