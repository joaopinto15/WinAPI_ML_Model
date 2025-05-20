import logging
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Optional: log to stdout/stderr so Gunicorn can capture it
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)  # or DEBUG, WARNING, etc.
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Remove default Flask handler if needed
    app.logger.propagate = False

    return app
