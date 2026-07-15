import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jobhunt.db")

def main():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, title, company, url FROM jobs")
        rows = cursor.fetchall()
        
        print(f"\n--- Total jobs in DB: {len(rows)} ---")
        
        linkedin_count = 0
        unknown_urls = 0
        
        for row in rows:
            url = row['url']
            job_id = row['id']
            title = repr(row['title'])
            company = repr(row['company'])
            
            # Check if url matches linkedin patterns
            if url:
                if 'linkedin.com' in url.lower():
                    linkedin_count += 1
                    print(f"[LinkedIn] ID {job_id}: {title} by {company} (URL: {url})")
                else:
                    print(f"[Other] ID {job_id}: {title} by {company} (URL: {url})")
            else:
                unknown_urls += 1
                print(f"[No URL] ID {job_id}: {title} by {company}")
                
        print(f"\nSummary:")
        print(f"  - LinkedIn Jobs: {linkedin_count}")
        print(f"  - Jobs without URLs: {unknown_urls}")
        print(f"  - Other Jobs: {len(rows) - linkedin_count - unknown_urls}")

    finally:
        conn.close()

if __name__ == '__main__':
    main()
