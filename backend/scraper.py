import os
import json
import random
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from database import get_settings

MOCK_JOBS = [
    {
        "title": "Technical Product Manager - Cloud Infrastructure",
        "company": "CyShield Technologies",
        "location": "Netanya",
        "url": "https://example.com/jobs/cyshield-tech-pm",
        "description": (
            "We are seeking a Technical Product Manager to lead our Cloud Infrastructure team. "
            "You will own the roadmap for our core platform, APIs, and cloud services (AWS/GCP). "
            "Requirements:\n"
            "- 3+ years of experience as a Product Manager in a technical domain.\n"
            "- Strong engineering background (former software engineer or DevOps highly preferred).\n"
            "- Deep understanding of microservices architecture, Docker, Kubernetes, and API design.\n"
            "- Excellent communication skills and experience writing technical specifications."
        )
    },
    {
        "title": "Senior Data Product Manager - Analytics Platform",
        "company": "ShopSmart Global",
        "location": "Netanya",
        "url": "https://example.com/jobs/shopsmart-senior-data-pm",
        "description": (
            "As a Senior Data Product Manager, you will define the vision and strategy for our enterprise "
            "data platform. You will work closely with Data Engineers, Data Scientists, and BI analysts to "
            "build robust data pipelines, analytics products, and ML-driven features.\n"
            "Requirements:\n"
            "- 5+ years of PM experience with a proven track record of shipping data products.\n"
            "- Strong SQL skills and experience with Snowflake, BigQuery, or Redshift.\n"
            "- Experience building ET/ELT pipelines, data lakes, and data warehouses.\n"
            "- Understanding of machine learning models and predictive analytics."
        )
    },
    {
        "title": "Product Manager - AI & Advanced Analytics",
        "company": "DriveVision",
        "location": "Netanya",
        "url": "https://example.com/jobs/drivevision-ai-pm",
        "description": (
            "DriveVision is a pioneer in autonomous driving technology. We are looking for an AI PM "
            "to lead our perception data platform. You will guide the development of data pipelines "
            "that process terabytes of sensor data and train computer vision models.\n"
            "Requirements:\n"
            "- Experience in AI, machine learning, or deep learning product management.\n"
            "- Deep understanding of computer vision or large-scale data ingestion.\n"
            "- Technical background in CS, Engineering, or Mathematics.\n"
            "- Hands-on attitude and familiarity with Python/SQL."
        )
    },
    {
        "title": "Product Manager - Growth & Conversion",
        "company": "PlayApex Studios",
        "location": "Netanya",
        "url": "https://example.com/jobs/playapex-growth-pm",
        "description": (
            "We are looking for a Growth Product Manager to optimize our user acquisition and monetization "
            "funnels. You will run A/B tests, analyze user behavior, and coordinate closely with marketing "
            "and UI/UX designers to increase retention and revenue.\n"
            "Requirements:\n"
            "- 2+ years of PM experience in mobile gaming or B2C SaaS.\n"
            "- Strong analytic mindset (Mixpanel, Amplitude, GA).\n"
            "- Experience with rapid experimentation and product-led growth strategies.\n"
            "- High empathy and passion for user experience design."
        )
    },
    {
        "title": "Technical Product Manager - Data & Integrations",
        "company": "FinFlow Solutions",
        "location": "Tel Aviv",  # Outside Netanya to test location filter
        "url": "https://example.com/jobs/finflow-data-pm",
        "description": (
            "FinFlow is building the next generation of financial integrations. We are looking for a Technical "
            "Product Manager to own our third-party API integrations and core data pipeline reliability.\n"
            "Requirements:\n"
            "- Experience managing API products, webhooks, and integrations.\n"
            "- Background in fintech or payment processing preferred.\n"
            "- Solid technical skills: reading API code, understanding databases, querying with SQL."
        )
    },
    {
        "title": "Director of Product - Platform & Security",
        "company": "SecureGrid",
        "location": "Netanya",
        "url": "https://example.com/jobs/securegrid-director",
        "description": (
            "Lead the product organization for SecureGrid's developer platforms. You will manage a team of PMs "
            "focusing on security protocols, network architectures, and global scaling.\n"
            "Requirements:\n"
            "- 8+ years of product management leadership.\n"
            "- Strong expertise in Cybersecurity, SaaS, and Enterprise infrastructure.\n"
            "- Excellent business acumen and stakeholder communication."
        )
    }
]

def fetch_mock_jobs(target_locations: list) -> list:
    """Generate mock jobs matching the target locations."""
    matched_jobs = []
    for job in MOCK_JOBS:
        # Check if the job's location is in our target list (case-insensitive)
        if any(loc.lower() in job["location"].lower() for loc in target_locations):
            # Create a copy and add a slightly random date found
            job_copy = job.copy()
            days_ago = random.randint(0, 3)
            job_copy["date_found"] = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            matched_jobs.append(job_copy)
    return matched_jobs

LOCATION_TRANSLATIONS = {
    "netanya": ["netanya", "natanya", "נתניה"],
    "tel aviv": ["tel aviv", "tel-aviv", "תל אביב", "ת\"א", "מרכז"],
    "herzliya": ["herzliya", "הרצליה"],
    "raanana": ["raanana", "רעננה"],
    "kfar saba": ["kfar saba", "כפר סבא"],
    "hod hasharon": ["hod hasharon", "הוד השרון"],
    "petah tikva": ["petah tikva", "פתח תקווה", "פתח-תקווה", "פ\"ת"],
    "haifa": ["haifa", "חיפה"]
}

def match_location(job_loc: str, target_locs: list) -> bool:
    """Check if job location matches target locations (case and translation-aware)."""
    job_loc_lower = job_loc.lower()
    for target in target_locs:
        target_clean = target.strip().lower()
        if not target_clean:
            continue
        
        # Check translation dictionary for variations (handles Hebrew/English mappings)
        if target_clean in LOCATION_TRANSLATIONS:
            variations = LOCATION_TRANSLATIONS[target_clean]
            if any(var in job_loc_lower for var in variations):
                return True
        else:
            # Substring match fallback for custom locations
            if target_clean in job_loc_lower:
                return True
    return False

def scrape_full_job_description(url: str, headers: dict) -> str:
    """Fetch the full description and requirements from the direct job page."""
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            desc_el = soup.find(class_="jobDes")
            req_el = soup.find(class_="job-requirements")
            
            description_parts = []
            if desc_el:
                description_parts.append(desc_el.get_text().strip())
            if req_el:
                description_parts.append(req_el.get_text().strip())
                
            if description_parts:
                return "\n\n".join(description_parts)
    except Exception as e:
        print(f"Error fetching full description from {url}: {e}")
    return ""

def scrape_jobmaster(target_locations: list) -> list:
    """Scrape JobMaster page 1 for 'מנהל מוצר' listings."""
    jobs = []
    url = "https://www.jobmaster.co.il/jobs/?q=%D7%9E%D7%A0%D7%94%D7%9C+%D7%9E%D7%95%D7%A6%D7%A8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    print(f"Scraping JobMaster listings: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            job_items = soup.find_all(class_="JobItem")
            print(f"Found {len(job_items)} raw job elements on JobMaster.")
            
            for item in job_items:
                # Title
                title_el = item.find(class_="CardHeader") or item.find("h2") or item.find("h3")
                title = title_el.text.strip() if title_el else ""
                
                # Company
                company_el = item.find(class_="ByTitle")
                company = company_el.text.strip() if company_el else "Unknown"
                
                # Location
                location_el = item.find(class_="jobLocation")
                location = location_el.text.strip() if location_el else "Unknown"
                
                # Description
                desc_el = item.find(class_="jobShortDescription")
                description = desc_el.text.strip() if desc_el else ""
                
                # Extract Job ID for direct URL
                job_url = ""
                onclick = item.get("onclick", "")
                import re
                match = re.search(r"ModaaClick\((\d+)", onclick)
                if match:
                    job_id = match.group(1)
                    job_url = f"https://www.jobmaster.co.il/jobs/?q={job_id}"
                else:
                    # Fallback to search term search link
                    job_url = "https://www.jobmaster.co.il/jobs/?q=%D7%9E%D7%A0%D7%94%D7%9C+%D7%9E%D7%95%D7%A6%D7%A8"
                
                # Filter by location (translation-aware check)
                if title and match_location(location, target_locations):
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": job_url,
                        "description": description,
                        "date_found": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            print(f"JobMaster: matched {len(jobs)} jobs for locations {target_locations}")
    except Exception as e:
        print(f"Error scraping JobMaster: {e}")
    return jobs

def scrape_gotfriends(target_locations: list) -> list:
    """Scrape GotFriends for active Product Manager listings."""
    jobs = []
    url = "https://www.gotfriends.co.il/jobslobby/projects/product-manager/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    print(f"Scraping GotFriends listings: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            list_div = soup.find(class_="jobs_list")
            if list_div:
                job_items = list_div.find_all(class_="item")
                print(f"Found {len(job_items)} raw job elements on GotFriends.")
                
                for item in job_items:
                    # Title & link
                    title_el = item.find("h2", class_="title") or item.find(class_="title")
                    title = title_el.text.strip() if title_el else ""
                    
                    link_el = item.find("a", class_="position") or item.find("a")
                    job_url = ""
                    if link_el and link_el.has_attr("href"):
                        job_url = link_el["href"]
                        if job_url.startswith("/"):
                            job_url = "https://www.gotfriends.co.il" + job_url
                            
                    # Location
                    loc_el = item.find(class_="info-data")
                    location = loc_el.text.strip() if loc_el else "Unknown"
                    
                    # Description (combination of desc divs)
                    desc_divs = item.find_all(class_="desc")
                    description = "\n\n".join([d.text.strip() for d in desc_divs]) if desc_divs else ""
                    
                    # Company
                    company = "GotFriends Tech Client"
                    
                    # Filter by location (translation-aware check)
                    if title and match_location(location, target_locations):
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "url": job_url,
                            "description": description,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                print(f"GotFriends: matched {len(jobs)} jobs for locations {target_locations}")
    except Exception as e:
        print(f"Error scraping GotFriends: {e}")
    return jobs

def search_live_jobs(target_locations: list, query: str = "Product Manager") -> list:
    """
    Scrape jobs from Drushim (pages 1-3), JobMaster (page 1), and GotFriends, then filter.
    Falls back to mock jobs on failure or if no jobs match.
    """
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    # 1. Scrape Drushim (Pages 1 to 3)
    for page in range(1, 4):
        if page == 1:
            search_url = "https://www.drushim.co.il/jobs/search/product%20manager/"
        else:
            search_url = f"https://www.drushim.co.il/jobs/search/product%20manager/{page}/"
            
        print(f"Scraping Drushim listings (page {page}): {search_url}")
        
        try:
            r = requests.get(search_url, headers=headers, timeout=8)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                job_items = soup.find_all("div", class_="job-item")
                print(f"Drushim page {page}: found {len(job_items)} raw job elements.")
                
                for item in job_items:
                    # Parse title
                    title_el = item.find("span", class_="job-url") or item.find("h3")
                    title = title_el.text.strip() if title_el else ""
                    
                    # Parse link
                    url = ""
                    link_el = item.find("a", href=True)
                    if link_el:
                        url = link_el["href"]
                        if url.startswith("/"):
                            url = "https://www.drushim.co.il" + url
                            
                    # Parse company
                    company_el = item.find(class_="grow-none")
                    company = "Unknown"
                    if company_el:
                        company_span = company_el.find("span")
                        if company_span:
                            company = company_span.text.strip()
                            
                    # Parse location
                    location = "Unknown"
                    sub_el = item.find(class_="job-details-sub")
                    if sub_el:
                        loc_span = sub_el.find("span", class_="display-18")
                        if loc_span:
                            location = loc_span.get_text().split("|")[0].strip()
                            
                    # Filter by location (translation-aware check)
                    if title and match_location(location, target_locations):
                        # We get the brief summary description as initial fallback
                        summary_el = item.find(class_="job-intro")
                        description = summary_el.text.strip() if summary_el else ""
                        
                        # Fetch full description from the direct page (to run detailed LLM match)
                        if url:
                            print(f"Drushim match: {location}. Fetching full details for '{title}'...")
                            full_desc = scrape_full_job_description(url, headers)
                            if full_desc:
                                description = full_desc
                                
                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "url": url,
                            "description": description,
                            "date_found": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
            else:
                print(f"Failed to fetch Drushim page {page}: Status {r.status_code}")
        except Exception as e:
            print(f"Error scraping Drushim page {page}: {e}")

    # 2. Scrape JobMaster (Page 1)
    try:
        jobmaster_jobs = scrape_jobmaster(target_locations)
        jobs.extend(jobmaster_jobs)
    except Exception as e:
        print(f"Error executing JobMaster scraper flow: {e}")

    # 3. Scrape GotFriends
    try:
        gotfriends_jobs = scrape_gotfriends(target_locations)
        jobs.extend(gotfriends_jobs)
    except Exception as e:
        print(f"Error executing GotFriends scraper flow: {e}")

    print(f"Combined scraper: parsed {len(jobs)} matching jobs in total.")

    # 4. Fallback / Mock combination
    # If no live jobs matched, fall back to mock jobs so the user always has demo data to verify
    if not jobs:
        print("No live jobs matched target locations. Loading mock listings...")
        jobs = fetch_mock_jobs(target_locations)
        
    return jobs
