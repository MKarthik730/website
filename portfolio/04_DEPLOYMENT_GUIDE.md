# FastAPI Deployment & Production Guide

## 1. REQUIREMENTS.TXT

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
PyJWT==2.8.1
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
psycopg2-binary==2.9.9
gunicorn==21.2.0
```

## 2. DOCKER DEPLOYMENT

### Dockerfile
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install wheels
RUN pip install --no-cache /wheels/*

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health/')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/fastapi_db
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fastapi_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

## 3. NGINX CONFIGURATION

### nginx.conf
```nginx
upstream fastapi {
    server web:8000;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 20M;

    location / {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    location /static/ {
        alias /app/static/;
    }
}

server {
    listen 443 ssl http2;
    server_name _;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
}
```

## 4. ENVIRONMENT VARIABLES

### .env
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379

# AWS (optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket
```

### .env.example
```
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 5. GUNICORN CONFIGURATION

### gunicorn_conf.py
```python
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "fastapi_app"

# Server mechanics
daemon = False
umask = 0
user = "appuser"
group = "appuser"
tmp_upload_dir = None

# SSL (if using directly, otherwise use nginx)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
```

### Run with Gunicorn
```bash
gunicorn -c gunicorn_conf.py main:app
```

## 6. SYSTEMD SERVICE

### /etc/systemd/system/fastapi.service
```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
Type=notify
User=appuser
Group=appuser
WorkingDirectory=/home/appuser/fastapi_app
Environment="PATH=/home/appuser/fastapi_app/venv/bin"
ExecStart=/home/appuser/fastapi_app/venv/bin/gunicorn \
    -c gunicorn_conf.py \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    main:app

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Manage Service
```bash
# Start
sudo systemctl start fastapi

# Stop
sudo systemctl stop fastapi

# Restart
sudo systemctl restart fastapi

# Enable on boot
sudo systemctl enable fastapi

# View logs
sudo journalctl -u fastapi -f
```

## 7. MONITORING & LOGGING

### main.py with Logging
```python
import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory
if not os.path.exists("logs"):
    os.mkdir("logs")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# File handler
file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)

# Add handler to root logger
logging.getLogger("").addHandler(file_handler)
```

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_TIME = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Start metrics server
start_http_server(8001)

# Middleware
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_TIME.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

## 8. CI/CD PIPELINE

### .github/workflows/deploy.yml
```yaml
name: Deploy FastAPI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        echo "Deploying to production..."
        # Add your deployment commands here
```

## 9. SECURITY CHECKLIST

- [ ] Change SECRET_KEY in production
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS/SSL
- [ ] Set CORS properly
- [ ] Implement rate limiting
- [ ] Use password hashing (bcrypt)
- [ ] Validate all inputs
- [ ] Use parameterized queries (SQLAlchemy)
- [ ] Implement proper error handling
- [ ] Set secure headers
- [ ] Use dependency injection for security
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Implement request signing (if needed)
- [ ] Use database encryption
- [ ] Implement backup strategy

## 10. PERFORMANCE OPTIMIZATION

```python
# Use async for all I/O operations
@app.get("/items/")
async def read_items():
    # Use async database operations
    items = await db.query(Item).all()
    return items

# Implement caching
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/items/", dependencies=[Depends(cache(expire=300))])
async def read_items():
    return [{"item": "Foo"}]

# Use pagination for large results
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

# Compress responses
from fastapi.middleware.gzip import GZIPMiddleware

app.add_middleware(GZIPMiddleware, minimum_size=1000)
```

## 11. DISASTER RECOVERY

```bash
# Database backup
pg_dump dbname > backup.sql

# Database restore
psql dbname < backup.sql

# Automated backups with cron
0 2 * * * pg_dump -U user dbname | gzip > /backups/db_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz
```

## 12. DEPLOYMENT CHECKLIST

- [ ] Test all endpoints
- [ ] Run full test suite
- [ ] Check environment variables
- [ ] Verify database migrations
- [ ] Review security settings
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Backup database
- [ ] Test rollback procedure
- [ ] Document deployment steps
- [ ] Set up alerting
- [ ] Monitor performance metrics
- [ ] Check disk space
- [ ] Verify SSL certificates
- [ ] Test failover procedures
