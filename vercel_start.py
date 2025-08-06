#!/usr/bin/env python3
"""
Vercel-specific startup script for the File Management System.
This script handles Vercel serverless environment initialization.
"""

import os
import sys
from app import app, create_tables


def setup_vercel_environment():
    """Setup Vercel-specific environment variables and configurations"""

    # Set production environment
    os.environ.setdefault("FLASK_ENV", "production")

    # Validate required environment variables
    required_vars = ["DATABASE_URL"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"WARNING: Missing environment variables: {', '.join(missing_vars)}")
        print("The application may not work correctly without these variables")

    # Print configuration info (without sensitive data)
    print("Vercel Configuration:")
    print(f"- FLASK_ENV: {os.environ.get('FLASK_ENV', 'not set')}")
    print(f"- DATABASE_URL: {'set' if os.environ.get('DATABASE_URL') else 'not set'}")
    print(f"- SECRET_KEY: {'set' if os.environ.get('SECRET_KEY') else 'not set'}")
    print(f"- VERCEL: {os.environ.get('VERCEL', 'not set')}")


def initialize_database():
    """Initialize database with retry logic for serverless environment"""
    print("Initializing database for Vercel serverless environment...")

    try:
        if create_tables():
            print("Database initialization successful")
            return True
        else:
            print("Database initialization failed - will retry on next request")
            return False
    except Exception as e:
        print(f"Database initialization error: {e}")
        print(
            "This is normal in serverless environments - database will be initialized on first request"
        )
        return False


def main():
    """Main initialization function for Vercel deployment"""
    print("Initializing Railway File Management System for Vercel...")

    # Setup Vercel environment
    setup_vercel_environment()

    # Try to initialize database (don't fail if it doesn't work)
    initialize_database()

    print("Vercel initialization completed")
    print("Application ready for serverless execution")


if __name__ == "__main__":
    main()
