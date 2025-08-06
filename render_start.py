#!/usr/bin/env python3
"""
Render.com startup script for the Railway File Management System.
This script handles Render-specific environment initialization.
"""

import os
import sys
import time
from app import app, create_tables


def setup_render_environment():
    """Setup Render-specific environment variables and configurations"""

    # Set Render environment flag
    os.environ["RENDER"] = "1"

    # Set production environment
    os.environ.setdefault("FLASK_ENV", "production")

    # Validate and fix DATABASE_URL
    print("Validating DATABASE_URL...")
    try:
        from fix_database_url import validate_and_fix_database_url

        if not validate_and_fix_database_url():
            print("ERROR: DATABASE_URL validation failed")
            return False
    except ImportError:
        print("DATABASE_URL validation script not found, using basic validation")
        # Basic validation
        database_url = os.environ.get("DATABASE_URL", "")
        if not database_url:
            print("ERROR: DATABASE_URL environment variable is not set")
            return False
        elif "port" in database_url and not any(
            char.isdigit() for char in database_url.split("port")[1][:10]
        ):
            print(
                "ERROR: DATABASE_URL appears malformed - contains 'port' without numeric value"
            )
            return False

    # Print configuration info (without sensitive data)
    print("Render Configuration:")
    print(f"- FLASK_ENV: {os.environ.get('FLASK_ENV', 'not set')}")
    print(f"- DATABASE_URL: {'set' if os.environ.get('DATABASE_URL') else 'not set'}")
    print(f"- SECRET_KEY: {'set' if os.environ.get('SECRET_KEY') else 'not set'}")
    print(f"- RENDER: {os.environ.get('RENDER', 'not set')}")

    # Validate and fix PORT environment variable
    port_value = os.environ.get("PORT", "10000")
    try:
        port_int = int(port_value)
        print(f"- PORT: {port_int}")
    except (ValueError, TypeError):
        print(f"- PORT: Invalid value '{port_value}', will use default")
        # Set a valid default port for Render
        os.environ["PORT"] = "10000"

    return True


def wait_for_database():
    """Wait for database to be ready with retry logic"""
    print("Waiting for database to be ready...")

    max_retries = 30
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            with app.app_context():
                from sqlalchemy import text
                from models import db

                # Test database connection
                db.session.execute(text("SELECT 1"))
                db.session.commit()
                print(f"Database connection successful on attempt {attempt + 1}")
                return True

        except Exception as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Database may not be ready.")
                return False

    return False


def initialize_database():
    """Initialize database with retry logic for Render environment"""
    print("Initializing database for Render environment...")

    # Wait for database to be ready
    if not wait_for_database():
        print("WARNING: Database not ready, but continuing startup...")
        return False

    try:
        if create_tables():
            print("Database initialization successful")
            return True
        else:
            print("Database initialization failed")
            return False
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False


def setup_upload_directory():
    """Setup upload directory for Render persistent disk"""
    try:
        upload_path = os.environ.get("UPLOAD_FOLDER", "uploads")

        # Create upload directory if it doesn't exist
        if not os.path.exists(upload_path):
            os.makedirs(upload_path, exist_ok=True)
            print(f"Created upload directory: {upload_path}")
        else:
            print(f"Upload directory exists: {upload_path}")

        # Test write permissions
        test_file = os.path.join(upload_path, ".render_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print("Upload directory is writable")
            return True
        except Exception as e:
            print(f"Upload directory is not writable: {e}")
            return False

    except Exception as e:
        print(f"Error setting up upload directory: {e}")
        return False


def main():
    """Main initialization function for Render deployment"""
    print("=" * 60)
    print("Initializing Railway File Management System for Render...")
    print("=" * 60)

    # Setup Render environment
    env_ready = setup_render_environment()
    if not env_ready:
        print("❌ Environment setup failed")
        return False

    # Setup upload directory
    setup_upload_directory()

    # Initialize database
    database_ready = initialize_database()

    if database_ready:
        print("✅ Render initialization completed successfully")
    else:
        print("⚠️  Render initialization completed with warnings")
        print("   Database may not be fully ready - will retry on first request")

    print("🚀 Application ready for Render deployment")
    print("=" * 60)
    return True


if __name__ == "__main__":
    main()
