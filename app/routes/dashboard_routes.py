from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import json
from io import BytesIO

from app.models.resume import Resume
from app.models.download import Download
from app.extensions import db
from app.services.pdf_service import generate_pdf
from app.config.templates_config import get_template_file, get_all_templates
from datetime import datetime, time
import pytz

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/api/dashboard")
@login_required
def index():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    templates = get_all_templates()
    
    resumes_json = [{
        "id": r.id,
        "title": r.title,
        "created_at": r.created_at.isoformat(),
        "template": r.template_id
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
        
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    midnight_ist = ist.localize(datetime.combine(now_ist.date(), time.min))
            
    if not current_user.is_premium:
        daily_downloads = Download.query.filter(
            Download.user_id == current_user.id,
            Download.downloaded_at >= midnight_ist
        ).count()
        
        if daily_downloads >= 10:
            return jsonify({
                "message": "Limit reached", 
                "status": "danger", 
                "redirect": "/upgrade"
            }), 403
            
        return jsonify({
            "message": "Payment required", 
            "status": "info", 
            "redirect": f"/payment/{resume.id}"
        }), 402
        
    else:
        daily_downloads = Download.query.filter(
            Download.user_id == current_user.id,
            Download.downloaded_at >= midnight_ist
        ).count()
        if daily_downloads >= 100:
            return jsonify({"message": "Pro limit reached", "status": "danger"}), 403
            
    return reconstruct_and_send_pdf(resume)

def reconstruct_and_send_pdf(resume):
    new_download = Download(user_id=current_user.id, resume_id=resume.id)
    db.session.add(new_download)
    db.session.commit()
    
    resume_data = json.loads(resume.data)
    template_name = resume.template_id or "template1"
    template_file = get_template_file(template_name)
    
    pdf = generate_pdf(resume_data, template_file)
    
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
