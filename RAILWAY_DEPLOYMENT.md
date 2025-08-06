# Railway Deployment Guide

This guide provides step-by-step instructions for deploying the Railway File Management System to Railway.

## Prerequisites

1. A GitHub account with your code repository
2. A Railway account (sign up at [railway.app](https://railway.app))
3. Basic understanding of environment variables

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository contains all the necessary files:

- ✅ `app.py` (main application)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `railway.json` (Railway configuration)
- ✅ `Procfile` (process configuration)
- ✅ `railway_start.py` (Railway startup script)
- ✅ `Dockerfile` (container configuration)

### 2. Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect it's a Python project

### 3. Add PostgreSQL Database

1. In your Railway project dashboard, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically set

### 4. Configure Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add:

#### Required Variables:

```
SECRET_KEY=your-super-secret-key-here-generate-a-secure-one
ADMIN_USER_1=your_admin_username
ADMIN_PASS_1=your_secure_password
```

#### Optional Variables:

```
ADMIN_USER_2=second_admin_username
ADMIN_PASS_2=second_secure_password
FLASK_ENV=production
UPLOAD_FOLDER=uploads
```

**Important Security Notes:**

- Generate a strong, random SECRET_KEY (use a password generator)
- Use strong, unique passwords for admin accounts
- Never use the default credentials in production

### 5. Deploy

1. Railway will automatically deploy when you push to your main branch
2. You can also manually trigger a deployment from the Railway dashboard
3. Monitor the deployment logs for any issues

### 6. Verify Deployment

1. Once deployed, Railway will provide a URL for your application
2. Visit the URL and verify the application loads
3. Test the health check endpoint: `https://your-app.railway.app/health`
4. Try logging in with your admin credentials

## Environment Variables Reference

| Variable        | Required | Description                   | Default                  |
| --------------- | -------- | ----------------------------- | ------------------------ |
| `DATABASE_URL`  | Yes      | PostgreSQL connection string  | Auto-provided by Railway |
| `SECRET_KEY`    | Yes      | Flask secret key for sessions | None (must be set)       |
| `ADMIN_USER_1`  | Yes      | Primary admin username        | `sdfmagra`               |
| `ADMIN_PASS_1`  | Yes      | Primary admin password        | `Admin@123`              |
| `ADMIN_USER_2`  | No       | Secondary admin username      | `adfmagra`               |
| `ADMIN_PASS_2`  | No       | Secondary admin password      | `Admin@1234`             |
| `FLASK_ENV`     | No       | Flask environment             | `production`             |
| `PORT`          | No       | Application port              | Auto-set by Railway      |
| `UPLOAD_FOLDER` | No       | Upload directory              | `uploads`                |

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

- **Check logs**: Look at Railway deployment logs for error messages
- **Database connection**: Ensure PostgreSQL service is running
- **Environment variables**: Verify all required variables are set

#### 2. Database Connection Errors

- **DATABASE_URL**: Should be automatically provided by Railway
- **PostgreSQL service**: Ensure the database service is running
- **Network**: Check if database and app are in the same Railway project

#### 3. Health Check Failures

- **Endpoint**: Health check is at `/health`
- **Database**: Health check tests database connectivity
- **Timeout**: Default timeout is 100 seconds

#### 4. File Upload Issues

- **Permissions**: Railway handles file system permissions automatically
- **Storage**: Files are stored in ephemeral storage (will be lost on restart)
- **Recommendation**: Consider using cloud storage (AWS S3, etc.) for production

### Debug Mode

To enable debug mode (not recommended for production):

```
FLASK_ENV=development
```

### Viewing Logs

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Logs" tab
4. Monitor real-time logs for issues

## Production Recommendations

### Security

1. **Change default credentials**: Never use default admin usernames/passwords
2. **Strong SECRET_KEY**: Generate a cryptographically secure secret key
3. **HTTPS**: Railway provides HTTPS automatically
4. **Environment variables**: Keep sensitive data in environment variables

### Performance

1. **Database indexing**: Add indexes for frequently queried columns
2. **Connection pooling**: Consider database connection pooling for high traffic
3. **Monitoring**: Set up monitoring and alerting

### File Storage

1. **Cloud storage**: Use AWS S3, Google Cloud Storage, or similar for file persistence
2. **Backup**: Implement regular backups for uploaded files
3. **CDN**: Use a CDN for static assets

### Monitoring

1. **Health checks**: Railway automatically monitors the `/health` endpoint
2. **Logs**: Monitor application logs for errors
3. **Database**: Monitor database performance and connections

## Support

If you encounter issues:

1. **Check logs**: Railway deployment and application logs
2. **Health check**: Visit `/health` endpoint to check application status
3. **Database**: Verify database connection and tables
4. **Environment**: Double-check environment variable configuration

## Updating Your Application

1. Push changes to your GitHub repository
2. Railway will automatically redeploy
3. Monitor deployment logs
4. Verify the update was successful

## Scaling

Railway supports automatic scaling:

1. Go to your service settings
2. Configure scaling options
3. Set resource limits as needed

For high-traffic applications, consider:

- Multiple worker processes
- Database connection pooling
- Caching strategies
- Load balancing
