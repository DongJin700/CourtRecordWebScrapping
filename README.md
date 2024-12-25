# CourtRecordWebScrapping
A Python-based web scraping tool leveraging Selenium to extract magistrate court records from a web portal, automating data collection and processing for eviction cases.

# Automated Magistrate Court Record Scraper

A Python-based web scraping project designed to automate the extraction of magistrate court records from a web portal. This tool leverages Selenium to navigate the website, perform smart searches, and collect detailed case information such as claim numbers, case types, claim dates, and party details. The scraped data is then stored in a CSV file for further analysis.

---

## Features

- **Automated Login**: Uses Selenium to log into the portal with credentials.
- **Smart Search Functionality**: Iterates through a range of claim numbers to locate relevant cases.
- **Dynamic Data Extraction**: Scrapes case details including claim dates, claim statuses, plaintiffs, defendants, and addresses.
- **Error Handling and Retry Logic**: Captures failed claims for retry and logs errors in the output CSV.
- **CSV Export**: Outputs structured data into a CSV file for further processing or reporting.

---

## How It Works

1. **Login to the Portal**: Automates login to the DeKalb County Magistrate Court portal.
2. **Search for Claims**: Iteratively searches for claim numbers in a specified range.
3. **Extract Data**: Scrapes details from each case, including:
   - Claim Number
   - Case Type
   - Claim Date
   - Claim Status
   - Plaintiff and Defendant Information
4. **Save Results**: Exports the collected data into a timestamped CSV file.

---

## Technologies Used

- **Python**
- **Selenium**
- **CSV Module**
- **WebDriver (ChromeDriver)**

---

## Prerequisites

1. Install Python and required libraries:
   ```bash
   pip install selenium
   
   
2. Download ChromeDriver and place it in your system's PATH: ChromeDriver Download

