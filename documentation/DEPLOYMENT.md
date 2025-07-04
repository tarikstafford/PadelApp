# Deployment Documentation

## Overview

PadelGo is deployed on Railway using a multi-service architecture with separate containers for the API backend and frontend applications. This document covers the complete deployment process, environment configuration, and troubleshooting.

## Architecture

### Service Structure

```
PadelGo Production Deployment
├── padelgo-backend-production (FastAPI)
├── padelgo-frontend-production (Next.js Web App)
└── club-admin-production (Next.js Admin Portal)
```

### Database

- **PostgreSQL**: Managed database on Railway
- **Migrations**: Automatic Alembic migrations on deployment
- **Backups**: Daily automated backups

## Environment Configuration

### Backend Environment Variables (`padelgo-backend`)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# Cloudinary (File Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=PadelGo API

# CORS Origins (Production URLs)
BACKEND_CORS_ORIGINS=["https://padelgo-frontend-production.up.railway.app","https://club-admin-production.up.railway.app"]
```

### Frontend Environment Variables (`padelgo-frontend`)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://padelgo-backend-production.up.railway.app

# Build Configuration
NODE_ENV=production
```

### Club Admin Environment Variables (`club-admin`)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://padelgo-backend-production.up.railway.app

# Build Configuration
NODE_ENV=production
```

## Deployment Process

### Automatic Deployment

All services use Railway's automatic deployment triggered by Git pushes:

1. **Code Push**: Push to main branch triggers deployment
2. **Build Process**: Railway builds Docker containers
3. **Health Checks**: Services must pass health checks
4. **Traffic Routing**: Successful deployments receive traffic

### Manual Deployment

```bash
# Using Railway CLI
railway login
railway environment production
railway deploy
```

### Database Migrations

Migrations run automatically on backend deployment:

```bash
# In entrypoint.sh
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Service Configuration

### Backend Service (`Dockerfile`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start script
CMD ["./entrypoint.sh"]
```

### Frontend Services (`Dockerfile`)

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy and build
COPY . .
RUN npm run build

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

## Railway Configuration

### Service Settings

Each service is configured with:

- **Build Command**: Automatic Docker build
- **Start Command**: Defined in Dockerfile
- **Health Check**: HTTP endpoint monitoring
- **Auto-scaling**: Based on CPU/memory usage

### Domain Configuration

```
Production URLs:
- Backend: https://padelgo-backend-production.up.railway.app
- Frontend: https://padelgo-frontend-production.up.railway.app  
- Admin: https://club-admin-production.up.railway.app
```

### Custom Domains (Optional)

```
Custom domains can be configured:
- API: api.padelgo.com
- Web: www.padelgo.com
- Admin: admin.padelgo.com
```

## Database Management

### Connection Configuration

```python
# app/database.py
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
```

### Migration Management

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Backup Strategy

- **Automated Backups**: Daily PostgreSQL dumps
- **Point-in-time Recovery**: Available through Railway
- **Manual Backup**: `pg_dump` for specific data exports

## Monitoring & Logging

### Application Logs

```bash
# Railway CLI
railway logs --service padelgo-backend
railway logs --service padelgo-frontend
railway logs --service club-admin
```

### Health Monitoring

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}
```

### Performance Metrics

- **Response Times**: API endpoint performance
- **Error Rates**: 4xx/5xx error tracking
- **Resource Usage**: CPU/memory consumption
- **Database Performance**: Query execution times

## Security Configuration

### HTTPS/SSL

- **Automatic SSL**: Railway provides automatic SSL certificates
- **Force HTTPS**: All traffic redirected to HTTPS
- **Security Headers**: Configured in Next.js applications

### CORS Configuration

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
```

### Environment Security

- **Secret Management**: Environment variables for sensitive data
- **Database Security**: SSL connections enforced
- **API Keys**: Rotated regularly and stored securely

## CI/CD Pipeline

### GitHub Integration

```yaml
# .github/workflows/deploy.yml (if using GitHub Actions)
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: railway deploy
```

### Build Process

1. **Dependency Installation**: Package manager installs dependencies
2. **Type Checking**: TypeScript compilation for frontend
3. **Testing**: Run test suites (if configured)
4. **Building**: Create production builds
5. **Deployment**: Deploy to Railway infrastructure

## Troubleshooting

### Common Deployment Issues

#### Build Failures

```bash
# Check build logs
railway logs --deployment <deployment-id>

# Common fixes:
- Update Node.js version in package.json
- Clear build cache
- Check dependency conflicts
```

#### Database Connection Issues

```bash
# Verify DATABASE_URL format
postgresql://username:password@host:port/database

# Test connection
railway run psql $DATABASE_URL
```

#### CORS Errors

```bash
# Update CORS origins in backend
BACKEND_CORS_ORIGINS=["https://your-frontend-domain.railway.app"]

# Verify environment variables
railway variables
```

### Service Health Checks

```bash
# Check service status
curl https://padelgo-backend-production.up.railway.app/health

# Expected response
{"status": "ok", "timestamp": "2024-01-01T12:00:00Z"}
```

### Database Issues

```sql
-- Check database connections
SELECT count(*) FROM pg_stat_activity;

-- Monitor long-running queries
SELECT query, query_start, state 
FROM pg_stat_activity 
WHERE state = 'active';

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Performance Optimization

### Backend Optimization

- **Database Indexing**: Optimize query performance
- **Connection Pooling**: Efficient database connections
- **Caching**: Redis for session/query caching (future)
- **Query Optimization**: Reduce N+1 queries

### Frontend Optimization

- **Static Generation**: Pre-build static pages
- **Image Optimization**: Next.js automatic optimization
- **Code Splitting**: Lazy load components
- **Bundle Analysis**: Monitor bundle sizes

### Database Optimization

- **Query Analysis**: Use EXPLAIN ANALYZE
- **Index Optimization**: Create appropriate indexes
- **Connection Limits**: Configure max connections
- **Backup Windows**: Schedule during low traffic

## Scaling Considerations

### Horizontal Scaling

- **Load Balancing**: Railway handles automatically
- **Database Scaling**: Upgrade instance sizes
- **CDN Integration**: Cloudinary for images
- **Caching Layer**: Redis for performance

### Vertical Scaling

- **Resource Allocation**: Increase CPU/memory
- **Database Upgrades**: Scale PostgreSQL instance
- **Storage Expansion**: Increase disk space

## Backup & Recovery

### Data Backup

```bash
# Manual database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore from backup
psql $DATABASE_URL < backup_20240101.sql
```

### Application Backup

- **Code Repository**: Git version control
- **Environment Variables**: Documented configurations
- **Database Schema**: Migration files
- **File Uploads**: Cloudinary storage

### Disaster Recovery

1. **Database Restore**: Point-in-time recovery
2. **Service Redeploy**: Redeploy from Git
3. **Environment Restore**: Reconfigure variables
4. **Domain Reconfiguration**: Update DNS if needed

## Cost Management

### Resource Monitoring

- **Usage Tracking**: Monitor monthly usage
- **Cost Alerts**: Set up billing notifications
- **Optimization**: Regular resource audits

### Cost Optimization

- **Right-sizing**: Match resources to needs
- **Development Environment**: Use lower-tier resources
- **Scheduled Scaling**: Scale down during low usage
- **Database Optimization**: Efficient queries reduce costs

---

This deployment documentation ensures reliable, scalable deployment of the PadelGo platform while maintaining security and performance best practices.