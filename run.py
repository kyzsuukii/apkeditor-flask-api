from flask import Flask
from app.api import register_api
from app.lib.env import EnvLoader

app = Flask(__name__)

env_loader = EnvLoader()
env_loader.load()

app.config["UPLOAD_FOLDER"] = env_loader.required("UPLOAD_FOLDER")
app.config["OUTPUT_FOLDER"] = env_loader.required("OUTPUT_FOLDER")
app.config["APK_EDITOR_PATH"] = env_loader.required("APK_EDITOR_PATH")

register_api(app)

if __name__ == "__main__":
    app.run(debug=True)
