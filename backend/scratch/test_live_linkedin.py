import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

def test_live_linkedin():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    # Query Google Search with a simpler query
    query = 'Product Manager Netanya site:linkedin.com'
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    
    print(f"Querying Google Search: {url}")
    response = requests.get(url, headers=headers)
    print(f"Google Status Code: {response.status_code}")
    
    links = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/url?q=" in href:
                match = re.search(r"q=(https://[^&]+)", href)
                if match:
                    clean = urllib.parse.unquote(match.group(1))
                    if "linkedin.com" in clean and clean.startswith("http"):
                        links.append(clean)
            elif href.startswith("http") and "linkedin.com" in href:
                links.append(href)
                
    print(f"Found {len(links)} LinkedIn links via Google:")
    for l in links[:15]:
        print(f" - {l}")
        
    # If no links from Google, try Bing
    if not links:
        url_bing = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        print(f"\nQuerying Bing Search: {url_bing}")
        res_bing = requests.get(url_bing, headers=headers)
        print(f"Bing Status: {res_bing.status_code}")
        if res_bing.status_code == 200:
            soup = BeautifulSoup(res_bing.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and "linkedin.com" in href:
                    links.append(href)
            print(f"Found {len(links)} LinkedIn links via Bing:")
            for l in links[:15]:
                print(f" - {l}")

    # Crawl first link to check details
    if links:
        target_link = links[0]
        # Clean target URL (remove query parameters)
        target_link = re.sub(r"\?.*$", "", target_link)
        print(f"\nCrawling LinkedIn Job: {target_link}")
        
        # We need custom headers to make LinkedIn return the public page (not login page)
        linkedin_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        res_job = requests.get(target_link, headers=linkedin_headers)
        print(f"LinkedIn Status Code: {res_job.status_code}")
        
        job_soup = BeautifulSoup(res_job.text, "html.parser")
        
        # Try finding title
        og_title = job_soup.find("meta", property="og:title")
        meta_title = og_title["content"] if og_title else ""
        
        title_tag = job_soup.find("title")
        page_title = title_tag.text if title_tag else ""
        
        print(f"Meta Title: {meta_title}")
        print(f"Page Title: {page_title}")
        
        # Try finding description
        desc_div = job_soup.find("div", class_="show-more-less-html__markup")
        if desc_div:
            print("\nFound description class show-more-less-html__markup!")
            print(desc_div.get_text()[:400].strip())
        else:
            meta_desc = job_soup.find("meta", name="description")
            print(f"\nMeta Description: {meta_desc['content'] if meta_desc else 'None'}")

if __name__ == "__main__":
    test_live_linkedin()
