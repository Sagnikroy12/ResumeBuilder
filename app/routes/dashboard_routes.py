from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
import json
from io import BytesIO

from app.models.resume import Resume
from app.services.pdf_service import generate_pdf
from app.config.templates_config import get_template_file

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def index():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return render_template("dashboard/index.html", resumes=resumes)

@dashboard_bp.route("/download/<int:resume_id>")
@login_required
def download(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    
    # Ensure a user only downloads their own resume
    if resume.user_id != current_user.id:
        flash("You are not authorized to view this resume.", "danger")
        return redirect(url_for("dashboard.index"))
        
    # Monetization check
    if not current_user.is_premium:
        flash("Downloading requires a Premium Pro plan.", "info")
        return redirect(url_for("dashboard.upgrade"))
        
    # User is premium, reconstruct template
    resume_data = json.loads(resume.data)
    template_name = "template1" # Fallback, ideally saved in DB
    template_file = get_template_file(template_name)
    
    pdf = generate_pdf(resume_data, template_file)
    
    return send_file(
        BytesIO(pdf),
        download_name=f"{resume.title}.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )

@dashboard_bp.route("/upgrade")
@login_required
def upgrade():
    return render_template("auth/upgrade.html")
