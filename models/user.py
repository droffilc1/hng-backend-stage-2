#!/usr/bin/env python3
"""User."""
import uuid
from app import db


class User(db.Model):
    """User class."""
    __tablename__ = 'users'

    userId = db.Column(db.String, primary_key=True,
                       default=lambda: str(uuid.uuid4()), unique=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    organisations = db.relationship(
        'Organisation', secondary='user_organisations', backref='users')
