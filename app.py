#!/usr/bin/env python3
"""Main Entry."""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)


class User(db.Model):
    """User class"""
    userId = db.Column(db.String, primary_key=True, unique=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)


@app.route('/auth/register', methods=['POST'])
def register():
    """POST /auth/register."""
    data = request.get_json()
    errors = validate_user_data(data)
    if errors:
        return jsonify({"errors": errors}), 422

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(
        firstName=data['firstName'],
        lastName=data['lastName'],
        email=data['email'],
        password=hashed_password,
        phone=data.get('phone')
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        access_token = create_access_token(identity=new_user.userId)
        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "accessToken": access_token,
                "user": {
                    "userId": new_user.userId,
                    "firstName": new_user.firstName,
                    "lastName": new_user.lastName,
                    "email": new_user.email,
                    "phone": new_user.phone,
                }
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "Bad request", "message": "Registration unsuccessful"}), 400


@app.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"status": "Bad request", "message": "Authentication failed"}), 401

    access_token = create_access_token(identity=user.userId)
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "data": {
            "accessToken": access_token,
            "user": {
                "userId": user.userId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phone": user.phone,
            }
        }
    }), 200


def validate_user_data(data):
    """Validate user."""
    errors = []
    required_fields = ["firstName", "lastName", "email", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append({"field": field, "message": f"{field} is required"})
    if 'email' in data and User.query.filter_by(email=data['email']).first():
        errors.append(
            {"field": "email", "message": "Email is already registered"})
    return errors
