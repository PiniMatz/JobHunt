import requests
from bs4 import BeautifulSoup

def test_jobmaster():
    url = "https://www.jobmaster.co.il/jobs/?q=%D7%9E%D7%A0%D7%94%D7%9C+%D7%9E%D7%95%D7%A6%D7%A8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"JobMaster Status: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            
            # JobMaster listings usually have class "jobItem" or similar.
            # Let's search for divs representing jobs
            job_items = soup.find_all("article", class_="jobItem") or soup.find_all("div", class_="jobItem")
            print(f"Found {len(job_items)} job items.")
            
            if not job_items:
                # Let's search for class containing "job"
                job_divs = soup.find_all(class_=lambda x: x and "job" in x.lower())
                print(f"Found {len(job_divs)} divs with 'job' in class name.")
                
            for item in job_items[:3]:
                # Title
                title_el = item.find("a", class_="jobTitle") or item.find("h2") or item.find("h3")
                title = title_el.text.strip() if title_el else "No Title"
                link = title_el["href"] if title_el and title_el.has_attr("href") else ""
                
                # Company
                company_el = item.find("a", class_="companyLink") or item.find(class_="company")
                company = company_el.text.strip() if company_el else "Unknown"
                
                # Location
                location_el = item.find(class_="jobLocation") or item.find(class_="location")
                location = location_el.text.strip() if location_el else "Unknown"
                
                print(f"  Title: {title}")
                print(f"  Link: {link}")
                print(f"  Company: {company}")
                print(f"  Location: {location}")
                print("---")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_jobmaster()
