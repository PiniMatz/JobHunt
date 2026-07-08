import google.generativeai as genai
import sys
import os

# Add parent directory to sys.path to import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_settings

def test_api():
    settings = get_settings()
    if not settings:
        print("Settings not initialized.")
        return
        
    api_key = settings.get("api_key")
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")
        
    if not api_key:
        print("No API Key found in settings or environment.")
        return
        
    print(f"API Key found (length {len(api_key)})")
    
    genai.configure(api_key=api_key)
    
    print("\nListing available models:")
    try:
        models = genai.list_models()
        for m in models:
            print(f" - Name: {m.name}, Supported Methods: {m.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")
        
    print("\nTesting simple prompt on gemini-1.5-flash:")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content("Hello, write one word response.")
        print(f"Result: {res.text.strip()}")
    except Exception as e:
        print(f"Error using gemini-1.5-flash: {e}")

if __name__ == "__main__":
    test_api()
