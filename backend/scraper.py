import os
import re
import json
import random
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from database import get_settings

# Mock jobs data removed to enforce 100% real crawling only.

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
            print(f"JobMaster: matched {len(jobs)} jobs.")
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
                print(f"GotFriends: matched {len(jobs)} jobs.")
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
    
    # 1. Scrape Drushim (Pages 1 to 10)
    for page in range(1, 11):
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
                            print("Drushim match found. Fetching full details...")
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

    # 4. Scrape Secret Tel Aviv
    try:
        secrettelaviv_jobs = scrape_secrettelaviv(target_locations)
        jobs.extend(secrettelaviv_jobs)
    except Exception as e:
        print(f"Error executing Secret Tel Aviv scraper flow: {e}")

    print(f"Combined scraper: parsed {len(jobs)} matching jobs in total.")
    return jobs

def scrape_secrettelaviv(target_locations: list) -> list:
    """Scrape Secret Tel Aviv Jobs for active Product Manager listings."""
    jobs = []
    url = "https://jobs.secrettelaviv.com/?s=product+manager"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    print(f"Scraping Secret Tel Aviv listings: {url}")
    try:
        from curl_cffi import requests as c_requests
        s = c_requests.Session()
        r = s.get(url, headers=headers, impersonate="chrome", timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            job_items = soup.find_all(class_=re.compile(r"post-\d+"))
            print(f"Found {len(job_items)} raw job elements on Secret Tel Aviv.")
            
            for item in job_items:
                # Title
                title_el = item.find(class_="post-title")
                if not title_el:
                    continue
                title = title_el.text.strip()
                
                # Link
                link_el = title_el.find("a")
                job_url = link_el["href"] if link_el else ""
                
                # Default values
                company = "Secret Tel Aviv Client"
                location = "Tel Aviv"
                description = ""
                
                # Fetch full details using curl_cffi session to bypass WAF
                if job_url:
                    try:
                        print("Fetching Secret Tel Aviv details...")
                        r_detail = s.get(job_url, headers={"Referer": url}, impersonate="chrome", timeout=6)
                        if r_detail.status_code == 200:
                            soup_detail = BeautifulSoup(r_detail.text, "html.parser")
                            
                            # Parse Company
                            company_el = soup_detail.find(class_="wpjb-top-header-title")
                            if company_el and company_el.contents:
                                company = company_el.contents[0].strip()
                                
                            # Parse Description
                            desc_el = soup_detail.find(class_="post-content")
                            if desc_el:
                                raw_text = desc_el.text.strip()
                                if "Description" in raw_text:
                                    description = raw_text.split("Description", 1)[1].strip()
                                else:
                                    description = raw_text
                    except Exception as ed:
                        print(f"Error fetching Secret Tel Aviv job page: {ed}")
                        
                # Fallback to search list snippet description if fetching detail page failed
                if not description:
                    list_desc_el = item.find(class_="post-content")
                    description = list_desc_el.text.strip() if list_desc_el else ""
                
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
            print(f"Secret Tel Aviv: matched {len(jobs)} jobs.")
    except Exception as e:
        print(f"Error scraping Secret Tel Aviv: {e}")
    return jobs
