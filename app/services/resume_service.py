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

        # Normalize simple list fields (rendered as bullet lists in templates)
        for field in ("skills", "certifications"):
            value = data.get(field, "")
            if isinstance(value, dict):
                # Handle dict mapping category to list of skills (from AI parse)
                flattened_parts = []
                for k, v in value.items():
                    if isinstance(v, list):
                        v_str = ", ".join(str(item) for item in v)
                    else:
                        v_str = str(v)
                    flattened_parts.append(f"{k}: {v_str}")
                data[field] = "\n".join(flattened_parts)
            elif isinstance(value, list):
                # Handle list of dicts (from AI parse)
                flattened_parts = []
                for item in value:
                    if isinstance(item, dict):
                        title = item.get("title", "")
                        points = item.get("points", "")
                        if isinstance(points, list):
                            points = "\n".join(points)
                        if title and points:
                            flattened_parts.append(f"{title}\n{points}")
                        elif title:
                            flattened_parts.append(title)
                        elif points:
                            flattened_parts.append(points)
                    elif isinstance(item, str):
                        flattened_parts.append(item)
                data[field] = "\n".join(flattened_parts)
            elif isinstance(value, str):
                # Keep as raw string for the editor, but clean it up
                bullets = parse_bullets(value)
                data[field] = "\n".join(bullets)

        # Normalize projects - keep as list-of-dicts for server-side Jinja templates
        # (templates iterate with project.title and project.points)
        projects = data.get("projects", "")
        if isinstance(projects, str):
            # Convert string to list-of-dicts format for template consistency
            bullets = parse_bullets(projects)
            if bullets:
                data["projects"] = [{"title": "", "points": bullets}]
            else:
                data["projects"] = []
        elif isinstance(projects, list):
            # Already a list - normalize each entry to ensure dict format
            normalized_projects = []
            for item in projects:
                if isinstance(item, dict):
                    points = item.get("points", "")
                    if isinstance(points, str):
                        item["points"] = parse_bullets(points)
                    normalized_projects.append(item)
                elif isinstance(item, str):
                    normalized_projects.append({"title": "", "points": [item]})
            data["projects"] = normalized_projects
        else:
            data["projects"] = []

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
        """Process and save/update a resume with versioning logic."""
        normalized_data = ResumeService.normalize_resume_data(raw_data)
        resume_id = raw_data.get('id') or raw_data.get('resume_id')
        
        # Strip meta fields from comparison to ensure bit-perfect content check
        comparison_data = normalized_data.copy()
        for k in ('id', 'resume_id', 'template', 'title', 'usedAi'):
            comparison_data.pop(k, None)
            
        new_data_json = json.dumps(comparison_data, sort_keys=True)
        new_template = normalized_data.get('template', raw_data.get('template', 'template1'))
        new_title = normalized_data.get('title', raw_data.get('title', f"{normalized_data.get('personal', {}).get('name', 'My')}'s Resume"))

        current_app.logger.info(f"--- Smart Save Check (User: {user_id}, ID: {resume_id}) ---")
        
        if resume_id:
            existing = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            if existing:
                existing_data = json.loads(existing.data)
                # Strip EVERYTHING that is stored in separate columns from the comparison
                for k in ('id', 'resume_id', 'template', 'title', 'usedAi'):
                    existing_data.pop(k, None)
                    
                existing_data_json = json.dumps(existing_data, sort_keys=True)
                
                # Check for absolute equality in content AND template AND title
                is_same_content = (existing_data_json == new_data_json)
                is_same_template = (existing.template_id == new_template)
                is_same_title = (existing.title == new_title)

                if is_same_content and is_same_template and is_same_title:
                    current_app.logger.info("NO CHANGES DETECTED. Overwriting existing resume.")
                    existing.used_ai = existing.used_ai or raw_data.get('usedAi', False)
                    db.session.commit()
                    return existing
                else:
                    current_app.logger.info(f"CHANGES DETECTED. Content: {is_same_content}, Template: {is_same_template}, Title: {is_same_title}. Creating NEW version.")
            else:
                current_app.logger.warning(f"Resume ID {resume_id} provided but not found for user {user_id}. Creating new.")

        # Create new record
        new_resume = Resume(
            user_id=user_id,
            title=new_title,
            data=new_data_json,
            template_id=new_template,
            used_ai=raw_data.get('usedAi', False)
        )
        
        db.session.add(new_resume)
        db.session.commit()
        return new_resume
