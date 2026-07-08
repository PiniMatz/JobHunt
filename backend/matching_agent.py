import os
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from database import get_settings

class JobMatchSchema(BaseModel):
    overall_score: int = Field(description="Overall match score from 0 to 100.")
    tech_score: int = Field(description="Technical direction match score from 0 to 100. Emphasizes technical architecture, system design, engineering alignment.")
    data_score: int = Field(description="Data orientation match score from 0 to 100. Emphasizes SQL, data products, analytics, pipelines, and ML.")
    pm_score: int = Field(description="Core Product Management match score from 0 to 100. Emphasizes roadmap, user research, execution, Agile, and stakeholder management.")
    fit_score: int = Field(description="Company fit / true demand compatibility score from 0 to 100. Evaluates if the company's real underlying need matches the candidate's career level and direction.")
    pros: list[str] = Field(description="List of key strengths, reasons why this is a good match.")
    cons: list[str] = Field(description="List of key weaknesses, missing skills, or mismatched requirements.")
    red_flags: list[str] = Field(description="List of potential concerns, warning signs in the listing, or high-risk requirements.")
    explanation: str = Field(description="A concise summary of the match analysis (2-3 sentences).")

def analyze_job_match(cv_markdown: str, job_title: str, job_description: str, api_key: str = None) -> dict:
    """Analyze a job listing against the user's CV using the Gemini API and return a structured match analysis."""
    if not cv_markdown or not job_description:
        return {
            "overall_score": 0,
            "tech_score": 0,
            "data_score": 0,
            "pm_score": 0,
            "fit_score": 0,
            "pros": ["CV or job description is missing"],
            "cons": ["Cannot perform matching analysis"],
            "red_flags": [],
            "explanation": "Missing input data."
        }

    if not api_key:
        settings = get_settings()
        api_key = settings.get("api_key") if settings else None

    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key or api_key.upper().startswith("MOCK"):
        # Generate a smart simulated match based on basic keyword matching for testing/demonstration
        desc_lower = job_description.lower()
        title_lower = job_title.lower()
        
        tech_score = 50
        data_score = 50
        pm_score = 60
        fit_score = 50
        
        pros = []
        cons = []
        red_flags = []
        
        # Tech evaluation
        if any(w in desc_lower or w in title_lower for w in ["tech", "api", "infra", "cloud", "developer", "aws", "kubernetes", "architecture"]):
            tech_score = 85
            pros.append("Strong alignment with technical direction and platform management.")
        else:
            tech_score = 40
            cons.append("Role lacks significant technical architecture or engineering interaction.")
            
        # Data evaluation
        if any(w in desc_lower or w in title_lower for w in ["data", "analytics", "sql", "pipeline", "etl", "snowflake", "bigquery", "ml", "ai"]):
            data_score = 90
            pros.append("Matches your experience building enterprise data platforms and pipelines.")
        else:
            data_score = 35
            cons.append("Minimal focus on data products, pipelines, or analytics.")
            
        # Core PM evaluation
        if any(w in desc_lower for w in ["roadmap", "strategy", "priorit", "scrum", "agile", "prd", "lifecycle"]):
            pm_score = 85
            pros.append("Robust core product management methodologies required.")
            
        # Fit evaluation
        if "netanya" in desc_lower or "netanya" in title_lower:
            fit_score = 90
            pros.append("Located in your target area (Netanya).")
        
        # Overall weighted score
        overall_score = int((tech_score + data_score + pm_score + fit_score) / 4)
        
        if overall_score > 70:
            pros.append("Underlying request aligns well with a Senior Technical/Data PM profile.")
        else:
            cons.append("The role seems to lean towards non-technical or standard business PM responsibilities.")
            
        return {
            "overall_score": overall_score,
            "tech_score": tech_score,
            "data_score": data_score,
            "pm_score": pm_score,
            "fit_score": fit_score,
            "pros": pros,
            "cons": cons,
            "red_flags": red_flags,
            "explanation": f"Simulated match of {overall_score}% for testing. Setup a real Gemini API Key in settings to enable LLM analysis."
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = (
            "You are a highly sophisticated Product Management recruitment agent. Your task is to analyze "
            "a job listing and determine its compatibility with a candidate's CV.\n\n"
            "The candidate is looking for a new role as a Product Manager with an emphasis on Data or Technological direction.\n\n"
            "Evaluate compatibility on multiple dimensions:\n"
            "1. Tech Score: Is there a demand for hands-on technical architecture, system design, developer products, APIs, or engineering leadership?\n"
            "2. Data Score: Is there a demand for data platforms, BI, SQL, analytics, machine learning, data engineering, or data products?\n"
            "3. PM Score: Core product management skills (execution, roadmap, agile/scrum, cross-functional collaboration, requirements gathering).\n"
            "4. Fit Score: Understanding the *underlying true request* of the company. Look past keyword buzzwords to see if they actually need a builder, a system design-oriented PM, or if the role is a standard business PM disguised as technical.\n\n"
            f"Candidate CV (Markdown):\n{cv_markdown}\n\n"
            f"Job Title: {job_title}\n"
            f"Job Description:\n{job_description}\n\n"
            "Provide the analysis strictly in JSON format matching the schema."
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=JobMatchSchema
            )
        )
        
        # Parse the JSON response
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error during Gemini matching analysis: {e}")
        return {
            "overall_score": 0,
            "tech_score": 0,
            "data_score": 0,
            "pm_score": 0,
            "fit_score": 0,
            "pros": [f"Error occurred during analysis: {str(e)}"],
            "cons": [],
            "red_flags": [],
            "explanation": "An error occurred while running the Gemini matching engine."
        }
