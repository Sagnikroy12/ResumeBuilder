from flask import render_template
import pdfkit

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

options = {
    "page-size": "A4",
    "margin-top": "0.5in",
    "margin-bottom": "0.5in",
    "margin-left": "0.5in",
    "margin-right": "0.5in",
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