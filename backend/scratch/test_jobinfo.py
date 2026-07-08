import requests
from bs4 import BeautifulSoup

def test_jobinfo():
    url = "https://www.jobinfo.co.il/%D7%93%D7%A8%D7%95%D7%A9%D7%99%D7%9D-%D7%94%D7%99%D7%99%D7%98%D7%A7"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"JobInfo Status: {r.status_code}")
        print(f"HTML length: {len(r.text)}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            print(f"Title: {soup.title.text.strip().encode('utf-8') if soup.title else 'None'}")
            
            # Let's search for typical job-related selectors, or links
            links = soup.find_all("a", href=True)
            print(f"Total links: {len(links)}")
            
            # Print sample links that might represent jobs or search categories
            sample_links = [l["href"] for l in links if "job" in l["href"].lower() or "%d7%9e" in l["href"].lower()][:15]
            print(f"Sample links: {[l.encode('utf-8') for l in sample_links]}")
            
            # Let's search for form actions or search boxes
            forms = soup.find_all("form")
            print(f"Found {len(forms)} forms.")
            for f in forms:
                print(f" - Form Action: {f.get('action')}, Method: {f.get('method')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_jobinfo()
