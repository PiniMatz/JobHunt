import requests

def test_import():
    url = "http://127.0.0.1:8000/api/jobs/import"
    payload = [
      {
        "title": "Staff Product Manager (Test Extension)",
        "company": "Extension Testing Corp",
        "location": "Tel Aviv",
        "url": "https://www.linkedin.com/jobs/view/test12345",
        "description": "This is a test description for the extension scraper to verify import endpoint works correctly."
      }
    ]
    try:
        r = requests.post(url, json=payload, timeout=5)
        print("Status Code:", r.status_code)
        print("Response Content:", r.json())
    except Exception as e:
        print("Failed to contact backend:", e)

if __name__ == "__main__":
    test_import()
