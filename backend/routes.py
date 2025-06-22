from flask import Blueprint, request, jsonify, send_file, session
from models import load_cards, save_cards
from utils import generate_qr_code
import uuid

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return jsonify({"message": "QR Code Generator API is running."})

@main_routes.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get("url")
    logo_path = data.get("logo_path")
    if not url:
        return jsonify({"error": "Missing 'url' in request."}), 400
    try:
        buf = generate_qr_code(url, logo_path)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_routes.route('/create_card', methods=['POST'])
def create_card():
    if not session.get("username"):
        return jsonify({"error": "Authentication required."}), 401
    data = request.json
    required_fields = ["name", "email", "title"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields: name, email, title"}), 400
    cards = load_cards()
    card_id = str(uuid.uuid4())
    card_data = {
        "id": card_id,
        "name": data["name"],
        "email": data["email"],
        "title": data["title"],
        "phone": data.get("phone", ""),
        "website": data.get("website", ""),
        "instagram": data.get("instagram", ""),
        "linkedin": data.get("linkedin", ""),
        "owner": session.get("username")
    }
    cards[card_id] = card_data
    save_cards(cards)
    return jsonify({"message": "Card created successfully", "id": card_id}), 201

@main_routes.route('/card/<card_id>', methods=['GET'])
def get_card(card_id):
    cards = load_cards()
    card = cards.get(card_id)
    if not card:
        return jsonify({"error": "Card not found."}), 404
    return jsonify(card)