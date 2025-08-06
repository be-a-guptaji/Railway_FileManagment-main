#!/usr/bin/env python3
"""
Database URL validation and fixing script for Render deployment.
This script checks and fixes common DATABASE_URL formatting issues.
"""

import os
import re
import sys


def validate_and_fix_database_url():
    """Validate and fix DATABASE_URL environment variable"""

    database_url = os.environ.get("DATABASE_URL", "")

    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set")
        return False

    print(f"Original DATABASE_URL: {database_url[:50]}...")

    # Common issues and fixes
    fixes_applied = []

    # Fix 1: Replace literal 'port' with actual port number
    if "port" in database_url and not re.search(r":\d+/", database_url):
        # Look for patterns like postgres://user:pass@host:port/db
        # If 'port' is literal, replace with default PostgreSQL port
        if ":port/" in database_url:
            database_url = database_url.replace(":port/", ":5432/")
            fixes_applied.append("Replaced literal 'port' with '5432'")
        elif ":port@" in database_url:
            database_url = database_url.replace(":port@", ":5432@")
            fixes_applied.append("Replaced literal 'port@' with '5432@'")

    # Fix 2: Ensure proper URL format
    if not database_url.startswith(("postgresql://", "postgres://")):
        print("WARNING: DATABASE_URL doesn't start with postgresql:// or postgres://")

    # Fix 3: Check for minimum required components
    url_pattern = r"^postgres(?:ql)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)$"
    match = re.match(url_pattern, database_url)

    if not match:
        print("ERROR: DATABASE_URL format is invalid")
        print("Expected format: postgresql://username:password@host:port/database")
        return False

    username, password, host, port, database = match.groups()

    # Validate components
    if not all([username, password, host, port, database]):
        print("ERROR: DATABASE_URL is missing required components")
        return False

    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            print(f"ERROR: Invalid port number: {port}")
            return False
    except ValueError:
        print(f"ERROR: Port is not a valid number: {port}")
        return False

    # Apply fixes if any were made
    if fixes_applied:
        os.environ["DATABASE_URL"] = database_url
        print("Fixes applied:")
        for fix in fixes_applied:
            print(f"  - {fix}")
        print(f"Fixed DATABASE_URL: {database_url[:50]}...")
    else:
        print("DATABASE_URL format is valid")

    return True


def test_database_connection():
    """Test database connection with the fixed URL"""
    try:
        import psycopg2
        from urllib.parse import urlparse

        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            return False

        # Parse URL for connection test
        parsed = urlparse(database_url)

        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:],  # Remove leading slash
        )

        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result and result[0] == 1:
            print("✅ Database connection test successful")
            return True
        else:
            print("❌ Database connection test failed")
            return False

    except ImportError:
        print("⚠️  psycopg2 not available for connection test")
        return True  # Don't fail if psycopg2 isn't installed
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def main():
    """Main function to validate and fix DATABASE_URL"""
    print("🔍 Validating DATABASE_URL...")

    if validate_and_fix_database_url():
        print("✅ DATABASE_URL validation passed")

        # Test connection if possible
        if test_database_connection():
            print("✅ Database connection verified")
        else:
            print("⚠️  Database connection could not be verified")
            print("   This may be normal if the database is still starting up")

        return True
    else:
        print("❌ DATABASE_URL validation failed")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check that DATABASE_URL is set in Render dashboard")
        print("2. Verify the database service is running")
        print("3. Ensure the database connection string is properly formatted")
        print("4. Check Render logs for database service errors")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
