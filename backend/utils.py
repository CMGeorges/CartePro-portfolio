import qrcode
from PIL import Image
import io
import os

DEFAULT_LOGO = 'static/logo.png'

def generate_qr_code(url, logo_path=None):
    logo_path = logo_path if logo_path and os.path.exists(logo_path) else DEFAULT_LOGO
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        basewidth = 60
        wpercent = basewidth / float(logo.size[0])
        hsize = int(float(logo.size[1]) * wpercent)
        logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf