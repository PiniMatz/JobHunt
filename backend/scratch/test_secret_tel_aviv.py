import requests
from bs4 import BeautifulSoup
import re

def test_secret():
    url = "https://jobs.secrettelaviv.com/?s=product+manager"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Let's search for elements with class post-XXXX
        items = soup.find_all(class_=re.compile(r"post-\d+"))
        print(f"Total post-XXXX elements: {len(items)}")
        
        if items:
            first_item = items[0]
            print(f"First element class list: {first_item.get('class')}")
            print("\nPrettified HTML:")
            print(first_item.prettify()[:1500].encode('utf-8'))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_secret()
