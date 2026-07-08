import requests
import re
import json

def test():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    url_embed = "https://airtable.com/embed/appwewqLk7iUY4azc/shrQBuWjXd0YgPqV6?backgroundColor=cyan&viewControls=on"
    r1 = s.get(url_embed)
    print("Embed Status:", r1.status_code)
    
    match = re.search(r"window\.initData\s*=\s*(\{.*\});", r1.text)
    if not match:
        print("No initData found")
        return
        
    init_data = json.loads(match.group(1))
    
    app_id = list(init_data['rawApplications'].keys())[0]
    view_id = init_data['sharedViewId']
    csrf = init_data['csrfToken']
    
    headers = {
        'Referer': url_embed,
        'X-Requested-With': 'XMLHttpRequest',
        'x-airtable-application-id': app_id,
        'x-airtable-page-load-id': init_data['pageLoadId'],
        'x-airtable-inter-service-client': 'webClient',
        'x-csrf-token': csrf,
        'x-user-locale': 'en'
    }
    
    url_api = f"https://airtable.com/v0.3/view/{view_id}/readSharedViewData?stringifiedObjectParams=%7B%22shouldUseNestedResponseFormat%22%3Atrue%7D"
    r2 = s.get(url_api, headers=headers)
    print("API Status:", r2.status_code)
    print("Response Length:", len(r2.text))
    if r2.status_code == 200:
        res_data = r2.json()
        print("Keys:", list(res_data.keys()))
        if "data" in res_data:
            rows = res_data["data"].get("rows", [])
            print(f"Total rows retrieved: {len(rows)}")
    else:
        print("Response text:", r2.text[:500])

if __name__ == "__main__":
    test()
