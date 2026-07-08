import requests
from bs4 import BeautifulSoup

def test_page(page_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(page_url, headers=headers, timeout=5)
        print(f"URL: {page_url} -> Status: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            job_items = soup.find_all("div", class_="job-item")
            print(f"  Found {len(job_items)} job elements.")
            if job_items:
                title_el = job_items[0].find("span", class_="job-url") or job_items[0].find("h3")
                print(f"  First title: {title_el.text.strip() if title_el else 'None'}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    print("Testing page 2 formats:")
    test_page("https://www.drushim.co.il/jobs/search/product%20manager/2/")
    test_page("https://www.drushim.co.il/jobs/search/product%20manager/?page=2")
    test_page("https://www.drushim.co.il/jobs/search/product%20manager/?p=2")
