import os
from app import create_app

app = create_app()


def parse_bool(value, default=False):
    if value is None:
        return default
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = parse_bool(os.environ.get("DEBUG"), default=False)
    app.run(host="0.0.0.0", port=port, debug=debug)