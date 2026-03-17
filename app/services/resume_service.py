import json
import pytz
from datetime import datetime, time
from flask import current_app
from app.extensions import db
from app.models.resume import Resume
from app.utils.text_utils import parse_bullets

class ResumeService:
    @staticmethod
    def to_li(items):
        """Convert list of strings into HTML <li> elements with bold formatting before colons."""
        result = []
        for item in items:
            if ':' in item:
                parts = item.split(':', 1)
                formatted_item = f"<li><strong>{parts[0].strip()}:</strong> {parts[1].strip()}</li>"
            else:
                formatted_item = f"<li>{item}</li>"
            result.append(formatted_item)
        return "".join(result)

    @staticmethod
    def normalize_resume_data(data):
        """Normalize resume data for rendering and storage."""
        if not isinstance(data, dict):
            return {}

        data = data.copy()

        # Normalize list fields
        for field in ("skills", "projects", "certifications"):
            value = data.get(field, "")
            if isinstance(value, str):
                bullets = parse_bullets(value)
                data[field] = ResumeService.to_li(bullets)

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

    @staticmethod
    def check_daily_limit(user):
        """Check if user has reached their daily resume generation limit."""
        if user.is_premium:
            return True, None

        ist = pytz.timezone('Asia/Kolkata')
        now_ist = datetime.now(ist)
        midnight_ist = ist.localize(datetime.combine(now_ist.date(), time.min))
        
        daily_generates = Resume.query.filter(
            Resume.user_id == user.id,
            Resume.created_at >= midnight_ist
        ).count()
        
        if daily_generates >= 10:
            return False, "Daily limit reached for free tier (10 resumes/day)."
        
        return True, None

    @staticmethod
    def create_resume(user_id, raw_data):
        """Process and save a new resume."""
        normalized_data = ResumeService.normalize_resume_data(raw_data)
        
        new_resume = Resume(
            user_id=user_id,
            title=normalized_data.get('title', f"{normalized_data.get('personal', {}).get('name', 'My')}'s Resume"),
            data=json.dumps(normalized_data),
            template_id=normalized_data.get('template', 'template1'),
            used_ai=raw_data.get('usedAi', False)
        )
        
        db.session.add(new_resume)
        db.session.commit()
        return new_resume
