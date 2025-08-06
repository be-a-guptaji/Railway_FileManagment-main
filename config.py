import os
from urllib.parse import urlparse


class Config:
    """Base configuration class"""

    SECRET_KEY = os.environ.get("SECRET_KEY", "yK@p1A$9vTz3!mB2#qW8^LrXeCfHsJ0u")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")

    # Database configuration
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL:
        # Fix for Railway/Heroku postgres URL format
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "SQLALCHEMY_DATABASE_URI",
            "postgresql://postgres:Password@localhost/file_management",
        )

    # Admin users configuration
    ADMIN_USERS = {
        os.environ.get("ADMIN_USER_1", "sdfmagra"): {
            "password": os.environ.get("ADMIN_PASS_1", "Admin@123"),
            "id": 1,
        },
        os.environ.get("ADMIN_USER_2", "adfmagra"): {
            "password": os.environ.get("ADMIN_PASS_2", "Admin@1234"),
            "id": 2,
        },
    }


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    FLASK_ENV = "production"

    # Use stronger secret key in production
    if os.environ.get("SECRET_KEY"):
        SECRET_KEY = os.environ.get("SECRET_KEY")
    else:
        # For Railway deployment, use a default secure key if not provided
        # In production, you should always set SECRET_KEY environment variable
        import secrets

        SECRET_KEY = secrets.token_urlsafe(32)
        print(
            "WARNING: Using generated SECRET_KEY. Set SECRET_KEY environment variable for production."
        )


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class VercelConfig(Config):
    """Vercel serverless configuration"""

    DEBUG = False
    FLASK_ENV = "production"

    # Vercel-specific optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": "railway_file_management",
        },
    }

    # Use stronger secret key in production
    if os.environ.get("SECRET_KEY"):
        SECRET_KEY = os.environ.get("SECRET_KEY")
    else:
        # For Vercel deployment, use a default secure key if not provided
        import secrets

        SECRET_KEY = secrets.token_urlsafe(32)
        print(
            "WARNING: Using generated SECRET_KEY. Set SECRET_KEY environment variable for production."
        )

    # Vercel has limited file system access
    UPLOAD_FOLDER = "/tmp/uploads"


class RenderConfig(Config):
    """Render.com configuration"""

    DEBUG = False
    FLASK_ENV = "production"

    # Render-specific optimizations
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # Longer recycle time for persistent containers
        "pool_size": 5,
        "max_overflow": 10,
        "connect_args": {
            "connect_timeout": 30,
            "application_name": "railway_file_management_render",
        },
    }

    # Use stronger secret key in production
    if os.environ.get("SECRET_KEY"):
        SECRET_KEY = os.environ.get("SECRET_KEY")
    else:
        # For Render deployment, use a default secure key if not provided
        import secrets

        SECRET_KEY = secrets.token_urlsafe(32)
        print(
            "WARNING: Using generated SECRET_KEY. Set SECRET_KEY environment variable for production."
        )

    # Render has persistent disk storage
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "vercel": VercelConfig,
    "render": RenderConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    # Detect Vercel environment
    if os.environ.get("VERCEL"):
        return config["vercel"]

    # Detect Render environment
    if os.environ.get("RENDER"):
        return config["render"]

    env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])
