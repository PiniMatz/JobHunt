import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

def test_google_drushim():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    # Query Google for Drushim PM Netanya jobs
    query = 'site:drushim.co.il "product manager" Netanya'
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    
    print(f"Querying Google for Drushim: {url}")
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    links = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/url?q=" in href:
                match = re.search(r"q=(https://www\.drushim\.co\.il/[^&]+)", href)
                if match:
                    clean_url = urllib.parse.unquote(match.group(1))
                    links.append(clean_url)
            elif href.startswith("http") and "drushim.co.il" in href:
                links.append(href)
                
    print(f"\nFound {len(links)} Drushim job links:")
    for l in links[:10]:
        print(f" - {l}")
        
    if links:
        target_job = links[0]
        print(f"\nScraping Drushim Job: {target_job}")
        res_job = requests.get(target_job, headers=headers)
        print(f"Drushim Status Code: {res_job.status_code}")
        
        job_soup = BeautifulSoup(res_job.text, "html.parser")
        
        # Extract title
        title_tag = job_soup.find("h1")
        title_text = title_tag.text.strip() if title_tag else "No Title tag"
        print(f"H1 Title: {title_text}")
        
        # Look for description (Drushim description container is usually a specific div class)
        # We can dump some text or classes to check
        desc_div = job_soup.find("div", class_="job-instruction") or job_soup.find("div", class_="job-description")
        if desc_div:
            print(f"Description container found! Content (first 300 chars):")
            print(desc_div.get_text().strip()[:300])
        else:
            # Fallback print body text snippet
            print("Description container not found. Page text snippet:")
            body_text = job_soup.get_text()
            print(body_text[:500].strip())

if __name__ == "__main__":
    test_google_drushim()
