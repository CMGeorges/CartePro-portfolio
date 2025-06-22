import os
import json

DATA_FILE = 'data/cards.json'
USERS_FILE = 'data/users.json'

def load_cards():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_cards(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Helper function to ensure from a db like SQLite or MongoDB
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Card(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    website = db.Column(db.String)
    instagram = db.Column(db.String)
    linkedin = db.Column(db.String)


class User(db.Model):
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Optionally, you can create an admin user here
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin')
            db.session.add(admin)
            db.session.commit()
# Initialize the database
def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app)
    db.create_all()
    # Optionally, you can create an admin user here
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin')
        db.session.add(admin)
        db.session.commit()
    return db
# Ensure the data directory exists
os.makedirs('data', exist_ok=True)
# Ensure the uploads directory exists
os.makedirs('uploads', exist_ok=True)
# Ensure the static directory exists
os.makedirs('static', exist_ok=True)