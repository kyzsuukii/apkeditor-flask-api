
import hashlib
import os
from flask import current_app

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def get_file_hash(file_path: str) -> str:
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

def save_file(file, upload_folder):
    file_content = file.read()
    file_hash = hashlib.md5(file_content).hexdigest()
    file.seek(0)
    upload_path = os.path.join(upload_folder, f"{file_hash}.apk")
    file.save(upload_path)
    return file_hash, upload_path

def prepare_folders():
    upload_folder = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
    output_folder = os.path.abspath(current_app.config["OUTPUT_FOLDER"])
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    return upload_folder, output_folder
