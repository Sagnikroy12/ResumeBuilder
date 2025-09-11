from flask import Flask, render_template, request, redirect, send_file
import json
from fpdf import FPDF

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        resume_data = {
            "Name": request.form['name'],
            "Address": request.form['address'],
            "Phone": request.form['phone'],
            "Email": request.form['email'],
            "LinkedIn": request.form['linkedin'],
            "Objective": request.form['objective'],
            "Education": request.form['education'],
            "Skills": request.form['skills'],
            "Experience": request.form['experience'],
            "Projects": request.form['projects'],
            "Certifications": request.form['certifications'],
        }
        with open("resume.json", "w") as json_file:
            json.dump(resume_data, json_file, indent=4)
        return redirect('/download_pdf')  # Change this line
    return render_template('form.html')

@app.route('/success')
def success():
    return "Resume data has been saved!"

def clean_text(text):
    if not isinstance(text, str):
        return str(text)
    return text.encode('latin-1', 'replace').decode('latin-1')

@app.route('/download_pdf')
def download_pdf():
    with open("resume.json", "r") as json_file:
        data = json.load(json_file)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", 'B', size=18)
    pdf.cell(0, 10, txt=f"{data['Name']}", ln=True, align='C')
    pdf.set_font("Times", 'B', size=12)
    pdf.cell(0, 10, txt=f"{data['Address']}      {data['Phone']}      {data['Email']}", ln=True, align='C')
    pdf.cell(0, 10, txt=f"{data['LinkedIn']}", ln=True, align='C')

    for key in ["Objective", "Experience", "Projects", "Education", "Skills", "Certifications"]:
        value = data.get(key, "")
        pdf.set_font("Times", 'B', size=12)
        pdf.cell(0, 10, txt=f"{key}:", ln=True, align='L')
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, txt=clean_text(str(value)))

    pdf.output("resume.pdf")
    return send_file("resume.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)