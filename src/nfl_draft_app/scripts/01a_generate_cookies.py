import os
import json
from playwright.sync_api import sync_playwright

# Define the path for the cookies file
COOKIES_FILE = "auth/cookies.json"
LOGIN_URL = "https://www.fantasypros.com/accounts/signin/"

def generate_cookies():
    """
    Launches a browser for the user to log in manually and then saves the session cookies.
    """
    # Ensure the auth directory exists
    os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"Navigating to {LOGIN_URL}...")
        page.goto(LOGIN_URL)

        print("\n" + "="*50)
        print("ACTION REQUIRED:")
        print("Please log in to your FantasyPros account in the browser window.")
        print("Complete any CAPTCHA challenges if they appear.")
        print("Once you are successfully logged in, the script will detect it and save the session cookies.")
        print("="*50 + "\n")

        # Wait for the user to navigate away from the login page after a successful login.
        # This is a simple way to detect that the login was successful.
        page.wait_for_url(lambda url: url != LOGIN_URL, timeout=300000) # 5-minute timeout

        print("Login detected. Saving session cookies...")

        # Save cookies from the browser context
        cookies = context.cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f)

        print(f"Cookies saved successfully to {COOKIES_FILE}")
        browser.close()

if __name__ == "__main__":
    generate_cookies()
