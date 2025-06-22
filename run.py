# run.py
from app import create_app
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    # Le mode debug sera contrôlé par la variable DEBUG dans config.py
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])