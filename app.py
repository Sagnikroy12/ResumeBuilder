from flask import Flask, render_template, request, send_file
from io import BytesIO
import pdfkit
import os

app = Flask(__name__)

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def format_bullets(text):
    if not text:
        return ""

    # Normalize bullet characters
    bullets = ["\uf0b7", "", "•", "●", "▪", "◦", "-", "–", "—"]

    for b in bullets:
        text = text.replace(b, "\n")

    items = [i.strip() for i in text.split("\n") if i.strip()]

    return "".join(f"<li>{i}</li>" for i in items)

def generate_html(data):

    template_path = os.path.join(BASE_DIR, "templates", "resume_template.html")

    with open(template_path, "r", encoding="utf-8") as file:
        html = file.read()

    # Convert bullet sections
    bullet_sections = [
        "Experience",
        "Projects",
        "Skills",
        "Certifications"
    ]

    for section in bullet_sections:
        data[section] = format_bullets(data.get(section, ""))

    for key, value in data.items():
        html = html.replace("{{" + key + "}}", value)

    return html


def generate_pdf(data):

    html_content = generate_html(data)

    pdf_bytes = pdfkit.from_string(
        html_content,
        None,
        configuration=config
    )

    return BytesIO(pdf_bytes)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        resume_data = {
            "Name": request.form["name"],
            "Address": request.form["address"],
            "Phone": request.form["phone"],
            "Email": request.form["email"],
            "LinkedIn": request.form["linkedin"],
            "Objective": request.form["objective"],
            "Education": request.form["education"],
            "Skills": request.form["skills"],
            "Experience": request.form["experience"],
            "Projects": request.form["projects"],
            "Certifications": request.form["certifications"],
        }

        pdf_buffer = generate_pdf(resume_data)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name="resume.pdf",
            mimetype="application/pdf"
        )

    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)