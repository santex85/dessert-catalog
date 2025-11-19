# Deployment Guide

## Quick Deploy

1. **Create deployment configuration:**
   ```bash
   cp deploy.env.example deploy.env
   # Edit deploy.env with your server details
   ```

2. **Deploy:**
   ```bash
   make deploy
   ```

## Configuration

Edit `deploy.env` with your server details:

```bash
# SSH connection
DEPLOY_HOST=your-server.com
DEPLOY_USER=deploy
DEPLOY_PORT=22
DEPLOY_KEY=~/.ssh/id_rsa

# Remote paths
DEPLOY_PATH=/var/www/catalog
DEPLOY_BRANCH=main

# Docker Compose
DEPLOY_COMPOSE_FILE=docker-compose.yml
DEPLOY_PROFILE=production
```

## Deployment Process

The `make deploy` command:

1. **Checks configuration** - Validates `deploy.env` file
2. **Connects to server** - SSH to remote server
3. **Updates code** - Pulls latest changes from git
4. **Builds images** - Rebuilds Docker containers
5. **Starts services** - Restarts all services with docker-compose
6. **Cleans up** - Removes old Docker images

## Commands

### Deploy
```bash
make deploy
```

### Check remote status
```bash
make deploy-status
```

### View remote logs
```bash
make deploy-logs
```

### Open remote shell
```bash
make deploy-shell
```

## Server Setup

Before first deployment, set up the server:

### 1. Install Docker and Docker Compose

```bash
# On Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository

```bash
git clone <your-repo-url> /var/www/catalog
cd /var/www/catalog
```

### 3. Create Environment Files

```bash
# Backend environment
cp backend/env.example backend/.env
# Edit backend/.env with production values

# Optional: Docker environment
cp .env.docker .env
# Edit .env if needed
```

### 4. Configure SSH Access

On your local machine:

```bash
# Generate SSH key if needed
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_rsa.pub deploy@your-server.com
```

### 5. First Deployment

```bash
# On server, manually run first time
cd /var/www/catalog
docker-compose --profile production up -d
docker-compose exec backend python init_db.py
```

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connection
ssh -i ~/.ssh/id_rsa deploy@your-server.com

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa
```

### Docker Not Found on Server

```bash
# Check Docker installation
ssh deploy@server "docker --version"
ssh deploy@server "docker-compose --version"
```

### Permission Denied

```bash
# Add user to docker group
ssh deploy@server "sudo usermod -aG docker $USER"
# Log out and log back in
```

### Deployment Fails

```bash
# Check remote logs
make deploy-logs

# Check remote status
make deploy-status

# Open remote shell to debug
make deploy-shell
```

## Advanced Configuration

### Custom Pre/Post Deploy Commands

Edit `deploy.env`:

```bash
DEPLOY_PRE_COMMANDS="cd /var/www/catalog && git fetch,cd /var/www/catalog && npm install"
DEPLOY_POST_COMMANDS="cd /var/www/catalog && docker-compose exec backend python init_db.py"
```

### Multiple Environments

Create separate config files:

```bash
# deploy.prod.env
DEPLOY_HOST=prod-server.com
DEPLOY_PATH=/var/www/catalog

# deploy.staging.env
DEPLOY_HOST=staging-server.com
DEPLOY_PATH=/var/www/catalog-staging
```

Deploy to specific environment:

```bash
cp deploy.prod.env deploy.env
make deploy
```

## Security Notes

1. **Never commit `deploy.env`** - It's in `.gitignore`
2. **Use SSH keys** - Don't use passwords
3. **Restrict SSH access** - Use firewall rules
4. **Secure secrets** - Use environment variables or secrets manager
5. **Regular updates** - Keep Docker and system updated

## CI/CD Integration

You can integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Deploy
  run: |
    echo "DEPLOY_HOST=${{ secrets.DEPLOY_HOST }}" >> deploy.env
    echo "DEPLOY_USER=${{ secrets.DEPLOY_USER }}" >> deploy.env
    make deploy
```

