import json
import pytz
from datetime import datetime, time
from flask import current_app
from app.extensions import db
from app.models.resume import Resume
from app.utils.text_utils import parse_bullets

class ResumeService:
    @staticmethod
    def _flatten_value(value):
        """Recursively flatten any list or dict into a single comma-separated string."""
        if not value:
            return ""
        if isinstance(value, str):
            # Ignore placeholder strings that AI failed to replace
            if "__" in value and "ADDRESS" in value:
                return ""
            return value.strip()
        if isinstance(value, list):
            # Flatten lists and remove empty/placeholder items
            items = [ResumeService._flatten_value(item) for item in value]
            return ", ".join(filter(None, items))
        if isinstance(value, dict):
            # Flatten dicts by concatenating all their values
            items = [ResumeService._flatten_value(v) for v in value.values()]
            return ", ".join(filter(None, items))
        return str(value).strip()

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
                # Handle dict mapping category to list/dict of skills (from AI parse)
                flattened_parts = []
                for k, v in value.items():
                    v_str = ResumeService._flatten_value(v)
                    if v_str.strip():
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

        # Normalize education and objective which can also sometimes come as dicts/lists
        for field in ("education", "objective"):
            value = data.get(field, "")
            if isinstance(value, dict):
                flattened_parts = []
                for k, v in value.items():
                    v_str = ResumeService._flatten_value(v)
                    if v_str.strip():
                        flattened_parts.append(f"{k}: {v_str}")
                data[field] = "\n\n".join(flattened_parts)
            elif isinstance(value, list):
                parts = []
                for item in value:
                    v_str = ResumeService._flatten_value(item)
                    if v_str:
                        parts.append(v_str)
                data[field] = "\n\n".join(parts)

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
                    points = item.get("points", [])
                    if isinstance(points, str):
                        item["points"] = parse_bullets(points)
                    elif not isinstance(points, list):
                        item["points"] = []
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
                points = exp.get("points", [])
                if isinstance(points, str):
                    exp["points"] = parse_bullets(points)
                elif not isinstance(points, list):
                    exp["points"] = []
                normalized_exp.append(exp)
            data["experience"] = normalized_exp
        else:
            data["experience"] = []

        # Normalize custom sections
        custom_sections = data.get("custom_sections", [])
        if isinstance(custom_sections, list):
            for section in custom_sections:
                if isinstance(section, dict):
                    points = section.get("points", [])
                    if isinstance(points, str):
                        section["points"] = parse_bullets(points)
                    elif not isinstance(points, list):
                        section["points"] = []
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
            Resume.user_id == user.email,
            Resume.created_at >= midnight_ist
        ).count()
        
        if daily_generates >= 10:
            return False, "Daily limit reached for free tier (10 resumes/day)."
        
        return True, None

    @staticmethod
    def create_resume(user_id, raw_data):
        """Process and save/update a resume. Overwrites existing record if ID is provided."""
        normalized_data = ResumeService.normalize_resume_data(raw_data)
        resume_id = raw_data.get('id') or raw_data.get('resume_id')
        
        # Strip meta fields from JSON storage to keep data clean
        comparison_data = normalized_data.copy()
        for k in ('id', 'resume_id', 'template', 'title', 'usedAi'):
            comparison_data.pop(k, None)
            
        new_data_json = json.dumps(comparison_data, sort_keys=True)
        
        # Priority: explicit 'template' in raw_data > 'template' in normalized_data > 'template_id' in existing record > default
        new_template = raw_data.get('template') or normalized_data.get('template')
        
        # Extract first name for title - check multiple locations
        full_name = (
            raw_data.get('name') or 
            normalized_data.get('name') or
            raw_data.get('personal', {}).get('name') or
            normalized_data.get('personal', {}).get('name') or
            ''
        )
        first_name = full_name.split()[0].strip("'s") if full_name else ''
        
        new_title = raw_data.get('title') or normalized_data.get('title') or (f"{first_name}'s Resume" if first_name else "My Resume")

        if resume_id:
            existing = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
            if existing:
                current_app.logger.info(f"Updating existing resume {resume_id} (User: {user_id})")
                
                # If template was not provided in POST, keep the existing one
                final_template = new_template or existing.template_id or 'template1'
                
                current_app.logger.info(f"Saving resume {resume_id} with template: {final_template}")
                
                existing.data = new_data_json
                existing.template_id = final_template
                existing.title = new_title
                existing.used_ai = existing.used_ai or raw_data.get('usedAi', False)
                db.session.commit()
                return existing
            else:
                current_app.logger.warning(f"Resume ID {resume_id} provided but not found for user {user_id}. Creating new.")

        # Create new record if no ID or ID not found
        final_template = new_template or 'template1'
        current_app.logger.info(f"Creating new resume for user {user_id} with template: {final_template}")
        
        new_resume = Resume(
            user_id=user_id,
            title=new_title,
            data=new_data_json,
            template_id=final_template,
            used_ai=raw_data.get('usedAi', False)
        )
        
        db.session.add(new_resume)
        db.session.commit()
        return new_resume
