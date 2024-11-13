from flask import Blueprint, current_app, request, jsonify
import os
import zipfile
from app.lib.apkeditor import ApkEditor, MergeOptions
from app.utils import allowed_file, save_file, prepare_folders

merge_bp = Blueprint("merge", __name__)

ALLOWED_EXTENSIONS = {"xapk", "apkm", "apks"}
MAX_FILE_SIZE = 15 * 1024 * 1024


@merge_bp.route("/merge", methods=["POST"])
def merge():
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

        original_filename = os.path.splitext(file.filename)[0]
        output_apk_path = os.path.join(output_folder, f"{original_filename}.apk")
        output_zip_path = os.path.join(output_folder, f"{file_hash}.zip")

        if not os.path.exists(output_zip_path):
            apk_editor = ApkEditor(current_app.config["APK_EDITOR_PATH"])
            apk_editor.merge(
                upload_path, output_apk_path, MergeOptions(clean_meta=True, f=True)
            )

            with zipfile.ZipFile(output_zip_path, "w") as zipf:
                zipf.write(output_apk_path, os.path.basename(output_apk_path))

            os.remove(output_apk_path)

        download_url = f"{request.host_url.rstrip('/')}/api/download/{file_hash}.zip"
        return jsonify({"hash": file_hash, "download_link": download_url}), 200

    return jsonify({"error": "File not allowed"}), 400
