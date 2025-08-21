import os
import time
import json
from playwright.sync_api import sync_playwright

# Define the URLs for the different positions
POSITION_URLS = {
    "qb": "https://www.fantasypros.com/nfl/projections/qb.php?week=draft",
    "rb": "https://www.fantasypros.com/nfl/projections/rb.php?week=draft",
    "wr": "https://www.fantasypros.com/nfl/projections/wr.php?week=draft",
    "te": "https://www.fantasypros.com/nfl/projections/te.php?week=draft",
    "k": "https://www.fantasypros.com/nfl/projections/k.php?week=draft",
    "dst": "https://www.fantasypros.com/nfl/projections/dst.php?week=draft",
}

# Define the URLs for ADP (Average Draft Position) data
ADP_URLS = {
    "overall": "https://www.fantasypros.com/nfl/adp/ppr-overall.php",
    "qb": "https://www.fantasypros.com/nfl/adp/ppr-qb.php",
    "rb": "https://www.fantasypros.com/nfl/adp/ppr-rb.php",
    "wr": "https://www.fantasypros.com/nfl/adp/ppr-wr.php",
    "te": "https://www.fantasypros.com/nfl/adp/ppr-te.php",
    "k": "https://www.fantasypros.com/nfl/adp/ppr-k.php",
    "dst": "https://www.fantasypros.com/nfl/adp/ppr-dst.php",
}

# Setup for cookies and download directory
COOKIES_FILE = "auth/cookies.json"
DOWNLOAD_DIR = "data/raw_projections/"

def download_projection_file(page, position, url):
    """Downloads the projection CSV for a given position."""
    print(f"Downloading {position.upper()} projections from {url}...")
    page.goto(url, timeout=30000)  # 30 second timeout

    download_path = os.path.join(DOWNLOAD_DIR, f"{position}_projections.csv")

    # Start waiting for the download before clicking the button
    try:
        with page.expect_download(timeout=30000) as download_info:  # 30 second timeout
            page.click('a.export:has(i.fa-fp-download)', timeout=10000)  # 10 second timeout

        download = download_info.value
        download.save_as(download_path)
        print(f"Successfully saved {position.upper()} projections to {download_path}")
    except Exception as e:
        print(f"Failed to download {position.upper()} projections: {e}")
        raise

def download_adp_file(page, position, url):
    """Downloads the ADP CSV for a given position."""
    print(f"Downloading {position.upper()} ADP data from {url}...")
    page.goto(url, timeout=30000)  # 30 second timeout

    download_path = os.path.join(DOWNLOAD_DIR, f"{position}_adp.csv")

    # Start waiting for the download before clicking the button
    try:
        with page.expect_download(timeout=30000) as download_info:  # 30 second timeout
            page.click('a.export:has(i.fa-fp-download)', timeout=10000)  # 10 second timeout

        download = download_info.value
        download.save_as(download_path)
        print(f"Successfully saved {position.upper()} ADP data to {download_path}")
    except Exception as e:
        print(f"Failed to download {position.upper()} ADP data: {e}")
        raise

def main():
    """Main function to orchestrate the downloading process using session cookies."""
    if not os.path.exists(COOKIES_FILE):
        print(f"Error: Cookies file not found at {COOKIES_FILE}")
        print("Please run the '01a_generate_cookies.py' script first to log in and create the cookies file.")
        return

    # Ensure the download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        with open(COOKIES_FILE, 'r') as f:
            cookies = json.load(f)
        
        context = browser.new_context(accept_downloads=True)
        context.add_cookies(cookies)
        page = context.new_page()
        
        print("Successfully loaded cookies. Starting download process...")
        
        # Download projections data
        print("\n=== Downloading Projections Data ===")
        for position, url in POSITION_URLS.items():
            try:
                download_projection_file(page, position, url)
            except Exception as e:
                print(f"Failed to download {position.upper()} projections: {e}")
            time.sleep(2)
        
        # Download ADP data
        print("\n=== Downloading ADP Data ===")
        for position, url in ADP_URLS.items():
            try:
                download_adp_file(page, position, url)
            except Exception as e:
                print(f"Failed to download {position.upper()} ADP: {e}")
            time.sleep(2)
            
        browser.close()
    print("\nDownload process completed.")

if __name__ == "__main__":
    main()
