from scraper import search_live_jobs
import sys

def test():
    # Set console encoding to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("Searching for Tel Aviv jobs...")
    jobs = search_live_jobs(["Tel Aviv"])
    print(f"\nCompleted search. Found {len(jobs)} jobs.")
    
    for idx, j in enumerate(jobs):
        print(f"\nJob #{idx+1}:")
        print(f"  Title: {j['title']}")
        print(f"  Company: {j['company']}")
        print(f"  Location: {j['location']}")
        print(f"  URL: {j['url']}")
        print(f"  Desc Snippet (150 chars): {j['description'][:150].strip()}...")
        print("-" * 40)

if __name__ == "__main__":
    test()
