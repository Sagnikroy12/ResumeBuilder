from flask import Blueprint, render_template, request, send_file
from io import BytesIO

from ..services.pdf_service import generate_pdf
from ..utils.text_utils import parse_bullets

resume_bp = Blueprint("resume", __name__)


def to_li(items):
    """Convert list of strings into HTML <li> elements"""
    return "".join([f"<li>{item}</li>" for item in items])


@resume_bp.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        # ---------- EXPERIENCE ----------

        titles = request.form.getlist("exp_title[]")
        durations = request.form.getlist("exp_duration[]")
        points = request.form.getlist("exp_points[]")

        experience = []

        for title, duration, point in zip(titles, durations, points):

            if not title.strip() and not duration.strip() and not point.strip():
                continue

            experience.append({
                "title": title.strip(),
                "duration": duration.strip(),
                "points": parse_bullets(point)
            })

        # ---------- CUSTOM SECTIONS ----------

        section_titles = request.form.getlist("section_title[]")
        section_points = request.form.getlist("section_points[]")

        custom_sections = []

        for title, pts in zip(section_titles, section_points):

            if not title.strip() and not pts.strip():
                continue

            custom_sections.append({
                "title": title.strip(),
                "points": parse_bullets(pts)
            })

        # ---------- PREPARE LIST DATA ----------

        skills_list = parse_bullets(request.form.get("skills", ""))
        projects_list = parse_bullets(request.form.get("projects", ""))
        cert_list = parse_bullets(request.form.get("certifications", ""))

        # ---------- RESUME DATA ----------

        resume_data = {

            "personal": {
                "name": request.form.get("name", "").strip(),
                "address": request.form.get("address", "").strip(),
                "phone": request.form.get("phone", "").strip(),
                "email": request.form.get("email", "").strip(),
                "linkedin": request.form.get("linkedin", "").strip()
            },

            "objective": request.form.get("objective", "").strip(),

            "skills": to_li(skills_list),

            "experience": experience,

            "projects": to_li(projects_list),

            "education": request.form.get("education", "").strip(),

            "certifications": to_li(cert_list),

            "custom_sections": custom_sections
        }

        # ---------- TEMPLATE SWITCHING ----------

        template_name = request.form.get("template", "template1")

        template_map = {
            "template1": "resume_template.html",
            "template2": "resume_template2.html"
        }

        template_file = template_map.get(template_name, "resume_template.html")

        # ---------- GENERATE PDF ----------

        pdf = generate_pdf(resume_data, template_file)

        return send_file(
            BytesIO(pdf),
            download_name="resume.pdf",
            as_attachment=True,
            mimetype="application/pdf"
        )

    return render_template("form.html")