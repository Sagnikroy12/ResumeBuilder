"""
Tests for text utilities
"""

import pytest
from app.utils.text_utils import parse_bullets


class TestParseBullets:
    """Test cases for parse_bullets utility function"""
    
    def test_parse_bullets_simple(self):
        """Test parse_bullets with simple text"""
        text = "Bullet 1\nBullet 2\nBullet 3"
        result = parse_bullets(text)
        assert result == ["Bullet 1", "Bullet 2", "Bullet 3"]
    
    def test_parse_bullets_with_windows_line_endings(self):
        """Test parse_bullets with Windows line endings"""
        text = "Bullet 1\r\nBullet 2\r\nBullet 3"
        result = parse_bullets(text)
        assert result == ["Bullet 1", "Bullet 2", "Bullet 3"]
    
    def test_parse_bullets_with_old_mac_line_endings(self):
        """Test parse_bullets with old Mac line endings"""
        text = "Bullet 1\rBullet 2\rBullet 3"
        result = parse_bullets(text)
        assert result == ["Bullet 1", "Bullet 2", "Bullet 3"]
    
    def test_parse_bullets_with_whitespace(self):
        """Test parse_bullets strips whitespace"""
        text = "  Bullet 1  \n  Bullet 2  \n  Bullet 3  "
        result = parse_bullets(text)
        assert result == ["Bullet 1", "Bullet 2", "Bullet 3"]
    
    def test_parse_bullets_with_empty_lines(self):
        """Test parse_bullets ignores empty lines"""
        text = "Bullet 1\n\nBullet 2\n\n\nBullet 3"
        result = parse_bullets(text)
        assert result == ["Bullet 1", "Bullet 2", "Bullet 3"]
    
    def test_parse_bullets_empty_string(self):
        """Test parse_bullets with empty string"""
        result = parse_bullets("")
        assert result == []
    
    def test_parse_bullets_none(self):
        """Test parse_bullets with None"""
        result = parse_bullets(None)
        assert result == []
    
    def test_parse_bullets_single_line(self):
        """Test parse_bullets with single line"""
        result = parse_bullets("Single bullet")
        assert result == ["Single bullet"]
    
    def test_parse_bullets_special_characters(self):
        """Test parse_bullets preserves special characters"""
        text = "C++ & Python\nJavaScript (ES6+)\nPHP/Laravel"
        result = parse_bullets(text)
        assert "C++ & Python" in result
        assert "JavaScript (ES6+)" in result
        assert "PHP/Laravel" in result
    
    def test_parse_bullets_unicode(self):
        """Test parse_bullets handles unicode"""
        text = "José García\n日本語\nРусский"
        result = parse_bullets(text)
        assert "José García" in result
        assert "日本語" in result
        assert "Русский" in result
