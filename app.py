# from flask import Flask, render_template, request, send_file
# from io import BytesIO
# import pdfkit
# import os

# app = Flask(__name__)

# config = pdfkit.configuration(
#     wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
# )

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# def format_bullets(text):
#     if not text:
#         return ""

#     # Normalize bullet characters
#     bullets = ["\uf0b7", "", "•", "●", "▪", "◦", "-", "–", "—"]

#     for b in bullets:
#         text = text.replace(b, "\n")

#     items = [i.strip() for i in text.split("\n") if i.strip()]

#     return "".join(f"<li>{i}</li>" for i in items)

# def generate_html(data):

#     template_path = os.path.join(BASE_DIR, "templates", "resume_template.html")

#     with open(template_path, "r", encoding="utf-8") as file:
#         html = file.read()

#     # Convert bullet sections
#     bullet_sections = [
#         "Experience",
#         "Projects",
#         "Skills",
#         "Certifications"
#     ]

#     for section in bullet_sections:
#         data[section] = format_bullets(data.get(section, ""))

#     for key, value in data.items():
#         html = html.replace("{{" + key + "}}", value)

#     return html


# def generate_pdf(data):

#     html_content = generate_html(data)

#     pdf_bytes = pdfkit.from_string(
#         html_content,
#         None,
#         configuration=config
#     )

#     return BytesIO(pdf_bytes)


# @app.route("/", methods=["GET", "POST"])
# def index():

#     if request.method == "POST":

#         resume_data = {
#             "Name": request.form["name"],
#             "Address": request.form["address"],
#             "Phone": request.form["phone"],
#             "Email": request.form["email"],
#             "LinkedIn": request.form["linkedin"],
#             "Objective": request.form["objective"],
#             "Education": request.form["education"],
#             "Skills": request.form["skills"],
#             "Experience": request.form["experience"],
#             "Projects": request.form["projects"],
#             "Certifications": request.form["certifications"],
#         }

#         pdf_buffer = generate_pdf(resume_data)

#         return send_file(
#             pdf_buffer,
#             as_attachment=True,
#             download_name="resume.pdf",
#             mimetype="application/pdf"
#         )

#     return render_template("form.html")


# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, request, send_file
from io import BytesIO
import pdfkit

app = Flask(__name__)

# Path to wkhtmltopdf
config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)


# Convert bullet text into list
def parse_bullets(text):

    if not text:
        return []

    bullets = ["\uf0b7", "", "•", "●", "▪", "◦", "-", "–", "—"]

    for b in bullets:
        text = text.replace(b, "\n")

    return [i.strip() for i in text.split("\n") if i.strip()]


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
            "margin-top": "15mm",
            "margin-bottom": "15mm",
            "margin-left": "15mm",
            "margin-right": "15mm"
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