# Deployment Guide

## Pre-Deployment Checklist

- [ ] Set all environment variables in `.env` file
- [ ] Change `SECRET_KEY` to a strong random value (min 32 chars)
- [ ] Configure `ALLOWED_ORIGINS` with your production domain
- [ ] Set up PostgreSQL database (recommended for production)
- [ ] Review and update CORS settings
- [ ] Test all functionality in staging environment
- [ ] Run security audit (`safety check`)
- [ ] Review `SECURITY.md` for security recommendations

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp backend/.env.example backend/.env
```

Required variables:
- `SECRET_KEY` - Strong random string (min 32 characters)
- `DATABASE_URL` - Database connection string
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins

## Backend Deployment

### Option 1: Using Uvicorn (Simple)

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 2: Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Option 3: Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t catalog-backend .
docker run -p 8000:8000 --env-file .env catalog-backend
```

### Option 4: Using Systemd Service

Create `/etc/systemd/system/catalog-backend.service`:

```ini
[Unit]
Description=Dessert Catalog API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable catalog-backend
sudo systemctl start catalog-backend
```

## Frontend Deployment

### Build for Production

```bash
cd frontend
npm install
npm run build
```

### Option 1: Serve with Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        proxy_pass http://localhost:8000;
    }
}
```

### Option 2: Serve with Node.js (serve)

```bash
npm install -g serve
serve -s dist -l 3000
```

### Option 3: Deploy to Vercel/Netlify

1. Connect your repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variables for API URL

## Database Setup

### SQLite (Development)
No setup needed, database is created automatically.

### PostgreSQL (Production)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE catalog_db;
CREATE USER catalog_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE catalog_db TO catalog_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://catalog_user:your_password@localhost:5432/catalog_db
```

## Reverse Proxy (Nginx)

Full Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static images
    location /static {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

## Monitoring

### Health Check

The API provides a health check endpoint:
```
GET /health
```

### Logging

Set up logging for production:
- Application logs
- Error logs
- Access logs
- Security event logs

## Backup Strategy

1. **Database Backups**
   - Daily automated backups
   - Store backups off-site
   - Test restore procedures

2. **File Backups**
   - Backup `uploads/` directory
   - Regular snapshots

## Updates and Maintenance

1. Keep dependencies updated:
   ```bash
   pip install --upgrade -r requirements.txt
   npm update
   ```

2. Check for security vulnerabilities:
   ```bash
   pip install safety
   safety check
   ```

3. Test updates in staging before production

4. Plan maintenance windows for updates

## Troubleshooting

### Backend won't start
- Check environment variables
- Verify database connection
- Check port availability
- Review logs

### Frontend can't connect to API
- Verify CORS settings
- Check API URL configuration
- Verify reverse proxy settings

### File upload issues
- Check directory permissions
- Verify disk space
- Check file size limits

