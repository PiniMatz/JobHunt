import requests
from bs4 import BeautifulSoup

def test_goozali():
    url = "https://en.goozali.com/jobs/search?q=product+manager"
    # Wait, let's check if goozali is open and what it returns
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"Goozali Status: {r.status_code}, HTML length: {len(r.text)}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            print(f"Goozali Title: {soup.title.text.strip() if soup.title else 'None'}")
            
            # Search for job blocks
            job_links = [a.get("href") for a in soup.find_all("a", href=True) if "/jobs/" in a.get("href")]
            print(f"Goozali: found {len(job_links)} links containing /jobs/")
            print(f"Sample Goozali links: {job_links[:5]}")
    except Exception as e:
        print(f"Goozali Error: {e}")

def test_secrettelaviv():
    url = "https://jobs.secrettelaviv.com/?s=product+manager"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"SecretTelAviv Status: {r.status_code}, HTML length: {len(r.text)}")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            print(f"SecretTelAviv Title: {soup.title.text.strip() if soup.title else 'None'}")
            
            # Search for job blocks
            job_links = [a.get("href") for a in soup.find_all("a", href=True) if "/jobs/" in a.get("href") or "/job/" in a.get("href")]
            print(f"SecretTelAviv: found {len(job_links)} links containing /job/")
            print(f"Sample SecretTelAviv links: {job_links[:5]}")
    except Exception as e:
        print(f"SecretTelAviv Error: {e}")

if __name__ == "__main__":
    print("Testing Goozali:")
    test_goozali()
    print("\nTesting Secret Tel Aviv:")
    test_secrettelaviv()
