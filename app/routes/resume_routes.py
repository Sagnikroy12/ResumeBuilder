from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
import json
from io import BytesIO

from ..services.pdf_service import generate_pdf
from ..utils.text_utils import parse_bullets
from ..config.templates_config import get_template_file
from app.models.resume import Resume
from app.extensions import db
from datetime import datetime, time
import pytz

resume_bp = Blueprint("resume", __name__)


def build_resume_title(name: str) -> str:
    clean_name = (name or "").strip()
    return clean_name if clean_name else "My Resume"


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
@login_required
def index():

    if request.method == "POST":
        # ---------- MONETIZATION LIMIT CHECK ----------
        if not current_user.is_premium:
            # Get IST midnight
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = datetime.now(ist)
            midnight_ist = ist.localize(datetime.combine(now_ist.date(), time.min))
            
            # Count resumes generated today
            daily_generates = Resume.query.filter(
                Resume.user_id == current_user.id,
                Resume.created_at >= midnight_ist
            ).count()
            
            if daily_generates >= 10:
                flash("You have reached your daily limit of 10 free generated resumes. Upgrade to Pro for unlimited generation!", "danger")
                return redirect(url_for('dashboard.upgrade'))
                
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

        # ---------- SAVE TO DB INSTEAD OF DOWNLOAD ----------
        
        # Save resume data as JSON string
        resume_name = resume_data.get("personal", {}).get("name", "")
        new_resume = Resume(
            user_id=current_user.id,
            title=build_resume_title(resume_name),
            data=json.dumps(resume_data)
        )
        db.session.add(new_resume)
        db.session.commit()
        
        flash("Resume successfully generated and saved to your dashboard!", "success")
        return redirect(url_for('dashboard.index'))

    return render_template("form.html")