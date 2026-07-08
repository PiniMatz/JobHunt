import requests
from bs4 import BeautifulSoup
import re

def test_search():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Query DuckDuckGo HTML search using POST (often more robust against 202 redirects)
    url = "https://html.duckduckgo.com/html/"
    data = {
        "q": 'site:il.linkedin.com/jobs/view "Product Manager" Netanya'
    }
    
    print(f"Querying DuckDuckGo POST: {url} with query '{data['q']}'")
    response = requests.post(url, data=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print("Failed to fetch search page. Trying simple GET fallback...")
        url_get = f"https://html.duckduckgo.com/html/?q=site:il.linkedin.com/jobs/view+Product+Manager+Netanya"
        response = requests.get(url_get, headers=headers)
        print(f"GET Fallback Status Code: {response.status_code}")
        
    if response.status_code != 200:
        print("Failed both methods.")
        return
        
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    
    # Extract links from DuckDuckGo results
    for a in soup.find_all("a", class_="result__snippet"):
        # Let's inspect the href attributes in parent container or snippet
        pass
        
    # The links are actually inside 'a.result__url' or 'a.result__snippet'
    for a in soup.find_all("a", class_="result__url"):
        href = a.get("href", "")
        # DuckDuckGo links sometimes redirect: we need to clean them
        # e.g., /l/?kh=-1&uddg=https%3A%2F%2Fil.linkedin.com%2Fjobs%2Fview%2F...
        if "uddg=" in href:
            match = re.search(r"uddg=(https%3A%2F%2F[^&]+)", href)
            if match:
                import urllib.parse
                clean_url = urllib.parse.unquote(match.group(1))
                if "linkedin.com/jobs/view" in clean_url:
                    links.append(clean_url)
        elif "linkedin.com/jobs/view" in href:
            links.append(href)
            
    print(f"Found {len(links)} LinkedIn job URLs:")
    for link in links:
        print(f" - {link}")
        
    # Test scraping details of the first link
    if links:
        test_link = links[0]
        print(f"\nScraping details for: {test_link}")
        res = requests.get(test_link, headers=headers)
        print(f"Status Code: {res.status_code}")
        
        detail_soup = BeautifulSoup(res.text, "html.parser")
        
        # og:title contains "Title at Company"
        og_title = detail_soup.find("meta", property="og:title")
        title_text = og_title["content"] if og_title else "Unknown Title"
        print(f"Meta Title: {title_text}")
        
        # Try extracting description
        desc_div = detail_soup.find("div", class_="show-more-less-html__markup")
        if desc_div:
            desc_text = desc_div.get_text(separator="\n").strip()
            print("Extracted Description (first 200 chars):")
            print(desc_text[:200])
        else:
            meta_desc = detail_soup.find("meta", name="description")
            desc_text = meta_desc["content"] if meta_desc else "No description found"
            print(f"Meta Description: {desc_text}")

if __name__ == "__main__":
    test_search()
