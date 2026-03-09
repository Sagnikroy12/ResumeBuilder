import json
import re
from fpdf import FPDF


class ResumePDF(FPDF):

    def header_section(self, data):
        self.set_font("Times", "B", 20)
        self.cell(0, 10, data["Name"], ln=True, align="C")

        self.set_font("Times", size=11)
        contact = f"{data['Address']}\n{data['Phone']} | {data['Email']}\n{data['LinkedIn']}"
        self.multi_cell(0, 8, contact, align="C")

        self.ln(5)

    def add_section(self, title, content):
        if not content:
            return

        # Section Title
        self.set_font("Times", "B", 14)
        self.cell(0, 10, title, ln=True)

        self.set_font("Times", size=12)

        # Normalize different bullet characters
        bullet_patterns = ["\uf0b7","","•","●","▪","◦","–","—","-"]

        for bullet in bullet_patterns:
            content = content.replace(bullet, "\n")

        # Replace multiple spaces with newline
        content = re.sub(r"\s{2,}", "\n", content)

        # Split into lines
        items = [line.strip() for line in content.split("\n") if line.strip()]

        # Print bullet points
        for item in items:
            self.cell(8)
            self.multi_cell(0, 8, f"• {item}")

        self.ln(2)


def collect_user_input():
    print("\nEnter your resume details:\n")

    return {
        "Name": input("Name: "),
        "Address": input("Address: "),
        "Phone": input("Phone: "),
        "Email": input("Email: "),
        "LinkedIn": input("LinkedIn: "),
        "Objective": input("Career Objective: "),
        "Experience": input("Work Experience: "),
        "Projects": input("Projects: "),
        "Education": input("Education: "),
        "Skills": input("Skills: "),
        "Certifications": input("Certifications: ")
    }


def save_json(data, filename="resume.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    print(f"\nData saved to {filename}")


def generate_pdf(data, filename="resume.pdf"):
    pdf = ResumePDF()

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.header_section(data)

    sections = [
        "Objective",
        "Experience",
        "Projects",
        "Education",
        "Skills",
        "Certifications"
    ]

    for section in sections:
        pdf.add_section(section, data.get(section, ""))

    pdf.output(filename)

    print(f"Resume generated successfully: {filename}")


def main():
    resume_data = collect_user_input()
    save_json(resume_data)
    generate_pdf(resume_data)


if __name__ == "__main__":
    main()