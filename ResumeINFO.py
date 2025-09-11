import json
from fpdf import FPDF

name =input("Enter your name: ")
address =input("Enter your address: ")
phone =input("Enter your phone number: ")
email =input("Enter your email: ")
linkedIn =input("Enter your LinkedIn profile URL: ")
objective =input("Enter your career objective: ")
education =input("Enter your educational qualifications: ")
skills =input("Enter your skills: ")
experience =input("Enter your work experience: ")
projects =input("Enter your projects: ")
certifications =input("Enter your certifications: ")

resume_data = {
    "Name": name,
    "Address": address,
    "Phone": phone,
    "Email": email,
    "LinkedIn": linkedIn,
    "Objective": objective,
    "Experience": experience,
    "Projects": projects,
    "Education": education,
    "Skills": skills,
    "Certifications": certifications,
}

with open("resume.json", "w") as json_file:
    json.dump(resume_data, json_file, indent=4)

print("Resume data has been saved to resume.json")

with open("resume.json", "r") as json_file:
    data = json.load(json_file)

pdf = FPDF()
pdf.add_page()

pdf.set_font("Times", 'B', size=18)
pdf.cell(0, 10, txt=f"{name}", ln=True, align='C')
pdf.set_font("Times", 'B', size=12)
pdf.cell(0, 10, txt=f"{resume_data['Address']}      {resume_data['Phone']}      {resume_data['Email']}", ln=True, align='C')
pdf.cell(0, 10, txt=f"{resume_data['LinkedIn']}", ln=True, align='C')


for key, value in data.items():
    pdf.set_font("Times", 'B', size=12)
    if(key in ["Name", "Address", "Phone", "Email", "LinkedIn"]):
        continue
    else:
        pdf.set_font("Times", 'B', size=16)
        pdf.cell(0, 10, txt=f"{key}:", ln=True, align='L')
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=f"{value}", align='JUSTIFY')

pdf.output("resume.pdf")

print("Resume has been generated as resume.pdf")