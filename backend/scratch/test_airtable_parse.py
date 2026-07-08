import requests
from bs4 import BeautifulSoup
import re
import json

def test_parse():
    url = "https://airtable.com/embed/appwewqLk7iUY4azc/shrQBuWjXd0YgPqV6?backgroundColor=cyan&viewControls=on"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        script = None
        for s in soup.find_all("script"):
            if "window.initData =" in s.text:
                script = s.text
                break
                
        if not script:
            print("No initData script found.")
            return
            
        # Match JSON string
        match = re.search(r"window\.initData\s*=\s*(\{.*?\});\n", script)
        if not match:
            # Try a broader match
            match = re.search(r"window\.initData\s*=\s*(\{.*\});", script)
            
        if match:
            json_str = match.group(1)
            data = json.loads(json_str)
            print("Successfully loaded JSON!")
            print("Keys:", list(data.keys()))
            
            # Let's explore nested structures
            # Airtable embeds usually store data under 'embedPageData' or similar keys
            for k, v in data.items():
                if isinstance(v, dict):
                    print(f" - Key: {k}, Sub-keys: {list(v.keys())}")
                    
            # Let's look for records
            embed_page_data = data.get("embedPageData", {})
            if embed_page_data:
                # Check for columns and rows
                table_schemas = embed_page_data.get("tableSchemas", [])
                print(f"Found {len(table_schemas)} table schemas.")
                
                # Check for rows / records
                # Sometimes it is under embedPageData['initialMinSchemaAndData']['tableSchemas'][0]['rows']
                initial_data = embed_page_data.get("initialMinSchemaAndData", {})
                if initial_data:
                    schemas = initial_data.get("tableSchemas", [])
                    for i, s in enumerate(schemas):
                        rows = s.get("rows", [])
                        columns = s.get("columns", [])
                        print(f"Schema {i}: {len(rows)} rows, {len(columns)} columns.")
                        if rows:
                            print("Sample row:", rows[0])
                        if columns:
                            print("Columns:", [c.get("name") for c in columns])
        else:
            print("Failed to match regex.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_parse()
