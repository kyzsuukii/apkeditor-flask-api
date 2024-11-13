from flask import Blueprint, current_app, request, jsonify
import os
import zipfile
import shutil
from app.lib.apkeditor import ApkEditor, DecodeOptions
from app.utils import allowed_file, save_file, prepare_folders

decode_bp = Blueprint("decode", __name__)

ALLOWED_EXTENSIONS = {"apk"}
MAX_FILE_SIZE = 15 * 1024 * 1024


def create_zip_from_folder(folder_path, output_zip_path):
    with zipfile.ZipFile(output_zip_path, "w") as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=os.path.relpath(file_path, folder_path))


@decode_bp.route("/decode", methods=["POST"])
def decompile():
    upload_folder, output_folder = prepare_folders()

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
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

        download_url = (
            f"{request.host_url.rstrip('/')}/api/download/{file_hash}_decode.zip"
        )
        return jsonify({"hash": file_hash, "download_link": download_url}), 200

    return jsonify({"error": "File not allowed"}), 400
