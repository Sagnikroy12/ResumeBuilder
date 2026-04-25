import os
from flask import render_template
import pdfkit

import shutil

options = {
    "page-size": "A4",
    "margin-top": "0.8in",
    "margin-bottom": "0.8in",
    "margin-left": "0.8in",
    "margin-right": "0.8in",
    "encoding": "UTF-8",
    "disable-smart-shrinking": "",
    "zoom": "1.0",
    "dpi": "96",
    "viewport-size": "1024x768",
    "print-media-type": ""
}

def _resolve_pdfkit_configuration():
    # Allow explicit override first (useful for local Windows installs).
    env_path = os.environ.get("WKHTMLTOPDF_PATH", "").strip()
    if env_path:
        if os.path.exists(env_path):
            return pdfkit.configuration(wkhtmltopdf=env_path)
        raise RuntimeError(f"WKHTMLTOPDF_PATH is set but file does not exist: {env_path}")

    # Then try common system locations/discovery.
    candidates = [
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        shutil.which("wkhtmltopdf"),
        "/usr/bin/wkhtmltopdf",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return pdfkit.configuration(wkhtmltopdf=path)

    raise RuntimeError(
        "wkhtmltopdf executable not found. Install wkhtmltopdf or set WKHTMLTOPDF_PATH."
    )

def generate_pdf(data, template_file, is_watermarked=False):
    # Pass watermark flag to template
    data['is_watermarked'] = is_watermarked

    # unpack dictionary so template receives variables directly
    html = render_template(template_file, **data)
    config = _resolve_pdfkit_configuration()

    pdf = pdfkit.from_string(
        html,
        False,
        configuration=config,
        options=options
    )

    return pdf