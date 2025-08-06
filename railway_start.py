#!/usr/bin/env python3
"""
Railway-specific startup script for the File Management System.
This script handles Railway-specific initialization and configuration.
"""

import os
import sys
import time
from app import app, create_tables


def wait_for_database(max_retries=30, delay=2):
    """Wait for database to be available with retries"""
    print("Waiting for database connection...")

    for attempt in range(max_retries):
        try:
            if create_tables():
                print("Database connection established successfully")
                return True
        except Exception as e:
            print(
                f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}"
            )
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)

    print("Failed to connect to database after all retries")
    return False


def setup_railway_environment():
    """Setup Railway-specific environment variables and configurations"""

    # Set production environment
    os.environ.setdefault("FLASK_ENV", "production")

    # Railway provides PORT automatically
    port = os.environ.get("PORT", "5000")
    print(f"Starting application on port {port}")

    # Validate required environment variables
    required_vars = ["DATABASE_URL"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"WARNING: Missing environment variables: {', '.join(missing_vars)}")
        print("The application may not work correctly without these variables")

    # Print configuration info (without sensitive data)
    print("Railway Configuration:")
    print(f"- FLASK_ENV: {os.environ.get('FLASK_ENV', 'not set')}")
    print(f"- PORT: {port}")
    print(f"- DATABASE_URL: {'set' if os.environ.get('DATABASE_URL') else 'not set'}")
    print(f"- SECRET_KEY: {'set' if os.environ.get('SECRET_KEY') else 'not set'}")
    print(f"- UPLOAD_FOLDER: {os.environ.get('UPLOAD_FOLDER', 'uploads')}")


def main():
    """Main startup function for Railway deployment"""
    print("Starting Railway File Management System...")

    # Setup Railway environment
    setup_railway_environment()

    # Wait for database to be ready
    if not wait_for_database():
        print("ERROR: Could not establish database connection")
        print("Please check your DATABASE_URL environment variable")
        sys.exit(1)

    print("Application startup completed successfully")
    print("Ready to handle requests")


if __name__ == "__main__":
    main()
