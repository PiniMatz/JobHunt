import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jobhunt.db")

def main():
    if not os.path.exists(DB_PATH):
        print("Database not found")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check jobs with linkedin.com in URL
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE url LIKE '%linkedin.com%'")
        linkedin_count = cursor.fetchone()[0]
        
        # Check jobs with no URL
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE url IS NULL OR url = ''")
        no_url_count = cursor.fetchone()[0]
        
        # Check total count
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_count = cursor.fetchone()[0]
        
        print(f"Total jobs in database: {total_count}")
        print(f"LinkedIn jobs (url contains linkedin.com): {linkedin_count}")
        print(f"Jobs without any URL: {no_url_count}")
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
