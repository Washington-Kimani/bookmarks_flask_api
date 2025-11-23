from flask import Flask, Blueprint, request, jsonify
from src.constants.http_status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from src.database import db, User
from flask_jwt_extended import jwt_required, get_jwt_identity

users = Blueprint('users', __name__, url_prefix='/api/v1/users')

# routes
# get users route
@users.route('/', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    if current_user is None:
        return jsonify({
            'status': 'error',
        }), HTTP_401_UNAUTHORIZED
    data = []
    all_users = User.query.all()
    for user in all_users:
        data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
        })
    return jsonify({
        "users": data
    }), HTTP_200_OK

# get user by id
@users.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user_by_id(id):
    current_user = get_jwt_identity()
    if current_user is None:
        return jsonify({
            'status': "error, you're not authorized",
        }), HTTP_401_UNAUTHORIZED
    user = User.query.filter_by(id=id).first()
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
    }), HTTP_200_OK
