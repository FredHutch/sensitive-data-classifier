#!/bin/bash
#
# Quick HTTPS Setup Script
# Sets up HTTPS with self-signed certificates for development
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "  Quick HTTPS Setup"
echo "=========================================="
echo

# Step 1: Generate certificates
echo "[1/3] Generating self-signed SSL certificates..."
"${SCRIPT_DIR}/generate-ssl-certs.sh"

# Step 2: Copy certificates to Docker volume
echo
echo "[2/3] Copying certificates to Docker volume..."
cd "${SCRIPT_DIR}"
docker-compose up -d --no-deps nginx  # Ensure volume exists
docker run --rm \
    -v "$(pwd)/ssl:/certs" \
    -v "phi-classifier_ssl-certs:/ssl" \
    alpine sh -c 'cp /certs/*.pem /ssl/ && chmod 644 /ssl/*.pem && ls -la /ssl/'

# Step 3: Restart nginx
echo
echo "[3/3] Restarting nginx..."
docker-compose restart nginx

echo
echo "=========================================="
echo "  HTTPS Setup Complete!"
echo "=========================================="
echo
echo "Your application is now accessible via:"
echo "  HTTP:  http://localhost"
echo "  HTTPS: https://localhost"
echo
echo "Note: Browsers will show a security warning for self-signed certificates."
echo "You can safely proceed by accepting the certificate."
echo
