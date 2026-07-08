import io
from pypdf import PdfReader
import google.generativeai as genai
from database import get_settings

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from a PDF file."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def convert_pdf_text_to_markdown(raw_text: str, api_key: str = None) -> str:
    """Use Gemini API to format raw resume text into clean, structured Markdown."""
    if not api_key:
        settings = get_settings()
        api_key = settings.get("api_key") if settings else None
        
    if not api_key:
        # Fallback to environment variable
        import os
        api_key = os.environ.get("GEMINI_API_KEY")
        
    if not api_key:
        # If no API key is available, just return the raw text with minimal styling
        return f"# Resume (Raw Text - Please configure Gemini API Key for auto-formatting)\n\n{raw_text}"
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = (
            "You are an expert CV/resume processing agent. "
            "Convert the following raw text extracted from a resume into clean, professional, "
            "standard Markdown. Maintain all details, formatting, sections (Education, Experience, Skills), "
            "and chronological order. Use proper headers, list bullets, bold text, and formatting. "
            "Do not omit any text or add any conversational introduction/outro. "
            "Return ONLY the markdown document:\n\n"
            f"{raw_text}"
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error converting PDF to Markdown with Gemini: {e}")
        # Return raw text on failure
        return f"# Resume (Fallback)\n\n{raw_text}"
