from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
import json
from io import BytesIO

from ..services.pdf_service import generate_pdf
from ..config.templates_config import get_template_file
from app.models.resume import Resume
from app.extensions import db
from ..services.ai_service import AIService
from ..services.resume_service import ResumeService
from ..utils.file_parser import extract_text_from_file
from ..utils.errors import success_response, error_response
from flask import current_app
from datetime import datetime, time
import pytz

resume_bp = Blueprint("resume", __name__)

@resume_bp.route("/")
@login_required
def index():
    """Render the resume editor form."""
    resume_id = request.args.get('id')
    resume_data = None
    selected_template = request.args.get('template', 'template3') # Default to template3
    
    if resume_id:
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        if resume:
            resume_data = json.loads(resume.data)
            # Add template_id to data if not present for the form to use
            if not resume_data.get('template'):
                resume_data['template'] = resume.template_id
            selected_template = resume.template_id
    
    # Enable AI by default for now
    return render_template("form.html", 
                         resume_data=resume_data, 
                         resume_id=resume_id, 
                         selected_template=selected_template,
                         ai_enabled=True)

@resume_bp.route("/resumes/<int:resume_id>/render")
@login_required
def render_view(resume_id):
    """Render a saved resume's template for the dashboard preview."""
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return error_response("Unauthorized", 403)
    
    data = json.loads(resume.data)
    normalized_data = ResumeService.normalize_resume_data(data)
    template_file = get_template_file(resume.template_id)
    
    # Pass dashboard_preview=True to templates if we want to hide certain things
    return render_template(template_file, **normalized_data, dashboard_preview=True)

@resume_bp.route("/upload")
@login_required
def upload_view():
    """Render the upload/parse page."""
    return render_template("resume/upload.html")

@resume_bp.route("/tailor")
@login_required
def tailor_view():
    """Render the resume tailoring page."""
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return render_template("resume/tailor.html", resumes=resumes)

@resume_bp.route("/ai-create")
@login_required
def ai_create():
    """Render a fresh editor but with AI prominence."""
    return render_template("form.html", resume_data=None, ai_enabled=True)


@resume_bp.route("/api/resumes", methods=["POST"])
@login_required
def create_resume():
    """Create and save a new resume."""
    try:
        # Handle both JSON and Form data
        if request.is_json:
            raw_data = request.get_json()
        else:
            # Reconstruct dictionary from form fields
            raw_data = request.form.to_dict()
            # Special handling for experience/custom blocks if they come as lists
            # Note: request.form.to_dict() might not capture lists well, but 
            # the current form.js/form.html doesn't use arrays in standard POST 
            # (they are typically handled via AJAX or simple scalar fields)
            pass
        
        # 1. Limit Check
        allowed, message = ResumeService.check_daily_limit(current_user)
        if not allowed:
            current_app.logger.warning(f"User {current_user.id} reached daily limit.")
            return error_response(message, 403)

        # 2. Create Resume via Service
        new_resume = ResumeService.create_resume(current_user.id, raw_data)
        
        current_app.logger.info(f"Resume created: {new_resume.id} by user {current_user.id}")
        
        # 3. Handle Redirect for Form Submits vs JSON for AJAX
        if not request.is_json:
            flash("Resume successfully generated and saved!", "success")
            return redirect(url_for('dashboard.index'))
            
        return success_response(
            "Resume successfully generated and saved!", 
            {"resume_id": new_resume.id}, 
            201
        )
    except Exception as e:
        current_app.logger.error(f"Error creating resume: {str(e)}")
        return error_response("Internal server error during resume creation", 500)


@resume_bp.route("/api/preview", methods=["POST"])
@login_required
def preview_resume():
    """Render a live preview of the resume based on current form data."""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    normalized_data = ResumeService.normalize_resume_data(data or {})
    template_file = get_template_file(normalized_data.get("template", "template1"))

    html = render_template(template_file, **normalized_data)
    return jsonify({"html": html}), 200

@resume_bp.route("/api/resumes/<int:resume_id>", methods=["GET"])
@login_required
def get_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return error_response("Unauthorized", 403)
    
    return success_response("Resume retrieved", {
        "id": resume.id,
        "title": resume.title,
        "data": json.loads(resume.data),
        "template_id": resume.template_id,
        "used_ai": resume.used_ai
    })


@resume_bp.route("/api/upload", methods=["POST"])
@login_required
def upload():
    current_app.logger.info("--- Magic Parse Request Started ---")
    file = request.files.get("file")
    if not file or not file.filename:
        current_app.logger.warning("Upload failed: No file found in request")
        return error_response("No file uploaded", 400)

    try:
        current_app.logger.info(f"Extracting text from file: {file.filename}")
        content = extract_text_from_file(file)
        
        if not content:
            current_app.logger.error("Text extraction returned empty or None")
            return error_response("Could not extract text from file", 400)
            
        current_app.logger.info(f"Extracted {len(content)} characters. Sending to AI for parsing...")
        extracted_data = AIService.parse_resume(content)
        
        if isinstance(extracted_data, dict) and "error" not in extracted_data:
            current_app.logger.info(f"Resume parsed successfully for user {current_user.id}")
            normalized_data = ResumeService.normalize_resume_data(extracted_data)
            return success_response("Resume successfully parsed!", {"extracted_data": normalized_data})
        else:
            error_msg = extracted_data.get('error') if isinstance(extracted_data, dict) else extracted_data
            current_app.logger.error(f"AI parsing failed with: {error_msg}")
            return error_response(f"AI Parsing Error: {error_msg}", 500)
    except Exception as e:
        current_app.logger.error(f"Critical error during upload/parsing: {str(e)}", exc_info=True)
        return error_response(f"Unexpected error: {str(e)}", 500)

@resume_bp.route("/api/tailor", methods=["POST"])
@login_required
def tailor():
    """Tailor an existing resume to a job description."""
    try:
        data = request.get_json() or {}
        resume_id = data.get("resume_id")
        jd = data.get("job_description")
        
        if not resume_id or not jd:
            return error_response("Missing Resume ID or Job Description", 400)
            
        resume = Resume.query.get_or_404(resume_id)
        if resume.user_id != current_user.id:
            return error_response("Unauthorized", 403)
            
        current_app.logger.info(f"Tailoring resume {resume_id} for user {current_user.id}")
        tailored_data = AIService.tailor_resume(resume.data, jd)
        
        if isinstance(tailored_data, dict) and "error" not in tailored_data:
            normalized_tailored = ResumeService.normalize_resume_data(tailored_data)
            return success_response("Resume successfully tailored!", {"tailored_data": normalized_tailored})
        else:
            error_msg = tailored_data.get('error') if isinstance(tailored_data, dict) else tailored_data
            current_app.logger.error(f"AI tailoring error: {error_msg}")
            return error_response(f"AI Tailoring Error: {error_msg}", 500)
    except Exception as e:
        current_app.logger.error(f"Error during tailoring: {str(e)}")
        return error_response("Unexpected error during resume tailoring", 500)

@resume_bp.route("/api/suggest", methods=["POST"])
@login_required
def suggest():
    """Get AI suggestions for a specific resume section."""
    try:
        data = request.json or {}
        section = data.get("section")
        context = data.get("context", "")
        
        full_resume = data.get("full_resume")
        
        if not section:
            return error_response("Section name is required", 400)
            
        current_app.logger.info(f"Requesting AI suggestion for section '{section}' (User: {current_user.id})")
        suggestion = AIService.get_suggestion(section, context, full_resume=full_resume)
        return success_response("Suggestion retrieved", {"suggestion": suggestion})
    except Exception as e:
        current_app.logger.error(f"Error fetching AI suggestion: {str(e)}")
        return error_response("Failed to fetch suggestion", 500)
 