"""
Base Database Model & Utilities.
Demonstrates:
- Reusable base class with timestamps
- Helper serialization methods
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance
db = SQLAlchemy()


class BaseModel(db.Model):
    """
    Abstract Base Model for all database entities.
    Demonstrates:
    - Inheritance: Reusable created_at, updated_at timestamps and helper methods
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Serializes entity columns into a dictionary."""
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
