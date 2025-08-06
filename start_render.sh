#!/bin/bash
# Render startup script for Railway File Management System

echo "Starting Railway File Management System on Render..."

# Set default PORT if not provided or invalid
if [ -z "$PORT" ] || ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "PORT not set or invalid, using default 10000"
    export PORT=10000
fi

echo "Using PORT: $PORT"

# Run the Python initialization script
python render_start.py

# Check if initialization was successful
if [ $? -eq 0 ]; then
    echo "Initialization successful, starting gunicorn..."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload app:app
else
    echo "Initialization failed, but starting gunicorn anyway..."
    exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload app:app
fi