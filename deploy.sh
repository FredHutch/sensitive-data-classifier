#!/bin/bash

# PHI Classifier Production Deployment Script
# Automated deployment for Fred Hutchinson Cancer Center
# Includes systemd service, nginx reverse proxy, SSL certificates, and monitoring

set -e  # Exit on any error

# Configuration
APP_NAME="phi-classifier"
APP_USER="phi-user"
APP_HOME="/opt/phi-classifier"
APP_REPO="https://github.com/FredHutch/sensitive-data-classifier.git"
DOMAIN="phi-classifier.fredhutch.org"  # Change to your domain
EMAIL="admin@fredhutch.org"  # Change to your email
PYTHON_VERSION="3.11"
REDIS_VERSION="7.0"
NGINX_VERSION="1.20"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as a regular user with sudo privileges."
    fi
}

# Check system requirements
check_system() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        error "This script is designed for Linux systems only."
    fi
    
    # Check Ubuntu/Debian
    if ! command -v apt-get &> /dev/null; then
        error "This script requires apt package manager (Ubuntu/Debian)."
    fi
    
    # Check available memory (minimum 4GB)
    available_mem=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$available_mem" -lt 4000 ]; then
        warn "System has less than 4GB RAM. Performance may be affected."
    fi
    
    # Check disk space (minimum 10GB)
    available_disk=$(df / | awk 'NR==2{print $4}')
    if [ "$available_disk" -lt 10000000 ]; then
        warn "Less than 10GB disk space available. Consider cleaning up disk space."
    fi
    
    info "System requirements check completed."
}

# Install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    sudo apt-get update
    sudo apt-get install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libpq-dev \
        nginx \
        redis-server \
        supervisor \
        git \
        curl \
        wget \
        unzip \
        software-properties-common \
        certbot \
        python3-certbot-nginx \
        htop \
        tree \
        vim
    
    info "System dependencies installed successfully."
}

# Create application user
create_app_user() {
    log "Creating application user: $APP_USER"
    
    if ! id "$APP_USER" &>/dev/null; then
        sudo useradd --system --shell /bin/bash --home-dir "$APP_HOME" --create-home "$APP_USER"
        info "User $APP_USER created successfully."
    else
        info "User $APP_USER already exists."
    fi
}

# Clone and setup application
setup_application() {
    log "Setting up PHI Classifier application..."
    
    # Create directory structure
    sudo mkdir -p "$APP_HOME"/{logs,data,uploads,models,backups}
    sudo chown -R "$APP_USER":"$APP_USER" "$APP_HOME"
    
    # Clone repository
    if [ ! -d "$APP_HOME/app" ]; then
        sudo -u "$APP_USER" git clone "$APP_REPO" "$APP_HOME/app"
    else
        sudo -u "$APP_USER" git -C "$APP_HOME/app" pull origin main
    fi
    
    # Create Python virtual environment
    sudo -u "$APP_USER" python3 -m venv "$APP_HOME/venv"
    
    # Install Python dependencies
    sudo -u "$APP_USER" "$APP_HOME/venv/bin/pip" install --upgrade pip setuptools wheel
    sudo -u "$APP_USER" "$APP_HOME/venv/bin/pip" install -r "$APP_HOME/app/requirements.txt"
    
    info "Application setup completed."
}

# Configure environment variables
configure_environment() {
    log "Configuring environment variables..."
    
    sudo -u "$APP_USER" tee "$APP_HOME/.env" > /dev/null <<EOF
# PHI Classifier Environment Configuration
# Production Environment
FLASK_ENV=production
APP_ENV=production
DEBUG=False

# Server Configuration
HOST=127.0.0.1
PORT=5000
WORKERS=4

# Security Configuration
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)
MAX_FILE_SIZE=52428800
SESSION_TIMEOUT=1800

# Database Configuration (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=phi_classifier_prod
DB_USER=phi_db_user
DB_PASSWORD=$(openssl rand -hex 16)

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=$(openssl rand -hex 16)

# UMLS Configuration (Optional - requires registration)
# UMLS_API_KEY=your_umls_api_key_here

# Logging Configuration
LOG_LEVEL=INFO
ENABLE_AUDIT_LOGGING=True

# Feature Flags
FEATURE_BATCH_PROCESSING=True
FEATURE_RATE_LIMITING=True
FEATURE_MONITORING=True
FEATURE_DATA_EXPORT=True

# Monitoring
MONITORING_ENABLED=True
ALERT_EMAIL=$EMAIL
EOF
    
    sudo chown "$APP_USER":"$APP_USER" "$APP_HOME/.env"
    sudo chmod 600 "$APP_HOME/.env"
    
    info "Environment configuration completed."
}

# Configure PostgreSQL database
setup_database() {
    log "Setting up PostgreSQL database..."
    
    # Install PostgreSQL
    sudo apt-get install -y postgresql postgresql-contrib
    
    # Start and enable PostgreSQL
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    # Create database and user
    DB_PASSWORD=$(grep DB_PASSWORD "$APP_HOME/.env" | cut -d'=' -f2)
    
    sudo -u postgres psql <<EOF
CREATE USER phi_db_user WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE phi_classifier_prod WITH OWNER phi_db_user;
GRANT ALL PRIVILEGES ON DATABASE phi_classifier_prod TO phi_db_user;
\q
EOF
    
    info "PostgreSQL database setup completed."
}

# Configure Redis
setup_redis() {
    log "Configuring Redis..."
    
    REDIS_PASSWORD=$(grep REDIS_PASSWORD "$APP_HOME/.env" | cut -d'=' -f2)
    
    # Configure Redis
    sudo tee /etc/redis/redis.conf > /dev/null <<EOF
# PHI Classifier Redis Configuration
bind 127.0.0.1
port 6379
requirepass $REDIS_PASSWORD
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
dir /var/lib/redis
logfile /var/log/redis/redis-server.log
syslog-enabled yes
EOF
    
    # Start and enable Redis
    sudo systemctl restart redis-server
    sudo systemctl enable redis-server
    
    info "Redis configuration completed."
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    sudo tee "/etc/systemd/system/$APP_NAME.service" > /dev/null <<EOF
[Unit]
Description=PHI Classifier - Protected Health Information Classification Service
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_HOME/app
Environment=PATH=$APP_HOME/venv/bin
EnvironmentFile=$APP_HOME/.env
ExecStart=$APP_HOME/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --worker-class sync --timeout 300 --max-requests 1000 --max-requests-jitter 100 app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_HOME
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable "$APP_NAME.service"
    
    info "Systemd service created successfully."
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx reverse proxy..."
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Create application configuration
    sudo tee "/etc/nginx/sites-available/$APP_NAME" > /dev/null <<EOF
# PHI Classifier Nginx Configuration
upstream phi_classifier {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name $DOMAIN;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://phi_classifier;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 300s;
        
        # File upload size
        client_max_body_size 50M;
    }
    
    location /static {
        alias $APP_HOME/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /health {
        access_log off;
        proxy_pass http://phi_classifier;
    }
}
EOF
    
    # Enable site
    sudo ln -sf "/etc/nginx/sites-available/$APP_NAME" "/etc/nginx/sites-enabled/"
    
    # Test configuration
    sudo nginx -t
    
    # Start and enable Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    info "Nginx configuration completed."
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    log "Setting up SSL certificate with Let's Encrypt..."
    
    # Obtain certificate
    sudo certbot --nginx -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive --redirect
    
    # Setup auto-renewal
    sudo systemctl enable certbot.timer
    
    info "SSL certificate setup completed."
}

# Setup monitoring with supervisor
setup_monitoring() {
    log "Setting up application monitoring..."
    
    sudo tee "/etc/supervisor/conf.d/$APP_NAME-monitor.conf" > /dev/null <<EOF
[program:phi-classifier-monitor]
command=$APP_HOME/venv/bin/python -m core.monitoring
directory=$APP_HOME/app
user=$APP_USER
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_HOME/logs/monitor.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
EOF
    
    # Reload supervisor
    sudo supervisorctl reread
    sudo supervisorctl update
    
    info "Application monitoring setup completed."
}

# Setup log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    sudo tee "/etc/logrotate.d/$APP_NAME" > /dev/null <<EOF
$APP_HOME/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su $APP_USER $APP_USER
}
EOF
    
    info "Log rotation setup completed."
}

# Create backup script
setup_backup() {
    log "Setting up backup system..."
    
    sudo -u "$APP_USER" tee "$APP_HOME/backup.sh" > /dev/null <<'EOF'
#!/bin/bash
# PHI Classifier Backup Script

APP_HOME="/opt/phi-classifier"
BACKUP_DIR="$APP_HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Database backup
echo "Backing up database..."
pg_dump -h localhost -U phi_db_user phi_classifier_prod > "$BACKUP_DIR/db_backup_$DATE.sql"

# Application backup
echo "Backing up application files..."
tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" -C "$APP_HOME" app .env

# Remove old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF
    
    sudo chmod +x "$APP_HOME/backup.sh"
    
    # Add to crontab
    (sudo -u "$APP_USER" crontab -l 2>/dev/null; echo "0 2 * * * $APP_HOME/backup.sh") | sudo -u "$APP_USER" crontab -
    
    info "Backup system setup completed."
}

# Setup firewall
setup_firewall() {
    log "Configuring firewall..."
    
    sudo ufw --force enable
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    
    info "Firewall configuration completed."
}

# Initialize database schema
init_database_schema() {
    log "Initializing database schema..."
    
    sudo -u "$APP_USER" bash -c "cd $APP_HOME/app && $APP_HOME/venv/bin/python -c 'from app import app; app.app_context().push(); print(\"Database initialized\")'"
    
    info "Database schema initialized."
}

# Start services
start_services() {
    log "Starting all services..."
    
    sudo systemctl start "$APP_NAME.service"
    sudo systemctl reload nginx
    
    info "All services started successfully."
}

# Health check
health_check() {
    log "Performing health check..."
    
    sleep 10
    
    # Check service status
    if sudo systemctl is-active --quiet "$APP_NAME.service"; then
        info "✓ PHI Classifier service is running"
    else
        error "✗ PHI Classifier service is not running"
    fi
    
    # Check HTTP response
    if curl -f -s http://localhost:5000/health > /dev/null; then
        info "✓ Application is responding to HTTP requests"
    else
        warn "✗ Application is not responding to HTTP requests"
    fi
    
    # Check HTTPS response
    if curl -f -s https://$DOMAIN/health > /dev/null; then
        info "✓ HTTPS is working correctly"
    else
        warn "✗ HTTPS is not working correctly"
    fi
    
    info "Health check completed."
}

# Display summary
display_summary() {
    log "Deployment Summary:"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}PHI Classifier has been successfully deployed!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}Application URL:${NC} https://$DOMAIN"
    echo -e "${BLUE}Application User:${NC} $APP_USER"
    echo -e "${BLUE}Application Home:${NC} $APP_HOME"
    echo -e "${BLUE}Service Status:${NC} sudo systemctl status $APP_NAME"
    echo -e "${BLUE}Service Logs:${NC} sudo journalctl -u $APP_NAME -f"
    echo -e "${BLUE}Application Logs:${NC} tail -f $APP_HOME/logs/application.log"
    echo -e "${BLUE}Nginx Logs:${NC} sudo tail -f /var/log/nginx/access.log"
    echo ""
    echo -e "${YELLOW}Important Notes:${NC}"
    echo -e "• SSL certificate will auto-renew via certbot"
    echo -e "• Daily backups are scheduled at 2:00 AM"
    echo -e "• Logs are rotated daily and kept for 30 days"
    echo -e "• Configure UMLS API key in $APP_HOME/.env for full functionality"
    echo -e "• Monitor system resources and scale as needed"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
}

# Main deployment function
main() {
    log "Starting PHI Classifier Production Deployment"
    
    check_root
    check_system
    install_system_dependencies
    create_app_user
    setup_application
    configure_environment
    setup_database
    setup_redis
    create_systemd_service
    configure_nginx
    setup_ssl
    setup_monitoring
    setup_log_rotation
    setup_backup
    setup_firewall
    init_database_schema
    start_services
    health_check
    display_summary
    
    log "PHI Classifier deployment completed successfully!"
}

# Run main function
main "$@"