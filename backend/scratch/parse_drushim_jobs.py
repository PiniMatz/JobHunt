from bs4 import BeautifulSoup
import json
import re

def parse_jobs():
    file_path = r'C:\Users\pini_\.gemini\antigravity\brain\b0f85213-9dca-4a95-9bab-52d2c1f45702\.system_generated\steps\317\content.md'
    
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    # Drushim job containers are typically div.job-item
    job_items = soup.find_all("div", class_="job-item")
    print(f"Found {len(job_items)} job items with class 'job-item'.")
    
    parsed_jobs = []
    
    for idx, item in enumerate(job_items):
        # Extract title
        title_el = item.find(class_="job-title") or item.find("h3") or item.find("a")
        title = title_el.text.strip() if title_el else "Unknown Title"
        
        # URL
        url = ""
        link_el = item.find("a", href=True)
        if link_el:
            url = link_el["href"]
            if url.startswith("/"):
                url = "https://www.drushim.co.il" + url
                
        # Company
        company_el = item.find(class_="job-hdr") or item.find(class_="company-name")
        # In Drushim, company might be in a span or div
        # Let's inspect text inside header or sub-headers
        company = "Unknown Company"
        if company_el:
            company = company_el.text.strip()
            
        # Location
        # Let's inspect location text. Often in class "job-details-sub" or text with icon
        location_el = item.find(class_="job-details-sub") or item.find(class_="job-intro")
        location = "Unknown Location"
        if location_el:
            location = location_el.text.strip()
            # Often includes hours, fields, etc. Let's clean it up
            
        # Description / Requirements
        desc_el = item.find(class_="job-details-top") or item.find(class_="job-intro")
        description = desc_el.text.strip() if desc_el else ""
        
        parsed_jobs.append({
            "index": idx,
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "url": url
        })
        
    print("\n--- SAMPLE PARSED JOBS ---")
    for j in parsed_jobs[:5]:
        print(f"Title: {j['title']}")
        print(f"Company: {j['company']}")
        print(f"Location: {j['location']}")
        print(f"URL: {j['url']}")
        print(f"Desc snippet: {j['description'][:100]}...")
        print("-" * 30)

if __name__ == "__main__":
    parse_jobs()
