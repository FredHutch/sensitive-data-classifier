# Manual HTTPS Setup Guide

If the automated `setup-https.sh` script doesn't work, follow these manual steps.

## Step 1: Generate SSL Certificates

```bash
cd deployment
./generate-ssl-certs.sh
```

This creates:
- `ssl/cert.pem` - SSL certificate
- `ssl/key.pem` - Private key
- `ssl/csr.pem` - Certificate signing request

## Step 2: Find Your Docker Volume Name

```bash
# Start services to create volumes
cd deployment
docker-compose up -d

# List all volumes and find the ssl-certs volume
docker volume ls | grep ssl
```

You should see something like:
- `sensitive-data-classifier_ssl-certs`
- `deployment_ssl-certs`
- `phi-classifier_ssl-certs`

**Note the exact volume name for the next step.**

## Step 3: Copy Certificates to Docker Volume

Replace `YOUR_VOLUME_NAME` with the actual volume name from Step 2:

```bash
cd deployment

docker run --rm \
  -v $(pwd)/ssl:/source:ro \
  -v YOUR_VOLUME_NAME:/dest \
  alpine sh -c 'cp -v /source/cert.pem /source/key.pem /dest/ && ls -lah /dest/'
```

Example with actual volume name:
```bash
docker run --rm \
  -v $(pwd)/ssl:/source:ro \
  -v sensitive-data-classifier_ssl-certs:/dest \
  alpine sh -c 'cp -v /source/cert.pem /source/key.pem /dest/ && ls -lah /dest/'
```

You should see output confirming the files were copied:
```
'/source/cert.pem' -> '/dest/cert.pem'
'/source/key.pem' -> '/dest/key.pem'
total 16
drwxr-xr-x    2 root     root          4096 Nov 12 23:00 .
drwxr-xr-x    3 root     root          4096 Nov 12 23:00 ..
-rw-r--r--    1 root     root          1234 Nov 12 23:00 cert.pem
-rw-r--r--    1 root     root          1678 Nov 12 23:00 key.pem
```

## Step 4: Verify Certificates in Volume

```bash
# Replace YOUR_VOLUME_NAME with your actual volume name
docker run --rm -v YOUR_VOLUME_NAME:/certs alpine ls -lah /certs/
```

You should see both `cert.pem` and `key.pem`.

## Step 5: Restart Nginx

```bash
cd deployment
docker-compose restart nginx
```

## Step 6: Check Nginx Logs

```bash
docker-compose logs nginx
```

You should NOT see any errors about missing certificate files.

## Step 7: Test HTTPS

```bash
# Test HTTP (should work)
curl http://localhost/health

# Test HTTPS (should work with -k flag to ignore self-signed cert)
curl -k https://localhost/health
```

Both should return:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  ...
}
```

## Troubleshooting

### Issue: "cannot load certificate"

**Cause**: Certificates not in Docker volume

**Solution**: Repeat Step 3, ensuring you use the correct volume name from Step 2

### Issue: Volume name not found

**Cause**: Volume not created yet

**Solution**:
```bash
# Recreate volumes
cd deployment
docker-compose down -v
docker-compose up -d
# Then repeat from Step 2
```

### Issue: nginx keeps restarting

**Check logs**:
```bash
docker-compose logs --tail=50 nginx
```

**Common fixes**:
1. Verify certificates exist in volume (Step 4)
2. Check file permissions (should be 644)
3. Verify certificate format (PEM format)

### Issue: http2 warning

This is just a warning and doesn't affect functionality. The newer nginx syntax is already in use.

## Alternative: HTTP Only

If you don't need HTTPS right now, you can disable it:

### Option 1: Comment out HTTPS server block

Edit `deployment/nginx.conf` and comment out lines 69-134 (the entire HTTPS server block):

```nginx
# HTTPS Server
# server {
#   listen 443 ssl;
#   ...
# }
```

### Option 2: Don't expose port 443

Edit `deployment/docker-compose.yml`:

```yaml
nginx:
  ports:
    - "80:80"
    # - "443:443"  # Comment out HTTPS port
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

## Production Setup with Let's Encrypt

For production with trusted certificates:

1. **Install Certbot**:
```bash
sudo apt-get update
sudo apt-get install certbot
```

2. **Get Certificate** (requires domain name):
```bash
sudo certbot certonly --standalone -d your-domain.com
```

3. **Copy to deployment directory**:
```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem deployment/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem deployment/ssl/key.pem
sudo chown $USER:$USER deployment/ssl/*.pem
```

4. **Copy to Docker volume** (from Step 3)

5. **Set up auto-renewal**:
```bash
# Add renewal hook
sudo nano /etc/letsencrypt/renewal-hooks/deploy/docker-copy.sh
```

Content:
```bash
#!/bin/bash
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /path/to/deployment/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /path/to/deployment/ssl/key.pem
cd /path/to/deployment
docker run --rm -v $(pwd)/ssl:/source:ro -v YOUR_VOLUME_NAME:/dest alpine cp /source/*.pem /dest/
docker-compose restart nginx
```

Make executable:
```bash
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/docker-copy.sh
```

---

## Quick Reference

**Generate certs**:
```bash
cd deployment && ./generate-ssl-certs.sh
```

**Find volume**:
```bash
docker volume ls | grep ssl
```

**Copy certs** (replace VOLUME_NAME):
```bash
docker run --rm -v $(pwd)/ssl:/source:ro -v VOLUME_NAME:/dest alpine cp /source/*.pem /dest/
```

**Restart**:
```bash
docker-compose restart nginx
```

**Test**:
```bash
curl -k https://localhost/health
```

---

**Need help?** Check the application logs:
```bash
docker-compose logs -f
```
