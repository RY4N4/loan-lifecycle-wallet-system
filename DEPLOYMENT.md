# 🚀 Production Deployment Guide

## Overview

This guide covers deploying the Loan Lifecycle Backend to a production environment with proper security, monitoring, and scalability considerations.

---

## Deployment Architecture

```
Internet
    ↓
[Load Balancer / CDN]
    ↓
[Nginx Reverse Proxy]
    ↓
[Gunicorn/Uvicorn Workers] (4-8 instances)
    ↓
[PostgreSQL Primary DB]
    ↓
[PostgreSQL Replica] (Optional - for read scaling)
```

---

## 1. Server Requirements

### Minimum Specifications

**Application Server:**
- CPU: 2 vCPUs
- RAM: 4GB
- Storage: 20GB SSD
- OS: Ubuntu 20.04 LTS or later

**Database Server:**
- CPU: 2 vCPUs
- RAM: 8GB
- Storage: 100GB SSD (depends on transaction volume)
- OS: Ubuntu 20.04 LTS or later

### Recommended for Production

**Application Server:**
- CPU: 4 vCPUs
- RAM: 8GB
- Storage: 50GB SSD

**Database Server:**
- CPU: 4 vCPUs
- RAM: 16GB
- Storage: 500GB SSD with IOPS provisioning

---

## 2. Server Setup

### Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Dependencies

```bash
# Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# PostgreSQL 14
sudo apt install postgresql postgresql-contrib -y

# Nginx
sudo apt install nginx -y

# Supervisor (process management)
sudo apt install supervisor -y

# SSL certificates
sudo apt install certbot python3-certbot-nginx -y
```

---

## 3. Database Setup

### PostgreSQL Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

-- Create production database
CREATE DATABASE loan_db_prod;

-- Create app user with strong password
CREATE USER loan_app WITH ENCRYPTED PASSWORD 'STRONG_RANDOM_PASSWORD';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE loan_db_prod TO loan_app;

-- Exit psql
\q
```

### Optimize PostgreSQL for Production

Edit `/etc/postgresql/14/main/postgresql.conf`:

```ini
# Connection Settings
max_connections = 100
shared_buffers = 2GB           # 25% of RAM
effective_cache_size = 6GB     # 75% of RAM
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9

# Write Ahead Log
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB

# Query Planner
random_page_cost = 1.1         # For SSD
effective_io_concurrency = 200

# Logging
log_destination = 'csvlog'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
log_min_duration_statement = 1000  # Log slow queries
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## 4. Application Deployment

### Create Application User

```bash
sudo useradd -m -s /bin/bash loanapp
sudo su - loanapp
```

### Clone and Setup Application

```bash
# Clone repository
git clone <your-repo-url> /home/loanapp/loan-backend
cd /home/loanapp/loan-backend

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install production WSGI server
pip install gunicorn
```

### Configure Environment Variables

Create `/home/loanapp/loan-backend/.env`:

```env
# Database
DATABASE_URL=postgresql://loan_app:STRONG_PASSWORD@localhost:5432/loan_db_prod

# Security
SECRET_KEY=<generate-with-secrets.token_urlsafe(64)>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENV=production
DEBUG=False
```

**Generate secure secret key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Database Migrations

```bash
# Run migrations (or initialize tables)
python -c "from app.database import init_db; init_db()"
```

---

## 5. Application Server Configuration

### Gunicorn Configuration

Create `/home/loanapp/loan-backend/gunicorn_config.py`:

```python
"""Gunicorn configuration for production"""

import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/loanapp/logs/access.log"
errorlog = "/home/loanapp/logs/error.log"
loglevel = "info"

# Process naming
proc_name = "loan-backend"

# Server mechanics
daemon = False
pidfile = "/home/loanapp/loan-backend.pid"
user = "loanapp"
group = "loanapp"
```

Create log directory:
```bash
mkdir -p /home/loanapp/logs
```

---

## 6. Supervisor Configuration

Create `/etc/supervisor/conf.d/loan-backend.conf`:

```ini
[program:loan-backend]
command=/home/loanapp/loan-backend/venv/bin/gunicorn -c gunicorn_config.py app.main:app
directory=/home/loanapp/loan-backend
user=loanapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/loanapp/logs/supervisor.log
environment=PATH="/home/loanapp/loan-backend/venv/bin"
```

Start application:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start loan-backend
```

Check status:
```bash
sudo supervisorctl status loan-backend
```

---

## 7. Nginx Configuration

### Create Nginx Configuration

Create `/etc/nginx/sites-available/loan-backend`:

```nginx
upstream loan_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # Logging
    access_log /var/log/nginx/loan-backend-access.log;
    error_log /var/log/nginx/loan-backend-error.log;

    # Max body size
    client_max_body_size 10M;

    location / {
        proxy_pass http://loan_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://loan_backend/health;
        access_log off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/loan-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 8. SSL/TLS Configuration

### Get SSL Certificate with Let's Encrypt

```bash
sudo certbot --nginx -d api.yourdomain.com
```

Certbot will:
- Obtain SSL certificate
- Modify Nginx configuration
- Set up auto-renewal

### Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

---

## 9. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow PostgreSQL (only from localhost)
sudo ufw allow from 127.0.0.1 to any port 5432

# Check status
sudo ufw status
```

---

## 10. Monitoring & Logging

### Application Monitoring

Install monitoring tools:

```bash
# Install Prometheus node exporter
sudo apt install prometheus-node-exporter -y

# Or use a SaaS solution:
# - New Relic
# - DataDog
# - Sentry (for error tracking)
```

### Log Rotation

Create `/etc/logrotate.d/loan-backend`:

```
/home/loanapp/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0640 loanapp loanapp
}
```

### PostgreSQL Monitoring

```sql
-- Monitor active connections
SELECT count(*) FROM pg_stat_activity;

-- Monitor database size
SELECT pg_size_pretty(pg_database_size('loan_db_prod'));

-- Monitor slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;
```

---

## 11. Backup Strategy

### Database Backups

Create backup script `/home/loanapp/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/loanapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="loan_db_prod"

# Create backup
pg_dump -U loan_app $DB_NAME | gzip > $BACKUP_DIR/$DB_NAME-$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $DB_NAME-$DATE.sql.gz"
```

Schedule with cron:
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/loanapp/backup.sh >> /home/loanapp/logs/backup.log 2>&1
```

### Restore from Backup

```bash
gunzip < backup.sql.gz | psql -U loan_app loan_db_prod
```

---

## 12. Performance Optimization

### PgBouncer (Connection Pooling)

Install:
```bash
sudo apt install pgbouncer -y
```

Configure `/etc/pgbouncer/pgbouncer.ini`:
```ini
[databases]
loan_db_prod = host=127.0.0.1 port=5432 dbname=loan_db_prod

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 100
default_pool_size = 20
```

Update application DATABASE_URL:
```env
DATABASE_URL=postgresql://loan_app:PASSWORD@localhost:6432/loan_db_prod
```

### Redis Caching (Optional)

```bash
sudo apt install redis-server -y
pip install redis aioredis
```

---

## 13. Security Checklist

- [ ] Strong SECRET_KEY generated (64+ characters)
- [ ] Database passwords are complex and unique
- [ ] SSL/TLS enabled (HTTPS only)
- [ ] Firewall configured (UFW)
- [ ] Database not exposed to internet
- [ ] Rate limiting enabled in Nginx
- [ ] Security headers configured
- [ ] Regular backups scheduled
- [ ] Log rotation configured
- [ ] Non-root user running application
- [ ] SSH key-based authentication only
- [ ] Fail2ban installed (optional)

---

## 14. Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Backup strategy tested

### Deployment

- [ ] Stop old version (if any)
- [ ] Pull latest code
- [ ] Run database migrations
- [ ] Restart application server
- [ ] Verify health endpoint
- [ ] Check logs for errors

### Post-Deployment

- [ ] Smoke test critical endpoints
- [ ] Monitor error rates
- [ ] Check database performance
- [ ] Verify SSL certificate
- [ ] Test from external network

---

## 15. Useful Commands

```bash
# Restart application
sudo supervisorctl restart loan-backend

# View application logs
tail -f /home/loanapp/logs/error.log

# View Nginx logs
sudo tail -f /var/log/nginx/loan-backend-error.log

# Check application status
sudo supervisorctl status

# Reload Nginx
sudo nginx -s reload

# Check PostgreSQL connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Monitor system resources
htop

# Check disk usage
df -h
```

---

## 16. Troubleshooting

### Application Won't Start

```bash
# Check supervisor logs
sudo tail -n 100 /home/loanapp/logs/supervisor.log

# Check if port is in use
sudo lsof -i :8000

# Test gunicorn manually
cd /home/loanapp/loan-backend
source venv/bin/activate
gunicorn -c gunicorn_config.py app.main:app
```

### Database Connection Issues

```bash
# Test database connection
psql -U loan_app -h localhost -d loan_db_prod

# Check PostgreSQL status
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### High CPU Usage

```bash
# Check slow queries
sudo -u postgres psql loan_db_prod

SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

---

## 17. Scaling Strategies

### Vertical Scaling
- Increase server CPU/RAM
- Optimize PostgreSQL configuration
- Enable PgBouncer connection pooling

### Horizontal Scaling
- Add more application servers behind load balancer
- Set up PostgreSQL read replicas
- Implement Redis caching layer

### Database Optimization
- Create appropriate indexes
- Partition transaction table by date
- Archive old data
- Optimize queries

---

## 18. Maintenance Schedule

**Daily:**
- Check error logs
- Monitor disk space
- Verify backups completed

**Weekly:**
- Review application metrics
- Check for security updates
- Analyze slow queries

**Monthly:**
- Update dependencies
- Review and clean old logs
- Test backup restoration
- Security audit

---

## 19. Cost Optimization

**DigitalOcean Pricing (Example):**
- App Server (4GB RAM): $24/month
- Database Server (8GB RAM): $48/month
- Load Balancer (optional): $12/month
- **Total: ~$84/month**

**AWS Pricing (Example):**
- EC2 t3.medium (2 vCPU, 4GB): ~$30/month
- RDS PostgreSQL db.t3.medium: ~$60/month
- **Total: ~$90/month**

---

## 20. Production Environment Variables

```env
# Application
ENV=production
DEBUG=False

# Database
DATABASE_URL=postgresql://loan_app:PASSWORD@localhost:6432/loan_db_prod

# Security
SECRET_KEY=<64-character-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (restrict to your frontend domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
NEW_RELIC_LICENSE_KEY=...
```

---

**🎉 Your production deployment is complete!**

Monitor logs and metrics closely for the first few days after deployment.
