"""
Tests for PDF service
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.pdf_service import generate_pdf


class TestPdfService:
    """Test cases for PDF generation service"""
    
    def test_generate_pdf_basic(self, app):
        """Test basic PDF generation"""
        with app.app_context():
            with patch('app.services.pdf_service.pdfkit.from_string') as mock_pdf:
                mock_pdf.return_value = b'PDF_CONTENT'
                
                data = {
                    "personal": {
                        "name": "John Doe",
                        "email": "john@example.com"
                    }
                }
                
                result = generate_pdf(data, "resume_template.html")
                
                assert result == b'PDF_CONTENT'
                assert mock_pdf.called
    
    def test_generate_pdf_with_full_data(self, app):
        """Test PDF generation with full resume data"""
        with app.app_context():
            with patch('app.services.pdf_service.pdfkit.from_string') as mock_pdf:
                mock_pdf.return_value = b'PDF_CONTENT'
                
                data = {
                    "personal": {
                        "name": "Jane Doe",
                        "email": "jane@example.com",
                        "phone": "123-456-7890",
                        "address": "123 Main St",
                        "linkedin": "https://linkedin.com/in/janedoe"
                    },
                    "objective": "Seeking a role in software development",
                    "skills": "<li>Python</li><li>JavaScript</li>",
                    "experience": [
                        {
                            "title": "Senior Developer",
                            "duration": "2020-2023",
                            "points": ["Developed features", "Led team"]
                        }
                    ],
                    "projects": "<li>Project 1</li>",
                    "education": "BS in Computer Science",
                    "certifications": "<li>AWS Certified</li>",
                    "custom_sections": []
                }
                
                result = generate_pdf(data, "resume_template.html")
                
                assert result == b'PDF_CONTENT'
                assert mock_pdf.called
    
    def test_generate_pdf_with_different_templates(self, app):
        """Test PDF generation with different templates"""
        with app.app_context():
            with patch('app.services.pdf_service.pdfkit.from_string') as mock_pdf:
                mock_pdf.return_value = b'PDF_CONTENT'
                
                templates = [
                    "resume_template.html",
                    "resume_template2.html",
                    "resume_template3.html"
                ]
                
                data = {
                    "personal": {
                        "name": "Test User",
                        "email": "test@example.com"
                    }
                }
                
                for template in templates:
                    result = generate_pdf(data, template)
                    assert result == b'PDF_CONTENT'
    
    def test_generate_pdf_special_characters(self, app):
        """Test PDF generation with special characters"""
        with app.app_context():
            with patch('app.services.pdf_service.pdfkit.from_string') as mock_pdf:
                mock_pdf.return_value = b'PDF_CONTENT'
                
                data = {
                    "personal": {
                        "name": "José García Müller",
                        "email": "jose@example.com",
                        "phone": "123-456-7890"
                    }
                }
                
                result = generate_pdf(data, "resume_template.html")
                assert result == b'PDF_CONTENT'
