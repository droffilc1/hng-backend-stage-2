#!/usr/bin/env python3
"""config."""
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """Config class."""
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    TESTING = False


class TestConfig(Config):
    """Test config."""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
