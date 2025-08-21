# NFL Draft App Project Tasks

## Phase 1: Data Scraping & Storage

- [ ] **1.1:** Set up project structure and install dependencies (`playwright`, `pandas`, `python-dotenv`, `SQLAlchemy`).
- [ ] **1.2:** Implement a script to log in to FantasyPros.
- [ ] **1.3:** Scrape projection data for all required positions (QB, RB, WR, TE, K, DST).
- [ ] **1.4:** Store the scraped data in a local SQLite database with separate tables for each position.
- [ ] **1.5:** Verify the data integrity and completeness in the database.

## Phase 2: Web Application Development

- [ ] **2.1:** Set up a basic Streamlit application.
- [ ] **2.2:** Create a data access layer to read from the SQLite database.
- [ ] **2.3:** Build the main user interface with position tabs.
- [ ] **2.4:** Display the projection data in sortable, filterable tables.
- [ ] **2.5:** Replicate core Excel app features (e.g., player highlighting, custom rankings).

## Phase 3: Deployment (Optional)

- [ ] **3.1:** Prepare the application for deployment.
- [ ] **3.2:** Deploy the application to a cloud service (e.g., Streamlit Cloud, Heroku).
