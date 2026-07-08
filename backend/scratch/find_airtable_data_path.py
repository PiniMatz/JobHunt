import requests
import re
import json

def find_val(d, val_lower, path=''):
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, str) and val_lower in v.lower():
                print(f"Found string containing '{val_lower}' at: {path}.{k} -> {v[:100]}")
            find_val(v, val_lower, f"{path}.{k}")
    elif isinstance(d, list):
        for i, item in enumerate(d):
            if isinstance(item, str) and val_lower in item.lower():
                print(f"Found string containing '{val_lower}' at: {path}[{i}] -> {item[:100]}")
            find_val(item, val_lower, f"{path}[{i}]")

def test():
    url = "https://airtable.com/embed/appwewqLk7iUY4azc/shrQBuWjXd0YgPqV6?backgroundColor=cyan&viewControls=on"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        match = re.search(r"window\.initData\s*=\s*(\{.*\});", r.text)
        if match:
            data = json.loads(match.group(1))
            print("Searching for 'Product'...")
            find_val(data, "product")
        else:
            print("No regex match.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
