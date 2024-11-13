from flask import Blueprint, current_app, request, jsonify, send_file
import hashlib
import os
import zipfile
import shutil
from app.lib.apkeditor import ApkEditor, DecodeOptions

decode_bp = Blueprint("decode", __name__)

ALLOWED_EXTENSIONS = {"apk"}
MAX_FILE_SIZE = 15 * 1024 * 1024


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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


def create_zip_from_folder(folder_path, output_zip_path):
    with zipfile.ZipFile(output_zip_path, "w") as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=os.path.relpath(file_path, folder_path))


def prepare_folders():
    upload_folder = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
    output_folder = os.path.abspath(current_app.config["OUTPUT_FOLDER"])
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    return upload_folder, output_folder


@decode_bp.route("/decode", methods=["POST"])
def decompile():
    upload_folder, output_folder = prepare_folders()

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({"error": "File exceeds maximum size"}), 400
        file.seek(0)

        file_hash, upload_path = save_file(file, upload_folder)

        output_zip_path = os.path.join(output_folder, f"{file_hash}_decode.zip")
        if not os.path.exists(output_zip_path):
            apk_editor = ApkEditor(current_app.config["APK_EDITOR_PATH"])
            decoded_output_path = os.path.join(output_folder, file_hash)
            apk_editor.decode(
                upload_path, decoded_output_path, DecodeOptions(no_dex_debug=True)
            )

            create_zip_from_folder(decoded_output_path, output_zip_path)
            shutil.rmtree(decoded_output_path)

        download_url = f"{request.host_url.rstrip('/')}/api/apkeditor/download/{file_hash}_decode.zip"
        return jsonify({"hash": file_hash, "download_link": download_url}), 200

    return jsonify({"error": "File not allowed"}), 400


@decode_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    output_folder = os.path.abspath(current_app.config["OUTPUT_FOLDER"])
    file_path = os.path.join(output_folder, filename)
    if os.path.exists(file_path):
        response = send_file(file_path, as_attachment=True)
        return response
    return jsonify({"error": "File not found"}), 404
