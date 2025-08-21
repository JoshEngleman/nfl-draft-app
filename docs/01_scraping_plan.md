# Phase 1: Scraping FantasyPros Projections

This document outlines the plan to scrape fantasy football projection data from FantasyPros.com and store it in a local database.

## 1. Objective

The primary goal is to replicate the data-gathering portion of the user's Excel-based application by programmatically fetching player projections for QB, RB, WR, TE, K, and DST positions from FantasyPros.

## 2. Tech Stack

- **Language:** Python
- **Package Manager:** Rye
- **Web Scraping:** `playwright` (for browser automation to handle login and dynamic content)
- **Data Handling:** `pandas` (to structure scraped data)
- **Database:** SQLite (for simple, local file-based storage)
- **Environment Variables:** `python-dotenv` (to manage credentials securely)

## 3. Implementation Plan

### Step 1: Project Setup & Dependencies

1.  Create a `scripts` directory within `src/nfl_draft_app/` to house our data collection scripts.
2.  Add the required Python packages using Rye:
    ```bash
    rye add "playwright" "pandas" "python-dotenv" "SQLAlchemy" "lxml"
    rye sync
    ```
3. Run `playwright install` to install browser binaries.

### Step 2: Create the Scraping Script

A new script, `src/nfl_draft_app/scripts/01_scrape_fantasypros.py`, will be created to perform the following actions:

1.  **Configuration:**
    *   Load FantasyPros credentials (`fp-username`, `fp-password`) from the `.env` file.
    *   Define a list of URLs for each position's projection page.

2.  **Authentication:**
    *   A function will launch a `playwright` browser instance.
    *   It will navigate to `https://www.fantasypros.com/login/`.
    *   It will programmatically fill in the username and password and click the login button.

3.  **Data Scraping:**
    *   For each position (QB, RB, WR, TE, K, DST):
        *   Navigate to the corresponding projections URL.
        *   Identify and extract the main data table from the page.
        *   Use `pandas.read_html` to parse the table into a DataFrame.
        *   Clean the data (e.g., handle multi-level headers if present, ensure correct data types).

4.  **Data Storage:**
    *   Initialize a connection to a SQLite database file (e.g., `data/fantasy_pros.db`).
    *   For each position's DataFrame, save it to a new table in the database. The table will be named after the position (e.g., `qb_projections`, `rb_projections`).

### Step 3: Execution and Verification

- The script will be runnable from the command line.
- After execution, we will verify that the SQLite database file is created and contains the expected tables with data.

## 4. Next Steps

Once the data is successfully scraped and stored, the next phase will involve building the web interface (likely with Streamlit) to display and interact with this data, replicating the functionality of the original Excel app.
