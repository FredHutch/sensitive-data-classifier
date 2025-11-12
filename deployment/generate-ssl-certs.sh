#!/bin/bash
#
# SSL Certificate Generation Script
# Generates self-signed certificates for development/testing
# For production, use certificates from a trusted CA (Let's Encrypt, DigiCert, etc.)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_DIR="${SCRIPT_DIR}/ssl"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}   SSL Certificate Generation${NC}"
echo -e "${GREEN}==================================================${NC}"
echo

# Check if certificates already exist
if [ -f "${CERT_DIR}/cert.pem" ] && [ -f "${CERT_DIR}/key.pem" ]; then
    echo -e "${YELLOW}WARNING: SSL certificates already exist in ${CERT_DIR}${NC}"
    read -p "Do you want to regenerate them? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi
fi

# Create certificate directory
mkdir -p "${CERT_DIR}"

# Prompt for certificate details
echo -e "${GREEN}Enter certificate details:${NC}"
read -p "Country Code (e.g., US): " COUNTRY
read -p "State/Province: " STATE
read -p "City/Locality: " CITY
read -p "Organization Name: " ORG
read -p "Organizational Unit (e.g., IT Department): " OU
read -p "Common Name (domain, e.g., phi-classifier.local): " CN

# Prompt for SANs (Subject Alternative Names)
echo
echo -e "${YELLOW}Enter Subject Alternative Names (SANs) - domains/IPs this cert will be valid for${NC}"
echo "Examples: localhost, 192.168.1.100, phi-classifier.mydomain.com"
read -p "SAN 1 (press Enter to skip): " SAN1
read -p "SAN 2 (press Enter to skip): " SAN2
read -p "SAN 3 (press Enter to skip): " SAN3

# Build SAN string
SAN_STRING="DNS:${CN}"
[ -n "$SAN1" ] && SAN_STRING="${SAN_STRING},DNS:${SAN1}"
[ -n "$SAN2" ] && SAN_STRING="${SAN_STRING},DNS:${SAN2}"
[ -n "$SAN3" ] && SAN_STRING="${SAN_STRING},DNS:${SAN3}"

# Add localhost and common SANs
SAN_STRING="${SAN_STRING},DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:::1"

# Certificate validity period
read -p "Certificate validity (days, default 365): " DAYS
DAYS=${DAYS:-365}

echo
echo -e "${GREEN}Generating SSL certificate...${NC}"
echo "  Country: ${COUNTRY}"
echo "  State: ${STATE}"
echo "  City: ${CITY}"
echo "  Organization: ${ORG}"
echo "  Organizational Unit: ${OU}"
echo "  Common Name: ${CN}"
echo "  SANs: ${SAN_STRING}"
echo "  Validity: ${DAYS} days"
echo

# Generate private key
echo -e "${GREEN}[1/3] Generating private key...${NC}"
openssl genrsa -out "${CERT_DIR}/key.pem" 4096

# Create OpenSSL config for SAN
cat > "${CERT_DIR}/openssl.cnf" <<EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=${COUNTRY}
ST=${STATE}
L=${CITY}
O=${ORG}
OU=${OU}
CN=${CN}

[v3_req]
keyUsage = keyEncipherment, dataEncipherment, digitalSignature
extendedKeyUsage = serverAuth
subjectAltName = ${SAN_STRING}
EOF

# Generate certificate signing request
echo -e "${GREEN}[2/3] Generating certificate signing request...${NC}"
openssl req -new -key "${CERT_DIR}/key.pem" -out "${CERT_DIR}/csr.pem" \
    -config "${CERT_DIR}/openssl.cnf"

# Generate self-signed certificate
echo -e "${GREEN}[3/3] Generating self-signed certificate...${NC}"
openssl x509 -req -days ${DAYS} \
    -in "${CERT_DIR}/csr.pem" \
    -signkey "${CERT_DIR}/key.pem" \
    -out "${CERT_DIR}/cert.pem" \
    -extensions v3_req \
    -extfile "${CERT_DIR}/openssl.cnf"

# Set appropriate permissions
chmod 600 "${CERT_DIR}/key.pem"
chmod 644 "${CERT_DIR}/cert.pem"

# Display certificate information
echo
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}   Certificate Generated Successfully!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo
echo "Certificate files created in: ${CERT_DIR}"
echo "  - Private Key: ${CERT_DIR}/key.pem"
echo "  - Certificate: ${CERT_DIR}/cert.pem"
echo "  - CSR: ${CERT_DIR}/csr.pem"
echo
echo -e "${YELLOW}Certificate Details:${NC}"
openssl x509 -in "${CERT_DIR}/cert.pem" -noout -text | grep -A 3 "Subject:"
openssl x509 -in "${CERT_DIR}/cert.pem" -noout -text | grep -A 1 "Subject Alternative Name"
echo
openssl x509 -in "${CERT_DIR}/cert.pem" -noout -dates
echo
echo -e "${YELLOW}To copy certificates to Docker volume:${NC}"
echo "  docker run --rm -v ssl-certs:/ssl -v ${CERT_DIR}:/certs alpine sh -c 'cp /certs/*.pem /ssl/'"
echo
echo -e "${YELLOW}To enable HTTPS in nginx.conf:${NC}"
echo "  1. Uncomment the 'return 301 https://...' line in the HTTP server block"
echo "  2. Restart nginx: docker-compose restart nginx"
echo
echo -e "${RED}WARNING: This is a self-signed certificate for development/testing only!${NC}"
echo -e "${RED}For production, use certificates from a trusted CA (Let's Encrypt, etc.)${NC}"
echo
