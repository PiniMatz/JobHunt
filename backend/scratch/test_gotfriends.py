import requests
from bs4 import BeautifulSoup

def test_gotfriends():
    # GotFriends product manager jobs page search
    # Let's test the general jobs page first
    url = "https://www.gotfriends.co.il/jobs/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"GotFriends Status: {r.status_code}")
        print(f"HTML length: {len(r.text)}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            print(f"Title: {soup.title.text.strip().encode('utf-8')}")
            
            # Let's search for divs representing jobs
            job_divs = soup.find_all(class_=lambda x: x and ("job" in x.lower() or "item" in x.lower()))
            print(f"Found {len(job_divs)} divs with 'job' or 'item' in class name.")
            
            # Let's print some class names
            classes = set()
            for div in job_divs[:20]:
                for c in div.get("class", []):
                    classes.add(c)
            print(f"Sample class names: {list(classes)}")
            
            # Let's search for links
            links = soup.find_all("a", href=True)
            job_links = [l["href"] for l in links if "/jobs/" in l["href"]]
            print(f"Found {len(job_links)} links containing '/jobs/'")
            print(f"Sample links: {[l.encode('utf-8') for l in job_links[:5]]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gotfriends()
