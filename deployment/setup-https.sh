#!/bin/bash
#
# Quick HTTPS Setup Script
# Sets up HTTPS with self-signed certificates
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}  HTTPS Setup for PHI Classifier${NC}"
echo -e "${GREEN}==========================================${NC}"
echo

# Check if we're in the deployment directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}ERROR: docker-compose.yml not found${NC}"
    echo "Please run this script from the deployment directory:"
    echo "  cd deployment"
    echo "  ./setup-https.sh"
    exit 1
fi

# Step 1: Check if certificates exist
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo -e "${YELLOW}[1/3] SSL certificates not found. Generating...${NC}"
    if [ ! -x "./generate-ssl-certs.sh" ]; then
        echo -e "${RED}ERROR: generate-ssl-certs.sh not found or not executable${NC}"
        exit 1
    fi
    ./generate-ssl-certs.sh
else
    echo -e "${GREEN}[1/3] SSL certificates found${NC}"
fi

# Step 2: Get the correct volume name
echo
echo -e "${GREEN}[2/3] Copying certificates to Docker volume...${NC}"

# Ensure services are running to create volumes
echo "Starting services to ensure volumes exist..."
docker-compose up -d

# Wait a moment for volumes to be created
sleep 2

# Try to detect the actual volume name
VOLUME_NAME=$(docker volume ls --format '{{.Name}}' | grep 'ssl-certs' | head -n 1)

if [ -z "$VOLUME_NAME" ]; then
    echo -e "${YELLOW}Could not auto-detect volume name. Trying common names...${NC}"
    # Try common project name patterns
    PROJECT_NAME=$(basename "$(dirname "$SCRIPT_DIR")" | tr '[:upper:]' '[:lower:]' | tr '-' '_' | tr '.' '_')
    VOLUME_NAME="${PROJECT_NAME}_ssl-certs"
fi

echo "Using volume name: ${VOLUME_NAME}"

# Copy certificates to volume
echo "Copying certificates..."
docker run --rm \
    -v "${SCRIPT_DIR}/ssl:/source:ro" \
    -v "${VOLUME_NAME}:/dest" \
    alpine sh -c 'cp -v /source/cert.pem /source/key.pem /dest/ && chmod 644 /dest/*.pem && ls -lah /dest/'

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Certificates copied successfully!${NC}"
else
    echo -e "${RED}Failed to copy certificates${NC}"
    echo
    echo "Manual copy instructions:"
    echo "1. List volumes: docker volume ls | grep ssl"
    echo "2. Copy manually: docker run --rm -v \$(pwd)/ssl:/source:ro -v YOUR_VOLUME_NAME:/dest alpine cp /source/*.pem /dest/"
    exit 1
fi

# Step 3: Restart nginx
echo
echo -e "${GREEN}[3/3] Restarting nginx...${NC}"
docker-compose restart nginx

# Wait for nginx to start
sleep 3

# Check if nginx is running
if docker-compose ps nginx | grep -q "Up"; then
    echo -e "${GREEN}Nginx restarted successfully!${NC}"
else
    echo -e "${RED}Nginx failed to start. Checking logs...${NC}"
    docker-compose logs --tail=20 nginx
    exit 1
fi

echo
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}  HTTPS Setup Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo
echo "Your application is now accessible via:"
echo -e "  HTTP:  ${GREEN}http://localhost${NC}"
echo -e "  HTTPS: ${GREEN}https://localhost${NC}"
echo
echo -e "${YELLOW}Note:${NC} Browsers will show a security warning for self-signed certificates."
echo "You can safely proceed by accepting the certificate."
echo
echo "To verify HTTPS is working:"
echo "  curl -k https://localhost/health"
echo
