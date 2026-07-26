import os
import json
import hashlib
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serviceAccountKey.json")

def get_firestore_client():
    if not firebase_admin._apps:
        if os.path.exists(SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to Application Default Credentials or default app
            try:
                firebase_admin.initialize_app(options={'projectId': 'jobhunt2-4ee1f'})
            except Exception:
                firebase_admin.initialize_app()
    return firestore.client()

def init_db():
    """Ensure default settings document exists in Firestore."""
    db = get_firestore_client()
    doc_ref = db.collection('settings').document('config')
    doc = doc_ref.get()
    if not doc.exists:
        default_settings = {
            "cv_markdown": "",
            "api_key": "",
            "locations": ["Netanya"],
            "threshold": 70,
            "must_have_keywords": ["Product Manager", "Product Owner", "PM"],
            "exclusion_keywords": ["Junior", "Intern", "Student"]
        }
        doc_ref.set(default_settings)
        print("[Firestore] Initialized default settings document.")

def get_settings():
    db = get_firestore_client()
    doc_ref = db.collection('settings').document('config')
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return {
            "cv_markdown": data.get("cv_markdown", ""),
            "api_key": data.get("api_key", ""),
            "locations": data.get("locations", ["Netanya"]),
            "threshold": data.get("threshold", 70),
            "must_have_keywords": data.get("must_have_keywords", ["Product Manager", "Product Owner", "PM"]),
            "exclusion_keywords": data.get("exclusion_keywords", ["Junior", "Intern", "Student"])
        }
    return {
        "cv_markdown": "",
        "api_key": "",
        "locations": ["Netanya"],
        "threshold": 70,
        "must_have_keywords": ["Product Manager", "Product Owner", "PM"],
        "exclusion_keywords": ["Junior", "Intern", "Student"]
    }

def update_settings(cv_markdown=None, api_key=None, locations=None, threshold=None, must_have_keywords=None, exclusion_keywords=None):
    db = get_firestore_client()
    doc_ref = db.collection('settings').document('config')
    
    update_data = {}
    if cv_markdown is not None: update_data["cv_markdown"] = cv_markdown
    if api_key is not None: update_data["api_key"] = api_key
    if locations is not None: update_data["locations"] = locations
    if threshold is not None: update_data["threshold"] = threshold
    if must_have_keywords is not None: update_data["must_have_keywords"] = must_have_keywords
    if exclusion_keywords is not None: update_data["exclusion_keywords"] = exclusion_keywords
    
    if update_data:
        doc_ref.set(update_data, merge=True)
    return get_settings()

def _get_job_doc_id(title, company):
    """Generate a consistent document ID for duplicate checking."""
    raw = f"{title.strip().lower()}_{company.strip().lower()}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()

def add_job(title, company, location, description, url=None):
    db = get_firestore_client()
    doc_id = _get_job_doc_id(title, company)
    doc_ref = db.collection('jobs').document(doc_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        job_data = {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": url,
            "status": "active",
            "date_found": datetime.utcnow().isoformat(),
            "match": None
        }
        doc_ref.set(job_data)
        
    return doc_id

def update_job_status(job_id, status):
    db = get_firestore_client()
    doc_ref = db.collection('jobs').document(str(job_id))
    doc_ref.set({"status": status}, merge=True)

def delete_job(job_id):
    db = get_firestore_client()
    doc_ref = db.collection('jobs').document(str(job_id))
    doc_ref.delete()

def save_match_result(job_id, overall_score, tech_score, data_score, pm_score, fit_score, pros, cons, red_flags, explanation=""):
    db = get_firestore_client()
    doc_ref = db.collection('jobs').document(str(job_id))
    
    match_data = {
        "match": {
            "overall_score": overall_score,
            "tech_score": tech_score,
            "data_score": data_score,
            "pm_score": pm_score,
            "fit_score": fit_score,
            "explanation": explanation,
            "pros": pros if isinstance(pros, list) else [],
            "cons": cons if isinstance(cons, list) else [],
            "red_flags": red_flags if isinstance(red_flags, list) else []
        }
    }
    doc_ref.set(match_data, merge=True)

def get_jobs_with_matches():
    db = get_firestore_client()
    docs = db.collection('jobs').get()
    
    jobs = []
    for doc in docs:
        d = doc.to_dict()
        job = {
            "id": doc.id,
            "title": d.get("title", ""),
            "company": d.get("company", ""),
            "location": d.get("location", ""),
            "description": d.get("description", ""),
            "url": d.get("url", ""),
            "status": d.get("status", "active"),
            "date_found": d.get("date_found", ""),
            "match": d.get("match", None)
        }
        jobs.append(job)
        
    # Sort by date_found descending
    jobs.sort(key=lambda x: x.get("date_found") or "", reverse=True)
    return jobs
