import os
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from database import get_settings

class CVSuggestionSchema(BaseModel):
    general_feedback: str = Field(description="Overall advice on how well the CV aligns with the job description.")
    suggested_phrasings: list[dict] = Field(
        description="Specific phrasing adjustments. Each item must contain: 'section' (e.g., 'Summary', 'Experience - BigDataCorp'), 'original_text', 'suggested_text', and 'rationale' explaining why this change aligns with the job's underlying need."
    )
    skills_to_highlight: list[str] = Field(description="Key technical or product skills from the candidate's background that should be elevated to the top or made more prominent.")
    skills_to_acquire_or_mention: list[str] = Field(description="Skills requested by the job that the candidate might have but didn't list, or needs to acquire/address in the interview.")

def suggest_cv_updates(cv_markdown: str, job_title: str, job_description: str, api_key: str = None) -> dict:
    """Compare CV and job description to suggest phrasing improvements on-demand."""
    if not cv_markdown or not job_description:
        return {
            "general_feedback": "Please ensure both your CV and the job description are provided.",
            "suggested_phrasings": [],
            "skills_to_highlight": [],
            "skills_to_acquire_or_mention": []
        }

    if not api_key:
        settings = get_settings()
        api_key = settings.get("api_key") if settings else None

    if not api_key:
        import os
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key or api_key.upper().startswith("MOCK"):
        return {
            "general_feedback": "Based on a simulated comparison, your CV has strong alignment. Here are mock recommendations (set a valid Gemini API key in settings for real AI advice):",
            "suggested_phrasings": [
                {
                    "section": "Professional Summary",
                    "original_text": "Senior Data Product Manager with 7+ years of experience leading enterprise AI...",
                    "suggested_text": "Technical PM with 7+ years of experience leading data platform, API, and cloud infrastructure lifecycles...",
                    "rationale": "Directly matches the target listing's request for a Technical PM managing database, API, and cloud lifecycles."
                },
                {
                    "section": "Professional Experience",
                    "original_text": "Experienced in product strategy, roadmap ownership, customer discovery, AI-powered capabilities...",
                    "suggested_text": "Lead product lifecycle from discovery through delivery, querying high-scale databases and designing APIs...",
                    "rationale": "Explicitly highlights hands-on API and high-scale database query experience demanded in the job description."
                }
            ],
            "skills_to_highlight": ["API Lifecycle Management", "SQL Database Querying", "Cloud Services (AWS/GCP)"],
            "skills_to_acquire_or_mention": ["Drafting technical PRDs", "Developer relations / technical product lifecycles"]
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            "You are an expert resume writer and career coach. Compare the candidate's CV "
            "with the target job description. Suggest specific, tailored phrasing adjustments "
            "to make the CV align better with the job's true requirements without inventing "
            "false experience. Focus on phrasing improvements, terminology translation, and "
            "highlighting relevant achievements.\n\n"
            f"Candidate CV (Markdown):\n{cv_markdown}\n\n"
            f"Job Title: {job_title}\n"
            f"Job Description:\n{job_description}\n\n"
            "Generate suggestions strictly adhering to the JSON schema."
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=CVSuggestionSchema
            )
        )
        
        return json.loads(response.text)
    except Exception as e:
        print(f"Error generating CV suggestions: {e}")
        return {
            "general_feedback": f"Error generating CV suggestions: {str(e)}",
            "suggested_phrasings": [],
            "skills_to_highlight": [],
            "skills_to_acquire_or_mention": []
        }
