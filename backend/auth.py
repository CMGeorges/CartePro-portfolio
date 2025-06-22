from flask import Blueprint, request, jsonify, session
from models import load_users, save_users

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400
    users = load_users()
    if username in users:
        return jsonify({"error": "Username already exists."}), 400
    users[username] = {"password": password}
    save_users(users)
    return jsonify({"message": "User registered successfully."}), 201

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400
    users = load_users()
    user = users.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials."}), 401
    session["username"] = username
    return jsonify({"message": "Login successful."})

@auth_routes.route('/logout', methods=['POST'])
def logout():
    session.pop("username", None)
    return jsonify({"message": "Logged out."})

@auth_routes.route('/me', methods=['GET'])
def me():
    username = session.get("username")
    if not username:
        return jsonify({"error": "Not logged in."}), 401
    return jsonify({"username": username})