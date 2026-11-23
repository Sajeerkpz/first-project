import logging
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from .config import (
    BASE_DIR,
    SERVER_HOST,
    SERVER_PORT,
    CORS_ORIGINS,
)
from .database import init_db
from .routes import api_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("selfstudy")


def create_app() -> Flask:
    app = Flask(__name__)

    # Enable CORS for frontend clients (VS Code Live Server, localhost, etc.)
    CORS(
        app,
        resources={r"/api/*": {"origins": CORS_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Authorization", "Content-Type"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    # Initialize Database and seed data
    init_db()

    # Register API blueprint
    app.register_blueprint(api_bp)

    # Serve static frontend files if requested directly from the backend server
    frontend_dir = BASE_DIR / "frontend"

    @app.route("/", methods=["GET"])
    def index():
        if (frontend_dir / "index.html").exists():
            return send_from_directory(frontend_dir, "index.html")
        return jsonify({"message": "Self Study API is running"}), 200

    @app.route("/<path:filename>", methods=["GET"])
    def static_frontend(filename: str):
        target = frontend_dir / filename
        if target.is_file():
            return send_from_directory(frontend_dir, filename)
        return jsonify({"message": "Not found", "detail": f"File '{filename}' not found."}), 404

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"message": "Resource not found", "detail": str(e)}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}", exc_info=True)
        return jsonify({"message": "Internal server error", "detail": "An unexpected error occurred."}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    logger.info(f"Starting Self Study Python API on http://{SERVER_HOST}:{SERVER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)

