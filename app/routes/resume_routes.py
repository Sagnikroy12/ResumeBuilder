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

# Logic moved to ResumeService


@resume_bp.route("/api/resumes", methods=["POST"])
@login_required
def create_resume():
    """Create and save a new resume."""
    try:
        data = request.get_json() or {}
        
        # 1. Limit Check
        allowed, message = ResumeService.check_daily_limit(current_user)
        if not allowed:
            current_app.logger.warning(f"User {current_user.id} reached daily limit.")
            return error_response(message, 403)

        # 2. Create Resume via Service
        new_resume = ResumeService.create_resume(current_user.id, data)
        
        current_app.logger.info(f"Resume created: {new_resume.id} by user {current_user.id}")
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
    data = request.get_json() or {}
    normalized_data = ResumeService.normalize_resume_data(data)
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
    file = request.files.get("file")
    if not file or not file.filename:
        return error_response("No file uploaded", 400)

    try:
        content = extract_text_from_file(file)
        if not content:
            return error_response("Could not extract text from file", 400)
            
        extracted_data = AIService.parse_resume(content)
        
        if isinstance(extracted_data, dict) and "error" not in extracted_data:
            current_app.logger.info(f"Resume parsed successfully for user {current_user.id}")
            return success_response("Resume successfully parsed!", {"extracted_data": extracted_data})
        else:
            error_msg = extracted_data.get('error') if isinstance(extracted_data, dict) else extracted_data
            current_app.logger.error(f"AI parsing error: {error_msg}")
            return error_response(f"AI Parsing Error: {error_msg}", 500)
    except Exception as e:
        current_app.logger.error(f"Error during upload/parsing: {str(e)}")
        return error_response("Unexpected error during resume parsing", 500)

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
            return success_response("Resume successfully tailored!", {"tailored_data": tailored_data})
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
        
        if not section:
            return error_response("Section name is required", 400)
            
        current_app.logger.info(f"Requesting AI suggestion for section '{section}' (User: {current_user.id})")
        suggestion = AIService.get_suggestion(section, context)
        return success_response("Suggestion retrieved", {"suggestion": suggestion})
    except Exception as e:
        current_app.logger.error(f"Error fetching AI suggestion: {str(e)}")
        return error_response("Failed to fetch suggestion", 500)
 