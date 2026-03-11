from flask import Blueprint, render_template, request, send_file
from io import BytesIO

from ..services.pdf_service import generate_pdf
from ..utils.text_utils import parse_bullets
from ..config.templates_config import get_template_file

resume_bp = Blueprint("resume", __name__)


def to_li(items):
    """Convert list of strings into HTML <li> elements with bold formatting before colons"""
    result = []
    for item in items:
        if ':' in item:
            # Split on first colon and make the part before it bold
            parts = item.split(':', 1)
            formatted_item = f"<li><strong>{parts[0].strip()}:</strong> {parts[1].strip()}</li>"
        else:
            formatted_item = f"<li>{item}</li>"
        result.append(formatted_item)
    return "".join(result)


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
        objective = request.form.get("objective", "").strip()
        education = request.form.get("education", "").strip()

        # ---------- RESUME DATA ----------

        resume_data = {

            "personal": {
                "name": request.form.get("name", "").strip(),
                "address": request.form.get("address", "").strip(),
                "phone": request.form.get("phone", "").strip(),
                "email": request.form.get("email", "").strip(),
                "linkedin": request.form.get("linkedin", "").strip()
            },

            "objective": objective if objective else None,

            "skills": to_li(skills_list) if skills_list else None,

            "experience": experience if experience else None,

            "projects": to_li(projects_list) if projects_list else None,

            "education": education if education else None,

            "certifications": to_li(cert_list) if cert_list else None,

            "custom_sections": custom_sections if custom_sections else None
        }

        # ---------- TEMPLATE SWITCHING ----------

        template_name = request.form.get("template", "template1")
        template_file = get_template_file(template_name)

        # ---------- GENERATE PDF ----------

        pdf = generate_pdf(resume_data, template_file)

        return send_file(
            BytesIO(pdf),
            download_name="resume.pdf",
            as_attachment=True,
            mimetype="application/pdf"
        )

    return render_template("form.html")