# backup_and_upload.py
import subprocess
import backup_db  # Exécute le script de backup ci-dessus
import glob

# Trouve le dernier backup .enc
latest = max(glob.glob("backups/*.enc"), key=os.path.getctime)

# Upload vers Google Drive
print(f"📤 Upload vers Google Drive : {latest}")
result = subprocess.run(["rclone", "copy", latest, "gdrive:qr-backups"], capture_output=True)

if result.returncode == 0:
    print("✅ Upload réussi !")
else:
    print("❌ Échec upload :")
    print(result.stderr.decode())
