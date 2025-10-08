# Production Deployment Guide

## 🚀 Overview

This guide covers deploying the AI Lead Scoring & Enrichment Dashboard to production environments.

## 📋 Prerequisites

- **Backend**: Python 3.12+, UV package manager
- **Frontend**: Node.js 18+ or Bun 1.0+
- **Server**: Linux server with 2GB+ RAM, 10GB+ storage
- **Domain**: Optional - for HTTPS and custom domain

## 🔧 Production Configuration

### Backend Configuration

1. **Create Environment File**
```bash
cd backend
cp .env.example .env
```

2. **Configure .env**
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False

# CORS - Add your frontend domains
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Upload Limits
MAX_UPLOAD_SIZE_MB=50
MAX_LEADS_PER_UPLOAD=50000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

3. **Install Dependencies**
```bash
uv sync
```

4. **Run Production Server**
```bash
# With Uvicorn directly (recommended for production)
uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn for better performance
uv run gunicorn src.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Configuration

1. **Create Environment File**
```bash
cd frontend
cp .env.example .env.production
```

2. **Configure .env.production**
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

3. **Build for Production**
```bash
bun install
bun run build
```

4. **Start Production Server**
```bash
bun start
# Runs on port 3000
```

## 🐳 Docker Deployment

### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
FROM oven/bun:1 AS build

WORKDIR /app

# Copy dependency files
COPY package.json bun.lock ./

# Install dependencies
RUN bun install

# Copy application
COPY . .

# Build
RUN bun run build

# Production image
FROM oven/bun:1-slim

WORKDIR /app

COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules

EXPOSE 3000

CMD ["bun", "start"]
```

### Docker Compose

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
    volumes:
      - ./backend/logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🌐 Nginx Configuration

Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Increase timeouts for large file uploads
            client_max_body_size 50M;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Health check
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
    }
}
```

## 🔐 SSL/HTTPS Setup

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## 📊 Monitoring & Health Checks

### Health Check Endpoint

```bash
# Check backend health
curl https://yourdomain.com/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-08T12:00:00",
  "service": "ai-lead-scoring-api",
  "version": "1.0.0"
}
```

### Log Monitoring

```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🎯 Performance Optimization

### Backend Optimizations

1. **Use Multiple Workers**
```bash
uvicorn src.app:app --workers 4
```

2. **Enable Gzip Compression**
```python
# In src/app.py
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

3. **Add Caching for Sample Leads**
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_sample_leads():
    # Load and cache sample leads
    pass
```

### Frontend Optimizations

1. **Enable Static Export** (if no server-side rendering needed)
```javascript
// next.config.ts
export default {
  output: 'export'
}
```

2. **Use CDN for Static Assets**
- Deploy static files to Cloudflare, AWS S3, or Vercel

3. **Enable Image Optimization**
- Use Next.js Image component for any images

## 🔒 Security Best Practices

1. **Rate Limiting** (add to backend)
```bash
uv add slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/upload-leads")
@limiter.limit("10/minute")
async def upload_leads(request: Request, file: UploadFile = File(...)):
    # ...
```

2. **API Key Authentication** (optional)
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
```

3. **CORS Configuration**
- Only allow specific frontend domains
- Don't use `allow_origins=["*"]` in production

4. **Input Validation**
- Already implemented with Pydantic models
- Add additional file type validation if needed

## 📦 Database Integration (Optional)

For production with persistent storage, consider adding PostgreSQL:

```python
# Install dependencies
uv add sqlalchemy psycopg2-binary alembic

# Database models
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LeadModel(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    company = Column(String)
    job_title = Column(String)
    industry = Column(String)
    location = Column(String)
    company_size = Column(String)
    linkedin_url = Column(String)
    email_valid = Column(Boolean)
    score = Column(Float)
```

## 🧪 Testing in Production

```bash
# Test upload endpoint
curl -X POST https://yourdomain.com/api/upload-leads \
  -F "file=@sample-leads.csv"

# Test pagination
curl "https://yourdomain.com/api/leads?limit=100&offset=0"

# Test export
curl https://yourdomain.com/api/export -o leads.csv

# Load test with Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/health
```

## 🔄 Deployment Workflow

### Automated Deployment with GitHub Actions

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/ai-lead-scoring
            git pull origin main
            docker-compose down
            docker-compose up -d --build
```

## 📈 Scaling Considerations

### For High Traffic (10,000+ requests/day)

1. **Load Balancer**: Use AWS ALB, Nginx, or HAProxy
2. **Multiple Backend Instances**: Scale horizontally with Docker Swarm or Kubernetes
3. **Database**: PostgreSQL with read replicas
4. **Caching**: Redis for frequently accessed data
5. **Queue System**: Celery + Redis for async lead processing
6. **CDN**: CloudFlare or AWS CloudFront for frontend

### Kubernetes Deployment (Advanced)

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: CORS_ORIGINS
          value: "https://yourdomain.com"
```

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check `CORS_ORIGINS` in backend `.env`
   - Ensure frontend URL matches exactly (including protocol)

2. **File Upload Fails**
   - Check `MAX_UPLOAD_SIZE_MB` setting
   - Verify Nginx `client_max_body_size`

3. **Slow Performance with Large Files**
   - Enable pagination: `/api/leads?limit=100`
   - Use streaming for export endpoint
   - Consider adding background job processing

4. **Memory Issues**
   - Increase server RAM (recommend 4GB+ for 10k leads)
   - Optimize enrichment/scoring to process in batches
   - Use database instead of in-memory storage

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/Jainam1673/AI-Lead-Scoring-and-Enrichment-Dashboard/issues
- Documentation: See README.md and DATASET.md

## ✅ Production Checklist

- [ ] Configure environment variables
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS for production domains
- [ ] Set up monitoring and health checks
- [ ] Configure log rotation
- [ ] Set up automated backups (if using database)
- [ ] Test all endpoints in production
- [ ] Load test the application
- [ ] Set up error tracking (Sentry, Rollbar, etc.)
- [ ] Configure rate limiting
- [ ] Set up continuous deployment
- [ ] Create backup and recovery plan
- [ ] Document deployment process for team

---

**Last Updated**: October 8, 2025
**Version**: 1.0.0
