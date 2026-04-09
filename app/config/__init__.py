# Configuration module for Resume Builder
@app.errorhandler(500)
def internal_error(error):
    app.logger.exception("Unhandled exception: %s", error)
    return {"error": "Internal server error"}, 500