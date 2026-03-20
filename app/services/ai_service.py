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
    def _call_gemini(prompt, model='gemini-2.5-flash'):
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
    def _call_gemini_with_fallback(prompt):
        """Internal Gemini fallback: tries multiple versions before giving up"""
        models = [
            # 'gemini-1.5-flash',
            # 'gemini-1.5-pro',
            # 'gemini-2.0-flash-exp',
            # 'gemini-2.0-flash',
            # 'gemini-1.5-flash-8b',
            'gemini-2.5-flash',
            'gemini-2.5-flash-lite',
            'gemini-2.5-flash-tts',
            'gemini-3-flash',
            'gemini-3.1-flash-lite'
        ]
        
        errors = []
        for model in models:
            try:
                print(f"  [GEMINI SUB-ATTEMPT] {model}...")
                res = AIService._call_gemini(prompt, model=model)
                if res: return res
            except Exception as e:
                err = str(e).upper()
                print(f"  [GEMINI SUB-ATTEMPT FAILED] {model}: {e}")
                errors.append(f"{model}: {e}")
                # If it's a 429, continue to next model. If it's a 401/Invalid Key, stop early.
                if "401" in err or "INVALID" in err:
                    break
        
        # If we get here, all failed. We return None so the main loop can move to SambaNova
        return None

    @staticmethod
    def _execute_with_fallback(prompt, is_json=False):
        """Sequential fallback: Gemini (Multi-model) -> SambaNova -> Groq -> Cerebras -> OpenAI -> Anthropic -> DeepSeek"""
        providers = [
            ('GEMINI', AIService._call_gemini_with_fallback),
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
    def get_suggestion(section, context="", full_resume=None):
        # Parsing logic: Extracts 'job_title' and 'existing_content' from tagged context
        job_title = ""
        user_input = context
        if context and "JOB_TITLE:" in context and "EXISTING_CONTENT:" in context:
            parts = context.split("EXISTING_CONTENT:", 1)
            job_title = parts[0].replace("JOB_TITLE:", "").strip()
            user_input = parts[1].strip()

        # Clean up whitespace but keep content structure
        cleaned_content = user_input.strip()
        
        # Format the background context if provided
        bg_context_block = ""
        if full_resume:
            bg_context_block = "\n### HOLISTIC BACKGROUND CONTEXT (Entire Resume) ###\n"
            if full_resume.get('skills'):
                bg_context_block += f"- SKILLS: {full_resume['skills']}\n"
            if full_resume.get('experience'):
                for i, exp in enumerate(full_resume['experience']):
                    if exp.get('title') and exp.get('points'):
                        bg_context_block += f"- EXPERIENCE {i+1} ({exp['title']}): {exp['points'][:300]}...\n"
            if full_resume.get('projects'):
                bg_context_block += f"- PROJECTS: {full_resume['projects'][:300]}...\n"
            bg_context_block += "#################################################\n\n"
        
        # Debugging prints for terminal tracking (helpful for user troubleshooting)
        print(f"\n--- AI SUGGESTION DEBUG ---")
        print(f"Section: {section} | Role: {job_title}")
        print(f"Input Length: {len(cleaned_content)} chars")
        if full_resume: print(f"Holistic context provided")
        print(f"---------------------------\n")

        # Decide if we are editing existing text or generating from a title
        # Heuristic: If content is very short (under 5 words), it might be a fragment/PII
        is_editing = bool(cleaned_content and len(cleaned_content.split()) > 5)
        is_experience = section.lower() == "experience"

        # Format rules based on section
        if is_experience:
            format_rules = """
- Return the EXACT SAME NUMBER of bullet points as the input.
- DO NOT use any bullet symbols (*, -, •, etc.). 
- Return each point on a NEW LINE only.
- Dont include the job title and duration in the output.
- No headers like 'Experience' or 'Professional Experience'."""
            experience_only_rule = "- SOLELY focus on the bullet points for roles and responsibilities for and during that role."
        else:
            format_rules = """
- Return a SINGLE paragraph (5-10 lines maximum).
- No bullet points or lists.
- No headers like 'Summary', 'Objective', or 'Professional Summary'."""
            experience_only_rule = ""
        
        # Build the transformation-only prompt
        if is_editing:
            prompt = f"""
You are a professional resume editor, not a content creator.
{bg_context_block}
Your task is to improve the 'TARGET CONTENT' for the '{section}' section by refining clarity, impact, and readability while strictly preserving the original meaning and domain.
Use the 'HOLISTIC BACKGROUND CONTEXT' provided above to understand the candidate's true skills and experience level, but ONLY refine the 'TARGET CONTENT'.

STRICT CONSTRAINTS:
- ZERO HALLUCINATION: Do NOT add or assume any new skills, tools, technologies, roles, certifications, or experience NOT found in either the background context or the target content.
- NO SENIORITY SHIFT: Do NOT upgrade or change the role level (e.g., engineer -> lead/manager).
- NO JOB TITLES/DATES: Do NOT include any job titles, company names, or dates/durations (e.g., 'Jan 2020 - Present') in the output.
- USE IMPACT METRICS: Explicitly include percentages, numbers, or achievements (e.g., 'Reduced regression time by 30%') IF they are present in the provided context.
- NO HALLUCINATED METRICS: If NO numbers are provided in the context, do NOT invent them.
- METRIC PRESERVATION: Keep all existing numbers and data EXACTLY as provided.
- CONTEXT LOCK: Stay strictly within the scope of the given target content.
- TRACEABILITY: Every statement must be directly derived from the input.
- KEYWORD ANCHORING: You MUST retain and reuse all important domain-specific terms (e.g., SDET, Playwright, Selenium, REST Assured, CI/CD).
- MANDATORY KEYWORD USAGE:
  If the input contains specific tools, technologies, role names, or domain terms, you MUST explicitly include them in the output.
  Outputs that omit these are INVALID and must be rewritten.- Use the same bullet points and rephrase them.
- ANTI-HALLUCINATION & IDENTITY LOCK:
  * IDENTITY LOCK: Stay strictly within the domain (e.g., SDET, Developer) found in the context. Never pivot to unrelated roles (e.g., System Admin).
  * ZERO HALLUCINATION: If specific metrics or career goals are NOT supported by the context, OMIT them. Do NOT invent/bluff data.
  * NO REFUSAL: Never respond with conversational text, questions, or excuses (e.g., "I cannot fulfill this request").
  * MINIMALIST FALLBACK: If context is sparse, provide a brief, factual summary based on the job title.
- CORE MISSION & GOAL for SUMMARY/OBJECTIVE section: The output should clearly state what the person did/does (with metrics) and the type of high-impact role/team the user is looking forward to join.
- GENERIC OUTPUT REJECTION:
  If the output can apply to any job role without change, it is INVALID. Rewrite it to include role-specific and domain-specific details.(Must follow this rule)
- Check for role and years of experience from input and background context provided, make sure the output is relevant to the role and years of experience. Also check for ATS score, if below 80% then rewrite and improve it.

{experience_only_rule}
- MINIMUM SPECIFICITY REQUIREMENT:
  The output MUST contain at least:
  * 1 role/domain identifier (e.g., SDET, Developer)
  * 2 domain-specific terms (tools, frameworks, systems, etc.)

ANTI-GENERIC ENFORCEMENT:
- DO NOT use vague phrases like 'dedicated professional', 'team player', 'detail-oriented', or 'results-driven'.
- DO NOT replace technical content with generic business language.

QUALITY IMPROVEMENT RULES:
- STRENGTHEN LANGUAGE: Use strong, direct verbs (e.g., 'builds', 'designed', 'implemented'). Prefer active voice (e.g., 'Reduced' instead of 'Proven track record of reducing').
- SIMPLIFY PHRASING: Replace wordy phrases with punchier alternatives (e.g., 'building' instead of 'designing and implementing').
- PRESERVE TECHNICAL DEPTH: Keep all tools, frameworks, and system context intact.
- IMPROVE FLOW: Ensure smooth, logical sentence progression.
- REMOVE FILLER: Eliminate redundancy and weak phrasing.

EXAMPLE TRANSFORMATION:
Input: SDET with ~3 years of experience designing and implementing scalable UI and API automation frameworks for web and microservices-based applications. Expertise in Playwright, Selenium, REST Assured, and familiar with CI/CD-integrated test automation. Proven track record of reducing regression time by 30% and transforming manual workflows into near real-time systems. Strong focus on test architecture, performance, reliability, and automation at scale.
Output: SDET with ~3 years of experience building scalable UI and API automation frameworks for web and microservices applications, utilizing Playwright, Selenium, and REST Assured for CI/CD-integrated test automation. Reduced regression time by 30% by transforming manual workflows into near real-time systems, with a strong focus on performance, reliability, and test architecture.

NEGATIVE EXAMPLE (HALLUCINATION - DO NOT DO THIS):
Background: SDET with Playwright/Selenium experience.
Hallucinated Output: "System Administrator with 5 years experience managing network infrastructure and server operations..."
REASON: This is a FAILURE because it invented an entirely different career path (SysAdmin) not found in the context.

FORMAT RULES:
{format_rules}
- No conversational text or self-checks.

TARGET CONTENT TO REWRITE:
{cleaned_content}

FINAL OUTPUT RULES:
- Return ONLY the rewritten text.
- No prefixes, no titles, no explanations.
- Plain professional English only.
"""
        else:
            prompt = f"""
Generate a concise and professional resume summary for a '{job_title or 'Professional'}' role in the '{section}' section.
Act as a resume editor, not a content creator.
{bg_context_block}
Use the 'HOLISTIC BACKGROUND CONTEXT' provided above to ensure the summary is accurate to the candidate's actual skills and experience.

STRICT CONSTRAINTS:
- ZERO HALLUCINATION: Do NOT add niche or advanced skills, tools, technologies, certifications, or experience NOT listed in the background context.
- NO SENIORITY INFLATION: Do NOT make the role sound more senior than standard expectations.
- USE IMPACT METRICS: Explicitly include percentages or quantified achievements (e.g., 'Reduced regression time by 30%') IF they are present in the background context.
- ANTI-HALLUCINATION & IDENTITY LOCK:
  * IDENTITY LOCK: Stay strictly within the domain (e.g., SDET, Developer) found in the context. Never pivot to unrelated roles (e.g., System Admin).
  * ZERO HALLUCINATION: If specific metrics or career goals are NOT supported by the context, OMIT them. Do NOT invent/bluff data.
  * NO REFUSAL: Never respond with conversational text, questions, or excuses (e.g., "I cannot fulfill this request").
  * MINIMALIST FALLBACK: If context is sparse, provide a brief, factual summary based on the job title.
- TRACEABILITY: All statements must be logically derivable from the role and background context.
- CORE MISSION & GOAL: The output should clearly state what the person did/does (with metrics) and the type of high-impact role/team the user is looking forward to join.
- MANDATORY KEYWORD USAGE:
  If the input contains specific tools, technologies, role names, or domain terms, you MUST explicitly include them in the output.
  Outputs that omit these are INVALID and must be rewritten.

- GENERIC OUTPUT REJECTION:
  If the output can apply to any job role without change, it is INVALID. Rewrite it to include role-specific and domain-specific details.

- MINIMUM SPECIFICITY REQUIREMENT:
  The output MUST contain at least:
  * 1 role/domain identifier (e.g., SDET, Developer)
  * 2 domain-specific terms (tools, frameworks, systems, etc.)

ANTI-GENERIC ENFORCEMENT:
- DO NOT use phrases like 'detail-oriented professional', 'team player', 'go-getter', or 'results-driven'.
- Avoid vague corporate language. Every sentence must convey real responsibility or capability.

QUALITY IMPROVEMENT RULES:
- USE STRONG LANGUAGE: Prefer clear and direct verbs (e.g., 'builds', 'develops', 'implements').
- FOCUS ON CORE WORK: Highlight what the role actually does, not abstract qualities.

FORMAT RULES:
{format_rules}
- No conversational text or self-checks.
- Return ONLY the generated summary text.
- No prefixes, no titles, no explanations, no quotes.
- Plain professional English only.
"""

        raw_response = AIService._execute_with_fallback(prompt)
        
        # Post-processing: Remove common AI prefixes/quotes
        if raw_response:
            import re
            # Initial stripping of quotes/outer whitespace
            clean_res = raw_response.strip().strip('"').strip("'").strip()
            
            # 1. Aggressive Regex Header Stripping: 
            # Removes patterns like "Summary:", "Role:", "IT Manager:", "Anything:"
            # at the very beginning of the response.
            header_regex = r"^(?i)(summary|objective|professional summary|career objective|suggestion|original role|[a-z0-9\s/&-]{2,30})[:.]\s*"
            clean_res = re.sub(header_regex, "", clean_res, count=1).strip()
            
            # 2. Dynamic Role Stripping (Extra safety for specific job title)
            role_label = (job_title or "Professional").lower()
            if clean_res.lower().startswith(role_label):
                check_prefix = clean_res[:len(role_label)+1].lower()
                if check_prefix == role_label + ":" or check_prefix == role_label + ".":
                    clean_res = clean_res[len(role_label)+1:].strip()

            # 4. Experience Cleanup: Bullet Symbols, Titles, & Durations (Line-by-Line)
            if is_experience:
                lines = clean_res.split('\n')
                new_lines = []
                for line in lines:
                    # a) Strip Bullet Symbols (*, -, •, etc.)
                    bullet_regex = r"^[\s\-\*\•\u2022\u2023\u2043\u254b\u203b]*\s*"
                    line = re.sub(bullet_regex, "", line).strip()
                    
                    # b) Remove duration patterns like "Jan 2020 - Present", "2022-2023", etc.
                    duration_regex = r"(?i)(\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\s*-\s*(present|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}))|(\b\d{4}\s*-\s*(present|\d{4}))"
                    line = re.sub(duration_regex, "", line).strip()
                    
                    # c) Remove accidental job title repeats at the start of a line
                    if job_title and line.lower().startswith(job_title.lower()):
                        line = re.sub(f"^(?i){re.escape(job_title)}[:.\s-]*", "", line).strip()
                    
                    if line: new_lines.append(line)
                clean_res = "\n".join(new_lines)

            return clean_res
            
        return raw_response

    @staticmethod
    def parse_resume(file_content):
        encoded_content, metadata = AIService._encode_context(file_content)
        
        prompt = f"""
        Act as an ATS parser. Extract key information from the following encoded resume text and return it as a structured JSON object.
        
        STRICT FORMATTING RULES:
        1. REUSE any placeholders (__NAME_0__, __EMAIL_0__, etc.) and keyword codes (@EX, @SK, etc.) you find in the encoded text.
        2. GLOSSARY: __NAME_x__ is Name, __EMAIL_x__ is Email, etc.
        3. EXTRACT the FULL summary/objective. DO NOT truncate.
        4. ANTI-PII: The 'objective' field MUST NOT contain the candidate's Name, Email, Phone, or Address. If the resume starts with these, skip them and only extract the professional summary text.
        5. DO NOT combine placeholders.
        6. For 'personal', only use the specific PII placeholders.
        7. For 'skills', group them into logical categories.
        8. For 'personal.address', ONLY include City, State, Country.
        
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
