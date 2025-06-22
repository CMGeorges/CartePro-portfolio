# app/auth.py

from flask import Blueprint, request, jsonify, session
from .models import db, User

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400

    # Vérifie si l'utilisateur existe déjà dans la base de données
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400

    # Crée un nouvel utilisateur et hashe son mot de passe
    new_user = User(username=username)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User '{username}' registered successfully."}), 201

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400
    
    user = User.query.filter_by(username=username).first()

    # Vérifie si l'utilisateur existe ET si le mot de passe est correct
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials."}), 401

    # Stocke l'ID de l'utilisateur dans la session
    session.clear()
    session["user_id"] = user.id
    
    return jsonify({"message": "Login successful."})

@auth_routes.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."})

@auth_routes.route('/me', methods=['GET'])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"id": user.id, "username": user.username})