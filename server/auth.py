from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from server.app import app, db, bcrypt
from server.models import User
from server.schemas import UserSchema

user_schema = UserSchema()


@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return {
            "error": "Request body is required"
        }, 400

    try:
        validated_data = user_schema.load(data)
    except ValidationError as err:
        return {
            "errors": err.messages
        }, 400

    username = validated_data["username"]
    email = validated_data["email"]
    password = validated_data["password"]

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return {
            "error": "Username already exists"
        }, 409

    existing_email = User.query.filter_by(email=email).first()

    if existing_email:
        return {
            "error": "Email already exists"
        }, 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "access_token": access_token
    }, 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return {
            "error": "Request body is required"
        }, 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            "error": "username and password are required"
        }, 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return {
            "error": "Invalid username or password"
        }, 401

    if not bcrypt.check_password_hash(user.password_hash, password):
        return {
            "error": "Invalid username or password"
        }, 401

    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "access_token": access_token
    }, 200

@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = db.session.get(User, user_id)

    if not user:
        return {
            "error": "User not found"
        }, 404

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }, 200