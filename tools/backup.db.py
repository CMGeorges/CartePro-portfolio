# backup_db.py
import shutil, datetime, os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("BACKUP_KEY")
if not KEY:
    raise Exception("BACKUP_KEY manquante dans .env")

fernet = Fernet(KEY)

os.makedirs("backups", exist_ok=True)

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
backup_raw = f"backups/cards_{timestamp}.db"
backup_enc = backup_raw + ".enc"

# Copier et chiffrer
shutil.copy("data/cards.db", backup_raw)

with open(backup_raw, "rb") as f:
    encrypted = fernet.encrypt(f.read())

with open(backup_enc, "wb") as f:
    f.write(encrypted)

os.remove(backup_raw)
print(f"✅ Backup chiffré enregistré : {backup_enc}")
