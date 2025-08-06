# Vercel Deployment Guide

This guide provides step-by-step instructions for deploying the Railway File Management System to Vercel.

## Prerequisites

1. A GitHub account with your code repository
2. A Vercel account (sign up at [vercel.com](https://vercel.com))
3. A PostgreSQL database (external provider like Neon, Supabase, or PlanetScale)

## Important Vercel Limitations

⚠️ **Serverless Constraints:**

- **File Storage**: Files are stored in `/tmp` and are ephemeral (lost after function execution)
- **Function Timeout**: Maximum 30 seconds execution time
- **Cold Starts**: Database connections may timeout on cold starts
- **Memory Limits**: Limited memory per function execution

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository contains the Vercel-specific files:

- ✅ `api/index.py` (Vercel entry point)
- ✅ `vercel.json` (Vercel configuration)
- ✅ `requirements-vercel.txt` (optimized dependencies)
- ✅ All other application files

### 2. Set Up External Database

Since Vercel doesn't provide built-in PostgreSQL, use an external provider:

#### Option A: Neon (Recommended)

1. Go to [neon.tech](https://neon.tech) and create account
2. Create a new project
3. Copy the connection string

#### Option B: Supabase

1. Go to [supabase.com](https://supabase.com) and create account
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string

#### Option C: PlanetScale

1. Go to [planetscale.com](https://planetscale.com) and create account
2. Create a new database
3. Copy the connection string

### 3. Deploy to Vercel

#### Method 1: Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect it as a Python project

#### Method 2: Vercel CLI

```bash
npm i -g vercel
vercel --prod
```

### 4. Configure Environment Variables

In your Vercel project dashboard, go to Settings → Environment Variables and add:

#### Required Variables:

```
DATABASE_URL=your-postgresql-connection-string
SECRET_KEY=your-super-secret-key-here
ADMIN_USER_1=your_admin_username
ADMIN_PASS_1=your_secure_password
```

#### Optional Variables:

```
ADMIN_USER_2=second_admin_username
ADMIN_PASS_2=second_secure_password
FLASK_ENV=production
```

### 5. Verify Deployment

1. Vercel will provide a URL for your application
2. Visit the URL and verify the application loads
3. Test the health check: `https://your-app.vercel.app/health`
4. Try logging in with your admin credentials

## Vercel Configuration Files

### `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  },
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

### `api/index.py`

```python
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, create_tables

try:
    create_tables()
except Exception as e:
    print(f"Warning: Could not initialize database tables: {e}")

if __name__ == "__main__":
    app.run()
```

## Environment Variables Reference

| Variable       | Required | Description                   | Default        |
| -------------- | -------- | ----------------------------- | -------------- |
| `DATABASE_URL` | Yes      | PostgreSQL connection string  | None           |
| `SECRET_KEY`   | Yes      | Flask secret key for sessions | Auto-generated |
| `ADMIN_USER_1` | Yes      | Primary admin username        | `sdfmagra`     |
| `ADMIN_PASS_1` | Yes      | Primary admin password        | `Admin@123`    |
| `ADMIN_USER_2` | No       | Secondary admin username      | `adfmagra`     |
| `ADMIN_PASS_2` | No       | Secondary admin password      | `Admin@1234`   |
| `FLASK_ENV`    | No       | Flask environment             | `production`   |

## Troubleshooting

### Common Issues

#### 1. Function Timeout

- **Problem**: Functions timeout after 30 seconds
- **Solution**: Optimize database queries, use connection pooling
- **Workaround**: Break large operations into smaller chunks

#### 2. Database Connection Issues

- **Problem**: Cold starts cause database timeouts
- **Solution**: Use connection pooling, shorter connection timeouts
- **Check**: Verify DATABASE_URL format and accessibility

#### 3. File Upload Issues

- **Problem**: Files disappear after function execution
- **Solution**: Implement cloud storage (AWS S3, Cloudinary, etc.)
- **Temporary**: Files stored in `/tmp` are ephemeral

#### 4. Memory Limits

- **Problem**: Large Excel files cause memory errors
- **Solution**: Process files in chunks, optimize pandas operations
- **Limit**: Vercel has memory limits per function

### Debug Mode

To enable debug logging:

```
FLASK_ENV=development
```

### Viewing Logs

1. Go to your Vercel project dashboard
2. Click on "Functions" tab
3. View real-time logs for debugging

## Vercel-Specific Optimizations

### 1. Database Configuration

```python
class VercelConfig(Config):
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'railway_file_management'
        }
    }
```

### 2. File Storage

```python
# Use /tmp for temporary files in Vercel
if os.environ.get('VERCEL'):
    upload_path = '/tmp'
    os.makedirs(upload_path, exist_ok=True)
```

### 3. Lightweight Dependencies

Use `requirements-vercel.txt` with only essential packages to reduce cold start time.

## Production Recommendations

### File Storage Solutions

Since Vercel has ephemeral storage, implement cloud storage:

#### AWS S3

```python
import boto3
s3 = boto3.client('s3')
```

#### Cloudinary

```python
import cloudinary
import cloudinary.uploader
```

#### Google Cloud Storage

```python
from google.cloud import storage
```

### Database Optimization

1. **Connection Pooling**: Use pgbouncer or similar
2. **Query Optimization**: Add indexes, optimize queries
3. **Connection Limits**: Set appropriate connection limits

### Performance Monitoring

1. **Vercel Analytics**: Enable Vercel Analytics
2. **Error Tracking**: Use Sentry or similar
3. **Database Monitoring**: Monitor database performance

## Limitations and Considerations

### Serverless Limitations

- ❌ **Persistent File Storage**: Files are lost after function execution
- ❌ **Long-Running Tasks**: 30-second timeout limit
- ❌ **Background Jobs**: No background processing
- ❌ **WebSockets**: Limited WebSocket support

### Recommended Alternatives

- **File Storage**: Use cloud storage services
- **Long Tasks**: Break into smaller operations
- **Background Jobs**: Use external job queues
- **Real-time Features**: Use external services

## Cost Considerations

### Vercel Pricing

- **Hobby Plan**: Free tier with limitations
- **Pro Plan**: $20/month with higher limits
- **Enterprise**: Custom pricing

### Database Costs

- **Neon**: Free tier available, paid plans start at $19/month
- **Supabase**: Free tier available, paid plans start at $25/month
- **PlanetScale**: Free tier available, paid plans start at $29/month

## Migration from Railway

If migrating from Railway:

1. **Database**: Export data from Railway PostgreSQL
2. **Environment Variables**: Copy all environment variables
3. **File Storage**: Implement cloud storage solution
4. **Testing**: Thoroughly test all functionality
5. **DNS**: Update domain settings if needed

## Support and Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **Flask on Vercel**: [vercel.com/guides/using-flask-with-vercel](https://vercel.com/guides/using-flask-with-vercel)

## Summary

Vercel deployment is suitable for:

- ✅ **Small to medium applications**
- ✅ **Read-heavy workloads**
- ✅ **Applications with external file storage**
- ✅ **Cost-effective hosting**

Not suitable for:

- ❌ **File-heavy applications without cloud storage**
- ❌ **Long-running operations**
- ❌ **Applications requiring persistent local storage**
- ❌ **High-frequency database writes**

Choose Vercel if you need cost-effective serverless hosting and can work within the serverless constraints.
