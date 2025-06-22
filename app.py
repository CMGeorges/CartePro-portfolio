# backend/app.py
from flask import Flask, request, send_file
from flask import Flask, request, send_file, jsonify
import qrcode
from PIL import Image
import io
import os

app = Flask(__name__)


# Configurations
UPLOAD_FOLDER = 'uploads'
DEFAULT_LOGO = 'static/logo.png'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

@app.route('/')
def index():
    return jsonify({"message": "QR Code Generator API is running."})

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' in request."}), 400

    logo_path = DEFAULT_LOGO
    if 'logo_path' in data and os.path.exists(data['logo_path']):
        logo_path = data['logo_path']

    try:
        # Generate QR code
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(url)
        qr.make()
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Add logo
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            basewidth = 60
            wpercent = basewidth / float(logo.size[0])
            hsize = int(float(logo.size[1]) * wpercent)
            logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, pos)

        # Save image to buffer
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
