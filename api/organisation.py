#!/usr/bin/env python3
"""organisation."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.user import User
from models.organisation import Organisation

organisation_bp = Blueprint('organisation', __name__)


@organisation_bp.route('/users/<string:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    """GET /users/<string:id>"""
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


@organisation_bp.route('/organisations', methods=['GET'])
@jwt_required()
def get_organisations():
    """GET /organisations"""
    current_user = get_jwt_identity()
    user = User.query.filter_by(userId=current_user).first()
    organisations = [org for org in user.organisations]
    orgs_data = [{"orgId": org.orgId, "name": org.name,
                  "description": org.description} for org in organisations]
    return jsonify({"status": "success", "message": "Organisations retrieved", "data": {"organisations": orgs_data}}), 200


@organisation_bp.route('/organisations/<string:orgId>', methods=['GET'])
@jwt_required()
def get_organisation(orgId):
    """GET /organisations/<string:orgId>"""
    current_user = get_jwt_identity()
    org = Organisation.query.filter_by(orgId=orgId).first()
    if not org or current_user not in [user.userId for user in org.users]:
        return jsonify({"status": "Not found", "message": "Organisation not found"}), 404

    org_data = {"orgId": org.orgId, "name": org.name,
                "description": org.description}
    return jsonify({"status": "success", "message": "Organisation retrieved", "data": org_data}), 200


@organisation_bp.route('/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    """POST /organisations"""
    current_user = get_jwt_identity()
    data = request.get_json()
    if 'name' not in data or not data['name']:
        return jsonify({"status": "Bad Request", "message": "Name is required"}), 400

    new_org = Organisation(
        name=data['name'],
        description=data.get('description'),
        created_by=current_user
    )
    user = User.query.filter_by(userId=current_user).first()
    user.organisations.append(new_org)
    try:
        db.session.add(new_org)
        db.session.commit()
        org_data = {"orgId": new_org.orgId, "name": new_org.name,
                    "description": new_org.description}
        return jsonify({"status": "success", "message": "Organisation created successfully", "data": org_data}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "Bad Request", "message": "Client error"}), 400


@organisation_bp.route('/organisations/<string:orgId>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(orgId):
    """POST /organisations/<string:orgId>/users"""
    current_user = get_jwt_identity()
    data = request.get_json()
    if 'userId' not in data or not data['userId']:
        return jsonify({"status": "Bad Request", "message": "userId is required"}), 400

    org = Organisation.query.filter_by(orgId=orgId).first()
    if not org:
        return jsonify({"status": "Not found", "message": "Organisation not found"}), 404

    user = User.query.filter_by(userId=data['userId']).first()
    if not user:
        return jsonify({"status": "Not found", "message": "User not found"}), 404

    org.users.append(user)
    db.session.commit()
    return jsonify({"status": "success", "message": "User added to organisation successfully"}), 200
