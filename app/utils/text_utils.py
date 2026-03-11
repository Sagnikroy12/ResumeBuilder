import re

def parse_bullets(text):
    if not text:
        return []

    # Normalize all line endings to \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split and clean lines
    bullets = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    return bullets