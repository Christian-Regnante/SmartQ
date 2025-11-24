"""Application configuration container.

This module defines the `Config` class used to configure the Flask
application. Values are read from environment variables when available,
with sensible defaults for local development. Update the environment
variables in production (especially `SECRET_KEY` and the database URI).
"""

import os


class Config:
    """Configuration values for Flask and extensions.

    Attributes are read by Flask via `app.config.from_object(Config)`.
    """
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'mysql+pymysql://smartq_user:smartq_password@localhost/smartq_db'
    
    # use this for docker setup

    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    # f"mysql+pymysql://{os.environ.get('DB_USER','smartq_user')}:" \
    # f"{os.environ.get('DB_PASSWORD','smartq_password')}@" \
    # f"{os.environ.get('DB_HOST','db')}/" \
    # f"{os.environ.get('DB_NAME','smartq_db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Twilio configuration (mock for now)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID') or 'mock_sid'
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN') or 'mock_token'
    TWILIO_PHONE_NUMBER = os.environ.get(
        'TWILIO_PHONE_NUMBER') or '+250788000000'
