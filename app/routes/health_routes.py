from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint for UptimeRobot and deployment monitoring."""
    return jsonify({"status": "ok", "message": "Backend is awake!"}), 200
