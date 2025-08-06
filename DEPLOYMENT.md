# Railway File Management System - Cloud Deployment Guide

This guide covers deploying the Railway File Management System to various cloud platforms.

## Prerequisites

1. A PostgreSQL database (cloud-hosted)
2. Environment variables configured
3. Python 3.11+ runtime

## Environment Variables

Set these environment variables in your cloud platform:

### Required Variables

- `DATABASE_URL`: PostgreSQL connection string (automatically provided by most cloud platforms)
- `SECRET_KEY`: Strong secret key for Flask sessions (generate a secure one for production)

### Optional Variables

- `FLASK_ENV`: Set to `production` for production deployment (default: `development`)
- `PORT`: Port number (default: `5000`, automatically set by most platforms)
- `UPLOAD_FOLDER`: Upload directory (default: `uploads`)

### Admin User Configuration

- `ADMIN_USER_1`: First admin username (default: `sdfmagra`)
- `ADMIN_PASS_1`: First admin password (default: `Admin@123`)
- `ADMIN_USER_2`: Second admin username (default: `adfmagra`)
- `ADMIN_PASS_2`: Second admin password (default: `Admin@1234`)

## Platform-Specific Deployment

### 1. Railway

1. **Connect Repository**: Link your GitHub repository to Railway
2. **Add PostgreSQL**: Add a PostgreSQL database service
3. **Set Environment Variables**:
   ```
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=production
   ADMIN_USER_1=your-admin-username
   ADMIN_PASS_1=your-secure-password
   ```
4. **Deploy**: Railway will automatically deploy using the `Procfile`

### 2. Heroku

1. **Create App**: `heroku create your-app-name`
2. **Add PostgreSQL**: `heroku addons:create heroku-postgresql:mini`
3. **Set Environment Variables**:
   ```bash
   heroku config:set SECRET_KEY=your-super-secret-key-here
   heroku config:set FLASK_ENV=production
   heroku config:set ADMIN_USER_1=your-admin-username
   heroku config:set ADMIN_PASS_1=your-secure-password
   ```
4. **Deploy**: `git push heroku main`

### 3. Vercel

1. **Install Vercel CLI**: `npm i -g vercel`
2. **Deploy**: `vercel --prod`
3. **Add PostgreSQL**: Use Vercel Postgres or external database
4. **Set Environment Variables** in Vercel dashboard

### 4. Google Cloud Run

1. **Build Container**: `docker build -t gcr.io/PROJECT-ID/railway-app .`
2. **Push to Registry**: `docker push gcr.io/PROJECT-ID/railway-app`
3. **Deploy**:
   ```bash
   gcloud run deploy railway-app \
     --image gcr.io/PROJECT-ID/railway-app \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### 5. AWS (Elastic Beanstalk)

1. **Install EB CLI**: `pip install awsebcli`
2. **Initialize**: `eb init`
3. **Create Environment**: `eb create production`
4. **Set Environment Variables** in AWS console
5. **Deploy**: `eb deploy`

### 6. DigitalOcean App Platform

1. **Create App** from GitHub repository
2. **Add Database**: PostgreSQL database component
3. **Set Environment Variables** in app settings
4. **Deploy**: Automatic deployment from repository

## Database Setup

The application will automatically create database tables on first run. Ensure your PostgreSQL database is accessible and the `DATABASE_URL` is correctly configured.

## File Storage Considerations

### Local File System (Default)

- Files are stored in the `uploads/` directory
- **Warning**: Files may be lost on container restarts in some platforms

### Cloud Storage (Recommended for Production)

Consider implementing cloud storage (AWS S3, Google Cloud Storage, etc.) for file persistence:

1. Update `app.py` to use cloud storage SDK
2. Modify file upload/download functions
3. Set appropriate environment variables for cloud storage credentials

## Security Recommendations

1. **Change Default Credentials**: Always change default admin usernames and passwords
2. **Use Strong Secret Key**: Generate a cryptographically secure secret key
3. **Enable HTTPS**: Ensure your deployment uses HTTPS
4. **Database Security**: Use strong database passwords and restrict access
5. **Environment Variables**: Never commit sensitive data to version control

## Monitoring and Logging

1. **Health Checks**: The app includes a health check endpoint at `/login`
2. **Logging**: Application logs are sent to stdout for cloud platform integration
3. **Error Tracking**: Consider adding error tracking services (Sentry, etc.)

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:

   - Verify `DATABASE_URL` format
   - Check database accessibility
   - Ensure PostgreSQL version compatibility

2. **File Upload Issues**:

   - Check `UPLOAD_FOLDER` permissions
   - Verify disk space availability
   - Consider file size limits

3. **Authentication Problems**:
   - Verify admin credentials in environment variables
   - Check session configuration

### Debug Mode

For debugging, set `FLASK_ENV=development` (not recommended for production).

## Performance Optimization

1. **Database Indexing**: Add indexes for frequently queried columns
2. **Connection Pooling**: Configure database connection pooling
3. **Caching**: Implement caching for static content
4. **CDN**: Use CDN for static assets

## Backup and Recovery

1. **Database Backups**: Set up automated database backups
2. **File Backups**: Implement file storage backups
3. **Disaster Recovery**: Plan for disaster recovery scenarios

## Support

For deployment issues, check:

1. Platform-specific documentation
2. Application logs
3. Database connectivity
4. Environment variable configuration
