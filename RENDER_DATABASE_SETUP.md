# Render Database Setup Guide

This guide helps you manually configure the DATABASE_URL when automatic connection fails.

## Issue: DATABASE_URL Connection Problems

If you're seeing errors like:

```
ValueError: invalid literal for int() with base 10: 'port'
```

This means the DATABASE_URL environment variable is malformed.

## Solution 1: Manual DATABASE_URL Configuration

### Step 1: Get Database Connection Details

1. Go to your Render dashboard
2. Click on your PostgreSQL service (`railway-file-management-db`)
3. Go to the "Info" tab
4. Note down these values:
   - **Host**: (e.g., `dpg-xxxxx-a.oregon-postgres.render.com`)
   - **Port**: (usually `5432`)
   - **Database**: `railway_file_management`
   - **Username**: `railway_user`
   - **Password**: (click "Show" to reveal)

### Step 2: Construct DATABASE_URL

Format: `postgresql://username:password@host:port/database`

Example:

```
postgresql://railway_user:your_password_here@dpg-xxxxx-a.oregon-postgres.render.com:5432/railway_file_management
```

### Step 3: Set DATABASE_URL Manually

1. Go to your web service (`railway-file-management`)
2. Go to "Environment" tab
3. Find the `DATABASE_URL` variable
4. Click "Edit"
5. Replace the value with your manually constructed URL
6. Click "Save Changes"
7. Redeploy your service

## Solution 2: Use render-fixed.yaml

Replace your current `render.yaml` with `render-fixed.yaml`:

```bash
mv render.yaml render-original.yaml
mv render-fixed.yaml render.yaml
git add .
git commit -m "Use fixed Render configuration"
git push origin main
```

This configuration:

- Runs the database URL validation script first
- Uses fewer workers to reduce memory usage
- Removes the automatic DATABASE_URL connection (you'll set it manually)

## Solution 3: Separate Service Creation

Instead of using render.yaml, create services manually:

### Create PostgreSQL Database First:

1. Go to Render dashboard
2. Click "New" → "PostgreSQL"
3. Configure:
   - **Name**: `railway-file-management-db`
   - **Database Name**: `railway_file_management`
   - **User**: `railway_user`
   - **Plan**: Starter
4. Wait for database to be ready
5. Note the connection details

### Create Web Service Second:

1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `railway-file-management`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python fix_database_url.py && python render_start.py && gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app`

### Set Environment Variables:

```
FLASK_ENV=production
RENDER=1
PORT=10000
DATABASE_URL=postgresql://railway_user:PASSWORD@HOST:5432/railway_file_management
SECRET_KEY=your_secret_key_here
ADMIN_USER_1=admin
ADMIN_PASS_1=your_admin_password
```

### Add Persistent Disk:

1. In web service settings
2. Go to "Disks" tab
3. Add disk:
   - **Name**: `uploads`
   - **Mount Path**: `/opt/render/project/src/uploads`
   - **Size**: `1 GB`

## Troubleshooting DATABASE_URL

### Check URL Format:

```python
# Test your DATABASE_URL format
import re
url = "your_database_url_here"
pattern = r'^postgres(?:ql)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)$'
match = re.match(pattern, url)
if match:
    print("URL format is valid")
    username, password, host, port, database = match.groups()
    print(f"Host: {host}, Port: {port}, Database: {database}")
else:
    print("URL format is invalid")
```

### Common URL Issues:

1. **Missing port**: `postgresql://user:pass@host/db` → `postgresql://user:pass@host:5432/db`
2. **Literal 'port'**: `postgresql://user:pass@host:port/db` → `postgresql://user:pass@host:5432/db`
3. **Wrong protocol**: `postgres://` vs `postgresql://` (both work, but be consistent)
4. **Special characters in password**: URL-encode special characters

### Test Database Connection:

```python
import psycopg2
import os

# Test connection
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()
    cursor.execute('SELECT version()')
    version = cursor.fetchone()
    print(f"Connected to: {version[0]}")
    cursor.close()
    conn.close()
    print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## Alternative: Use External Database

If Render's PostgreSQL continues to have issues, you can use an external database:

### Option 1: Neon (Recommended)

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Get the connection string
4. Set as DATABASE_URL in Render

### Option 2: Supabase

1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string
5. Set as DATABASE_URL in Render

### Option 3: ElephantSQL

1. Sign up at [elephantsql.com](https://elephantsql.com)
2. Create a new instance
3. Copy the URL
4. Set as DATABASE_URL in Render

## Verification

After setting up DATABASE_URL:

1. **Check Environment Variable**:

   ```bash
   # In Render shell
   echo $DATABASE_URL
   ```

2. **Test Application**:

   ```bash
   python verify_render.py
   ```

3. **Check Health Endpoint**:
   ```bash
   curl https://your-app.onrender.com/health
   ```

## Success Indicators

Your setup is working when:

- ✅ No "invalid literal for int()" errors in logs
- ✅ Health endpoint returns `"database": "connected"`
- ✅ Application starts without database errors
- ✅ You can log in and use the application

## Getting Help

If you're still having issues:

1. **Check Render Logs**: Look for specific error messages
2. **Verify Database Service**: Ensure PostgreSQL service is running
3. **Test Connection**: Use the Python script above to test connectivity
4. **Contact Support**: Render support can help with database connection issues

Remember: The DATABASE_URL must be exactly correct - even a small typo will cause connection failures.
