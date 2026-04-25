from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
import json
from io import BytesIO

from app.models.resume import Resume
from app.models.download import Download
from app.extensions import db
from app.services.pdf_service import generate_pdf
from app.config.templates_config import get_template_file
from datetime import datetime, time
import pytz

dashboard_bp = Blueprint("dashboard", __name__)


def build_download_filename(resume, resume_data):
    personal_name = (resume_data.get("personal", {}).get("name", "") or "").strip()
    if personal_name:
        return f"{personal_name}.pdf"

    fallback_title = (resume.title or "").strip() or "My Resume"
    return f"{fallback_title}.pdf"

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
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    midnight_ist = ist.localize(datetime.combine(now_ist.date(), time.min))
            
    if not current_user.is_premium:
        
        # Count downloads today
        daily_downloads = Download.query.filter(
            Download.user_id == current_user.id,
            Download.downloaded_at >= midnight_ist
        ).count()
        
        if daily_downloads >= 10:
            flash("You have reached your daily limit of 10 free downloads. Upgrade to Pro for 100 downloads!", "danger")
            return redirect(url_for("dashboard.upgrade"))
            
        # Basic user wants to download -> redirect to payment gateway (50 INR)
        # Note: If they actually paid, we would skip this via a database flag, 
        # but the prompt requires presenting the choice upon clicking download.
        return redirect(url_for("dashboard.payment", resume_id=resume.id))
        
    else:
        # Premium User - Check their 100 limit
        daily_downloads = Download.query.filter(
            Download.user_id == current_user.id,
            Download.downloaded_at >= midnight_ist
        ).count()
        if daily_downloads >= 100:
            flash("You have reached your Pro limit of 100 downloads today.", "danger")
            return redirect(url_for("dashboard.index"))
            
    # User is premium (or completed a payment flow mock), reconstruct file
    return reconstruct_and_send_pdf(resume)

def reconstruct_and_send_pdf(resume):
    # Track the download before sending
    new_download = Download(user_id=current_user.id, resume_id=resume.id)
    db.session.add(new_download)
    db.session.commit()
    
    resume_data = json.loads(resume.data)
    template_name = "template1" # Fallback, ideally saved in DB
    template_file = get_template_file(template_name)
    
    pdf = generate_pdf(resume_data, template_file)
    download_filename = build_download_filename(resume, resume_data)
    
    return send_file(
        BytesIO(pdf),
        download_name=download_filename,
        as_attachment=True,
        mimetype="application/pdf"
    )

@dashboard_bp.route("/payment/<int:resume_id>")
@login_required
def payment(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return redirect(url_for("dashboard.index"))
    return render_template("payment/checkout.html", resume=resume)

@dashboard_bp.route("/verify_payment/<int:resume_id>", methods=["POST"])
@login_required
def verify_payment(resume_id):
    """Mock verification endpoint for the 50 INR payment"""
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return redirect(url_for("dashboard.index"))
    
    flash("Payment of ₹50 successfully mocked! Your download has started.", "success")
    return reconstruct_and_send_pdf(resume)

@dashboard_bp.route("/upgrade_pro", methods=["POST"])
@login_required
def upgrade_pro():
    """Mock endpoint to grant Pro status for 100k INR"""
    current_user.is_premium = True
    db.session.commit()
    flash("Congratulations! You are now a Premium Pro member.", "success")
    return redirect(url_for("dashboard.index"))

@dashboard_bp.route("/upgrade")
@login_required
def upgrade():
    return render_template("auth/upgrade.html")
