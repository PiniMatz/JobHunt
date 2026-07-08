import requests

def test_engines():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    engines = {
        "DuckDuckGo HTML GET": "https://html.duckduckgo.com/html/?q=Product+Manager+Netanya",
        "DuckDuckGo Lite GET": "https://lite.duckduckgo.com/lite/?q=Product+Manager+Netanya",
        "Google": "https://www.google.com/search?q=Product+Manager+Netanya",
        "Bing": "https://www.bing.com/search?q=Product+Manager+Netanya",
        "Yahoo": "https://search.yahoo.com/search?q=Product+Manager+Netanya"
    }
    
    for name, url in engines.items():
        try:
            r = requests.get(url, headers=headers, timeout=5)
            print(f"{name}: Status {r.status_code}, Length {len(r.text)}")
            if r.status_code == 200:
                print(f" -> SUCCESS! First 100 chars: {r.text[:100].strip()}")
        except Exception as e:
            print(f"{name} Error: {e}")

if __name__ == "__main__":
    test_engines()
