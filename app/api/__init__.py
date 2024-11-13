from flask import Flask
from .apkeditor.decode import decode_bp


def register_api(app: Flask) -> None:
    app.register_blueprint(decode_bp, url_prefix="/api/apkeditor")
