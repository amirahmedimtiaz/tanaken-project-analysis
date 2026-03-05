import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import hashlib

# Set the base URL for the Tanaken website
BASE_URL = "https://www.tanaken-1982.co.jp"
MAIN_PAGE_URL = f"{BASE_URL}/ja/case.html"
CACHE_DIR = "cache"

# Ensure cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Set the headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_soup(url):
    """
    Fetches a URL and returns a BeautifulSoup object, using a local cache if available.
    """
    # Create a unique filename for the cache based on the URL
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{url_hash}.html")

    # Check if we have a cached version
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return BeautifulSoup(f.read(), "lxml")

    # If not cached, fetch from the web
    try:
        print(f"Fetching from web: {url}")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        # Save to cache
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        return BeautifulSoup(response.text, "lxml")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_projects_from_main_page(soup):
    """
    Parses the main list page to get all project titles, dates, and links.
    """
    projects = []
    case_items = soup.find_all("h3")
    
    for item in case_items:
        link_tag = item.select_one('span.news_tx a')
        if not link_tag:
            continue
            
        title = link_tag.get_text(strip=True)
        link = link_tag['href']
        
        if not link.startswith("http"):
            link = f"{BASE_URL}{link}"
            
        date_tag = item.select_one('span.date')
        date = date_tag.get_text(strip=True) if date_tag else "N/A"
        
        img_tag = item.select_one('span.n_img img')
        thumbnail = img_tag['src'] if img_tag else "N/A"
        if thumbnail.startswith("/"):
            thumbnail = f"{BASE_URL}{thumbnail}"
            
        projects.append({
            "title": title,
            "date": date,
            "link": link,
            "thumbnail": thumbnail
        })
        
    print(f"Found {len(projects)} projects on the main page.")
    return projects

def get_project_details(project_url):
    """
    Visits a project detail page and extracts additional information.
    """
    soup = get_soup(project_url)
    if not soup:
        return {}
    
    details = {}
    
    # 1. Extract Structured Data from the Vertical Tables (New)
    # This captures fields like "完工年月", "場所", "建物種別", etc.
    tables = soup.select('.vertical-table table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.get_text(strip=True)
                val = td.get_text(strip=True)
                if key:
                    details[key] = val

    # 2. Extract description
    info_section = soup.select_one('.caseInfo') or soup.select_one('.detail_tx')
    details['description'] = info_section.get_text(separator="\n", strip=True) if info_section else "N/A"
    
    # 3. Extract main image
    main_img = soup.select_one('.caseDetail .main_img img')
    details['main_image'] = f"{BASE_URL}{main_img['src']}" if main_img and main_img['src'].startswith('/') else "N/A"
    
    # 4. Extract gallery images
    gallery_images = []
    for img in soup.select('.gallery img, .caseDetail img'):
        src = img.get('src', '')
        if src.startswith("/"):
            gallery_images.append(f"{BASE_URL}{src}")
    details['gallery'] = ", ".join(list(set(gallery_images)))
    
    return details

def main():
    print(f"Starting crawl of {MAIN_PAGE_URL}...")
    main_soup = get_soup(MAIN_PAGE_URL)
    
    if not main_soup:
        return
        
    projects = extract_projects_from_main_page(main_soup)
    all_data = []
    
    for i, p in enumerate(projects):
        print(f"[{i+1}/{len(projects)}] Processing: {p['title']}")
        
        detail_data = get_project_details(p['link'])
        all_data.append({**p, **detail_data})
        
        # Only sleep if we are actually hitting the network
        # (Simplified: always sleep for safety, or check if cache exists)
        url_hash = hashlib.md5(p['link'].encode()).hexdigest()
        if not os.path.exists(os.path.join(CACHE_DIR, f"{url_hash}.html")):
            time.sleep(1) 
        
    df = pd.DataFrame(all_data)
    df.to_csv("tanaken_projects.csv", index=False, encoding="utf-8-sig")
    print("\nSuccess! Data saved to 'tanaken_projects.csv'.")

if __name__ == "__main__":
    main()
