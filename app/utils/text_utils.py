import re

# def parse_bullets(text):

#     if not text:
#         return []

#     text = re.sub(r'\s*[-•●▪◦]\s*', ' ', text)

#     text = text.replace("\n"," ")

#     sentences = re.split(r'\.\s+', text)

#     bullets = []

#     for s in sentences:

#         s = s.strip()

#         if s:

#             if not s.endswith("."):
#                 s += "."

#             bullets.append(s)

#     return bullets

def parse_bullets(text):
    if not text:
        return []

    return [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]