import requests
import re
import urllib.parse
import json

def test():
    url = "https://airtable.com/embed/appwewqLk7iUY4azc/shrQBuWjXd0YgPqV6?backgroundColor=cyan&viewControls=on"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        # Search for stringifiedObjectParams
        matches = re.findall(r"stringifiedObjectParams=([^&\"\'\\]+)", r.text)
        print(f"Found {len(matches)} stringifiedObjectParams matches:")
        for m in set(matches):
            decoded = urllib.parse.unquote(m)
            print(f"Decoded: {decoded}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
