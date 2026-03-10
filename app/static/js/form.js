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

  div.innerHTML = ` <input name="section_title[]" placeholder="Section Title" oninput="updatePreview()">

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

  const expContainer = document.getElementById("experience-container");

  if (expContainer) {
    new Sortable(expContainer, {
      animation: 150,
      ghostClass: "dragging",
      onEnd: function () {
        updatePreview();
      },
    });
  }

  const sectionsContainer = document.getElementById("sections-container");

  if (sectionsContainer) {
    new Sortable(sectionsContainer, {
      animation: 200,
      ghostClass: "dragging",
      onEnd: function () {
        updatePreview();
      },
    });
  }
};

/* ===============================
LIVE PREVIEW
=============================== */

function updatePreview() {
  const name = document.querySelector("[name='name']").value;
  const email = document.querySelector("[name='email']").value;
  const phone = document.querySelector("[name='phone']").value;
  const linkedin = document.querySelector("[name='linkedin']").value;
  const address = document.querySelector("[name='address']").value;

  const objective = document.querySelector("[name='objective']").value;
  const skills = document.querySelector("[name='skills']").value;
  const projects = document.querySelector("[name='projects']").value;
  const education = document.querySelector("[name='education']").value;
  const certs = document.querySelector("[name='certifications']").value;

  const titles = document.querySelectorAll("[name='exp_title[]']");
  const durations = document.querySelectorAll("[name='exp_duration[]']");
  const points = document.querySelectorAll("[name='exp_points[]']");

  const customTitles = document.querySelectorAll("[name='section_title[]']");
  const customPoints = document.querySelectorAll("[name='section_points[]']");

  let html = `

<h2>${name}</h2>
<p>${email} | ${phone} | ${linkedin}</p>
<p>${address}</p>
`;

  const sections = document.querySelectorAll(
    "#sections-container .resume-section",
  );

  sections.forEach((section) => {
    const type = section.dataset.section;

    if (type === "objective") {
      html += `

<h3>Objective</h3>
<p>${objective}</p>
`;
    }

    if (type === "skills") {
      html += `

<h3>Skills</h3>
<ul>
${skills
  .split("\n")
  .filter((s) => s.trim() !== "")
  .map((s) => `<li>${s}</li>`)
  .join("")}
</ul>
`;
    }

    if (type === "experience") {
      if (titles.length > 0) {
        html += `<h3>Experience</h3>`;

        titles.forEach((t, i) => {
          if (t.value.trim() === "") return;

          html += `<b>${t.value}</b> (${durations[i].value})<ul>`;

          points[i].value.split("\n").forEach((p) => {
            if (p.trim() !== "") {
              html += `<li>${p}</li>`;
            }
          });

          html += `</ul>`;
        });
      }
    }

    if (type === "projects") {
      html += `


<h3>Projects</h3>
<ul>
${projects
  .split("\n")
  .filter((p) => p.trim() !== "")
  .map((p) => `<li>${p}</li>`)
  .join("")}
</ul>
`;
    }

    if (type === "education") {
      html += `


<h3>Education</h3>
<p>${education}</p>
`;
    }

    if (type === "certifications") {
      html += `


<h3>Certifications</h3>
<ul>
${certs
  .split("\n")
  .filter((c) => c.trim() !== "")
  .map((c) => `<li>${c}</li>`)
  .join("")}
</ul>
`;
    }

    if (type === "custom") {
      customTitles.forEach((t, i) => {
        if (t.value.trim() === "") return;

        html += `<h3>${t.value}</h3><ul>`;

        customPoints[i].value.split("\n").forEach((p) => {
          if (p.trim() !== "") {
            html += `<li>${p}</li>`;
          }
        });

        html += `</ul>`;
      });
    }
  });

  document.getElementById("preview-box").innerHTML = html;
}
