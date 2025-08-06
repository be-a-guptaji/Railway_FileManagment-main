# Render Deployment Troubleshooting Guide

This guide helps you troubleshoot common issues when deploying the Railway File Management System to Render.com.

## Common Issues and Solutions

### 1. PORT Environment Variable Error

**Error**: `ValueError: invalid literal for int() with base 10: 'port'`

**Cause**: Render sometimes sets PORT to an invalid value or the environment variable is not properly configured.

**Solutions**:

#### Option A: Use render-simple.yaml

Replace your `render.yaml` with `render-simple.yaml` which explicitly sets PORT:

```bash
mv render.yaml render-original.yaml
mv render-simple.yaml render.yaml
```

#### Option B: Fix PORT in render.yaml

Add explicit PORT environment variable:

```yaml
envVars:
  - key: PORT
    value: "10000"
```

#### Option C: Use the shell script approach

The `start_render.sh` script handles PORT validation automatically.

### 2. Database Connection Issues

**Error**: Database connection timeouts or failures

**Solutions**:

#### Check Database Service

1. Ensure PostgreSQL service is running in Render dashboard
2. Verify DATABASE_URL is properly connected
3. Check database logs for errors

#### Increase Connection Timeout

The `render_start.py` script includes retry logic with 30 attempts.

#### Manual Database Connection Test

```python
# Test in Render shell
import os
import psycopg2
conn = psycopg2.connect(os.environ['DATABASE_URL'])
```

### 3. File Upload/Storage Issues

**Error**: Files not persisting or upload errors

**Solutions**:

#### Verify Persistent Disk

1. Check that disk is mounted at `/opt/render/project/src/uploads`
2. Verify disk size is sufficient (1GB default)
3. Check disk permissions

#### Test Upload Directory

```bash
# In Render shell
ls -la /opt/render/project/src/uploads
touch /opt/render/project/src/uploads/test.txt
```

### 4. Build Failures

**Error**: Build command fails

**Solutions**:

#### Check Python Version

Ensure Python 3.11.9 is specified:

```yaml
envVars:
  - key: PYTHON_VERSION
    value: 3.11.9
```

#### Verify Requirements

Check that `requirements.txt` is present and valid:

```bash
pip install -r requirements.txt
```

#### Build Command Issues

Try alternative build commands:

```yaml
buildCommand: pip install --upgrade pip && pip install -r requirements.txt
```

### 5. Health Check Failures

**Error**: Service marked as unhealthy

**Solutions**:

#### Check Health Endpoint

Test the health endpoint manually:

```bash
curl https://your-app.onrender.com/health
```

#### Verify Health Check Path

Ensure health check path is correct in render.yaml:

```yaml
healthCheckPath: /health
```

#### Check Application Logs

Review logs in Render dashboard for health check errors.

### 6. Environment Variables Not Set

**Error**: Missing environment variables

**Solutions**:

#### Verify in Render Dashboard

1. Go to your service settings
2. Check "Environment" tab
3. Ensure all required variables are set

#### Required Variables Checklist

- [ ] `DATABASE_URL` (auto-filled from database)
- [ ] `SECRET_KEY` (auto-generated or custom)
- [ ] `ADMIN_USER_1` (default: admin)
- [ ] `ADMIN_PASS_1` (auto-generated or custom)
- [ ] `FLASK_ENV` (production)
- [ ] `RENDER` (1)

### 7. Gunicorn Worker Issues

**Error**: Workers failing to start or crashing

**Solutions**:

#### Reduce Worker Count

For starter plan, use fewer workers:

```yaml
startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload app:app
```

#### Increase Timeout

For large operations:

```yaml
startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --preload app:app
```

#### Remove Preload

If preload causes issues:

```yaml
startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
```

## Debugging Steps

### 1. Check Service Logs

1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. Look for error messages

### 2. Test Database Connection

```python
# In Python shell or script
import os
from sqlalchemy import create_engine, text

engine = create_engine(os.environ['DATABASE_URL'])
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print("Database connection successful")
```

### 3. Verify File System

```bash
# Check upload directory
ls -la uploads/
df -h  # Check disk space
```

### 4. Test Environment Variables

```python
import os
print("Environment Variables:")
for key in ['DATABASE_URL', 'SECRET_KEY', 'PORT', 'RENDER']:
    print(f"{key}: {'SET' if os.environ.get(key) else 'NOT SET'}")
```

### 5. Manual Health Check

```bash
# Test health endpoint
curl -v https://your-app.onrender.com/health
```

## Alternative Deployment Methods

### Method 1: Manual Service Creation

Instead of using render.yaml, create services manually:

1. **Create Web Service**:

   - Repository: Your GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python render_start.py && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload app:app`

2. **Create PostgreSQL Database**:

   - Name: `railway-file-management-db`
   - Database: `railway_file_management`
   - User: `railway_user`

3. **Add Persistent Disk**:
   - Name: `uploads`
   - Mount Path: `/opt/render/project/src/uploads`
   - Size: `1 GB`

### Method 2: Simplified Configuration

Use minimal render.yaml:

```yaml
services:
  - type: web
    name: railway-file-management
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:10000 --workers 1 --timeout 120 app:app
    envVars:
      - key: PORT
        value: "10000"
      - key: RENDER
        value: "1"
```

## Performance Optimization

### For Starter Plan (512MB RAM)

```yaml
startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 app:app
```

### For Standard Plan (2GB RAM)

```yaml
startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --preload app:app
```

## Monitoring and Alerts

### Set Up Monitoring

1. Enable health checks in render.yaml
2. Set up email notifications in Render dashboard
3. Monitor resource usage

### Log Analysis

```bash
# Common log patterns to look for
grep -i error logs.txt
grep -i "database" logs.txt
grep -i "port" logs.txt
```

## Getting Help

### Render Support Channels

- **Documentation**: [render.com/docs](https://render.com/docs)
- **Community**: [community.render.com](https://community.render.com)
- **Status**: [status.render.com](https://status.render.com)
- **Support**: Available via dashboard (paid plans)

### Application-Specific Help

- Check application logs for specific error messages
- Use the `verify_render.py` script to test deployment
- Review the `RENDER_DEPLOYMENT.md` guide

## Quick Fixes Summary

1. **PORT Error**: Use `render-simple.yaml` or set PORT explicitly
2. **Database Issues**: Wait for database to be ready, check connection string
3. **File Storage**: Verify persistent disk configuration
4. **Build Failures**: Check Python version and requirements.txt
5. **Health Checks**: Verify `/health` endpoint is accessible
6. **Worker Issues**: Reduce worker count for starter plan

## Emergency Rollback

If deployment fails completely:

1. **Revert to Working Configuration**:

   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Use Minimal Configuration**:
   Replace render.yaml with basic configuration

3. **Manual Service Setup**:
   Create services manually through Render dashboard

4. **Contact Support**:
   If all else fails, contact Render support with logs

Remember: Render deployments can take a few minutes to complete. Be patient and check logs for detailed error information.
