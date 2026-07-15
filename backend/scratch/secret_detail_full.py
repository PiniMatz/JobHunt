from curl_cffi import requests
from bs4 import BeautifulSoup

def test():
    url = "https://jobs.secrettelaviv.com/job/staff-product-manager-2/"
    headers = {
        "Referer": "https://jobs.secrettelaviv.com/?s=product+manager",
    }
    try:
        r = requests.get(url, headers=headers, impersonate="chrome", timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        entry_content = soup.find(class_="entry-content")
        if entry_content:
            with open("scratch/secret_detail.txt", "w", encoding="utf-8") as f:
                f.write(entry_content.get_text().strip())
            print("Successfully wrote full details to scratch/secret_detail.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
