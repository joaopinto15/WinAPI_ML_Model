import logging
from flask import Flask
from .routes import main_bp  # make sure your routes are loaded here

def create_app():
    app = Flask(__name__)

    # Register routes
    app.register_blueprint(main_bp)

    # Setup logging to stdout (Gunicorn will capture this)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)  # or DEBUG
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)

    # Remove existing handlers to avoid duplicate logs
    if app.logger.hasHandlers():
        app.logger.handlers.clear()

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)  # Ensure Flask uses the same level

    # Optional: don't propagate to root logger
    app.logger.propagate = False

    app.logger.info("Flask app created and logging configured.")

    return app
