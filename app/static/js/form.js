/* ===============================
DYNAMIC ADD / REMOVE BLOCKS
=============================== */

function addExperience() {
  const container = document.getElementById("experience-container");

  const block = document.createElement("div");
  block.className = "exp-block";

  block.innerHTML = `
    Title <input name="exp_title[]" oninput="updatePreview()">
    Duration <input name="exp_duration[]" oninput="updatePreview()">
    Responsibilities
    <textarea name="exp_points[]" oninput="updatePreview()"></textarea>
    <button type="button" onclick="removeBlock(this)">Remove</button>
  `;

  container.appendChild(block);
  updatePreview();

  // Add AI button for experience if ai_enabled is somehow detected (or just always for now if we want)
  if (typeof aiEnabled !== 'undefined' && aiEnabled) {
    const aiBtn = document.createElement("button");
    aiBtn.type = "button";
    aiBtn.className = "btn-ai";
    aiBtn.innerHTML = "✨ AI Suggest Content";
    aiBtn.onclick = function() {
        const textarea = block.querySelector('textarea');
        const title = block.querySelector('input[name="exp_title[]"]').value;
        getAiSuggestion('experience', textarea, title);
    };
    block.appendChild(aiBtn);
  }
}

async function getAiSuggestion(section, element = null, context = "") {
    const targetElement = element || document.getElementById(section);
    const originalText = targetElement.innerText || "AI Suggest";
    
    // UI Feedback
    const btn = event.target;
    const originalBtnText = btn.innerHTML;
    btn.innerHTML = "🌀 Thinking...";
    btn.classList.add("suggesting");

    try {
        const response = await fetch('/resume/api/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ section: section, context: context })
        });
        const data = await response.json();
        
        if (data.suggestion) {
            if (targetElement.tagName === 'TEXTAREA' || targetElement.tagName === 'INPUT') {
                targetElement.value = data.suggestion;
                updatePreview();
            }
        }
    } catch (error) {
        console.error("AI Error:", error);
    } finally {
        btn.innerHTML = originalBtnText;
        btn.classList.remove("suggesting");
    }
}

function removeBlock(btn) {
  btn.parentElement.remove();
  updatePreview();
}

function addCustomSection() {
  const container = document.getElementById("custom-section-container");

  const div = document.createElement("div");
  div.classList.add("custom-section");

  div.innerHTML = `
    <input name="section_title[]" placeholder="Section Title" oninput="updatePreview()">
    <textarea name="section_points[]" placeholder="One point per line" oninput="updatePreview()"></textarea>
    <button type="button" onclick="removeBlock(this)">Remove</button>
  `;

  container.appendChild(div);
  updatePreview();
}

/* ===============================
PAGE LOAD
=============================== */

// Function to add cloud character animation to text
function addCloudAnimation(text) {
  if (!text) return '';
  return text
    .split('')
    .map((char, index) => {
      return `<span class="cloud-char" style="animation-delay: ${index * 0.05}s">${char}</span>`;
    })
    .join('');
}

window.onload = function () {
  addExperience();
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
