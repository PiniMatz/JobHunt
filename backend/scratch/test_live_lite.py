import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def test_lite_search():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Origin": "https://lite.duckduckgo.com",
        "Referer": "https://lite.duckduckgo.com/"
    }
    
    url = "https://lite.duckduckgo.com/lite/"
    # We query for Product Manager jobs in Netanya
    data = {
        "q": 'site:il.linkedin.com/jobs/view "Product Manager" Netanya'
    }
    
    print(f"Querying DuckDuckGo Lite: {url} with '{data['q']}'")
    response = requests.post(url, data=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print("Failed to fetch Lite page.")
        return
        
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    
    # DuckDuckGo Lite results links are typically inside td.result-snippet or a forms
    # Let's inspect all links
    for a in soup.find_all("a"):
        href = a.get("href", "")
        # Inspect for clean redirect or direct link
        # DDG Lite has links like /l/?kh=-1&uddg=https%3A%2F%2Fil.linkedin.com%2Fjobs%2Fview%2F...
        if "uddg=" in href:
            match = re.search(r"uddg=(https%3A%2F%2F[^&]+)", href)
            if match:
                clean_url = urllib.parse.unquote(match.group(1))
                if "linkedin.com/jobs/view" in clean_url:
                    links.append(clean_url)
        elif "linkedin.com/jobs/view" in href:
            links.append(href)
            
    print(f"Found {len(links)} LinkedIn job URLs:")
    for link in links:
        print(f" - {link}")
        
    if links:
        # Test fetching the first LinkedIn job details
        test_link = links[0]
        print(f"\nScraping details for: {test_link}")
        res = requests.get(test_link, headers=headers)
        print(f"Status Code: {res.status_code}")
        
        detail_soup = BeautifulSoup(res.text, "html.parser")
        og_title = detail_soup.find("meta", property="og:title")
        title_text = og_title["content"] if og_title else "Unknown Title"
        print(f"Meta Title: {title_text}")

if __name__ == "__main__":
    test_lite_search()
