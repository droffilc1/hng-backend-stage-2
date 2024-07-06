#!/usr/bin/env python3
"""organisation."""
import uuid
from app import db


user_organisations = db.Table('user_organisations',
                              db.Column('user_id', db.String, db.ForeignKey(
                                  'users.userId'), primary_key=True),
                              db.Column('organisation_id', db.String, db.ForeignKey(
                                  'organisations.orgId'), primary_key=True)
                              )


class Organisation(db.Model):
    """Organisation class."""
    __tablename__ = 'organisations'

    orgId = db.Column(db.String, primary_key=True,
                      default=lambda: str(uuid.uuid4()), unique=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_by = db.Column(db.String, db.ForeignKey('users.userId'))
