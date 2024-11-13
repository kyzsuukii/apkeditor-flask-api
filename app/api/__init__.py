from flask import Flask
from .apkeditor.decode import decode_bp
from .apkeditor.merge import merge_bp
from .download import download_bp

def register_api(app: Flask) -> None:
    app.register_blueprint(decode_bp, url_prefix="/api/apkeditor")
    app.register_blueprint(merge_bp, url_prefix="/api/apkeditor")
    app.register_blueprint(download_bp, url_prefix="/api")
