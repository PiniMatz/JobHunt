import sqlite3
import json
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import firestore_db

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "jobhunt.db")

def main():
    print("--- JobHunt SQLite to Firestore Migration ---")
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"Error: SQLite database not found at {SQLITE_DB_PATH}")
        return

    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        db = firestore_db.get_firestore_client()
        print("Connected to Firestore successfully.")

        # 1. Migrate Settings
        cursor.execute("SELECT cv_markdown, api_key, locations, threshold, must_have_keywords, exclusion_keywords FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        if settings_row:
            settings_data = {
                "cv_markdown": settings_row["cv_markdown"] or "",
                "api_key": settings_row["api_key"] or "",
                "locations": json.loads(settings_row["locations"]) if settings_row["locations"] else ["Netanya"],
                "threshold": settings_row["threshold"] or 70,
                "must_have_keywords": json.loads(settings_row["must_have_keywords"]) if settings_row["must_have_keywords"] else ["Product Manager"],
                "exclusion_keywords": json.loads(settings_row["exclusion_keywords"]) if settings_row["exclusion_keywords"] else ["Junior"]
            }
            db.collection('settings').document('config').set(settings_data)
            print("[OK] Settings migrated to Firestore ('settings/config').")

        # 2. Migrate Jobs and Matches
        cursor.execute("""
            SELECT j.id, j.title, j.company, j.location, j.description, j.url, j.status, j.date_found,
                   m.overall_score, m.tech_score, m.data_score, m.pm_score, m.fit_score,
                   m.explanation, m.pros, m.cons, m.red_flags
            FROM jobs j
            LEFT JOIN matches m ON j.id = m.job_id
        """)
        jobs_rows = cursor.fetchall()

        print(f"\nFound {len(jobs_rows)} jobs in SQLite DB. Starting batch upload to Firestore...")

        migrated_jobs = 0
        migrated_matches = 0

        for r in jobs_rows:
            doc_id = firestore_db._get_job_doc_id(r["title"], r["company"])
            doc_ref = db.collection('jobs').document(doc_id)

            match_obj = None
            if r["overall_score"] is not None:
                match_obj = {
                    "overall_score": r["overall_score"],
                    "tech_score": r["tech_score"],
                    "data_score": r["data_score"],
                    "pm_score": r["pm_score"],
                    "fit_score": r["fit_score"],
                    "explanation": r["explanation"] or "",
                    "pros": json.loads(r["pros"]) if r["pros"] else [],
                    "cons": json.loads(r["cons"]) if r["cons"] else [],
                    "red_flags": json.loads(r["red_flags"]) if r["red_flags"] else []
                }
                migrated_matches += 1

            job_doc = {
                "title": r["title"],
                "company": r["company"],
                "location": r["location"],
                "description": r["description"],
                "url": r["url"],
                "status": r["status"] or "active",
                "date_found": r["date_found"] or "",
                "match": match_obj
            }

            doc_ref.set(job_doc)
            migrated_jobs += 1

        print(f"\n==========================================")
        print(f" Migration Complete!")
        print(f"  - Jobs Migrated: {migrated_jobs}")
        print(f"  - Match Scores Migrated: {migrated_matches}")
        print(f"==========================================")

    except Exception as e:
        print(f"\n[X] Migration Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
