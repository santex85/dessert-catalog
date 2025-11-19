# Docker Setup Guide

## Quick Start

### Development (SQLite)

1. **Create environment file:**
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env and set SECRET_KEY
   ```

2. **Start services:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```
   
   The database will be **automatically initialized** with test data on first start.

3. **Access application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production (PostgreSQL)

1. **Create environment files:**
   ```bash
   cp backend/env.example backend/.env
   cp .env.docker .env
   # Edit both files with production values
   ```

2. **Update backend/.env:**
   ```env
   DATABASE_URL=postgresql://catalog_user:your_password@postgres:5432/catalog_db
   ENVIRONMENT=production
   SECRET_KEY=your-strong-secret-key-min-32-chars
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **Start all services:**
   ```bash
   docker-compose --profile production up -d
   ```
   
   The database will be **automatically initialized** with test data on first start.

## Test Data

When the database is initialized, it creates:

- **20 test desserts** in various categories:
  - Cakes: New York Cheesecake, Red Velvet, Strawberry Shortcake, Carrot Cake
  - Desserts: Tiramisu, Panna Cotta, Chocolate Mousse, Creme Brulee
  - Pastries: Chocolate Eclair, Macarons Assortment
  - Cookies: Chocolate Chip Cookies
  - Tarts: Lemon Tart, Fruit Tart
  - Pies: Apple Pie, Pecan Pie
  - Vegan: Vegan Brownie
  - Sugar-Free: Sugar-Free Cake
  - Gluten-Free: Gluten-Free Chocolate Cake
  - Ice Cream: Ice Cream Sundae
  - Breads: Banana Bread

- **2 test users**:
  - **Admin**: `admin` / `admin123` (has admin privileges)
  - **Regular user**: `user` / `user123` (regular user)

### Manual Initialization

If you need to manually initialize or re-initialize the database:

```bash
make docker-init-db
```

Or directly:

```bash
docker compose exec backend python init_db.py
```

**Note**: The script checks if data already exists and won't duplicate it. To reset the database, remove the database file or volume first.

## Docker Compose Commands

### Start services
```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose --profile production up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild containers
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Execute commands in container
```bash
# Backend shell
docker-compose exec backend bash

# Run Python script
docker-compose exec backend python init_db.py

# Create admin user
docker-compose exec backend python create_admin.py admin admin@example.com admin123
```

### Check service status
```bash
docker-compose ps
```

### View resource usage
```bash
docker stats
```

## Service Details

### Backend
- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Volumes**:
  - `./backend/uploads` - Uploaded images
  - `./backend/catalog.db` - SQLite database (dev only)

### Frontend
- **Port**: 3000
- **Nginx**: Serves built React app
- **Proxy**: Routes `/api` and `/static` to backend

### PostgreSQL (Production)
- **Port**: 5432
- **Volume**: `postgres_data` - Persistent database storage
- **Health Check**: PostgreSQL readiness check

## Environment Variables

### Backend (.env)
See `backend/env.example` for all backend environment variables.

### Docker Compose (.env.docker)
- `BACKEND_PORT` - Backend port mapping
- `FRONTEND_PORT` - Frontend port mapping
- `POSTGRES_*` - PostgreSQL configuration
- `DATABASE_URL` - Database connection string

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing SECRET_KEY in .env
# 2. Database connection error
# 3. Port already in use
```

### Frontend can't connect to backend
- Check that backend is running: `docker-compose ps`
- Verify network: `docker network ls`
- Check nginx config: `docker-compose exec frontend cat /etc/nginx/conf.d/default.conf`

### Database connection issues
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check connection string in `.env`
- Test connection: `docker-compose exec backend python -c "from app.database import engine; engine.connect()"`

### Permission issues
```bash
# Fix uploads directory permissions
docker-compose exec backend chmod -R 755 uploads
```

### Rebuild everything
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

1. **Set production environment:**
   ```bash
   export ENVIRONMENT=production
   ```

2. **Use production compose:**
   ```bash
   docker-compose --profile production up -d
   ```

3. **Configure reverse proxy (Nginx/Traefik):**
   - Point to frontend container on port 3000
   - Configure SSL/TLS
   - Set security headers

4. **Set up backups:**
   ```bash
   # Backup PostgreSQL
   docker-compose exec postgres pg_dump -U catalog_user catalog_db > backup.sql

   # Backup uploads
   tar -czf uploads_backup.tar.gz backend/uploads/
   ```

## Development Tips

- Use `docker-compose.dev.yml` for hot-reload
- Mount source code as volume for live changes
- Use `docker-compose logs -f` to watch logs
- Access containers with `docker-compose exec <service> bash`

