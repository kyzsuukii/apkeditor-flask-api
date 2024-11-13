from flask import Blueprint, current_app, jsonify, send_file
import os

download_bp = Blueprint("download", __name__)

@download_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    output_folder = os.path.abspath(current_app.config["OUTPUT_FOLDER"])
    file_path = os.path.join(output_folder, filename)
    if os.path.exists(file_path):
        response = send_file(file_path, as_attachment=True)
        return response
    return jsonify({"error": "File not found"}), 404
