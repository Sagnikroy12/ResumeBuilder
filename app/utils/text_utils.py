import re

def parse_bullets(text):
    if not text:
        return []

    return [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]