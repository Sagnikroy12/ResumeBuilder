from flask import Blueprint, render_template, request, send_file
from io import BytesIO

from ..services.pdf_service import generate_pdf
from ..utils.text_utils import parse_bullets

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        # ---------- EXPERIENCE ----------

        titles = request.form.getlist("exp_title[]")
        durations = request.form.getlist("exp_duration[]")
        points = request.form.getlist("exp_points[]")

        experience = []

        for title, duration, point in zip(titles, durations, points):

            if title.strip() == "" and duration.strip() == "" and point.strip() == "":
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

        for title, points in zip(section_titles, section_points):

            if title.strip() == "" and points.strip() == "":
                continue

            custom_sections.append({
                "title": title.strip(),
                "points": parse_bullets(points)
            })

        # ---------- RESUME DATA (JSON STRUCTURE) ----------

        resume_data = {

            "personal": {
                "name": request.form.get("name", "").strip(),
                "address": request.form.get("address", "").strip(),
                "phone": request.form.get("phone", "").strip(),
                "email": request.form.get("email", "").strip(),
                "linkedin": request.form.get("linkedin", "").strip()
            },

            "objective": request.form.get("objective", "").strip(),

            "skills": parse_bullets(request.form.get("skills", "")),

            "experience": experience,

            "projects": parse_bullets(request.form.get("projects", "")),

            "education": request.form.get("education", "").strip(),

            "certifications": parse_bullets(request.form.get("certifications", "")),

            "custom_sections": custom_sections
        }

        # ---------- TEMPLATE SWITCHING ----------

        template_name = request.form.get("template", "classic")

        template_map = {
            "classic": "resume_template.html",
            "modern": "resume_template2.html",
            "minimal": "resume_template.html"
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