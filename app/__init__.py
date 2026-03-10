from flask import Flask
from .routes.resume_routes import resume_bp

def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "supersecretkey"

    app.register_blueprint(resume_bp)

    return app