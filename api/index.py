"""
Vercel entry point for the Railway File Management System.
This file serves as the main entry point for Vercel's serverless functions.
"""

import os
import sys

# Add the parent directory to the Python path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Vercel environment flag
os.environ["VERCEL"] = "1"

from app import app, create_tables

# Initialize database tables on cold start (with error handling for serverless)
try:
    with app.app_context():
        create_tables()
        print("Database tables initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize database tables: {e}")
    print(
        "This is normal in serverless environments - tables will be created on first database access"
    )

# Vercel expects the Flask app to be available as 'app'
# This is the WSGI application that Vercel will use
if __name__ == "__main__":
    app.run(debug=False)
