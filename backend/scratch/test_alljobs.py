import requests
from bs4 import BeautifulSoup

def test_alljobs():
    url = "https://www.alljobs.co.il/SearchResults.aspx?key=product%20manager"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"AllJobs Status: {r.status_code}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            # AllJobs listings usually have class "open-board" or "job-item" or similar
            # Let's write the response snippet length and save HTML to check classes
            print(f"HTML length: {len(r.text)}")
            # Search for typical elements
            job_divs = soup.find_all(class_=lambda x: x and ("job" in x or "board" in x))
            print(f"Found {len(job_divs)} divs with 'job' or 'board' in class name.")
            
            # Let's inspect some text to see if there are job titles
            titles = [t.text.strip() for t in soup.find_all("h3")]
            print(f"Found h3 tags: {titles[:10]}")
            
            # Let's find links containing /JobDetails/ or similar
            links = soup.find_all("a", href=True)
            job_links = [l["href"] for l in links if "/JobDetails/" in l["href"]]
            print(f"Found {len(job_links)} job details links.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_alljobs()
