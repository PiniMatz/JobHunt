import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import local modules
import database
from pdf_parser import extract_text_from_pdf, convert_pdf_text_to_markdown
from matching_agent import analyze_job_match
from scraper import search_live_jobs
from cv_optimizer import suggest_cv_updates
from pre_filter import pre_screen_job

app = FastAPI(title="JobHunt API Server", description="Backend services for JobHunt smart PM job matcher")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database on startup
@app.on_event("startup")
def startup_event():
    database.init_db()

# Pydantic schemas for request/response validation
class SettingsUpdate(BaseModel):
    cv_markdown: Optional[str] = None
    api_key: Optional[str] = None
    locations: Optional[List[str]] = None
    threshold: Optional[int] = None
    must_have_keywords: Optional[List[str]] = None
    exclusion_keywords: Optional[List[str]] = None

class StatusUpdate(BaseModel):
    status: str

@app.get("/api/jobs")
def get_jobs():
    try:
        return database.get_jobs_with_matches()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/scan")
def scan_jobs():
    try:
        settings = database.get_settings()
        if not settings:
            raise HTTPException(status_code=400, detail="Settings are not initialized.")
            
        locations = settings.get("locations", ["Netanya"])
        cv_markdown = settings.get("cv_markdown", "")
        api_key = settings.get("api_key", "")
        
        # 1. Fetch listings
        listings = search_live_jobs(locations)
        new_jobs_count = 0
        
        for job in listings:
            # 2. Add to database (checks duplicates internally)
            job_id = database.add_job(
                title=job["title"],
                company=job["company"],
                location=job["location"],
                description=job["description"],
                url=job.get("url")
            )
            
            # 3. If there is a CV, perform matching analysis (unless already analyzed)
            # To check if already matched, let's see if we should fetch matches
            # For simplicity, we match all new/updated jobs
            if cv_markdown:
                # Local pre-screening check to save API costs
                is_relevant, reason = pre_screen_job(job["title"], job["description"], settings)
                
                if is_relevant:
                    match_analysis = analyze_job_match(
                        cv_markdown=cv_markdown,
                        job_title=job["title"],
                        job_description=job["description"],
                        api_key=api_key
                    )
                    database.save_match_result(
                        job_id=job_id,
                        overall_score=match_analysis["overall_score"],
                        tech_score=match_analysis["tech_score"],
                        data_score=match_analysis["data_score"],
                        pm_score=match_analysis["pm_score"],
                        fit_score=match_analysis["fit_score"],
                        pros=match_analysis["pros"],
                        cons=match_analysis["cons"],
                        red_flags=match_analysis["red_flags"]
                    )
                else:
                    # Skip LLM call entirely
                    database.save_match_result(
                        job_id=job_id,
                        overall_score=5,
                        tech_score=0,
                        data_score=0,
                        pm_score=0,
                        fit_score=0,
                        pros=[],
                        cons=[f"Local Pre-screen: {reason}"],
                        red_flags=["Screened out locally to save API cost."]
                    )
            new_jobs_count += 1
            
        return {"status": "success", "jobs_scanned": len(listings), "new_jobs": new_jobs_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/{job_id}/status")
def update_job_status(job_id: int, payload: StatusUpdate):
    try:
        if payload.status not in ["active", "starred", "dismissed", "applied"]:
            raise HTTPException(status_code=400, detail="Invalid status value.")
        database.update_job_status(job_id, payload.status)
        return {"status": "success", "job_id": job_id, "new_status": payload.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int):
    try:
        database.delete_job(job_id)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
def get_settings():
    try:
        settings = database.get_settings()
        if not settings:
            raise HTTPException(status_code=500, detail="Settings could not be retrieved.")
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings")
def update_settings(payload: SettingsUpdate):
    try:
        database.update_settings(
            cv_markdown=payload.cv_markdown,
            api_key=payload.api_key,
            locations=payload.locations,
            threshold=payload.threshold,
            must_have_keywords=payload.must_have_keywords,
            exclusion_keywords=payload.exclusion_keywords
        )
        return {"status": "success", "settings": database.get_settings()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cv/upload")
async def upload_cv(file: UploadFile = File(...)):
    try:
        # Read uploaded file
        pdf_bytes = await file.read()
        
        # Extract raw text
        raw_text = extract_text_from_pdf(pdf_bytes)
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded PDF file appears to be empty or unscannable.")
            
        # Get Gemini API key for formatting
        settings = database.get_settings()
        api_key = settings.get("api_key") if settings else None
        
        # Convert to Markdown
        markdown_cv = convert_pdf_text_to_markdown(raw_text, api_key=api_key)
        
        # Save to database
        database.update_settings(cv_markdown=markdown_cv)
        
        return {"status": "success", "cv_markdown": markdown_cv}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/{job_id}/cv-suggestions")
def get_cv_suggestions(job_id: int):
    try:
        settings = database.get_settings()
        if not settings or not settings.get("cv_markdown"):
            raise HTTPException(status_code=400, detail="Please upload or paste your CV before requesting optimization suggestions.")
            
        # Get job details
        jobs = database.get_jobs_with_matches()
        target_job = next((j for j in jobs if j["id"] == job_id), None)
        
        if not target_job:
            raise HTTPException(status_code=404, detail="Job listing not found.")
            
        suggestions = suggest_cv_updates(
            cv_markdown=settings["cv_markdown"],
            job_title=target_job["title"],
            job_description=target_job["description"],
            api_key=settings.get("api_key")
        )
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
