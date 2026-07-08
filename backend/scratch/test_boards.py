import requests
from bs4 import BeautifulSoup

def test_boards():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    urls = {
        "IsraWork": "https://israwork.co.il/",
        "IsraWork Jobs": "https://israwork.co.il/jobs",
        "AllJobs": "https://www.alljobs.co.il/",
        "Drushim": "https://www.drushim.co.il/",
    }
    
    for name, url in urls.items():
        try:
            r = requests.get(url, headers=headers, timeout=5)
            print(f"{name}: Status {r.status_code}, Length {len(r.text)}")
            if r.status_code == 200:
                print(f" -> SUCCESS! Title: {BeautifulSoup(r.text, 'html.parser').find('title').text.strip()}")
        except Exception as e:
            print(f"{name} Error: {e}")

if __name__ == "__main__":
    test_boards()
