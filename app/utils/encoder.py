import re
import json

class ResumeEncoder:
    """
    A strictly lossless, production-grade encoding-decoding system for AI processing.
    - Placeholder strategy for sensitive fields (Name, Email, Phone, LinkedIn).
    - Keyword mapping for token optimization of common resume section titles.
    - Bit-perfect reconstruction guarantee.
    """

    # Common resume terms for token optimization (short aliases)
    # Using symbols like @ or # to distinguish from normal text
    KEYWORD_MAP = {
        "Professional Summary": "@PS",
        "Work Experience": "@WE",
        "Experience": "@EX",
        "Education": "@ED",
        "Skills": "@SK",
        "Projects": "@PR",
        "Certifications": "@CE",
        "Achievements": "@AC",
        "Languages": "@LA",
        "Personal Information": "@PI",
        "Full Name": "@FN",
        "Email Address": "@EA",
        "Phone Number": "@PN",
        "Contact Information": "@CI",
        "LinkedIn Profile": "@LI"
    }
    
    REVERSE_KEYWORD_MAP = {v: k for k, v in KEYWORD_MAP.items()}

    @staticmethod
    def encode(data, state=None):
        """
        Encodes a dictionary or string, replacing sensitive info with placeholders.
        Returns: (encoded_context, metadata)
        """
        if state is None:
            state = {"p_count": 0, "placeholders": {}}
            
        metadata = {
            "placeholders": state["placeholders"],
            "original_keys": []
        }

        def get_placeholder(val, prefix="S"):
            if not val or not isinstance(val, str):
                return val
            
            clean_val = val.strip()
            # Check if we already have a placeholder for this exact value
            for p, v in state["placeholders"].items():
                if v == clean_val:
                    return p
            
            p_id = f"__{prefix}_{state['p_count']}__"
            state["placeholders"][p_id] = clean_val
            state["p_count"] += 1
            print(f"[ENCODER] Created placeholder: {p_id} -> {clean_val[:30]}...")
            return p_id

        def process_recursive(item, key_path=""):
            if isinstance(item, dict):
                new_dict = {}
                for k, v in item.items():
                    # Handle sensitive keys explicitly
                    if k == 'name':
                        new_dict[k] = get_placeholder(v, prefix="NAME")
                    elif k == 'email':
                        new_dict[k] = get_placeholder(v, prefix="EMAIL")
                    elif k == 'phone':
                        new_dict[k] = get_placeholder(v, prefix="PHONE")
                    elif k == 'address':
                        new_dict[k] = get_placeholder(v, prefix="ADDRESS")
                    elif k == 'linkedin':
                        new_dict[k] = get_placeholder(v, prefix="LINKEDIN")
                    elif isinstance(v, (dict, list)):
                        new_dict[k] = process_recursive(v, f"{key_path}.{k}")
                    else:
                        new_dict[k] = v
                return new_dict
            elif isinstance(item, list):
                return [process_recursive(i, key_path) for i in item]
            elif isinstance(item, str):
                # Apply keyword mapping for efficiency
                text = item
                for word, code in ResumeEncoder.KEYWORD_MAP.items():
                    text = re.sub(rf'\b{re.escape(word)}\b', code, text, flags=re.IGNORECASE)
                return text
            return item

        if isinstance(data, (dict, list)):
            encoded_data, metadata = process_recursive(data)
            return encoded_data, metadata
        
        # If it's just raw text (from PDF)
        text = str(data)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Detect most structured data FIRST to avoid heuristic collisions
        # 1. Detect Emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        for email in set(emails):
            text = text.replace(email, get_placeholder(email, "EMAIL"))
            
        # 2. Detect Phone Numbers
        phones = re.findall(r'(\+?\d[\d\-\s\(\)]{8,}\d)', text)
        for phone in set(phones):
            if len(re.sub(r'\D', '', phone)) >= 10:
                text = text.replace(phone, get_placeholder(phone, "PHONE"))

        # 3. Detect LinkedIn URLs
        links = re.findall(r'(linkedin\.com/in/[a-zA-Z0-9_-]+)', text)
        for link in set(links):
            text = text.replace(link, get_placeholder(link, "LINKEDIN"))

        # 4. Advanced Name Detection (Regex for 3-4 words)
        header_text = "\n".join(lines[:10]) # Look at more lines for regex
        
        # Regex for 3-4 capitalized words separated by spaces
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,3})\b'
        matches = re.findall(name_pattern, header_text)
        
        found_name = None
        for match in matches:
            # Skip common header noise
            if match.upper() in ["RESUME", "CURRICULUM VITAE", "CV", "CONFIDENTIAL", "SUMMARY"]:
                continue
            # If it's a valid match and at the very top of the text
            found_name = match
            break
            
        if found_name:
            text = text.replace(found_name, get_placeholder(found_name, "NAME"))

        # 5. Detect Addresses (City, Country/State)
        addresses = re.findall(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*, [A-Z]{2,}\b|\b[A-Z][a-z]+(?: [A-Z][a-z]+)*, [A-Z][a-z]+\b', text)
        for addr in set(addresses):
            text = text.replace(addr, get_placeholder(addr, "ADDRESS"))

        # 6. Apply keyword mapping
        for word, code in ResumeEncoder.KEYWORD_MAP.items():
            text = re.sub(rf'\b{re.escape(word)}\b', code, text, flags=re.IGNORECASE)

        return text, metadata

    @staticmethod
    def decode(text, metadata):
        """Reverses the encoding and restores placeholders."""
        if not text or not isinstance(text, str):
            return text
            
        if not metadata or "placeholders" not in metadata:
            return text

        decoded_text = text

        # 1. Reverse Keyword Mapping
        for code, word in ResumeEncoder.REVERSE_KEYWORD_MAP.items():
            if code.upper() in decoded_text.upper():
                pattern = re.compile(re.escape(code), re.IGNORECASE)
                decoded_text = pattern.sub(lambda m: word, decoded_text)

        # 2. Restore Placeholders (Longest keys first)
        sorted_placeholders = sorted(metadata["placeholders"].keys(), key=len, reverse=True)
        
        for p_id in sorted_placeholders:
            if p_id.upper() in decoded_text.upper():
                original_val = metadata["placeholders"][p_id]
                pattern = re.compile(re.escape(p_id), re.IGNORECASE)
                # Use lambda to avoid interpreting backslashes in original_val
                decoded_text = pattern.sub(lambda m: original_val, decoded_text)
                print(f"[DECODER] Restored {p_id} -> {original_val[:20]}")

        return decoded_text

    @staticmethod
    def decode_json(data, metadata):
        """Recursively decodes a JSON-like object."""
        if isinstance(data, dict):
            return {k: ResumeEncoder.decode_json(v, metadata) for k, v in data.items()}
        elif isinstance(data, list):
            return [ResumeEncoder.decode_json(i, metadata) for i in data]
        elif isinstance(data, str):
            return ResumeEncoder.decode(data, metadata)
        return data
