# Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] Change `SECRET_KEY` in .env to a strong random value
- [ ] Set `DEBUG=False` in .env
- [ ] Update database credentials
- [ ] Review and update ALLOWED_HOSTS
- [ ] Run security check: `python security_check.py`
- [ ] Run all tests: `pytest test_main.py -v`
- [ ] Backup existing database
- [ ] Migrate passwords if upgrading: `python migrate_passwords.py`

### Security Configuration

1. **Generate Secret Key**
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```
   
   Add to .env:
   ```
   SECRET_KEY=your_generated_secret_key_here
   DEBUG=False
   ```

2. **Database Security**
   - Use strong database password
   - Restrict database access to localhost or specific IPs
   - Enable SSL for database connections if remote

3. **Environment Variables**
   ```bash
   # Production .env example
   DB_HOST=localhost
   DB_USER=clothing_shop_user
   DB_PASSWORD=your_strong_password_here
   DB_NAME=clothing_shop_production
   DB_CHARSET=utf8mb4
   
   SECRET_KEY=your_generated_secret_key
   DEBUG=False
   
   HOST=0.0.0.0
   PORT=8000
   ```

### Deployment Options

## Option 1: Direct Server Deployment

### Using Systemd (Recommended for Linux)

1. **Create service file**
   ```bash
   sudo nano /etc/systemd/system/clothing-shop.service
   ```

2. **Service configuration**
   ```ini
   [Unit]
   Description=Clothing Shop FastAPI Application
   After=network.target mysql.service
   
   [Service]
   Type=notify
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/clothing_shop_fastapi
   Environment="PATH=/var/www/clothing_shop_fastapi/venv/bin"
   ExecStart=/var/www/clothing_shop_fastapi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable clothing-shop
   sudo systemctl start clothing-shop
   sudo systemctl status clothing-shop
   ```

### Using Nginx as Reverse Proxy

1. **Install Nginx**
   ```bash
   sudo apt install nginx
   ```

2. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/clothing-shop
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       client_max_body_size 10M;
   
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   
       location /static {
           alias /var/www/clothing_shop_fastapi/static;
           expires 30d;
       }
   }
   ```

3. **Enable site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/clothing-shop /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

## Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application
   COPY . .
   
   # Create non-root user
   RUN useradd -m appuser && chown -R appuser:appuser /app
   USER appuser
   
   EXPOSE 8000
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       env_file:
         - .env
       depends_on:
         - db
       restart: always
   
     db:
       image: mysql:8
       environment:
         MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
         MYSQL_DATABASE: ${DB_NAME}
       volumes:
         - mysql_data:/var/lib/mysql
       restart: always
   
   volumes:
     mysql_data:
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   docker-compose logs -f
   ```

## Option 3: Cloud Platform (Heroku, Railway, etc.)

### Heroku Example

1. **Create Procfile**
   ```
   web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   heroku addons:create cleardb:ignite
   git push heroku main
   ```

## Performance Optimization

### 1. Worker Configuration
```bash
# For CPU-bound tasks
workers = (2 * CPU_cores) + 1

# Example: 4 CPU cores
uvicorn main:app --workers 9 --host 0.0.0.0 --port 8000
```

### 2. Database Connection Pool
Already configured in `db.py`. Adjust pool size if needed:
```python
pool_size=10  # Increase for high traffic
```

### 3. Static File Serving
Let Nginx serve static files directly (faster than FastAPI)

### 4. Enable Gzip Compression in Nginx
```nginx
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript;
```

## Monitoring

### 1. Application Logs
```bash
# View service logs
sudo journalctl -u clothing-shop -f

# Docker logs
docker-compose logs -f web
```

### 2. Error Monitoring
Consider integrating:
- Sentry for error tracking
- Prometheus for metrics
- Grafana for visualization

### 3. Health Checks
Add health check endpoint:
```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Backup Strategy

### Database Backups
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u ${DB_USER} -p${DB_PASSWORD} ${DB_NAME} > backup_${DATE}.sql
```

### Automated Backups (Cron)
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_script.sh
```

## Scaling

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Deploy multiple application instances
- Use shared session storage (Redis)

### Database Scaling
- Read replicas for read-heavy workload
- Database indexing (see DATABASE.md)
- Query optimization

## Troubleshooting

### Application Won't Start
1. Check logs: `sudo journalctl -u clothing-shop -n 50`
2. Verify .env file exists and is readable
3. Check database connection
4. Ensure port is not in use

### High Memory Usage
1. Reduce worker count
2. Adjust connection pool size
3. Check for memory leaks in custom code

### Slow Performance
1. Enable database query logging
2. Add missing indexes
3. Implement caching (Redis)
4. Use CDN for static files

## Security Maintenance

### Regular Updates
```bash
# Update dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
python security_check.py
```

### Security Headers (Nginx)
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## Rollback Procedure

1. **Stop service**
   ```bash
   sudo systemctl stop clothing-shop
   ```

2. **Restore from backup**
   ```bash
   mysql -u user -p database < backup_file.sql
   ```

3. **Switch to previous version**
   ```bash
   git checkout previous-tag
   pip install -r requirements.txt
   ```

4. **Restart service**
   ```bash
   sudo systemctl start clothing-shop
   ```

## Support

For deployment issues:
1. Check application logs
2. Review this deployment guide
3. Consult FastAPI documentation
4. Open issue on GitHub
