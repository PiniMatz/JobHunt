import requests
from bs4 import BeautifulSoup
import re

def print_drushim():
    print("\n--- Drushim Raw Locations ---")
    headers = {"User-Agent": "Mozilla/5.0"}
    locations_found = set()
    for page in range(1, 4):
        url = f"https://www.drushim.co.il/jobs/search/product%20manager/{page}/" if page > 1 else "https://www.drushim.co.il/jobs/search/product%20manager/"
        try:
            r = requests.get(url, headers=headers, timeout=8)
            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.find_all("div", class_="job-item")
            for item in items:
                title_el = item.find("span", class_="job-url") or item.find("h3")
                title = title_el.text.strip() if title_el else "Unknown Title"
                
                sub_el = item.find(class_="job-details-sub")
                location = "Unknown"
                if sub_el:
                    loc_span = sub_el.find("span", class_="display-18")
                    if loc_span:
                        location = loc_span.get_text().split("|")[0].strip()
                locations_found.add(location)
                print(f"Title: {title[:40]}, Location: {location}")
        except Exception as e:
            print(f"Error page {page}: {e}")
    print("Unique Locations:", list(locations_found))

def print_jobmaster():
    print("\n--- JobMaster Raw Locations ---")
    url = "https://www.jobmaster.co.il/jobs/?q=%D7%9E%D7%A0%D7%94%D7%9C+%D7%9E%D7%95%D7%A6%D7%A8"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all(class_="JobItem")
        for item in items:
            title_el = item.find(class_="CardHeader") or item.find("h2") or item.find("h3")
            title = title_el.text.strip() if title_el else "Unknown Title"
            loc_el = item.find(class_="jobLocation")
            location = loc_el.text.strip() if loc_el else "Unknown"
            print(f"Title: {title[:40]}, Location: {location}")
    except Exception as e:
        print(f"Error: {e}")

def print_gotfriends():
    print("\n--- GotFriends Raw Locations ---")
    url = "https://www.gotfriends.co.il/jobslobby/projects/product-manager/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        list_div = soup.find(class_="jobs_list")
        if list_div:
            items = list_div.find_all(class_="item")
            for item in items:
                title_el = item.find("h2", class_="title") or item.find(class_="title")
                title = title_el.text.strip() if title_el else ""
                loc_el = item.find(class_="info-data")
                location = loc_el.text.strip() if loc_el else "Unknown"
                print(f"Title: {title[:40]}, Location: {location}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    # Redirect stdout to raw_locations.txt
    with open("scratch/raw_locations.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        print_drushim()
        print_jobmaster()
        print_gotfriends()
    print("Done writing to scratch/raw_locations.txt")
