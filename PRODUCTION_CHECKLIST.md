# Production Deployment Checklist

## Security

- [ ] **SECRET_KEY**: Set a strong random secret key (min 32 characters)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- [ ] **ALLOWED_ORIGINS**: Configure CORS with your production domain
  ```env
  ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  ```

- [ ] **ENVIRONMENT**: Set to production
  ```env
  ENVIRONMENT=production
  ```

- [ ] **Database**: Use PostgreSQL instead of SQLite
  ```env
  DATABASE_URL=postgresql://user:password@host:5432/dbname
  ```

- [ ] **HTTPS**: Configure SSL/TLS certificates
- [ ] **Security Headers**: Verify security headers are set
- [ ] **File Permissions**: Set correct permissions for uploads directory
- [ ] **Dependencies**: Run security audit
  ```bash
  pip install safety
  safety check
  ```

## Configuration

- [ ] Copy `backend/env.example` to `backend/.env`
- [ ] Fill in all required environment variables
- [ ] Verify `.env` is in `.gitignore`
- [ ] Test database connection
- [ ] Verify file upload directory exists and is writable

## Testing

- [ ] Test authentication flow
- [ ] Test file upload with various file types
- [ ] Test PDF generation
- [ ] Test admin endpoints protection
- [ ] Test CORS configuration
- [ ] Load testing (if applicable)

## Monitoring

- [ ] Set up application logging
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Set up health check monitoring
- [ ] Configure backup strategy
- [ ] Set up alerts for critical errors

## Deployment

- [ ] Choose deployment method (Docker, systemd, etc.)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up process manager (PM2, systemd, etc.)
- [ ] Configure firewall rules
- [ ] Set up SSL certificates
- [ ] Test deployment in staging environment

## Post-Deployment

- [ ] Verify all endpoints work correctly
- [ ] Test from different browsers/devices
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify backups are working
- [ ] Document any custom configurations

## Maintenance

- [ ] Schedule regular dependency updates
- [ ] Plan regular security audits
- [ ] Set up automated backups
- [ ] Document incident response procedures
- [ ] Keep deployment documentation updated

