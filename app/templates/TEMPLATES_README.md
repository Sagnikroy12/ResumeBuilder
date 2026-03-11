# Resume Templates Guide

This directory contains all resume templates used by the Resume Builder application.

## Current Templates

1. **resume_template.html** (Classic) - Classic style with skills displayed in 2 columns
2. **resume_template2.html** (Modern) - Modern style with clean layout and single-column skills

## How to Add a New Template

### Step 1: Create the Template File
Create a new HTML file in this directory (e.g., `resume_template3.html`). 

**Template Requirements:**
- Use Jinja2 syntax for templating
- All sections should be wrapped in `{% if section_name %}...{% endif %}` conditionals to hide empty sections
- Each template receives the following data:
  - `personal.name`, `personal.address`, `personal.phone`, `personal.email`, `personal.linkedin`
  - `objective` - Optional string
  - `skills` - HTML list items (already formatted with `<li>` tags)
  - `experience` - Array of objects with: `title`, `duration`, `points` (array)
  - `projects` - HTML list items
  - `education` - Optional string
  - `certifications` - HTML list items
  - `custom_sections` - Array of objects with: `title`, `points` (array)

**Example Structure:**
```html
{% if objective %}
<div class="section-title">Objective</div>
<p>{{ objective }}</p>
{% endif %}

{% if skills %}
<div class="section-title">Skills</div>
<ul>
  {{ skills | safe }}
</ul>
{% endif %}
```

### Step 2: Register the Template
Add an entry to `app/config/templates_config.py`:

```python
"template3": {
    "name": "Template Name",
    "file": "resume_template3.html",
    "description": "Your template description"
},
```

### Step 3: Add Frontend Template (Optional)
If you want the preview to show your template in the form, add a JavaScript template to `app/static/js/form.js`:

```javascript
const template3 = (data) => `
<!-- Your template HTML here -->
`;
```

Then check the template selection logic in `updatePreview()` function.

## Template Best Practices

1. **Conditional Rendering**: Always wrap sections with `{% if section_name %}...{% endif %}`
2. **Styling**: Keep styles within the `<style>` tag in the template for PDF generation compatibility
3. **Bold Formatting**: Text before colons is automatically formatted as bold by the backend (e.g., "Python: Flask, Django" becomes "<strong>Python:</strong> Flask, Django")
4. **Mobile Responsive**: Remember these are PDFs, so responsive design isn't critical but should still look good in A4 format
5. **Testing**: Test with various data lengths to ensure proper layout

## Template Variables Reference

### Personal Data Object
```python
personal = {
    "name": str,        # Full name
    "address": str,     # Address
    "phone": str,       # Phone number
    "email": str,       # Email address
    "linkedin": str     # LinkedIn URL
}
```

### Experience Array (if not empty)
```python
experience = [
    {
        "title": str,           # Job title
        "duration": str,        # Duration (e.g., "Jan 2020 - Dec 2022")
        "points": [str, ...]    # List of responsibilities
    }
]
```

### Custom Sections Array
```python
custom_sections = [
    {
        "title": str,           # Section title
        "points": [str, ...]    # Section points
    }
]
```

## CSS Considerations for PDF Generation

- Use simple, standard CSS properties for best compatibility
- Avoid complex layouts; keep it simple and linear
- Test the PDF output before deploying
- Remember that wkhtmltopdf has some CSS limitations
