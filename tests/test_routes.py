"""
Tests for resume routes and functionality
"""

import pytest
from app.routes.resume_routes import to_li


class TestResumeRoutes:
    """Test cases for resume routes"""
    
    def test_index_get_request(self, client):
        """Test GET request to index page"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_index_post_request_with_basic_data(self, client):
        """Test POST request with basic resume data"""
        data = {
            "template": "template1",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890",
            "address": "123 Main St",
            "linkedin": "https://linkedin.com/in/johndoe"
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_with_experience(self, client):
        """Test POST request with experience data"""
        data = {
            "template": "template1",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "987-654-3210",
            "address": "456 Oak St",
            "linkedin": "https://linkedin.com/in/janedoe",
            "exp_title[]": ["Software Engineer", "Junior Developer"],
            "exp_duration[]": ["2020-2023", "2018-2020"],
            "exp_points[]": ["Developed features\nFixed bugs", "Learned technologies"]
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_with_skills(self, client):
        """Test POST request with skills data"""
        data = {
            "template": "template1",
            "name": "John Doe",
            "email": "john@example.com",
            "skills": "Python\nJavaScript\nFlask\nReactJS",
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_with_projects(self, client):
        """Test POST request with projects data"""
        data = {
            "template": "template1",
            "name": "John Doe",
            "email": "john@example.com",
            "projects": "Project 1: Built a web app\nProject 2: Mobile app",
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_with_certifications(self, client):
        """Test POST request with certifications"""
        data = {
            "template": "template1",
            "name": "John Doe",
            "email": "john@example.com",
            "certifications": "AWS Certified\nGoogle Cloud",
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_with_education(self, client):
        """Test POST request with education data"""
        data = {
            "template": "template1",
            "name": "John Doe",
            "email": "john@example.com",
            "education": "BS in Computer Science - University of XYZ",
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_with_objective(self, client):
        """Test POST request with objective"""
        data = {
            "template": "template1",
            "name": "John Doe",
            "email": "john@example.com",
            "objective": "Seeking a role in software development",
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_with_custom_sections(self, client):
        """Test POST request with custom sections"""
        data = {
            "template": "template1",
            "name": "John Doe",
            "email": "john@example.com",
            "section_title[]": ["Awards", "Publications"],
            "section_points[]": ["Award 1\nAward 2", "Article 1\nArticle 2"]
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_all_templates(self, client):
        """Test POST request with all template options"""
        templates = ["template1", "template2", "template3"]
        for template in templates:
            data = {
                "template": template,
                "name": "Test User",
                "email": "test@example.com",
            }
            response = client.post("/", data=data)
            assert response.status_code == 200
    
    def test_index_post_empty_data(self, client):
        """Test POST request with minimal data"""
        data = {}
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_index_post_with_special_characters(self, client):
        """Test POST request with special characters in data"""
        data = {
            "template": "template1",
            "name": "José García García",
            "email": "jose@example.com",
            "objective": "Specializing in PYTHON & C++",
        }
        response = client.post("/", data=data)
        assert response.status_code == 200
    
    def test_pdf_generation_for_all_templates(self, client):
        """Test PDF generation for all templates"""
        templates = ["template1", "template2", "template3"]
        for template in templates:
            data = {
                "template": template,
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "address": "123 Main St",
                "linkedin": "https://linkedin.com/in/johndoe",
                "objective": "Seeking a role",
                "skills": "Python\nJavaScript",
                "exp_title[]": ["Developer"],
                "exp_duration[]": ["2020-2023"],
                "exp_points[]": ["Built features"],
            }
            response = client.post("/", data=data)
            assert response.status_code == 200

class TestToLi:
    """Test cases for to_li helper function"""
    
    def test_to_li_simple_list(self):
        """Test to_li with simple list"""
        items = ["Python", "JavaScript", "Flask"]
        result = to_li(items)
        assert "<li>Python</li>" in result
        assert "<li>JavaScript</li>" in result
        assert "<li>Flask</li>" in result
    
    def test_to_li_with_colons(self):
        """Test to_li with items containing colons"""
        items = ["Languages: Python, JavaScript", "Tools: Git, Docker"]
        result = to_li(items)
        assert "<strong>Languages:</strong>" in result
        assert "Python, JavaScript" in result
        assert "<strong>Tools:</strong>" in result
        assert "Git, Docker" in result
    
    def test_to_li_mixed_items(self):
        """Test to_li with mixed items (with and without colons)"""
        items = ["Python", "Languages: Python, JavaScript", "Flask"]
        result = to_li(items)
        assert "<li>Python</li>" in result
        assert "<strong>Languages:</strong>" in result
        assert "<li>Flask</li>" in result
    
    def test_to_li_empty_list(self):
        """Test to_li with empty list"""
        items = []
        result = to_li(items)
        assert result == ""
    
    def test_to_li_multiple_colons(self):
        """Test to_li with items containing multiple colons"""
        items = ["URL: https://example.com:8080/path"]
        result = to_li(items)
        assert "<strong>URL:</strong>" in result
        assert "https://example.com:8080/path" in result
