from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_401_UNAUTHORIZED
import validators
import logging
from src.database import db, User

from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


# routes
# registration route
@auth.post("/register")
def register():
    username = request.json.get("username", '')
    email = request.json.get("email", '')
    password = request.json.get("password", '')

    # check password length
    if len(password) < 6:
        return jsonify({"message": "Password is too short!"}), HTTP_400_BAD_REQUEST
    
    # check username length
    if len(username) < 6:
        return jsonify({"message": "User name is too short!"}), HTTP_400_BAD_REQUEST
    
    # check if username is alphanumeric
    if not username.isalnum() or ' ' in username:
        return jsonify({"message": "Username should be alphanumeric and have no spaces"}), HTTP_400_BAD_REQUEST
    
    # check if username exists in the database
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User name is already created in the database"}), HTTP_409_CONFLICT

    # check if email has valid format
    if not validators.email(email):
        return jsonify({"message": "The email you entered is not valid"}), HTTP_400_BAD_REQUEST
    
    # check if email exists in database
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email is already in the system"}), HTTP_409_CONFLICT

    # hash password
    pwd_hash = generate_password_hash(password)

    # save user to db
    user = User(username=username, email=email, password=pwd_hash)
    db.session.add(user)
    db.session.commit()

    # return message
    return jsonify({
        "message": "user created successfully",
        "user": {
            "username": username,
            "email": email
        },
    }), HTTP_201_CREATED

# login route
@auth.post("/login")
def login():
    email = request.json.get('email','')
    password = request.json.get('password','')

    # check if user exists
    user = User.query.filter_by(email=email).first()
    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=str(user.id))
            access = create_access_token(identity=str(user.id))

            return jsonify({
                "user": {
                    "refresh_token": refresh,
                    "access": access,
                    "username": user.username,
                    "email": user.email
                }
            }), HTTP_201_CREATED
        
    return jsonify({
        "message": "Wrong credentials"
    }), HTTP_401_UNAUTHORIZED



@auth.get("/profile")
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    logging.info(f"User ID from JWT: {user_id}")
    
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        logging.warning(f"No user found with ID: {user_id}")
        return jsonify({"message": "User not found"}), HTTP_404_NOT_FOUND

    return jsonify({
        "username": user.username,
        "email": user.email
    }), HTTP_200_OK


# refresh token route
@auth.get("/token")
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()

    access = create_access_token(identity=identity)

    return jsonify({
        "message": "token refreshed sucessfully",
        "access": access
    }), HTTP_200_OK