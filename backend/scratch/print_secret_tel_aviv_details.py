from curl_cffi import requests
from bs4 import BeautifulSoup

def test_details():
    url = "https://jobs.secrettelaviv.com/job/staff-product-manager-2/"
    headers = {
        "Referer": "https://jobs.secrettelaviv.com/?s=product+manager",
    }
    try:
        r = requests.get(url, headers=headers, impersonate="chrome", timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Let's search for typical job-related selectors, like div with class "job-description" or "description"
        # Or standard WordPress elements
        print("Page Title:", soup.title.text.strip().encode('utf-8'))
        
        # Print headings
        print("Headings:", [h.text.strip().encode('utf-8') for h in soup.find_all(["h1", "h2", "h3"])])
        
        # Search for company name
        # Often it is in a meta tag or a specific header block
        company_div = soup.find(class_="company") or soup.find(class_="job-company") or soup.find(class_="job-details")
        if company_div:
            print("Company Div:", company_div.text.strip().encode('utf-8')[:300])
            
        # Try to find the main content / entry content area
        entry_content = soup.find(class_="entry-content") or soup.find(class_="job-description") or soup.find(class_="post-content")
        if entry_content:
            print("Found main content box!")
            # Print first 1000 characters of text
            print("Main text snippet:")
            print(entry_content.get_text().strip()[:1000].encode('utf-8'))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_details()
