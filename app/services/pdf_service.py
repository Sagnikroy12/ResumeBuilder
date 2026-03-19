from flask import render_template
import pdfkit

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

options = {
    "page-size": "A4",
    "margin-top": "0in",
    "margin-bottom": "0in",
    "margin-left": "0in",
    "margin-right": "0in",
    "encoding": "UTF-8",
    "disable-smart-shrinking": "",
    "zoom": "1.0",
    "dpi": "96",
    "viewport-size": "1024x768"
}

def generate_pdf(data, template_file):

    # unpack dictionary so template receives variables directly
    html = render_template(template_file, **data)

    pdf = pdfkit.from_string(
        html,
        False,
        configuration=config,
        options=options
    )

    return pdf