from google import genai
import os
import json
import openai
import anthropic
import base64

class AIService:
    @staticmethod
    def _get_gemini_client():
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: return None
        return genai.Client(api_key=api_key)

    @staticmethod
    def _get_openai_client():
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: return None
        return openai.OpenAI(api_key=api_key)

    @staticmethod
    def _get_anthropic_client():
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key: return None
        return anthropic.Anthropic(api_key=api_key)

    @staticmethod
    def _call_gemini(prompt, model='gemini-2.0-flash'):
        client = AIService._get_gemini_client()
        if not client: return None
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text.strip()

    @staticmethod
    def _call_openai(prompt, model='gpt-3.5-turbo'):
        client = AIService._get_openai_client()
        if not client: return None
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _call_anthropic(prompt, model='claude-3-haiku-20240307'):
        client = AIService._get_anthropic_client()
        if not client: return None
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    @staticmethod
    def _get_groq_client():
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key: return None
        return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    @staticmethod
    def _get_cerebras_client():
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key: return None
        return openai.OpenAI(api_key=api_key, base_url="https://api.cerebras.ai/v1")

    @staticmethod
    def _get_sambanova_client():
        api_key = os.getenv("SAMBANOVA_API_KEY")
        if not api_key: return None
        return openai.OpenAI(api_key=api_key, base_url="https://api.sambanova.ai/v1")

    @staticmethod
    def _call_groq(prompt, model='llama-3.3-70b-versatile'):
        client = AIService._get_groq_client()
        if not client: 
            print("Groq Error: API Key missing in environment")
            return None
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _call_cerebras(prompt, model='llama3.1-8b'):
        client = AIService._get_cerebras_client()
        if not client: 
            print("Cerebras Error: API Key missing in environment")
            return None
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _call_sambanova(prompt, model='Meta-Llama-3.3-70B-Instruct'):
        client = AIService._get_sambanova_client()
        if not client: 
            print("SambaNova Error: API Key missing in environment")
            return None
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _get_deepseek_client():
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key: return None
        return openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    @staticmethod
    def _call_deepseek(prompt, model='deepseek-chat'):
        client = AIService._get_deepseek_client()
        if not client: return None
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _execute_with_fallback(prompt, is_json=False):
        """Sequential fallback: Gemini -> Groq -> Cerebras -> SambaNova -> OpenAI -> Anthropic -> DeepSeek"""
        providers = [
            ('GEMINI', AIService._call_gemini),
            ('SAMBANOVA', AIService._call_sambanova),
            ('GROQ', AIService._call_groq),
            ('CEREBRAS', AIService._call_cerebras),
            ('OPENAI', AIService._call_openai),
            ('ANTHROPIC', AIService._call_anthropic),
            ('DEEPSEEK', AIService._call_deepseek)
        ]

        errors = []
        for name, func in providers:
            try:
                # Skip if key is missing (func returns None if key missing)
                print(f"Attempting with {name}...")
                result = func(prompt)
                if result:
                    print(f"\n[{name} RAW RESPONSE:]\n{result}\n" + "="*50)
                    if is_json:
                        # Basic JSON extraction
                        clean_json = result.replace('```json', '').replace('```', '').strip()
                        parsed_json = json.loads(clean_json)
                        print(f"[{name} PARSED JSON:]\n{json.dumps(parsed_json, indent=2)}\n" + "="*50)
                        return parsed_json
                    return result
                else:
                    errors.append(f"{name}: API Key missing")
            except Exception as e:
                err_msg = str(e).upper()
                print(f"{name} Error: {e}")
                
                # Categorize common errors for the user
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "RATE_LIMIT" in err_msg:
                    errors.append(f"{name}: Quota/Rate Limit")
                elif "402" in err_msg or "INSUFFICIENT" in err_msg or "BALANCE" in err_msg or "CREDIT" in err_msg:
                    errors.append(f"{name}: No Balance")
                elif "401" in err_msg or "AUTHENTICATION" in err_msg or "INVALID_KEY" in err_msg:
                    errors.append(f"{name}: Invalid Key")
                else:
                    errors.append(f"{name}: {str(e)[:30]}")
                
                # Continue to next provider
                continue
        
        error_summary = " | ".join(errors)
        if is_json:
            return {"error": f"All AI providers failed. {error_summary}"}
        return f"AI Error: All available providers exhausted. Details: {error_summary}"

    @staticmethod
    def _encode_context(text_or_dict):
        """
        Compresses and encrypts context. If it's a JSON string or dict, 
        it selectively avoids encrypting personal info and titles to prevent hallucination.
        """
        if not text_or_dict:
            return "", ""
            
        import re
        import json
        
        vowel_map = {'a': '1', 'e': '2', 'i': '3', 'o': '4', 'u': '5',
                     'A': '1', 'E': '2', 'I': '3', 'O': '4', 'U': '5'}
        
        def encode_str(s):
            if not isinstance(s, str):
                return s
            compressed = re.sub(r'\s+', ' ', s).strip()
            return "".join(vowel_map.get(c, c) for c in compressed)

        data = text_or_dict
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                pass # Not JSON, just encode the whole string
                
        if isinstance(data, dict):
            # It's a structured resume, let's selectively encode
            encoded_dict = {}
            for k, v in data.items():
                if k == 'personal':
                    encoded_dict[k] = v # Do not encode personal info
                elif k == 'experience' and isinstance(v, list):
                    encoded_dict[k] = []
                    for exp in v:
                        if isinstance(exp, dict):
                            new_exp = exp.copy()
                            if 'points' in new_exp:
                                new_exp['points'] = encode_str(new_exp['points'])
                            encoded_dict[k].append(new_exp)
                elif k in ['objective', 'skills', 'projects', 'certifications', 'education']:
                    if isinstance(v, list):
                        encoded_dict[k] = [encode_str(item.get('points', '')) if isinstance(item, dict) else encode_str(item) for item in v]
                    else:
                        encoded_dict[k] = encode_str(v)
                else:
                    encoded_dict[k] = v
                    
            instructions = (
                "DECRYPTION INSTRUCTIONS:\n"
                "The text is a JSON object where ONLY specific fields like 'objective', 'skills', 'projects', and 'points' "
                "are compressed and encrypted using a Vowel-Number cipher (1=a/A, 2=e/E, 3=i/I, 4=o/O, 5=u/U).\n"
                "Personal details, Names, Contacts, Job titles, Companies, and Durations remain UNENCRYPTED in plain text.\n"
                "Read and decrypt the encrypted fields carefully before performing any extraction or tailoring."
            )
            return json.dumps(encoded_dict, indent=2), instructions

        # Fallback to full string encoding (for raw PDF text)
        encoded = encode_str(text_or_dict)
        instructions = (
            "DECRYPTION INSTRUCTIONS:\n"
            "The context provided is compressed (extra spaces removed) and encrypted using a Vowel-Number cipher.\n"
            "To decrypt, replace numbers back to vowels: 1=a/A, 2=e/E, 3=i/I, 4=o/O, 5=u/U.\n"
            "Read and decrypt the context carefully before performing any extraction or tailoring."
        )
        return encoded, instructions

    @staticmethod
    def get_suggestion(section, context=""):
        prompt = f"Act as a professional resume writer. Provide high-quality, ATS-friendly content for the '{section}' section of a resume. "
        if context:
            encoded_context, decode_instructions = AIService._encode_context(context)
            prompt += f"{decode_instructions}\nEncoded Context: '{encoded_context}'.\n\nPlease enhance and expand upon the decoded context to make it professional and impactful. "
        else:
            prompt += "Provide a general professional example. "
        prompt += "Return ONLY the suggested content text, no preamble, no quotes, and no extra formatting."
        return AIService._execute_with_fallback(prompt)

    @staticmethod
    def parse_resume(file_content):
        encoded_content, decode_instructions = AIService._encode_context(file_content)
        prompt = f"""
        Act as an ATS parser. Extract key information from the following resume text and return it as a structured JSON object.
        
        {decode_instructions}
        
        CRITICAL INSTRUCTIONS for parsing:
        1. All output MUST be in plain English. DO NOT output any encrypted text.
        2. Extract the candidate's Name, Email, or LinkedIn URL from the DECRYPTED text exactly as they appear.
        3. Extract Job Titles, Company Names, Locations, and Durations from the DECRYPTED text.
        4. For 'skills', group them into logical categories (e.g., 'Automation & Testing', 'Languages', 'DevOps & Tools', 'Methodologies'). Format each category on a new line as 'Category: Skill 1, Skill 2'. Do NOT use a single long list of bullet points.
        
        JSON Structure MUST be exactly like this:
        {{
            "personal": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "+91 9876543210",
                "address": "City, Country",
                "linkedin": "linkedin.com/in/username"
            }},
            "objective": "Professional summary...",
            "skills": "Category 1: Skill A, Skill B\\nCategory 2: Skill C, Skill D",
            "education": "Brief education history...",
            "experience": [
                {{
                    "title": "Job Title",
                    "duration": "Jan 2020 - Present",
                    "points": "Point 1\\nPoint 2"
                }}
            ],
            "projects": "Project 1: Point 1\\nProject 2: Point 2",
            "certifications": "Cert 1\\nCert 2"
        }}
        
        Important:
        - Return 'skills', 'projects', and 'certifications' ONLY as multiline strings (a single string with \\n separators format). DO NOT return arrays for these.
        - 'experience' MUST be an array of objects.
        - Normalize the metadata into the 'personal' object.
        
        Encoded Resume Text:
        {encoded_content}
        
        Return ONLY the raw JSON object. No other text.
        """
        return AIService._execute_with_fallback(prompt, is_json=True)

    @staticmethod
    def tailor_resume(file_content, job_description):
        encoded_resume, resume_instructions = AIService._encode_context(file_content)
        encoded_jd, _ = AIService._encode_context(job_description)
        
        prompt = f"""
        Act as an expert career coach. Your task is to aggressively TAILOR the following resume to perfectly match the provided job description.
        You must highlight relevant skills, adjust the objective, and rewrite experience points to align with the job requirements.
        
        {resume_instructions}
        
        CRITICAL INSTRUCTIONS for tailoring:
        0. ALL output in the JSON MUST be plain English. NEVER output encrypted/vowel-replaced strings. Decrypt everything first.
        1. Keep the candidate's DECRYPTED Name, Email, Phone, Address, and LinkedIn EXACTLY the same as in the original DECRYPTED resume.
        2. Keep the DECRYPTED Job Titles, Company Names, Locations, and Durations under experience. ONLY rewrite the bullet points ("points").
        3. Keep the DECRYPTED Education history. ONLY rewrite Project and Experience bullet points.
        4. For 'skills', group them into logical categories (e.g., 'Automation & Testing', 'Languages', 'DevOps & Tools', 'Methodologies'). Format each category on a new line as 'Category: Skill 1, Skill 2'. Do NOT use a single long list of bullet points.
        5. Ensure the tailored content is short, concise, and punchy for quick attraction. Maintain a professional tone while being impactful.
        
        Extract and adapt information into this EXACT structured JSON object:
        
        {{
            "personal": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "+91 9876543210",
                "address": "City, Country",
                "linkedin": "linkedin.com/in/username"
            }},
            "objective": "A highly tailored professional summary matching the JD...",
            "skills": "Category 1: Skill A, Skill B\\nCategory 2: Skill C, Skill D",
            "education": "Brief education history...",
            "experience": [
                {{
                    "title": "Job Title",
                    "duration": "Jan 2020 - Present",
                    "points": "Tailored Point 1\\nTailored Point 2\\n(Rewrite to match JD)"
                }}
            ],
            "projects": "Tailored Project 1: Point 1\\nTailored Project 2",
            "certifications": "Cert 1\\nCert 2"
        }}
        
        Important:
        - Return 'skills', 'projects', and 'certifications' ONLY as multiline strings (a single string with \\n separators format). DO NOT return arrays for these.
        - 'experience' MUST be an array of objects.
        
        Encoded Resume Text:
        {encoded_resume}
        
        Encoded Job Description:
        {encoded_jd}
        
        Return ONLY the raw JSON object. No other text.
        """
        return AIService._execute_with_fallback(prompt, is_json=True)
