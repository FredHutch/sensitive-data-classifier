# SAML Authentication with Microsoft Entra ID (Azure AD)

This guide explains how to configure SAML-based Single Sign-On (SSO) authentication using Microsoft Entra ID (formerly Azure Active Directory) or other SAML 2.0 identity providers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Setup Instructions](#setup-instructions)
  - [Step 1: Configure Microsoft Entra ID](#step-1-configure-microsoft-entra-id)
  - [Step 2: Configure Application SAML Settings](#step-2-configure-application-saml-settings)
  - [Step 3: Enable SAML in Docker](#step-3-enable-saml-in-docker)
  - [Step 4: Test Authentication](#step-4-test-authentication)
- [Troubleshooting](#troubleshooting)
- [Other Identity Providers](#other-identity-providers)

---

## Prerequisites

- Microsoft Entra ID (Azure AD) tenant with administrator access
- Application deployed with HTTPS enabled (required for SAML)
- Domain name or public IP for your application

---

## Architecture Overview

```
┌──────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Browser    │────────▶│  PHI Classifier │────────▶│  Entra ID (IdP) │
│              │         │  (Service Prov.)│         │                 │
└──────────────┘         └─────────────────┘         └─────────────────┘
       ▲                          │                            │
       │                          │                            │
       └──────────────────────────┴────────────────────────────┘
              SAML Assertion (after authentication)
```

**SAML Flow**:
1. User accesses protected resource
2. Application redirects to Entra ID for authentication
3. User authenticates with Entra ID
4. Entra ID sends SAML assertion back to application
5. Application validates assertion and creates session

---

## Setup Instructions

### Step 1: Configure Microsoft Entra ID

#### 1.1 Create Enterprise Application

1. Sign in to [Azure Portal](https://portal.azure.com)
2. Navigate to **Microsoft Entra ID** (formerly Azure Active Directory)
3. Go to **Enterprise applications** → **New application**
4. Click **Create your own application**
5. Name: `PHI Classifier`
6. Select: **Integrate any other application you don't find in the gallery (Non-gallery)**
7. Click **Create**

#### 1.2 Configure Single Sign-On

1. In your new application, go to **Single sign-on**
2. Select **SAML**
3. Click **Edit** on **Basic SAML Configuration**

Configure the following:

**Identifier (Entity ID)**:
```
https://your-domain.com/saml/metadata
```

**Reply URL (Assertion Consumer Service URL)**:
```
https://your-domain.com/saml/acs
```

**Sign on URL** (optional):
```
https://your-domain.com/
```

**Logout URL**:
```
https://your-domain.com/saml/sls
```

4. Click **Save**

#### 1.3 Configure Attributes & Claims

Default claims are usually sufficient, but you can customize:

- **user.mail** → `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress`
- **user.displayname** → `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name`
- **user.groups** → `http://schemas.microsoft.com/ws/2008/06/identity/claims/groups`

#### 1.4 Download Certificate

1. In **SAML Certificates** section
2. Download **Certificate (Base64)**
3. Save as `entra_id.cer`

#### 1.5 Get Configuration URLs

From the **Set up PHI Classifier** section, note down:

- **Login URL**: `https://login.microsoftonline.com/<TENANT-ID>/saml2`
- **Microsoft Entra Identifier**: `https://sts.windows.net/<TENANT-ID>/`
- **Logout URL**: `https://login.microsoftonline.com/<TENANT-ID>/saml2`

Replace `<TENANT-ID>` with your actual tenant ID (a GUID).

#### 1.6 Assign Users

1. Go to **Users and groups**
2. Click **Add user/group**
3. Select users or groups that should have access
4. Click **Assign**

---

### Step 2: Configure Application SAML Settings

#### 2.1 Prepare Certificate

Convert the downloaded certificate to single-line format:

```bash
# Remove line breaks from certificate
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' entra_id.cer > entra_id_oneline.txt
```

Or manually:
1. Open `entra_id.cer` in text editor
2. Remove `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`
3. Remove all line breaks (make it one continuous string)
4. Save the result

#### 2.2 Create SAML Configuration Files

The application needs two configuration files in `/app/config/saml/`:

**File 1: `settings.json`**

```json
{
    "strict": true,
    "debug": false,
    "sp": {
        "entityId": "https://your-domain.com/saml/metadata",
        "assertionConsumerService": {
            "url": "https://your-domain.com/saml/acs",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "singleLogoutService": {
            "url": "https://your-domain.com/saml/sls",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        "x509cert": "",
        "privateKey": ""
    },
    "idp": {
        "entityId": "https://sts.windows.net/YOUR-TENANT-ID/",
        "singleSignOnService": {
            "url": "https://login.microsoftonline.com/YOUR-TENANT-ID/saml2",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "singleLogoutService": {
            "url": "https://login.microsoftonline.com/YOUR-TENANT-ID/saml2",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": "YOUR-CERTIFICATE-STRING-HERE"
    },
    "security": {
        "nameIdEncrypted": false,
        "authnRequestsSigned": false,
        "logoutRequestSigned": false,
        "logoutResponseSigned": false,
        "signMetadata": false,
        "wantMessagesSigned": false,
        "wantAssertionsSigned": true,
        "wantAssertionsEncrypted": false,
        "wantNameIdEncrypted": false,
        "requestedAuthnContext": true,
        "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
        "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256"
    }
}
```

Replace:
- `your-domain.com` with your actual domain
- `YOUR-TENANT-ID` with your Entra ID tenant ID
- `YOUR-CERTIFICATE-STRING-HERE` with the single-line certificate from Step 2.1

**File 2: `advanced_settings.json`**

```json
{
    "security": {
        "authnRequestsSigned": false,
        "wantAssertionsSigned": true
    },
    "contactPerson": {
        "technical": {
            "givenName": "IT Support",
            "emailAddress": "it@your-organization.com"
        },
        "support": {
            "givenName": "Help Desk",
            "emailAddress": "helpdesk@your-organization.com"
        }
    },
    "organization": {
        "en-US": {
            "name": "Your Organization",
            "displayname": "Your Organization Name",
            "url": "https://your-organization.com"
        }
    }
}
```

---

### Step 3: Enable SAML in Docker

#### 3.1 Update Environment Variables

Edit `deployment/app.env`:

```bash
# Enable SAML authentication
SAML_ENABLED=true
SAML_SETTINGS_PATH=/app/config/saml

# Session configuration for SAML
SESSION_TYPE=filesystem
SESSION_FILE_DIR=/app/flask_sessions
```

#### 3.2 Copy SAML Configuration to Docker

```bash
# Create local SAML config directory
mkdir -p deployment/saml_config

# Copy your settings.json and advanced_settings.json to this directory
cp settings.json deployment/saml_config/
cp advanced_settings.json deployment/saml_config/

# Update docker-compose.yml to mount local config (for testing)
# Add to app service volumes:
volumes:
  - uploads-data:/app/uploads
  - saml-config:/app/config/saml
  - flask-sessions:/app/flask_sessions
  - ./saml_config:/app/config/saml:ro  # Mount local config
```

Alternatively, copy files directly to the Docker volume:

```bash
# Start services to create volumes
cd deployment
docker-compose up -d

# Copy SAML config files to volume
docker run --rm \
  -v "$(pwd)/saml_config:/source" \
  -v "phi-classifier_saml-config:/dest" \
  alpine sh -c 'cp /source/*.json /dest/ && ls -la /dest/'

# Restart application to pick up config
docker-compose restart app
```

#### 3.3 Rebuild and Restart

```bash
cd deployment
docker-compose down
docker-compose build
docker-compose up -d
```

#### 3.4 Verify Logs

```bash
docker-compose logs app | grep -i saml
```

You should see:
```
SAML authentication enabled
Flask-Session initialized for SAML authentication
```

---

### Step 4: Test Authentication

#### 4.1 Access Application

1. Navigate to `https://your-domain.com`
2. You should be redirected to Microsoft Entra ID login
3. Sign in with your credentials
4. You should be redirected back and logged in

#### 4.2 Verify SAML Metadata

Visit: `https://your-domain.com/saml/metadata`

You should see XML metadata describing your Service Provider (SP) configuration.

#### 4.3 Check Session

Visit: `https://your-domain.com/saml/status`

Response (authenticated):
```json
{
  "authenticated": true,
  "email": "user@your-organization.com",
  "name": "User Name",
  "groups": ["group-id-1", "group-id-2"]
}
```

#### 4.4 Test Logout

Visit: `https://your-domain.com/saml/logout`

You should be logged out from both the application and Entra ID.

---

## Troubleshooting

### Common Issues

#### Issue 1: "SAML libraries not available"

**Cause**: Python SAML dependencies not installed

**Solution**:
```bash
# In Docker container
docker-compose exec app pip install python3-saml flask-session

# Or rebuild
docker-compose build
docker-compose up -d
```

#### Issue 2: "Certificate validation failed"

**Cause**: Incorrect certificate format

**Solution**:
- Ensure certificate is single-line with no headers/footers
- Verify no extra spaces or line breaks
- Re-download certificate from Entra ID if needed

#### Issue 3: "Invalid relay state"

**Cause**: HTTPS not properly configured

**Solution**:
- SAML requires HTTPS
- Verify SSL certificates are properly installed
- Check nginx is forwarding HTTPS headers correctly:
  ```nginx
  proxy_set_header X-Forwarded-Proto https;
  proxy_set_header X-Forwarded-Ssl on;
  ```

#### Issue 4: "Audience mismatch"

**Cause**: Entity ID doesn't match between SP and IdP

**Solution**:
- Verify `entityId` in `settings.json` matches exactly with Entra ID configuration
- Both must be: `https://your-domain.com/saml/metadata`

#### Issue 5: "Signature validation failed"

**Cause**: Certificate mismatch or security settings

**Solution**:
1. Re-download certificate from Entra ID
2. Verify security settings in `settings.json`:
   ```json
   "wantAssertionsSigned": true
   ```
3. Check Entra ID is signing assertions

### Debug Mode

Enable SAML debug logging:

Edit `settings.json`:
```json
{
    "debug": true,
    ...
}
```

View logs:
```bash
docker-compose logs -f app
```

---

## Other Identity Providers

The SAML implementation supports any SAML 2.0 compliant IdP:

### Okta

1. Create new SAML 2.0 application in Okta
2. Configure:
   - Single sign-on URL: `https://your-domain.com/saml/acs`
   - Audience URI: `https://your-domain.com/saml/metadata`
3. Download certificate and metadata
4. Update `settings.json` with Okta URLs

### OneLogin

1. Add application from OneLogin catalog
2. Configure SAML endpoints
3. Download X.509 certificate
4. Update configuration files

### Auth0

1. Create new SAML application
2. Configure callback URLs
3. Download signing certificate
4. Update `settings.json` with Auth0 tenant information

### Generic SAML 2.0 Provider

Required information:
- IdP Entity ID
- SSO Service URL
- SLO Service URL (optional)
- X.509 Signing Certificate

Update `settings.json` with your IdP's specific values.

---

## Security Best Practices

1. **Always use HTTPS** - SAML requires secure transport
2. **Rotate certificates regularly** - Update IdP certificate before expiration
3. **Enable assertion signing** - Verify SAML responses are signed
4. **Restrict access** - Only assign necessary users/groups in IdP
5. **Monitor authentication logs** - Review SAML auth attempts regularly
6. **Use short session timeouts** - Balance security vs. usability
7. **Enable MFA** - Configure multi-factor authentication in Entra ID

---

## Additional Resources

- [Microsoft Entra ID SAML Documentation](https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-saml-single-sign-on)
- [python3-saml Documentation](https://github.com/SAML-Toolkits/python3-saml)
- [SAML 2.0 Specification](http://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)

---

## Support

For issues with:
- **Entra ID configuration**: Contact Microsoft Support
- **Application SAML setup**: Check application logs and GitHub issues
- **Certificate problems**: Verify certificate format and expiration
- **Authentication flow**: Enable debug mode and review SAML traces

---

**Last Updated**: November 2025
