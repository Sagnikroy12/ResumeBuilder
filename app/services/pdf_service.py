import os
from flask import render_template
import pdfkit

options = {
    "page-size": "A4",
    "margin-top": "0.5in",
    "margin-bottom": "0.5in",
    "margin-left": "0.5in",
    "margin-right": "0.5in",
    "encoding": "UTF-8"
}

def _get_pdfkit_configuration():
    wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    if os.path.exists(wkhtmltopdf_path):
        return pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    return pdfkit.configuration()

def generate_pdf(data, template_file):

    # unpack dictionary so template receives variables directly
    html = render_template(template_file, **data)
    config = _get_pdfkit_configuration()

    pdf = pdfkit.from_string(
        html,
        False,
        configuration=config,
        options=options
    )

    return pdf