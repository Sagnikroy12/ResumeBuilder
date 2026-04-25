from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import json
import time
from io import BytesIO

from app.models.resume import Resume
from app.models.download import Download
from app.extensions import db
from app.services.pdf_service import generate_pdf
from app.config.templates_config import get_template_file, get_all_templates
from datetime import datetime, time
import pytz
dashboard_bp = Blueprint("dashboard", __name__)

MASTER_EMAIL = "sagnikruproy11@gmail.com"

@dashboard_bp.route("/toggle-premium", methods=["POST"])
@login_required
def toggle_premium():
    """Toggle Pro status for master user."""
    if current_user.email != MASTER_EMAIL:
        return jsonify({"message": "Unauthorized"}), 403
    
    current_user.is_premium = not current_user.is_premium
    db.session.commit()
    
    status = "Pro" if current_user.is_premium else "Free"
    flash(f"Account toggled to {status}!", "info")
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route("/")
@login_required
def index():
    """Render the main dashboard HTML."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    templates = get_all_templates()
    return render_template("dashboard/index.html", resumes=resumes, templates=templates, now=int(time.time()))

@dashboard_bp.route("/api/dashboard")
@login_required
def index_data():
    """API endpoint for dashboard data."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    templates = get_all_templates()
    
    resumes_json = [{
        "id": r.id,
        "title": r.title,
        "created_at": r.created_at.isoformat(),
        "template": r.template_id,
        "data": json.loads(r.data)
    } for r in resumes]
    
    return jsonify({
        "resumes": resumes_json,
        "templates": templates
    }), 200

@dashboard_bp.route("/api/download/<int:resume_id>")
@login_required
def download(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    
    if resume.user_id != current_user.id:
        return jsonify({"message": "You are not authorized to view this resume.", "status": "danger"}), 403
    
    # MASTER USER PRIVILEGES
    is_master = current_user.email == MASTER_EMAIL
    
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    midnight_ist = ist.localize(datetime.combine(now_ist.date(), time.min))
            
    # Check if this user gets a watermark (Free users get watermarked downloads)
    if not current_user.is_premium:
        return reconstruct_and_send_pdf(resume, is_watermarked=True)
        
    # Premium users get full downloads
    return reconstruct_and_send_pdf(resume, is_watermarked=False)

def reconstruct_and_send_pdf(resume, is_watermarked=False):
    new_download = Download(user_id=current_user.id, resume_id=resume.id)
    db.session.add(new_download)
    db.session.commit()
    
    resume_data = json.loads(resume.data)
    template_name = resume.template_id or "template1"
    template_file = get_template_file(template_name)
    
    pdf = generate_pdf(resume_data, template_file, is_watermarked=is_watermarked)
    
    return send_file(
        BytesIO(pdf),
        download_name=f"{resume.title}.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )

@dashboard_bp.route("/api/verify_payment/<int:resume_id>", methods=["POST"])
@login_required
def verify_payment(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403
    
    # In a real app, verify the payment token here
    return reconstruct_and_send_pdf(resume)

@dashboard_bp.route("/api/upgrade_pro", methods=["POST"])
@login_required
def upgrade_pro():
    current_user.is_premium = True
    db.session.commit()
    return jsonify({"message": "Congratulations! You are now a Premium Pro member.", "status": "success"}), 200

@dashboard_bp.route("/api/delete/<int:resume_id>", methods=["DELETE"])
@login_required
def delete(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    
    if resume.user_id != current_user.id:
        return jsonify({"message": "You are not authorized to delete this resume.", "status": "danger"}), 403
        
    db.session.delete(resume)
    db.session.commit()
    
    return jsonify({"message": "Resume deleted successfully!", "status": "success"}), 200
