# Resume Templates Guide

This directory contains all resume templates used by the Resume Builder application.

## Current Templates

1. **resume_template.html** (Classic) - Classic style with skills displayed in 2 columns
2. **resume_template2.html** (Modern) - Modern style with clean layout and single-column skills
3. **resume_template3.html** (Minimalist) - Compact style with minimalist design

## How to Add a New Template

### Step 1: Create the Template File
Create a new HTML file in this directory (e.g., `resume_template4.html`).

### ⚠️ CRITICAL REQUIREMENTS FOR AI PROMPT

When prompting an AI to generate a new template, use this complete specification:

---

## AI PROMPT SPECIFICATION - Copy This Entire Section

You are generating a Jinja2 HTML resume template for a Flask application. Follow ALL requirements exactly.

### MANDATORY STRUCTURAL REQUIREMENTS

1. **File Structure**
   - DOCTYPE: `<!doctype html>`
   - Must have `<head>` with CSS in `<style>` tag
   - Use Jinja2 templating syntax for all dynamic content

2. **DATA VARIABLES AVAILABLE** (These will be provided by backend)
   ```
   personal.name (str) - Full name
   personal.address (str) - Address
   personal.phone (str) - Phone number
   personal.email (str) - Email address
   personal.linkedin (str) - LinkedIn URL
   
   objective (str or None) - Career objective paragraph
   education (str or None) - Education text
   
   skills (HTML str) - Pre-formatted <li> items with bold before colons
   projects (HTML str) - Pre-formatted <li> items
   certifications (HTML str) - Pre-formatted <li> items
   
   experience (list of dicts or None):
     - title (str) - Job title
     - duration (str) - Employment duration
     - points (list of str) - Responsibility bullet points
   
   custom_sections (list of dicts or None):
     - title (str) - Section name
     - points (list of str) - Section bullet points
   ```

3. **CONDITIONAL RENDERING - ABSOLUTELY REQUIRED**

   a) **Header/Contact Section** (MOST IMPORTANT - ALWAYS DO THIS):
      ```html
      {% if personal.name or personal.address or personal.phone or personal.email or personal.linkedin %}
      <div class="header">
        {% if personal.name %}
        <div class="name">{{ personal.name }}</div>
        {% endif %}

        {% if personal.address or personal.phone or personal.email or personal.linkedin %}
        <div class="contact">
          {{ personal.address }}{% if personal.address and personal.phone %} | {% endif %}{{ personal.phone }}{% if (personal.address or personal.phone) and personal.email %} | {% endif %}{{ personal.email }}{% if (personal.address or personal.phone or personal.email) and personal.linkedin %} | {% endif %}{{ personal.linkedin }}
        </div>
        {% endif %}
      </div>
      {% endif %}
      ```
      
      WHY: Shows nothing if ALL contact fields are empty. Shows separators only when adjacent fields exist.

   b) **For All Content Sections** (objective, skills, experience, projects, education, certifications, custom_sections):
      ```html
      {% if skills %}
      <div class="section">
        <div class="section-title">Skills</div>
        <ul>
          {{ skills | safe }}
        </ul>
      </div>
      {% endif %}
      ```

   c) **For Experience Section** (Loop through array):
      ```html
      {% if experience %}
      <div class="section">
        <div class="section-title">Experience</div>
        {% for job in experience %}
        <div class="job">
          <div class="job-header">
            <span>{{ job.title }}</span>
            <span>{{ job.duration }}</span>
          </div>
          <ul>
            {% for point in job.points %}
            <li>{{ point }}</li>
            {% endfor %}
          </ul>
        </div>
        {% endfor %}
      </div>
      {% endif %}
      ```

   d) **For Custom Sections** (Loop through array):
      ```html
      {% if custom_sections %}
      {% for section in custom_sections %}
      <div class="section">
        <div class="section-title">{{ section.title }}</div>
        <ul>
          {% for p in section.points %}
          <li>{{ p }}</li>
          {% endfor %}
        </ul>
      </div>
      {% endfor %}
      {% endif %}
      ```

4. **SAFE FILTER FOR GENERATED HTML**
   - When using pre-formatted HTML from backend (skills, projects, certifications), use: `{{ variable | safe }}`
   - Example: `{{ skills | safe }}`
   - Do NOT use safe filter for user text inputs like objective or education

5. **CSS REQUIREMENTS**
   - Keep all CSS in `<style>` tag in `<head>` section
   - Use simple, standard CSS properties (avoid complex layouts)
   - A4 page size: approximately 210mm × 297mm, margins 10-40px
   - Recommended margins: 20px total
   - Font: "Times New Roman", Times, serif (for PDF compatibility)
   - Line-height: 1.2-1.35 for compact resumes, 1.4+ for spacious ones
   - Use flexbox for headers only (job title + duration side-by-side)

6. **FORMATTING FEATURES ALREADY BUILT-IN**
   - Bold text before colons: Skills like "Python: Django, Flask" are already formatted as `<strong>Python:</strong> Django, Flask`
   - Do NOT add extra formatting for this
   - Lists come pre-formatted with `<li>` tags
   - Do NOT add manual bullet points

7. **LIST STYLING REQUIREMENTS**
   - Always use `<ul>` with `<li>` for bullet points
   - CSS must include: `list-style-type: disc;` and `list-style-position: outside;`
   - Ensure `padding-left: 20px;` on `<ul>` elements
   - Ensure `text-align: left;` on `<li>` elements for alignment consistency

8. **DO NOT INCLUDE**
   - Do NOT hardcode any sample data
   - Do NOT use JavaScript in the template
   - Do NOT create responsive/mobile designs (PDF only)
   - Do NOT use external stylesheets or imports
   - Do NOT use CSS Grid or complex layouts
   - Do NOT assume any fields will be present without checking

9. **MUST USE `{{ variable | safe }}`**
   - `{{ skills | safe }}`
   - `{{ projects | safe }}`
   - `{{ certifications | safe }}`
   - NEVER use `| safe` on objective or education (user text fields)

### COMPLETE WORKING EXAMPLE
See `resume_template3.html` in this directory for a complete, production-ready template that follows all these rules.

---

### Step 2: Register the Template
Add an entry to `app/config/templates_config.py`:

```python
TEMPLATES = {
    # ... existing templates ...
    "template4": {
        "name": "Your Template Name",
        "file": "resume_template4.html",
        "description": "Description of your template style"
    },
}
```

### Step 3: (Optional) Add Live Preview Support
If you want live preview in the form, add a JavaScript template function to `app/static/js/form.js`, but this is optional - the backend PDF generation will work without it.

## Common Mistakes to Avoid

❌ **WRONG**: Not wrapping header in conditional
```html
<div class="header">
  <div class="name">{{ personal.name }}</div>  <!-- Shows even if empty -->
</div>
```

✅ **CORRECT**: Wrapping header with conditional
```html
{% if personal.name or personal.address or personal.phone or personal.email or personal.linkedin %}
<div class="header">
  {% if personal.name %}
  <div class="name">{{ personal.name }}</div>
  {% endif %}
  ...
</div>
{% endif %}
```

---

❌ **WRONG**: Not using safe filter for pre-formatted HTML
```html
<ul>
  {{ skills }}  <!-- HTML will be escaped and displayed as text -->
</ul>
```

✅ **CORRECT**: Using safe filter
```html
<ul>
  {{ skills | safe }}  <!-- HTML renders correctly -->
</ul>
```

---

❌ **WRONG**: Adding manual formatting to auto-formatted data
```html
<li><strong>{{ skill }}</strong></li>  <!-- Skills already include <strong> -->
```

✅ **CORRECT**: Just render the pre-formatted data
```html
{{ skills | safe }}  <!-- Already properly formatted by backend -->
```

## Template Variables Reference

### Personal Data Object
```python
personal = {
    "name": str,        # Full name (can be empty)
    "address": str,     # Address (can be empty)
    "phone": str,       # Phone number (can be empty) 
    "email": str,       # Email address (can be empty)
    "linkedin": str     # LinkedIn URL (can be empty)
}
```

### Optional Strings
```python
objective = str or None      # Career objective
education = str or None      # Education info
```

### Pre-formatted HTML Lists
```python
skills = str (HTML) or None        # Example: "<li><strong>Python:</strong> Django, Flask</li><li>..."
projects = str (HTML) or None      # Example: "<li>Project Name - Description</li><li>..."
certifications = str (HTML) or None # Example: "<li>AWS Certified Solutions Architect</li><li>..."
```

### Experience Array
```python
experience = [
    {
        "title": str,           # Job title
        "duration": str,        # "Jan 2020 - Dec 2022"
        "points": [str, str, ...] # ["Achievement 1", "Achievement 2"]
    },
    ...
] or None
```

### Custom Sections Array
```python
custom_sections = [
    {
        "title": str,        # Section name
        "points": [str, ...] # ["Point 1", "Point 2"]
    },
    ...
] or None
```

## Testing Your Template

1. Fill only the Name field - header should show only name
2. Fill only Skills field - only Skills section should render
3. Fill only Experience with one job - Experience section should render with that job
4. Leave all fields empty - page should be blank or show minimal content
5. Test with both single-line and multi-line text fields
6. Verify PDF output looks correct (use the form to download PDF)

## CSS Considerations for PDF Generation

- wkhtmltopdf CSS Support: Uses WebKit, supports CSS 2.1 and some CSS 3
- Supported: flexbox, basic layout, colors, fonts
- NOT Supported: CSS Grid, complex transforms, animations
- Font Size: 13-18px works best
- Margins: 10-40px is typical
- Keep margins reasonable to fit content on A4 page

