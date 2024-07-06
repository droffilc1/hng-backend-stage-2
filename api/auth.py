#!/usr/bin/env python3
"""auth."""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.organisation import Organisation

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """POST /register"""
    data = request.get_json()
    errors = validate_user_data(data)
    if errors:
        return jsonify({"errors": errors}), 422

    hashed_password = generate_password_hash(
        data['password'], method='pbkdf2:sha256')
    new_user = User(
        firstName=data['firstName'],
        lastName=data['lastName'],
        email=data['email'],
        password=hashed_password,
        phone=data.get('phone')
    )

    default_org = Organisation(
        name=f"{data['firstName']}'s Organisation",
        created_by=new_user.userId
    )
    new_user.organisations.append(default_org)

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


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /login"""
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
