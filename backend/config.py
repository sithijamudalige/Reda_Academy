import os
from datetime import datetime, timedelta
# backend/config.py
class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1230@localhost:5432/online_learning_platform_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "supersecretkey"