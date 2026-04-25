import re
import json

def parse_bullets(text):
    if not text:
        return []

    # Normalize all line endings to \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split and clean lines
    bullets = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    return bullets


def parse_resume_basic(text):
    """Simple regex-based resume parser that doesn't use AI.
    Falls back to pattern matching when AI services are unavailable.
    """
    if not text:
        return {}
    
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") if line.strip()]
    
    result = {
        "personal": {},
        "objective": "",
        "skills": "",
        "education": "",
        "experience": [],
        "projects": [],
        "certifications": ""
    }
    
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'[\+]?[(]?\d{1,3}[)]?[-\s\.]?\(?\d{3}\)?[-\s\.]?\d{3}[-\s\.]?\d{4}'
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    
    current_section = None
    exp_buffer = []
    skill_lines = []
    edu_lines = []
    cert_lines = []
    obj_lines = []
    
    section_keywords = {
        "experience": ["experience", "work", "employment", "professional", "history"],
        "education": ["education", "academic", "degree", "university", "college", "school"],
        "skills": ["skills", "technical", "technologies", "competencies"],
        "projects": ["projects", "project"],
        "certifications": ["certifications", "certificates", "certifications", "licenses"],
        "objective": ["objective", "summary", "profile", "about"]
    }
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if this line is a section header
        is_header = False
        for section, keywords in section_keywords.items():
            if any(kw in line_lower for kw in keywords) and len(line) < 50:
                current_section = section
                is_header = True
                break
        
        if is_header:
            continue
        
        # Extract personal info from any line
        email_match = re.search(email_pattern, line)
        if email_match and not result["personal"].get("email"):
            result["personal"]["email"] = email_match.group()
        
        phone_match = re.search(phone_pattern, line)
        if phone_match and not result["personal"].get("phone"):
            result["personal"]["phone"] = phone_match.group()
        
        linkedin_match = re.search(linkedin_pattern, line, re.IGNORECASE)
        if linkedin_match and not result["personal"].get("linkedin"):
            result["personal"]["linkedin"] = "https://" + linkedin_match.group()
        
        # Extract name - assume first non-email/phone line is name
        if not result["personal"].get("name") and line and current_section is None:
            if "@" not in line and not re.search(r'\d{3}', line) and len(line) < 40:
                result["personal"]["name"] = line
        
        # Build section content
        if current_section == "experience" or (not current_section and len(line) > 30):
            exp_buffer.append(line)
        elif current_section == "skills":
            skill_lines.append(line)
        elif current_section == "education":
            edu_lines.append(line)
        elif current_section == "certifications":
            cert_lines.append(line)
        elif current_section == "objective":
            obj_lines.append(line)
        elif not current_section and not result["personal"].get("name") and "@" not in line:
            obj_lines.append(line)
    
    # Build experience entries (group every 2-3 lines)
    i = 0
    while i < len(exp_buffer):
        title = exp_buffer[i] if i < len(exp_buffer) else ""
        duration = exp_buffer[i+1] if i+1 < len(exp_buffer) else ""
        points_start = i + 2
        points = "\n".join(exp_buffer[points_start:points_start+5]) if points_start < len(exp_buffer) else ""
        
        if title:
            result["experience"].append({
                "title": title,
                "duration": duration,
                "points": points
            })
        i += 3
    
    result["skills"] = "\n".join(skill_lines[:10])
    result["education"] = "\n".join(edu_lines[:5])
    result["certifications"] = "\n".join(cert_lines[:5])
    result["objective"] = "\n".join(obj_lines[:5])
    
    return result