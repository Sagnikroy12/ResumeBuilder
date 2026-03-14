from google import genai
import os
import json
import openai
import anthropic

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
                    if is_json:
                        # Basic JSON extraction
                        clean_json = result.replace('```json', '').replace('```', '').strip()
                        return json.loads(clean_json)
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
    def get_suggestion(section, context=""):
        prompt = f"Act as a professional resume writer. Provide high-quality, ATS-friendly content for the '{section}' section of a resume. "
        if context:
            prompt += f"The user has provided this initial draft/context: '{context}'. Please enhance and expand upon this to make it professional and impactful. "
        else:
            prompt += "Provide a general professional example. "
        prompt += "Return ONLY the suggested content text, no preamble, no quotes, and no extra formatting."
        return AIService._execute_with_fallback(prompt)

    @staticmethod
    def parse_resume(file_content):
        prompt = f"""
        Act as an ATS parser. Extract key information from the following resume text and return it as a structured JSON object.
        
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
            "skills": "Skill 1\\nSkill 2\\nSkill 3",
            "education": "Brief education history...",
            "experience": [
                {{
                    "title": "Job Title",
                    "duration": "Jan 2020 - Present",
                    "points": "Point 1\\nPoint 2"
                }}
            ],
            "projects": "Project 1\\nProject 2",
            "certifications": "Cert 1\\nCert 2"
        }}
        
        Important:
        - Return 'skills', 'projects', and 'certifications' as multiline strings (each item on a new line).
        - 'experience' list items should have 'points' as a multiline string.
        - Normalize the metadata into the 'personal' object.
        
        Resume Text:
        {file_content}
        
        Return ONLY the raw JSON object. No other text.
        """
        return AIService._execute_with_fallback(prompt, is_json=True)

    @staticmethod
    def tailor_resume(file_content, job_description):
        prompt = f"""
        Act as an expert career coach. Tailor the following resume to better match the job description provided.
        Extract and adapt information into this structured JSON object:
        
        {{
            "personal": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "+91 9876543210",
                "address": "City, Country",
                "linkedin": "linkedin.com/in/username"
            }},
            "objective": "Tailored summary...",
            "skills": "Tailored Skill 1\\nTailored Skill 2",
            "education": "Brief education history...",
            "experience": [
                {{
                    "title": "Job Title",
                    "duration": "Jan 2020 - Present",
                    "points": "Tailored Point 1\\nTailored Point 2"
                }}
            ],
            "projects": "Tailored Project 1",
            "certifications": "Certs..."
        }}
        
        Resume:
        {file_content}
        
        Job Description:
        {job_description}
        
        Return ONLY the raw JSON object.
        """
        return AIService._execute_with_fallback(prompt, is_json=True)
