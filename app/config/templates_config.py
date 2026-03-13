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
        "description": "Classic style with skills in 2 columns",
        "thumbnail": "img/templates/classic.png"
    },
    "template2": {
        "name": "Modern",
        "file": "resume_template2.html",
        "description": "Modern style with clean layout",
        "thumbnail": "img/templates/modern.png"
    },
    "template3": {
    "name": "Professional",
    "file": "resume_template3.html",
    "description": "Clean ATS-optimized professional layout",
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
