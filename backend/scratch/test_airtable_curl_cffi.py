from curl_cffi import requests
import re
import json
import urllib.parse

def test():
    s = requests.Session()
    
    url_embed = "https://airtable.com/embed/appwewqLk7iUY4azc/shrQBuWjXd0YgPqV6?backgroundColor=cyan&viewControls=on"
    r1 = s.get(url_embed, impersonate="chrome")
    print("Embed status:", r1.status_code)
    
    match = re.search(r"window\.initData\s*=\s*(\{.*\});", r1.text)
    if not match:
        print("No initData found")
        return
        
    init_data = json.loads(match.group(1))
    
    app_id = list(init_data['rawApplications'].keys())[0]
    view_id = init_data['sharedViewId']
    csrf = init_data['csrfToken']
    access_policy = init_data['accessPolicy']
    
    # Structure parameters
    params = {
        "shouldUseNestedResponseFormat": True,
        "accessPolicy": access_policy
    }
    stringified_params = json.dumps(params)
    encoded_params = urllib.parse.quote(stringified_params)
    
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'x-airtable-application-id': app_id,
        'x-airtable-page-load-id': init_data['pageLoadId'],
        'x-airtable-inter-service-client': 'webClient',
        'x-csrf-token': csrf,
        'x-user-locale': 'en'
    }
    
    url_api = f"https://airtable.com/v0.3/view/{view_id}/readSharedViewData?stringifiedObjectParams={encoded_params}"
    r2 = s.get(url_api, headers=headers, impersonate="chrome")
    print("API status:", r2.status_code)
    print("Response Length:", len(r2.text))
    if r2.status_code == 200:
        res_data = r2.json()
        print("Keys:", list(res_data.keys()))
        if "data" in res_data:
            rows = res_data["data"].get("rows", [])
            print(f"Total rows: {len(rows)}")
    else:
        print("Response text:", r2.text[:500])

if __name__ == "__main__":
    test()
