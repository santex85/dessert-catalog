# Quick Start with Docker Compose

## Fastest Way to Run

```bash
# 1. Start everything
make docker-up

# 2. Initialize database
make docker-init-db

# 3. Open in browser
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

That's it! 🎉

## What Happens

1. **Backend** starts on port 8000
2. **Frontend** starts on port 3000 (proxies API to backend)
3. **Database** uses SQLite (stored in `backend/catalog.db`)

## Default Credentials

After running `make docker-init-db`, you can login with:
- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

## Common Commands

```bash
# View logs
make docker-logs

# Stop services
make docker-down

# Restart services
make docker-restart

# Rebuild containers
make docker-build

# Access backend shell
make docker-shell-backend
```

## Production Setup

For production with PostgreSQL:

```bash
# 1. Create .env file
cp backend/env.example backend/.env
# Edit and set SECRET_KEY, DATABASE_URL, etc.

# 2. Start with PostgreSQL
make docker-up-prod

# 3. Initialize database
make docker-init-db
```

See [DOCKER.md](DOCKER.md) for detailed instructions.

