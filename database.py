"""
Shared SQLAlchemy database instance.
Imported by app.py and all models.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()