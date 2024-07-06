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
    userId = db.Column(db.String, primary_key=True,
                       default=lambda: str(uuid.uuid4()), unique=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)


class Organisation(db.Model):
    """Organisation class."""
    orgId = db.Column(db.String, primary_key=True,
                      default=lambda: str(uuid.uuid4()), unique=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_by = db.Column(db.String, db.ForeignKey('user.userId'))


user_organisations = db.Table('user_organisations',
                              db.Column('user_id', db.String, db.ForeignKey(
                                  'user.userId'), primary_key=True),
                              db.Column('organisation_id', db.String, db.ForeignKey(
                                  'organisation.orgId'), primary_key=True)
                              )


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


@app.route('/api/users/<string:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    """GET /api/users/<string:id>"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(userId=id).first()
    if not user:
        return jsonify({"status": "Not found", "message": "User not found"}), 404

    user_data = {
        "userId": user.userId,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "phone": user.phone
    }
    return jsonify({"status": "success", "message": "User found", "data": user_data}), 200


@app.route('/api/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    """GET /api/organisations"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(userId=current_user).first()
    organisations = [org for org in user.organisations]
    orgs_data = [{"orgId": org.orgId, "name": org.name,
                  "description": org.description} for org in organisations]
    return jsonify({"status": "success", "message": "Organisations retrieved", "data": {"organisations": orgs_data}}), 200


@app.route('/api/organisations/<string:orgId>', methods=['GET'])
@jwt_required()
def get_organisation(orgId):
    """GET /api/organisations/<string:orgId>"""
    current_user = get_jwt_identity()
    org = Organisation.query.filter_by(orgId=orgId).first()
    if not org or current_user not in [user.userId for user in org.users]:
        return jsonify({"status": "Not found", "message": "Organisation not found"}), 404

    org_data = {"orgId": org.orgId, "name": org.name,
                "description": org.description}
    return jsonify({"status": "success", "message": "Organisation retrieved", "data": org_data}), 200


@app.route('/api/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    """POST /api/organisations"""
    current_user = get_jwt_identity()
    data = request.get_json()
    if 'name' not in data or not data['name']:
        return jsonify({"status": "Bad Request", "message": "Name is required"}), 400

    new_org = Organisation(
        name=data['name'],
        description=data.get('description'),
        created_by=current_user
    )

    try:
        db.session.add(new_org)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Organisation created successfully",
            "data": {
                "orgId": new_org.orgId,
                "name": new_org.name,
                "description": new_org.description
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "Bad Request", "message": "Client error"}), 400


@app.route('/api/organisations/<string:orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(orgId):
    """POST /api/organisations/<string:orgId>/users"""
    current_user = get_jwt_identity()
    data = request.get_json()
    user = User.query.filter_by(userId=data['userId']).first()
    organisation = Organisation.query.filter_by(orgId=orgId).first()

    if not user or not organisation:
        return jsonify({"status": "Not found", "message": "User or organisation not found"}), 404

    organisation.users.append(user)
    try:
        db.session.commit()
        return jsonify({"status": "success", "message": "User added to organisation successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "Bad Request", "message": "Client error"}), 400
