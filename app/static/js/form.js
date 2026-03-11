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
}

h1{
text-align:center;
margin-bottom:4px;
}

.contact{
text-align:center;
font-weight:bold;
margin-top:4px;
}

.section{
margin-top:10px;
}

h3{
margin-bottom:4px;
font-size:22px;
border-bottom:1px solid #000;
padding-bottom:2px;
}

ul{
margin:4px 0 8px 25px;
padding:0;
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

<h1>${data.name}</h1>

<hr>

<div class="contact">
${data.address} | ${data.phone} | ${data.email}<br>
${data.linkedin}
</div>

<hr>

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
margin:40px;
color:#222;
line-height:1.25;
font-size:16px;
}

.header-table{
width:100%;
margin-bottom:20px;
}

.name{
font-size:32px;
font-weight:800;
}

.contact-block{
text-align:right;
font-weight:600;
font-size:14px;
}

.section-title{
font-size:18px;
font-weight:700;
margin:20px 0 8px 0;
border-bottom:1.5px solid #000;
padding-bottom:2px;
text-transform:uppercase;
}

ul{
margin:4px 0 8px 20px;
}

.job-header{
display:flex;
justify-content:space-between;
font-weight:bold;
margin-bottom:4px;
}

.skill-list{
column-count:2;
column-gap:25px;
}

</style>

</head>

<body>

<table class="header-table">
<tr>

<td>
<div class="name">${data.name}</div>
</td>

<td class="contact-block">
${data.address}<br>
${data.phone}<br>
${data.email}<br>
${data.linkedin}
</td>

</tr>
</table>

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
    if (!t.value.trim()) return;

    const pts = points[i].value
      .split(/\r?\n/)
      .filter((p) => p.trim())
      .map((p) => `<li>${p}</li>`)
      .join("");

    expHTML += `
<div class="job-header">
<span>${t.value}</span>
<span>${durations[i].value}</span>
</div>
<ul>${pts}</ul>
`;
  });

  /* ADD EXPERIENCE HEADING ONLY IF EXPERIENCE EXISTS */

  if (expHTML.trim()) {
    if (template === "modern") {
      expHTML = `
<div class="section-title">Experience</div>
${expHTML}
`;
    } else {
      expHTML = `
<div class="section">
<h3>Experience</h3>
${expHTML}
</div>
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

  if (template === "template2") {
    html = template2(data);
  } else {
    html = template1(data);
  }

  /* RENDER PREVIEW */

  const preview = document.getElementById("preview-box");

  if (preview.tagName === "IFRAME") {
    preview.srcdoc = html;
  } else {
    preview.innerHTML = html;
  }
}
