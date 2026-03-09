# import json
# import re
# from fpdf import FPDF


# class ResumePDF(FPDF):

#     def header_section(self, data):
#         self.set_font("Times", "B", 20)
#         self.cell(0, 10, data["Name"], ln=True, align="C")

#         self.set_font("Times", size=11)
#         contact = f"{data['Address']}\n{data['Phone']} | {data['Email']}\n{data['LinkedIn']}"
#         self.multi_cell(0, 8, contact, align="C")

#         self.ln(5)

#     def add_section(self, title, content):
#         if not content:
#             return

#         # Section Title
#         self.set_font("Times", "B", 14)
#         self.cell(0, 10, title, ln=True)

#         self.set_font("Times", size=12)

#         # Normalize different bullet characters
#         bullet_patterns = ["\uf0b7","","•","●","▪","◦","–","—","-"]

#         for bullet in bullet_patterns:
#             content = content.replace(bullet, "\n")

#         # Replace multiple spaces with newline
#         content = re.sub(r"\s{2,}", "\n", content)

#         # Split into lines
#         items = [line.strip() for line in content.split("\n") if line.strip()]

#         # Print bullet points
#         for item in items:
#             self.cell(8)
#             self.multi_cell(0, 8, f"• {item}")

#         self.ln(2)


# def collect_user_input():
#     print("\nEnter your resume details:\n")

#     return {
#         "Name": input("Name: "),
#         "Address": input("Address: "),
#         "Phone": input("Phone: "),
#         "Email": input("Email: "),
#         "LinkedIn": input("LinkedIn: "),
#         "Objective": input("Career Objective: "),
#         "Experience": input("Work Experience: "),
#         "Projects": input("Projects: "),
#         "Education": input("Education: "),
#         "Skills": input("Skills: "),
#         "Certifications": input("Certifications: ")
#     }


# def save_json(data, filename="resume.json"):
#     with open(filename, "w") as file:
#         json.dump(data, file, indent=4)

#     print(f"\nData saved to {filename}")


# def generate_pdf(data, filename="resume.pdf"):
#     pdf = ResumePDF()

#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.add_page()

#     pdf.header_section(data)

#     sections = [
#         "Objective",
#         "Experience",
#         "Projects",
#         "Education",
#         "Skills",
#         "Certifications"
#     ]

#     for section in sections:
#         pdf.add_section(section, data.get(section, ""))

#     pdf.output(filename)

#     print(f"Resume generated successfully: {filename}")


# def main():
#     resume_data = collect_user_input()
#     save_json(resume_data)
#     generate_pdf(resume_data)


# if __name__ == "__main__":
#     main()

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

        self.set_font("Times", "B", 14)
        self.cell(0, 10, title, ln=True)

        self.set_font("Times", size=12)

        bullet_patterns = ["\uf0b7", "", "•", "●", "▪", "◦", "–", "—", "-"]

        for bullet in bullet_patterns:
            content = content.replace(bullet, "\n")

        content = re.sub(r"\s{2,}", "\n", content)

        items = [line.strip() for line in content.split("\n") if line.strip()]

        for item in items:
            self.cell(8)
            self.multi_cell(0, 8, f"• {item}")

        self.ln(2)

    def add_experience(self, experiences):

        if not experiences:
            return

        self.set_font("Times", "B", 14)
        self.cell(0, 10, "Experience", ln=True)

        for exp in experiences:

            # Company + Role LEFT
            self.set_font("Times", "B", 12)
            self.cell(0, 8, f"{exp['company']} - {exp['role']}", 0, 0)

            # Duration RIGHT
            duration_width = self.get_string_width(exp["duration"])
            page_width = self.w - 20
            self.set_x(page_width - duration_width)

            self.cell(duration_width, 8, exp["duration"], ln=True)

            # Description bullets
            self.set_font("Times", size=12)

            for desc in exp["description"]:
                self.cell(8)
                self.multi_cell(0, 8, f"• {desc}")

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
        "Education": input("Education: "),
        "Skills": input("Skills: "),
        "Certifications": input("Certifications: ")
    }


def collect_experience():

    experiences = []

    print("\nEnter Work Experience (type 'done' as company name to stop)\n")

    while True:

        company = input("Company Name: ")

        if company.lower() == "done":
            break

        role = input("Designation: ")

        duration = input("Duration (e.g. Jan 2023 - Present): ")

        print("Enter responsibilities (type 'done' when finished):")

        descriptions = []

        while True:

            line = input("- ")

            if line.lower() == "done":
                break

            descriptions.append(line)

        experiences.append({
            "company": company,
            "role": role,
            "duration": duration,
            "description": descriptions
        })

    return experiences


def collect_dynamic_sections():

    sections = {}

    print("\nAdd additional sections (type 'done' when finished)\n")

    while True:

        section_name = input("Section Name: ")

        if section_name.lower() == "done":
            break

        print(f"Enter content for {section_name}: ")

        content = input()

        sections[section_name] = content

    return sections


def save_json(data, filename="resume.json"):

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

    print(f"\nData saved to {filename}")


def generate_pdf(data, filename="resume.pdf"):

    pdf = ResumePDF()

    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()

    pdf.header_section(data)

    pdf.add_section("Objective", data.get("Objective", ""))

    pdf.add_experience(data.get("Experience", []))

    pdf.add_section("Education", data.get("Education", ""))

    pdf.add_section("Skills", data.get("Skills", ""))

    pdf.add_section("Certifications", data.get("Certifications", ""))

    # Dynamic sections
    for title, content in data.get("ExtraSections", {}).items():
        pdf.add_section(title, content)

    pdf.output(filename)

    print(f"Resume generated successfully: {filename}")


def main():

    basic_data = collect_user_input()

    experiences = collect_experience()

    extra_sections = collect_dynamic_sections()

    data = {
        **basic_data,
        "Experience": experiences,
        "ExtraSections": extra_sections
    }

    save_json(data)

    generate_pdf(data)


if __name__ == "__main__":
    main()