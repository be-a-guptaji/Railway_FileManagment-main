# Render.com Deployment Guide

This guide provides step-by-step instructions for deploying the Railway File Management System to Render.com.

## Prerequisites

1. A GitHub account with your code repository
2. A Render account (sign up at [render.com](https://render.com))
3. Your code pushed to a GitHub repository

## Render.com Advantages

✅ **Persistent Storage**: Files survive container restarts with persistent disks
✅ **Built-in PostgreSQL**: Managed PostgreSQL database included
✅ **Auto-scaling**: Automatic scaling based on traffic
✅ **Free Tier**: Generous free tier for small projects
✅ **Easy Deployment**: Git-based deployment with minimal configuration
✅ **SSL/HTTPS**: Automatic SSL certificates
✅ **Custom Domains**: Easy custom domain setup

## Step-by-Step Deployment

### Method 1: Using render.yaml (Recommended)

#### 1. Prepare Your Repository

Ensure your repository contains:

- ✅ `render.yaml` (Render configuration)
- ✅ `render_start.py` (Render startup script)
- ✅ `requirements.txt` (Python dependencies)
- ✅ All application files

#### 2. Deploy via Render Dashboard

1. Go to [render.com](https://render.com) and sign in
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml`
5. Review the configuration and click "Apply"

#### 3. Configure Environment Variables (Optional)

The `render.yaml` includes auto-generated values, but you can customize:

- `SECRET_KEY` - Will be auto-generated
- `ADMIN_USER_1` - Default: `admin`
- `ADMIN_PASS_1` - Will be auto-generated
- `ADMIN_USER_2` - Default: `manager`
- `ADMIN_PASS_2` - Will be auto-generated

### Method 2: Manual Setup

#### 1. Create Web Service

1. Go to Render dashboard
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `railway-file-management`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python render_start.py && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload app:app`

#### 2. Create PostgreSQL Database

1. Click "New" → "PostgreSQL"
2. Configure:
   - **Name**: `railway-file-management-db`
   - **Database Name**: `railway_file_management`
   - **User**: `railway_user`

#### 3. Add Persistent Disk

1. In your web service settings
2. Go to "Disks" tab
3. Add disk:
   - **Name**: `uploads`
   - **Mount Path**: `/opt/render/project/src/uploads`
   - **Size**: `1 GB` (or more as needed)

#### 4. Set Environment Variables

Add these in your web service "Environment" tab:

```
FLASK_ENV=production
RENDER=1
DATABASE_URL=[auto-filled from database]
SECRET_KEY=[generate secure key]
ADMIN_USER_1=your_admin_username
ADMIN_PASS_1=your_secure_password
ADMIN_USER_2=your_second_admin_username
ADMIN_PASS_2=your_second_secure_password
```

## render.yaml Configuration

```yaml
services:
  # Web Service - Main Flask Application
  - type: web
    name: railway-file-management
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: python render_start.py && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload app:app
    healthCheckPath: /health
    envVars:
      - key: FLASK_ENV
        value: production
      - key: RENDER
        value: "1"
      - key: DATABASE_URL
        fromDatabase:
          name: railway-file-management-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ADMIN_USER_1
        value: admin
      - key: ADMIN_PASS_1
        generateValue: true
    disk:
      name: uploads
      mountPath: /opt/render/project/src/uploads
      sizeGB: 1

  # PostgreSQL Database
  - type: pserv
    name: railway-file-management-db
    env: postgresql
    plan: starter
    databaseName: railway_file_management
    databaseUser: railway_user
```

## Environment Variables Reference

| Variable       | Required | Description                   | Default/Auto   |
| -------------- | -------- | ----------------------------- | -------------- |
| `DATABASE_URL` | Yes      | PostgreSQL connection string  | Auto-filled    |
| `SECRET_KEY`   | Yes      | Flask secret key for sessions | Auto-generated |
| `ADMIN_USER_1` | Yes      | Primary admin username        | `admin`        |
| `ADMIN_PASS_1` | Yes      | Primary admin password        | Auto-generated |
| `ADMIN_USER_2` | No       | Secondary admin username      | `manager`      |
| `ADMIN_PASS_2` | No       | Secondary admin password      | Auto-generated |
| `FLASK_ENV`    | No       | Flask environment             | `production`   |
| `RENDER`       | No       | Render environment flag       | `1`            |

## Render-Specific Features

### Persistent Storage

- Files are stored on persistent disk at `/opt/render/project/src/uploads`
- Files survive container restarts and deployments
- Configurable disk size (1GB default, can be increased)

### Database Integration

- Built-in PostgreSQL with automatic connection string
- Managed backups and maintenance
- Connection pooling optimized for Render

### Auto-scaling

- Automatic scaling based on CPU and memory usage
- Zero-downtime deployments
- Health check monitoring

### SSL/HTTPS

- Automatic SSL certificate provisioning
- Custom domain support
- HTTP to HTTPS redirect

## Pricing

### Free Tier

- **Web Service**: 750 hours/month (enough for personal projects)
- **PostgreSQL**: 1GB storage, 1 million rows
- **Bandwidth**: 100GB/month
- **Custom domains**: Not included

### Starter Plan ($7/month per service)

- **Web Service**: Always-on, no sleep
- **PostgreSQL**: 1GB storage, unlimited rows
- **Bandwidth**: 100GB/month
- **Custom domains**: Included
- **SSL**: Included

### Standard Plan ($25/month per service)

- **Web Service**: 2GB RAM, always-on
- **PostgreSQL**: 4GB storage
- **Bandwidth**: 500GB/month
- **Priority support**: Included

## Deployment Process

### 1. Initial Deployment

```bash
# Push your code to GitHub
git add .
git commit -m "Add Render configuration"
git push origin main

# Render will automatically deploy when you connect the repository
```

### 2. Automatic Deployments

- Every push to your main branch triggers a new deployment
- Zero-downtime deployments
- Automatic rollback on failure

### 3. Manual Deployments

- You can trigger manual deployments from the Render dashboard
- Useful for testing specific commits

## Monitoring and Logs

### Application Logs

- Real-time logs available in Render dashboard
- Searchable and filterable
- Download logs for analysis

### Health Monitoring

- Automatic health checks via `/health` endpoint
- Email notifications on service issues
- Uptime monitoring

### Metrics

- CPU and memory usage graphs
- Request rate and response time metrics
- Database connection monitoring

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

- **Problem**: App can't connect to database
- **Solution**: Check DATABASE_URL environment variable
- **Debug**: Look for connection errors in logs

#### 2. File Upload Issues

- **Problem**: Files not persisting
- **Solution**: Ensure persistent disk is properly mounted
- **Check**: Verify disk mount path in render.yaml

#### 3. Build Failures

- **Problem**: Build command fails
- **Solution**: Check requirements.txt and Python version
- **Debug**: Review build logs in Render dashboard

#### 4. Health Check Failures

- **Problem**: Service marked as unhealthy
- **Solution**: Check `/health` endpoint response
- **Debug**: Review application logs for errors

### Debug Commands

Check service status:

```bash
curl https://your-app.onrender.com/health
```

View logs:

- Go to Render dashboard → Your service → Logs

Test database connection:

```python
# In your application logs, look for:
# "Database connection successful"
# "Database tables created successfully"
```

## Performance Optimization

### Database

- Connection pooling configured for Render
- Optimized query execution
- Automatic connection management

### File Storage

- Persistent disk for file uploads
- Optimized file operations
- Configurable storage size

### Application

- Gunicorn with 2 workers (optimized for Starter plan)
- 120-second timeout for large operations
- Preload application for faster response times

## Security Best Practices

### Environment Variables

- Never commit secrets to repository
- Use Render's environment variable management
- Generate strong SECRET_KEY

### Database Security

- Use strong database passwords
- Enable SSL connections
- Regular security updates via Render

### Application Security

- HTTPS enforced automatically
- Secure session management
- Input validation and sanitization

## Backup and Recovery

### Database Backups

- Automatic daily backups (Starter plan and above)
- Point-in-time recovery available
- Manual backup triggers available

### File Backups

- Persistent disk data is backed up
- Consider additional backup strategy for critical files
- Can integrate with cloud storage for redundancy

## Scaling Considerations

### Vertical Scaling

- Upgrade to Standard plan for more RAM
- Increase persistent disk size as needed
- Monitor resource usage in dashboard

### Horizontal Scaling

- Multiple instances available on higher plans
- Load balancing handled automatically
- Session management considerations

## Migration from Other Platforms

### From Railway

1. Export database data
2. Copy environment variables
3. Update configuration for Render
4. Test deployment thoroughly

### From Vercel

1. Set up persistent storage (major change)
2. Update file handling code
3. Configure database connection
4. Test file upload functionality

### From Heroku

1. Similar deployment process
2. Update buildpacks to Render configuration
3. Configure persistent storage
4. Update environment variables

## Support and Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Community Forum**: [community.render.com](https://community.render.com)
- **Status Page**: [status.render.com](https://status.render.com)
- **Support**: Available via dashboard (paid plans)

## Summary

Render.com provides an excellent balance of features for the Railway File Management System:

### ✅ Advantages

- Persistent file storage with disks
- Built-in PostgreSQL database
- Automatic SSL and custom domains
- Generous free tier
- Easy deployment and scaling
- Zero-downtime deployments

### ⚠️ Considerations

- Slightly more expensive than some alternatives
- Limited customization compared to AWS
- Newer platform (less mature than Heroku)

### 🎯 Best For

- Small to medium applications
- Teams wanting managed infrastructure
- Projects needing persistent file storage
- Applications requiring built-in database

Render.com is an excellent choice for deploying the Railway File Management System with minimal configuration and maximum reliability.
