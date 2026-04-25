import os
from flask import render_template
import pdfkit

import platform
import shutil

# Dynamically decide wkhtmltopdf path based on OS
if platform.system() == "Windows":
    wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
else:
    # Linux (Docker)
    wkhtmltopdf_path = shutil.which("wkhtmltopdf") or "/usr/bin/wkhtmltopdf"

config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
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

def generate_pdf(data, template_file, is_watermarked=False):
    # Pass watermark flag to template
    data['is_watermarked'] = is_watermarked

    # unpack dictionary so template receives variables directly
    html = render_template(template_file, **data)

    pdf = pdfkit.from_string(
        html,
        False,
        configuration=config,
        options=options
    )

    return pdf