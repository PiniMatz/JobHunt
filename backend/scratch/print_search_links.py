import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

def dump_pages():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    
    query = 'Product Manager Netanya'
    
    # Test Google
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    print(f"Fetching Google: {url}")
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("title")
    print(f"Google Title: '{title.text if title else 'None'}' (Status: {r.status_code})")
    
    with open("google.html", "w", encoding="utf-8") as f:
        f.write(r.text)
        
    # Test Bing
    url_bing = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    print(f"Fetching Bing: {url_bing}")
    r_bing = requests.get(url_bing, headers=headers)
    soup_bing = BeautifulSoup(r_bing.text, "html.parser")
    title_bing = soup_bing.find("title")
    print(f"Bing Title: '{title_bing.text if title_bing else 'None'}' (Status: {r_bing.status_code})")
    
    with open("bing.html", "w", encoding="utf-8") as f:
        f.write(r_bing.text)
        
    print(f"Saved google.html and bing.html to {os.getcwd()}")

if __name__ == "__main__":
    dump_pages()
