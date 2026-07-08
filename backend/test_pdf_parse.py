import os
import sys
from pdf_parser import extract_text_from_pdf, convert_pdf_text_to_markdown
from database import init_db, update_settings, get_settings

def test_pdf_parsing():
    # PDF is in the root directory (one level up from backend)
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Pini_Matzner_2026.pdf")
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return
        
    print(f"Found PDF at {pdf_path}. Reading...")
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        
    print(f"Read {len(pdf_bytes)} bytes.")
    
    raw_text = extract_text_from_pdf(pdf_bytes)
    print(f"Extracted raw text with {len(raw_text)} characters.")
    print("--- FIRST 500 CHARACTERS ---")
    print(raw_text[:500])
    print("----------------------------")
    
    # Try converting to Markdown
    # We will check if Gemini API key is configured
    init_db()
    settings = get_settings()
    api_key = settings.get("api_key") if settings else None
    
    print("\nConverting PDF text to Markdown...")
    if not api_key:
        print("Note: Gemini API key is not configured in database. Using environment variable or fallback mode.")
        
    markdown_cv = convert_pdf_text_to_markdown(raw_text, api_key=api_key)
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsed_cv.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_cv)
        
    print(f"Saved converted Markdown CV to: {output_path}")
    
    # Update settings
    update_settings(cv_markdown=markdown_cv)
    print("Successfully updated database settings with the parsed CV.")

if __name__ == "__main__":
    test_pdf_parsing()
