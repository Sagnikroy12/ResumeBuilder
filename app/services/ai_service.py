class AIService:
    @staticmethod
    def get_suggestion(section, context=""):
        suggestions = {
            "objective": "Results-driven professional with a proven track record of success in [industry]. Strong leadership skills and expertise in [key skill]. Seeking to leverage my background to drive growth at [Company Name].",
            "skills": "Python, JavaScript, SQL, Flask, Git, Docker, Agile Methodology",
            "projects": "Portfolio Website - Built a responsive personal website using HTML, CSS, and JS.\nE-commerce Bot - Automated purchase flow for high-demand items using Python.",
            "experience": f"Developed and maintained scalable web applications for {context or 'a leading tech firm'}.\nCollaborated with cross-functional teams to deliver high-quality software solutions.\nOptimized database queries, resulting in a 20% improvement in application performance."
        }
        return suggestions.get(section, "Click to generate suggestions...")

    @staticmethod
    def parse_resume(file_content):
        # Mock parsing logic
        return {
            "personal": {"name": "Extracted Name", "email": "extracted@email.com"},
            "skills": "Extracted Skill 1, Extracted Skill 2",
            "experience": [{"title": "Extracted Role", "duration": "2020-Present", "points": "Did things."}]
        }

    @staticmethod
    def tailor_resume(file_content, job_description):
        # Mock tailoring logic
        return f"Tailored resume content based on JD: {job_description[:50]}..."
