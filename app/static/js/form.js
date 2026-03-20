/* ===============================
DYNAMIC ADD / REMOVE BLOCKS
=============================== */

function addExperience(initialData = null) {
  const container = document.getElementById("experience-container");

  const block = document.createElement("div");
  block.className = "exp-block";

  block.innerHTML = `
    Title <input name="exp_title[]" value="${initialData ? (initialData.title || '') : ''}" oninput="updatePreview()">
    Duration <input name="exp_duration[]" value="${initialData ? (initialData.duration || '') : ''}" oninput="updatePreview()">
    Responsibilities
    <textarea name="exp_points[]" oninput="updatePreview()">${initialData ? (Array.isArray(initialData.points) ? initialData.points.join('\n') : initialData.points || '') : ''}</textarea>
    <button type="button" onclick="removeBlock(this)">Remove</button>
  `;

  container.appendChild(block);
  updatePreview();

  if (typeof aiEnabled !== 'undefined' && aiEnabled) {
    const aiBtn = document.createElement("button");
    aiBtn.type = "button";
    aiBtn.className = "btn-ai";
    aiBtn.innerHTML = "✨ AI Suggest Content";
    aiBtn.onclick = function(e) {
        const textarea = block.querySelector('textarea');
        const title = block.querySelector('input[name="exp_title[]"]').value;
        const responsibilities = textarea.value || "";
        // Send using clear tags so the AI service can separate background context from content to reframe
        let fullContext = `JOB_TITLE: ${title}\nEXISTING_CONTENT: ${responsibilities}`;
        getAiSuggestion(e, 'Experience', textarea, fullContext);
    };
    block.appendChild(aiBtn);
  }
}

async function getAiSuggestion(event, section, element = null, context = "") {
    const targetElement = element || document.getElementById(section);
    
    // If context is empty, try to get value from the field itself (helpful for 'SDET' etc)
    if (!context && targetElement) {
        context = targetElement.value || "";
    }

    const originalText = targetElement.innerText || "AI Suggest";
    
    // UI Feedback
    const btn = event.currentTarget;
    const originalBtnText = btn.innerHTML;
    btn.innerHTML = "🌀 Thinking...";
    btn.classList.add("loading");
    btn.disabled = true;

    try {
        const response = await fetch(suggestApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                section: section, 
                context: context,
                full_resume: getFormData()
            })
        });
        const data = await response.json();
        
        if (data.suggestion) {
            if (targetElement.tagName === 'TEXTAREA' || targetElement.tagName === 'INPUT') {
                targetElement.value = data.suggestion;
                updatePreview();
            }
        } else if (data.error) {
            // Show user-facing error if all providers failed
            alert("AI Error: " + (data.error || "Multiple providers exhausted. Please try again later."));
        }
    } catch (error) {
        console.error("AI Error:", error);
        alert("AI Error: Failed to connect to service. Please check your connection.");
    } finally {
        btn.innerHTML = originalBtnText;
        btn.classList.remove("loading");
        btn.disabled = false;
    }
}

function removeBlock(btn) {
  btn.parentElement.remove();
  updatePreview();
}

/**
 * Collects all current form data into a structured JSON object
 */
function getFormData() {
    const data = {};
    data.name = document.querySelector("[name='name']")?.value || "";
    data.email = document.querySelector("[name='email']")?.value || "";
    data.phone = document.querySelector("[name='phone']")?.value || "";
    data.linkedin = document.querySelector("[name='linkedin']")?.value || "";
    data.address = document.querySelector("[name='address']")?.value || "";
    data.objective = document.querySelector("[name='objective']")?.value || "";
    data.skills = document.querySelector("[name='skills']")?.value || "";
    data.education = document.querySelector("[name='education']")?.value || "";
    data.projects = document.querySelector("[name='projects']")?.value || "";

    /* EXPERIENCE */
    const expBlocks = document.querySelectorAll(".exp-block");
    data.experience = Array.from(expBlocks).map(block => ({
        title: block.querySelector("[name='exp_title[]']")?.value || "",
        duration: block.querySelector("[name='exp_duration[]']")?.value || "",
        points: block.querySelector("[name='exp_points[]']")?.value || ""
    }));

    /* CUSTOM SECTIONS */
    const customBlocks = document.querySelectorAll(".custom-section");
    data.custom_sections = Array.from(customBlocks).map(block => {
        const title = block.querySelector("[name='section_title[]']")?.value || "";
        const points = block.querySelector("[name='section_points[]']")?.value || "";
        return { title, points };
    });

    return data;
}

function addCustomSection(initialData = null) {
  const container = document.getElementById("custom-section-container");

  const div = document.createElement("div");
  div.classList.add("custom-section");

  div.innerHTML = `
    <input name="section_title[]" placeholder="Section Title" value="${initialData ? (initialData.title || '') : ''}" oninput="updatePreview()">
    <textarea name="section_points[]" placeholder="One point per line" oninput="updatePreview()">${initialData ? (Array.isArray(initialData.points) ? initialData.points.join('\n') : initialData.points || '') : ''}</textarea>
    <button type="button" onclick="removeBlock(this)">Remove</button>
  `;

  container.appendChild(div);
  updatePreview();

  if (typeof aiEnabled !== 'undefined' && aiEnabled) {
    const aiBtn = document.createElement("button");
    aiBtn.type = "button";
    aiBtn.className = "btn-ai";
    aiBtn.innerHTML = "✨ AI Suggest Content";
    aiBtn.onclick = function(e) {
        const textarea = div.querySelector('textarea');
        const title = div.querySelector('input[name="section_title[]"]').value || "Custom Section";
        const content = textarea.value || "";
        getAiSuggestion(e, title, textarea, content);
    };
    div.appendChild(aiBtn);
  }
}

/* ===============================
PAGE LOAD
=============================== */

window.onload = function () {
  const expContainer = document.getElementById("experience-container");
  const customContainer = document.getElementById("custom-section-container");
  
  // Clear any default/hardcoded content
  expContainer.innerHTML = "";
  customContainer.innerHTML = "";

  if (typeof initialResumeData !== 'undefined' && initialResumeData) {
    console.log("Populating with initial AI data:", initialResumeData);
    
    // Populate Experience
    if (initialResumeData.experience && Array.isArray(initialResumeData.experience)) {
      initialResumeData.experience.forEach(exp => addExperience(exp));
    }
    
    // Populate Projects textarea if it's an array of objects (from magic parse)
    if (initialResumeData.projects && Array.isArray(initialResumeData.projects)) {
      const projectsField = document.querySelector("[name='projects']");
      if (projectsField) {
        const projectText = initialResumeData.projects.map(p => {
          if (typeof p === 'object' && p !== null) {
            let line = p.title || '';
            if (p.points) {
              const pts = Array.isArray(p.points) ? p.points.join('\n') : p.points;
              line += (line ? '\n' : '') + pts;
            }
            return line;
          }
          return String(p);
        }).join('\n');
        projectsField.value = projectText;
      }
    }
    
    // Populate Custom Sections if any
    if (initialResumeData.custom_sections && Array.isArray(initialResumeData.custom_sections)) {
      initialResumeData.custom_sections.forEach(sec => addCustomSection(sec));
    }
    
    // If no experience was added, add one empty one
    if (expContainer.children.length === 0) addExperience();
  } else {
    // Standard new resume flow
    addExperience();
  }
  
  updatePreview();
};

/* ===============================
TEMPLATE 1
=============================== */

const template1 = (data) => `
<!doctype html>
<html>
<head>
<meta charset="utf-8">

<style>

body{
font-family:"Times New Roman";
margin:10px;
line-height:1.4;
font-size:16px;
background-color: white;
color: #000;
}

h1{
text-align:center;
margin-bottom:4px;
color: #000;
}

.contact{
text-align:center;
font-weight:bold;
margin-top:4px;
color: #000;
}

.section{
margin-top:10px;
}

h3{
margin-bottom:4px;
font-size:22px;
color: #000;
border-bottom:1px solid #000;
padding-bottom:2px;
}

ul{
margin:4px 0 8px 25px;
padding:0;
list-style-type:disc;
list-style-position:outside;
}

li{
color: #000;
}

p{
color: #000;
}

/* Cloud character animation */
.cloud-char {
  display: inline-block;
  animation: cloudCharacter 0.15s ease-out forwards;
}

@keyframes cloudCharacter {
  0% {
    opacity: 0;
    transform: translateY(-15px) scale(0.5);
  }
  60% {
    opacity: 1;
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.job-header{
display:flex;
justify-content:space-between;
font-weight:bold;
margin-bottom:4px;
}

</style>
</head>

<body>

${data.name ? `<h1>${data.name}</h1>` : ""}

${
  data.name || data.address || data.phone || data.email || data.linkedin
    ? `
<hr>

<div class="contact">
${data.address || ""} ${data.address && data.phone ? "|" : ""} ${data.phone || ""} ${(data.address || data.phone) && data.email ? "|" : ""} ${data.email || ""}<br>
${data.linkedin || ""}
</div>

<hr>
`
    : ""
}

${
  data.objective
    ? `
<div class="section">
<h3>Objective</h3>
<p>${data.objective}</p>
</div>
`
    : ""
}

${
  data.skills
    ? `
<div class="section">
<h3>Skills</h3>
<ul>${data.skills}</ul>
</div>
`
    : ""
}

${data.experience}

${
  data.projects
    ? `
<div class="section">
<h3>Projects</h3>
<ul>${data.projects}</ul>
</div>
`
    : ""
}

${
  data.education
    ? `
<div class="section">
<h3>Education</h3>
<p>${data.education}</p>
</div>
`
    : ""
}

${
  data.certifications
    ? `
<div class="section">
<h3>Certifications</h3>
<ul>${data.certifications}</ul>
</div>
`
    : ""
}

${data.custom}

</body>
</html>
`;

/* ===============================
TEMPLATE 2
=============================== */

const template2 = (data) => `
<!doctype html>
<html>
<head>
<meta charset="utf-8">

<style>

body{
font-family:"Times New Roman";
margin:10px;
color:#000;
line-height:1.25;
font-size:16px;
background-color: white;
}

.header-table{
width:100%;
margin-bottom:20px;
}

.name{
font-size:32px;
font-weight:800;
color: #000;
}

.contact-block{
text-align:right;
font-weight:600;
font-size:14px;
color: #000;
}

.section-title{
font-size:18px;
font-weight:700;
margin:20px 0 8px 0;
border-bottom:1.5px solid #000;
padding-bottom:2px;
text-transform:uppercase;
color: #000;
}

ul{
margin:4px 0 8px 20px;
list-style-type:disc;
list-style-position:outside;
padding-left:20px;
}

li{
color: #000;
}

p{
color: #000;
}

/* Cloud character animation */
.cloud-char {
  display: inline-block;
  animation: cloudCharacter 0.15s ease-out forwards;
}

@keyframes cloudCharacter {
  0% {
    opacity: 0;
    transform: translateY(-15px) scale(0.5);
  }
  60% {
    opacity: 1;
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

li{
text-align:left;
}

.job-header{
display:flex;
justify-content:space-between;
font-weight:bold;
margin-bottom:4px;
}

.skill-list{
column-count:1;
column-gap:25px;
}

</style>

</head>

<body>

${
  data.name || data.address || data.phone || data.email || data.linkedin
    ? `
<table class="header-table">
<tr>

<td>
<div class="name">${data.name || ""}</div>
</td>

<td class="contact-block">
${data.address || ""}<br>
${data.phone || ""}<br>
${data.email || ""}<br>
${data.linkedin || ""}
</td>

</tr>
</table>
`
    : ""
}

${
  data.objective
    ? `
<div class="section-title">Objective</div>
<p>${data.objective}</p>
`
    : ""
}

${
  data.skills
    ? `
<div class="section-title">Skills</div>
<ul class="skill-list">${data.skills}</ul>
`
    : ""
}

${data.experience}

${
  data.projects
    ? `
<div class="section-title">Projects</div>
<ul>${data.projects}</ul>
`
    : ""
}

${
  data.education
    ? `
<div class="section-title">Education</div>
<p>${data.education}</p>
`
    : ""
}

${
  data.certifications
    ? `
<div class="section-title">Certifications</div>
<ul>${data.certifications}</ul>
`
    : ""
}

${data.custom}

</body>
</html>
`;

/* ===============================
TEMPLATE 3
=============================== */
const template3 = (data) => `
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {
  font-family: Arial, sans-serif;
  background-color: white;
  color: #000;
  margin: 0;
  padding: 25px;
}

h1 {
  color: #000;
  text-align: center;
  margin: 0 0 15px 0;
}

h3 {
  color: #000;
  margin-top: 20px;
  margin-bottom: 10px;
  border-bottom: 1px solid #333;
  padding-bottom: 5px;
}

p {
  color: #000;
  margin: 0 0 10px 0;
}

ul {
  color: #000;
  margin: 5px 0 10px 20px;
  padding: 0;
}

li {
  color: #000;
  margin-bottom: 5px;
}

/* Cloud character animation */
.cloud-char {
  display: inline-block;
  animation: cloudCharacter 0.15s ease-out forwards;
}

@keyframes cloudCharacter {
  0% {
    opacity: 0;
    transform: translateY(-15px) scale(0.5);
  }
  60% {
    opacity: 1;
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
</head>
<body>

<h1>${data.name}</h1>

<p>
${(() => {
  const contactParts = [];
  if (data.address?.trim()) contactParts.push(data.address);
  if (data.phone?.trim()) contactParts.push(data.phone);
  if (data.email?.trim()) contactParts.push(data.email);
  if (data.linkedin?.trim()) contactParts.push(data.linkedin);
  return contactParts.join(' | ');
})()}
</p>

${
  data.objective
    ? `
<h3>Summary</h3>
<p>${data.objective}</p>
`
    : ""
}

${
  data.skills
    ? `
<h3>Skills</h3>
<ul>${data.skills}</ul>
`
    : ""
}

${
  data.experience
    ? `
${data.experience}
`
    : ""
}

${
  data.projects
    ? `
<h3>Projects</h3>
<ul>${data.projects}</ul>
`
    : ""
}

${
  data.education
    ? `
<h3>Education</h3>
<p>${data.education}</p>
`
    : ""
}

${
  data.certifications
    ? `
<h3>Certifications</h3>
<ul>${data.certifications}</ul>
`
    : ""
}

</body>
</html>
`;
/* ===============================
LIVE PREVIEW
=============================== */

function updatePreview() {
  // const template = document.querySelector("[name='template']:checked")?.value || "template1";
  const template = document.getElementById("template").value;

  const data = {};

  data.name = document.querySelector("[name='name']").value;
  data.email = document.querySelector("[name='email']").value;
  data.phone = document.querySelector("[name='phone']").value;
  data.linkedin = document.querySelector("[name='linkedin']").value;
  data.address = document.querySelector("[name='address']").value;

  data.objective = document.querySelector("[name='objective']").value;
  data.education = document.querySelector("[name='education']").value;

  /* SKILLS */

  const skills = document.querySelector("[name='skills']").value;

  data.skills = skills
    .split(/\r?\n/)
    .filter((s) => s.trim())
    .map((s) => {
      if (s.includes(":")) {
        const parts = s.split(":");
        const category = parts[0];
        const values = parts.slice(1).join(":");

        return `<li><strong>${category}:</strong> ${values}</li>`;
      }
      return `<li>${s}</li>`;
    })
    .join("");

  /* PROJECTS */

  const projects = document.querySelector("[name='projects']").value;
  data.projects = projects
    .split("\n")
    .filter((p) => p.trim())
    .map((p) => `<li>${p}</li>`)
    .join("");

  /* CERTIFICATIONS */

  const certs = document.querySelector("[name='certifications']").value;
  data.certifications = certs
    .split("\n")
    .filter((c) => c.trim())
    .map((c) => `<li>${c}</li>`)
    .join("");

  /* EXPERIENCE */

  const titles = document.querySelectorAll("[name='exp_title[]']");
  const durations = document.querySelectorAll("[name='exp_duration[]']");
  const points = document.querySelectorAll("[name='exp_points[]']");

  let expHTML = "";

  titles.forEach((t, i) => {
    // Get trimmed values
    const titleTrimmed = t.value.trim();
    const durationTrimmed = durations[i].value.trim();
    const pointsTrimmed = points[i].value.trim();

    // Skip completely empty entries
    if (!titleTrimmed && !durationTrimmed && !pointsTrimmed) return;

    // Build points list
    const pts = pointsTrimmed
      .split(/\r?\n/)
      .filter((p) => p.trim())
      .map((p) => `<li>${p}</li>`)
      .join("");

    // Only render job-header if title OR duration has actual content
    if (titleTrimmed || durationTrimmed) {
      expHTML += `
<div class="job-header">
<span>${titleTrimmed}</span>
<span>${durationTrimmed}</span>
</div>`;
    }
    
    // Only render bullet points if they exist
    if (pts) {
      expHTML += `
<ul>${pts}</ul>
`;
    }
  });

  /* ADD EXPERIENCE HEADING ONLY IF EXPERIENCE EXISTS */

  if (expHTML.trim()) {
    if (template === "template2") {
      expHTML = `
<div class="section-title">Experience</div>
${expHTML}
`;
    } else if (template === "template1") {
      expHTML = `
<div class="section">
<h3>Experience</h3>
${expHTML}
</div>
`;
    } else if (template === "template3") {
      // For professional template, just pass the experience content
      // The template will add the heading
      expHTML = `
<h3>Experience</h3>
${expHTML}
`;
    }
  }

  data.experience = expHTML;

  /* CUSTOM */

  const customTitles = document.querySelectorAll("[name='section_title[]']");
  const customPoints = document.querySelectorAll("[name='section_points[]']");

  let customHTML = "";

  customTitles.forEach((t, i) => {
    if (!t.value.trim()) return;

    const pts = customPoints[i].value
      .split("\n")
      .filter((p) => p.trim())
      .map((p) => `<li>${p}</li>`)
      .join("");

    customHTML += `
<div class="section-title">${t.value}</div>
<ul>${pts}</ul>
`;
  });

  data.custom = customHTML;

  /* TEMPLATE SWITCH */

  let html = "";

  if (template === "template1") {
    html = template1(data);
  } else if (template === "template2") {
    html = template2(data);
  } else {
    html = template3(data);
  }

  /* RENDER PREVIEW */

  const preview = document.getElementById("preview-box");

  if (preview.tagName === "IFRAME") {
    preview.srcdoc = html;
  } else {
    preview.innerHTML = html;
  }
}
