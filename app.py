from flask import Flask, render_template, request, send_file
from io import BytesIO
import pdfkit

app = Flask(__name__)

# Path to wkhtmltopdf
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)


# Convert bullet text into list
import re

def parse_bullets(text):
    if not text:
        return []
    # Remove bullet characters ONLY at the start of items
    text = re.sub(r'\s*[-•●▪◦]\s*', ' ', text)
    # Normalize spaces
    text = text.replace("\n", " ")
    # Split sentences using full stop
    sentences = re.split(r'\.\s+', text)
    bullets = []
    for s in sentences:
        s = s.strip()
        if s:
            if not s.endswith("."):
                s += "."
            bullets.append(s)
    return bullets


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        # Get experience fields
        titles = request.form.getlist("exp_title[]")
        durations = request.form.getlist("exp_duration[]")
        points = request.form.getlist("exp_points[]")

        experience = []

        for title, duration, point in zip(titles, durations, points):

            exp = {
                "title": title.strip(),
                "duration": duration.strip(),
                "points": parse_bullets(point)
            }

            experience.append(exp)

        # Resume data
        data = {
            "name": request.form.get("name", ""),
            "address": request.form.get("address", ""),
            "phone": request.form.get("phone", ""),
            "email": request.form.get("email", ""),
            "linkedin": request.form.get("linkedin", ""),
            "objective": request.form.get("objective", ""),
            "education": request.form.get("education", ""),
            "skills": parse_bullets(request.form.get("skills", "")),
            "projects": parse_bullets(request.form.get("projects", "")),
            "certifications": parse_bullets(request.form.get("certifications", "")),
            "experience": experience
        }

        # Render HTML using Jinja
        html = render_template("resume_template.html", data=data)

        # PDF options
        options = {
                "page-size": "A4",
                "encoding": "UTF-8",
                "margin-top": "0.5in",
                "margin-bottom": "0.5in",
                "margin-left": "0.5in",
                "margin-right": "0.5in"
                }

        pdf = pdfkit.from_string(
            html,
            False,
            configuration=config,
            options=options
        )

        return send_file(
            BytesIO(pdf),
            download_name="resume.pdf",
            as_attachment=True,
            mimetype="application/pdf"
        )

    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)