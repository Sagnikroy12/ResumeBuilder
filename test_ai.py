import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.getcwd())

load_dotenv()

try:
    from app.services.ai_service import AIService
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_ai():
    print("Testing AI Service...")
    prompt = "Hi, reply with 'Hello from AI'"
    try:
        result = AIService._execute_with_fallback(prompt)
        print(f"\nFinal Result: {result}")
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    test_ai()
