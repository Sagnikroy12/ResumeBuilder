from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
import json
from io import BytesIO

from ..services.pdf_service import generate_pdf
from ..utils.text_utils import parse_bullets
from ..config.templates_config import get_template_file
from app.models.resume import Resume
from app.extensions import db
from ..services.ai_service import AIService
from ..utils.file_parser import extract_text_from_file
from datetime import datetime, time
import pytz

resume_bp = Blueprint("resume", __name__)

def to_li(items):
    """Convert list of strings into HTML <li> elements with bold formatting before colons"""
    result = []
    for item in items:
        if ':' in item:
            parts = item.split(':', 1)
            formatted_item = f"<li><strong>{parts[0].strip()}:</strong> {parts[1].strip()}</li>"
        else:
            formatted_item = f"<li>{item}</li>"
        result.append(formatted_item)
    return "".join(result)


def _normalize_resume_data(data):
    """Normalize resume data for rendering and storage.

    This ensures that template expects lists (for bullets) and safe HTML is provided where needed.
    """
    if not isinstance(data, dict):
        return {}

    data = data.copy()

    # Normalize list fields
    for field in ("skills", "projects", "certifications"):
        value = data.get(field, "")
        if isinstance(value, str):
            bullets = parse_bullets(value)
            data[field] = to_li(bullets)

    # Normalize experience entries
    experience = data.get("experience", [])
    if isinstance(experience, list):
        normalized_exp = []
        for exp in experience:
            if not isinstance(exp, dict):
                continue
            points = exp.get("points", "")
            if isinstance(points, str):
                exp["points"] = parse_bullets(points)
            normalized_exp.append(exp)
        data["experience"] = normalized_exp
    else:
        data["experience"] = []

    # Normalize custom sections
    custom_sections = data.get("custom_sections", [])
    if isinstance(custom_sections, list):
        for section in custom_sections:
            if isinstance(section, dict):
                points = section.get("points", "")
                if isinstance(points, str):
                    section["points"] = parse_bullets(points)
    else:
        data["custom_sections"] = []

    return data


@resume_bp.route("/api/resumes", methods=["POST"])
@login_required
def create_resume():
    # ---------- MONETIZATION LIMIT CHECK ----------
    if not current_user.is_premium:
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        midnight_ist = ist.localize(datetime.combine(now_ist.date(), time.min))
        
        daily_generates = Resume.query.filter(
            Resume.user_id == current_user.id,
            Resume.created_at >= midnight_ist
        ).count()
        
        if daily_generates >= 10:
            return jsonify({"message": "Daily limit reached.", "status": "danger"}), 403

    data = request.get_json() or {}

    # Normalize data so templates get the formats they expect (lists for bullets, HTML list items, etc.)
    normalized_data = _normalize_resume_data(data)

    new_resume = Resume(
        user_id=current_user.id,
        title=normalized_data.get('title', f"{normalized_data.get('personal', {}).get('name', 'My')}'s Resume"),
        data=json.dumps(normalized_data),
        template_id=normalized_data.get('template', 'template1'),
        used_ai=data.get('usedAi', False)
    )
    db.session.add(new_resume)
    db.session.commit()
    
    return jsonify({
        "message": "Resume successfully generated and saved!", 
        "status": "success",
        "resume_id": new_resume.id
    }), 201


@resume_bp.route("/api/preview", methods=["POST"])
@login_required
def preview_resume():
    """Render a live preview of the resume based on current form data."""
    data = request.get_json() or {}
    normalized_data = _normalize_resume_data(data)
    template_file = get_template_file(normalized_data.get("template", "template1"))

    html = render_template(template_file, **normalized_data)
    return jsonify({"html": html}), 200

@resume_bp.route("/api/resumes/<int:resume_id>", methods=["GET"])
@login_required
def get_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 403
    
    return jsonify({
        "id": resume.id,
        "title": resume.title,
        "data": json.loads(resume.data),
        "template_id": resume.template_id,
        "used_ai": resume.used_ai
    }), 200


@resume_bp.route("/api/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")
    if file and file.filename:
        content = extract_text_from_file(file)
        if not content:
            return jsonify({"message": "Could not extract text.", "status": "danger"}), 400
            
        extracted_data = AIService.parse_resume(content)
        
        if isinstance(extracted_data, dict) and "error" not in extracted_data:
            # Optionally store in session or return for frontend to pre-fill
            return jsonify({
                "message": "Resume successfully parsed!", 
                "status": "success",
                "extracted_data": extracted_data
            }), 200
        else:
            return jsonify({
                "message": f"AI Parsing Error: {extracted_data.get('error') if isinstance(extracted_data, dict) else extracted_data}", 
                "status": "danger"
            }), 500
        
    return jsonify({"message": "No file uploaded.", "status": "danger"}), 400

@resume_bp.route("/api/tailor", methods=["POST"])
@login_required
def tailor():
    data = request.get_json()
    resume_id = data.get("resume_id")
    jd = data.get("job_description")
    
    if resume_id and jd:
        resume = Resume.query.get_or_404(resume_id)
        if resume.user_id != current_user.id:
            return jsonify({"message": "Unauthorized"}), 403
            
        # Extract text from existing resume data or stored file
        # For simplicity, we use the stored JSON data as content or re-parse it
        content = resume.data 
        tailored_data = AIService.tailor_resume(content, jd)
        
        if isinstance(tailored_data, dict) and "error" not in tailored_data:
            return jsonify({
                "message": "Resume successfully tailored!", 
                "status": "success",
                "tailored_data": tailored_data
            }), 200
        else:
            return jsonify({
                "message": f"AI Tailoring Error: {tailored_data.get('error') if isinstance(tailored_data, dict) else tailored_data}", 
                "status": "danger"
            }), 500
        
    return jsonify({"message": "Missing Resume ID or JD.", "status": "danger"}), 400

@resume_bp.route("/api/suggest", methods=["POST"])
@login_required
def suggest():
    data = request.json
    section = data.get("section")
    context = data.get("context", "")
    suggestion = AIService.get_suggestion(section, context)
    return jsonify({"suggestion": suggestion}), 200
