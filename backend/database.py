import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobhunt.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create jobs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT NOT NULL,
        description TEXT NOT NULL,
        url TEXT,
        status TEXT NOT NULL DEFAULT 'active', -- 'active', 'starred', 'dismissed', 'applied'
        date_found DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create matches table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL UNIQUE,
        overall_score INTEGER NOT NULL,
        tech_score INTEGER NOT NULL,
        data_score INTEGER NOT NULL,
        pm_score INTEGER NOT NULL,
        fit_score INTEGER NOT NULL,
        pros TEXT,      -- JSON list
        cons TEXT,      -- JSON list
        red_flags TEXT, -- JSON list
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
    )
    """)
    
    # Create settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cv_markdown TEXT,
        api_key TEXT,
        locations TEXT DEFAULT '["Netanya"]', -- JSON list of locations
        threshold INTEGER DEFAULT 70,
        must_have_keywords TEXT DEFAULT '["Product Manager", "Product Owner", "PM"]',
        exclusion_keywords TEXT DEFAULT '["Junior", "Intern", "Student"]'
    )
    """)
    
    # Run migrations for existing DBs
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN must_have_keywords TEXT DEFAULT '[\"Product Manager\", \"Product Owner\", \"PM\"]'")
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute("ALTER TABLE settings ADD COLUMN exclusion_keywords TEXT DEFAULT '[\"Junior\", \"Intern\", \"Student\"]'")
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    # Initialize settings row if empty
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO settings (cv_markdown, api_key, locations, threshold, must_have_keywords, exclusion_keywords) VALUES ('', '', '[\"Netanya\"]', 70, '[\"Product Manager\", \"Product Owner\", \"PM\"]', '[\"Junior\", \"Intern\", \"Student\"]')"
        )
        
    conn.commit()
    conn.close()

# Database Helper functions

def get_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cv_markdown, api_key, locations, threshold, must_have_keywords, exclusion_keywords FROM settings LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "cv_markdown": row["cv_markdown"],
            "api_key": row["api_key"],
            "locations": json.loads(row["locations"]),
            "threshold": row["threshold"],
            "must_have_keywords": json.loads(row["must_have_keywords"]) if row["must_have_keywords"] else ["Product Manager", "Product Owner", "PM"],
            "exclusion_keywords": json.loads(row["exclusion_keywords"]) if row["exclusion_keywords"] else ["Junior", "Intern", "Student"]
        }
    return None

def update_settings(cv_markdown=None, api_key=None, locations=None, threshold=None, must_have_keywords=None, exclusion_keywords=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    
    if cv_markdown is not None:
        fields.append("cv_markdown = ?")
        values.append(cv_markdown)
    if api_key is not None:
        fields.append("api_key = ?")
        values.append(api_key)
    if locations is not None:
        fields.append("locations = ?")
        values.append(json.dumps(locations))
    if threshold is not None:
        fields.append("threshold = ?")
        values.append(threshold)
    if must_have_keywords is not None:
        fields.append("must_have_keywords = ?")
        values.append(json.dumps(must_have_keywords))
    if exclusion_keywords is not None:
        fields.append("exclusion_keywords = ?")
        values.append(json.dumps(exclusion_keywords))
        
    if fields:
        values.append(1)  # Limit 1 (settings row id is 1)
        query = f"UPDATE settings SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, tuple(values))
        conn.commit()
        
    conn.close()

def add_job(title, company, location, description, url=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if job already exists by matching title + company
        cursor.execute("SELECT id FROM jobs WHERE title = ? AND company = ?", (title, company))
        row = cursor.fetchone()
        if row:
            job_id = row["id"]
        else:
            cursor.execute(
                "INSERT INTO jobs (title, company, location, description, url) VALUES (?, ?, ?, ?, ?)",
                (title, company, location, description, url)
            )
            job_id = cursor.lastrowid
            conn.commit()
        return job_id
    finally:
        conn.close()

def update_job_status(job_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    # Cascade delete on matches manually to be safe (sqlite foreign key cascade requires PRAGMA foreign_keys = ON)
    cursor.execute("DELETE FROM matches WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()

def save_match_result(job_id, overall_score, tech_score, data_score, pm_score, fit_score, pros, cons, red_flags):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Save or update match
    cursor.execute("SELECT id FROM matches WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    
    pros_json = json.dumps(pros)
    cons_json = json.dumps(cons)
    red_flags_json = json.dumps(red_flags)
    
    if row:
        cursor.execute(
            """UPDATE matches SET 
               overall_score = ?, tech_score = ?, data_score = ?, pm_score = ?, fit_score = ?, 
               pros = ?, cons = ?, red_flags = ?, created_at = CURRENT_TIMESTAMP
               WHERE job_id = ?""",
            (overall_score, tech_score, data_score, pm_score, fit_score, pros_json, cons_json, red_flags_json, job_id)
        )
    else:
        cursor.execute(
            """INSERT INTO matches 
               (job_id, overall_score, tech_score, data_score, pm_score, fit_score, pros, cons, red_flags) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (job_id, overall_score, tech_score, data_score, pm_score, fit_score, pros_json, cons_json, red_flags_json)
        )
    conn.commit()
    conn.close()

def get_jobs_with_matches():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.id, j.title, j.company, j.location, j.description, j.url, j.status, j.date_found,
               m.overall_score, m.tech_score, m.data_score, m.pm_score, m.fit_score,
               m.pros, m.cons, m.red_flags
        FROM jobs j
        LEFT JOIN matches m ON j.id = m.job_id
        ORDER BY j.date_found DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    jobs = []
    for r in rows:
        job = {
            "id": r["id"],
            "title": r["title"],
            "company": r["company"],
            "location": r["location"],
            "description": r["description"],
            "url": r["url"],
            "status": r["status"],
            "date_found": r["date_found"],
            "match": None
        }
        if r["overall_score"] is not None:
            job["match"] = {
                "overall_score": r["overall_score"],
                "tech_score": r["tech_score"],
                "data_score": r["data_score"],
                "pm_score": r["pm_score"],
                "fit_score": r["fit_score"],
                "pros": json.loads(r["pros"]) if r["pros"] else [],
                "cons": json.loads(r["cons"]) if r["cons"] else [],
                "red_flags": json.loads(r["red_flags"]) if r["red_flags"] else []
            }
        jobs.append(job)
    return jobs

# Run initialization
if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
