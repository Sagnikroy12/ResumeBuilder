from flask import jsonify

def error_response(message, status_code=400, details=None):
    """Standardize JSON error responses."""
    payload = {
        "error": message,
        "status": "danger"
    }
    if details:
        payload["details"] = details
    return jsonify(payload), status_code

def success_response(message, data=None, status_code=200):
    """Standardize JSON success responses."""
    payload = {
        "message": message,
        "status": "success"
    }
    if data:
        payload.update(data)
    return jsonify(payload), status_code
