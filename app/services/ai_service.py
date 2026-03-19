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
        """Sequential fallback: Gemini -> SambaNova -> Groq -> Cerebras -> OpenAI -> Anthropic -> DeepSeek"""
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
                        print(f"[{name} PARSED JSON successfully]")
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
    def _encode_context(data):
        """Uses ResumeEncoder for lossless encoding/placeholder substitution."""
        from app.utils.encoder import ResumeEncoder
        return ResumeEncoder.encode(data)

    @staticmethod
    def _decode_response(response, metadata, is_json=False):
        """Decodes the AI response using the mapping metadata."""
        from app.utils.encoder import ResumeEncoder
        print(f"[AIService] Decoding response (is_json={is_json})")
        
        if is_json and isinstance(response, (dict, list)):
            decoded = ResumeEncoder.decode_json(response, metadata)
            return decoded
        
        decoded = ResumeEncoder.decode(response, metadata)
        return decoded

    @staticmethod
    def get_suggestion(section, context=""):
        prompt = f"Act as a professional resume writer. Provide high-quality, ATS-friendly content for the '{section}' section of a resume. "
        if context:
            encoded_context, metadata = AIService._encode_context(context)
            prompt += (
                "\nINSTRUCTIONS:\n"
                "1. The following context uses placeholders like __NAME_0__ and @-codes for sensitive info.\n"
                "2. You MUST REUSE these exact placeholders and mappings in your response. DO NOT attempt to invent real data for them.\n"
                "3. If providing @SK (Skills), group them into logical categories (e.g. 'Languages: Java, Python\\nTools: Git, Docker').\n"
                f"Encoded Context: '{encoded_context}'\n\n"
                "Please enhance and expand upon this content to make it professional and impactful. "
            )
        else:
            prompt += "Provide a general professional example. "
        
        prompt += (
            "\nFINAL RULES:\n"
            "- Return ONLY the suggested content text.\n"
            "- NO preamble, NO prefixes like 'Skill:' or 'Summary:', and NO empty lines.\n"
            "- All text must be in plain English except for placeholders/codes."
        )
        
        raw_response = AIService._execute_with_fallback(prompt)
        if context:
            # Ensure we use the exact same mapping from metadata
            return AIService._decode_response(raw_response.strip(), metadata)
        return raw_response

    @staticmethod
    def parse_resume(file_content):
        encoded_content, metadata = AIService._encode_context(file_content)
        
        prompt = f"""
        Act as an ATS parser. Extract key information from the following encoded resume text and return it as a structured JSON object.
        
        STRICT FORMATTING RULES:
        1. REUSE any placeholders (__NAME_0__, __EMAIL_0__, etc.) and keyword codes (@EX, @SK, etc.) you find in the encoded text.
        2. GLOSSARY: __NAME_x__ is Name, __EMAIL_x__ is Email, etc.
        3. EXTRACT the FULL summary/objective. DO NOT truncate or omit any sentences. Every detail matters.
        4. DO NOT combine placeholders. If you see "__NAME_0__, Kolkata", the name is "__NAME_0__" and the address is "Kolkata".
        5. DO NOT add prefixes like 'Skill:' inside the fields.
        6. DO NOT output empty bullet points.
        7. For 'skills', group them into logical categories (e.g. 'Languages: Python, Java').
        
        JSON STRUCTURE TEMPLATE:
        {{
            "personal": {{
                "name": "Extracted Name",
                "email": "Extracted Email",
                "phone": "Extracted Phone",
                "address": "Extracted Address",
                "linkedin": "Extracted LinkedIn"
            }},
            "objective": "A full, detailed summary capturing all years of experience and core expertise...",
            "skills": "Frontend: React, Vue\\nTools: Docker, Git",
            "education": "Degree, University",
            "experience": [
                {{
                    "title": "Job Title",
                    "duration": "Dates",
                    "points": "Point 1\\nPoint 2"
                }}
            ],
            "projects":[
                {{
                    "title": "Project Name",
                    "points": "Feature 1\\nFeature 2"
                }}
            ],
            "certifications": "Cert 1\\nCert 2"
        }}
        
        Encoded Resume Text:
        {encoded_content}
        
        Return ONLY the raw JSON object. No preamble or markdown code blocks.
        """
        raw_json = AIService._execute_with_fallback(prompt, is_json=True)
        return AIService._decode_response(raw_json, metadata, is_json=True)

    @staticmethod
    def tailor_resume(file_content, job_description):
        from app.utils.encoder import ResumeEncoder
        state = {"p_count": 0, "placeholders": {}}
        
        # If file_content is a JSON string (from DB), parse it first so we encode the DICT
        resume_data = file_content
        if isinstance(file_content, str):
            try:
                resume_data = json.loads(file_content)
                print("[AIService] Parsed resume JSON string for tailoring")
            except:
                pass
                
        encoded_resume_obj, resume_metadata = ResumeEncoder.encode(resume_data, state=state)
        # Convert back to JSON string for the prompt if it was a dict
        encoded_resume = json.dumps(encoded_resume_obj, indent=2) if isinstance(encoded_resume_obj, (dict, list)) else encoded_resume_obj

        encoded_jd, jd_metadata = ResumeEncoder.encode(job_description, state=state)
        
        # Combined metadata uses the same global placeholder map
        combined_metadata = {"placeholders": state["placeholders"]}

        prompt = f"""
        Act as an expert career coach. Your task is to TAILOR the resume to perfectly match the job description.
        
        STRICT FORMATTING RULES:
        1. REUSE placeholders and @-codes.
        2. EXTRACT the FULL tailored summary. DO NOT truncate. Keep every detail.
        3. CRITICAL: If you see "__NAME_0__, City", DO NOT put both in address. Split them.
        4. DO NOT add prefix labels like 'Tailored Skill:'.
        5. DO NOT output empty bullet points.
        6. For 'skills', group them into logical categories.
        
        JSON STRUCTURE TEMPLATE:
        {{
            "personal": {{
                "name": "Name from input",
                "email": "Email from input",
                "phone": "Phone from input",
                "address": "Address from input",
                "linkedin": "LinkedIn from input"
            }},
            "objective": "A full, tailored professional summary capturing the SDET/Engineer experience in detail...",
            "skills": "Category title: Skill 1, Skill 2\\nNext Category: Skill 3",
            "education": "Education details...",
            "experience": [
                {{
                    "title": "Job Title",
                    "duration": "Dates",
                    "points": "Punchy tailored point 1\\nPunchy tailored point 2"
                }}
            ],
            "projects": [
                {{
                    "title": "Project Name",
                    "points": "Relevant feature 1\\nRelevant feature 2"
                }}
            ],
            "certifications": "Relevant Certs"
        }}
        
        Encoded Resume:
        {encoded_resume}
        
        Encoded Job Description:
        {encoded_jd}
        
        Return ONLY the raw JSON object. No preamble or markdown blocks.
        """
        raw_json = AIService._execute_with_fallback(prompt, is_json=True)
        return AIService._decode_response(raw_json, combined_metadata, is_json=True)
