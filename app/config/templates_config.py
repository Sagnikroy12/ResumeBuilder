"""
Template Configuration Registry
Centralized location to manage all resume templates.
To add a new template:
  1. Create the HTML template file in app/templates/
  2. Add an entry below with the template ID and file reference
"""

TEMPLATES = {
    "template1": {
        "name": "Classic",
        "file": "resume_template.html",
        "description": "Centered elegant layout with symmetric headers and 2-column skills section. Professional Times New Roman aesthetic.",
        "thumbnail": "img/templates/classic.png"
    },
    "template2": {
        "name": "Modern",
        "file": "resume_template2.html",
        "description": "Elegant asymmetrical header with name on left and contact info on right. Clean single-column section flow.",
        "thumbnail": "img/templates/modern.png"
    },
    "template3": {
    "name": "Professional",
    "file": "resume_template3.html",
    "description": "ATS-optimized minimalist layout with clean line separators and high readability. Perfect for corporate applications.",
    "thumbnail": "img/templates/professional.png"
    },
    # To add a new template:
    # "template3": {
    #     "name": "Template Name",
    #     "file": "resume_template3.html",
    #     "description": "Template description"
    # },
}


def get_template_file(template_id):
    """Get template filename by ID"""
    template = TEMPLATES.get(template_id)
    if template:
        return template["file"]
    return TEMPLATES["template1"]["file"]  # Default to template1


def get_all_templates():
    """Get all available templates"""
    return TEMPLATES


def is_valid_template(template_id):
    """Check if template ID exists"""
    return template_id in TEMPLATES
