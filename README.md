# LinkedIn Content Scraper

A Python-based tool for scraping LinkedIn posts and sending them via email. This scraper is designed to help you stay updated with relevant content from LinkedIn by automatically collecting posts and delivering them to your inbox.

## Features

- Automated LinkedIn post scraping
- Email delivery of scraped content
- Configurable search parameters
- Chrome profile persistence
- Beautiful formatting of scraped content
- Hashtag extraction

## Prerequisites

- Python 3.x
- Chrome browser installed
- Gmail account (for sending emails)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv env
# On Windows
env\Scripts\activate
# On Unix or MacOS
source env/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
   - Copy `.envexample` to `.env`
   - Fill in your email credentials and configuration:
     ```
     EMAIL_USER=your_email@gmail.com
     EMAIL_PASSWORD=your_app_password
     SCRAPE_URL=your_linkedin_search_url
     RECIPIENT_EMAIL=recipient@example.com
     ```

## Usage

1. Configure your search URL in the `.env` file
2. Run the scraper:
```bash
python linked_scraper.py
```

Or use the provided batch file on Windows:
```bash
run_scraper.bat
```

## Configuration

### Email Setup
For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password as `EMAIL_PASSWORD` in your `.env` file

### LinkedIn Search URL
Configure your search URL in the `.env` file. The URL should be a LinkedIn search results page URL.

## Project Structure

- `linked_scraper.py` - Main scraper script
- `scraper.py` - Additional scraping utilities
- `requirements.txt` - Python dependencies
- `.env` - Environment configuration (create from .envexample)
- `chrome_profile/` - Chrome profile directory for automation

## Dependencies

- selenium==4.18.1
- webdriver-manager==4.0.1
- python-dotenv==1.0.1
- beautifulsoup4==4.12.3

## Notes

- The scraper uses a persistent Chrome profile to maintain session state
- Posts are limited to the first 5 results by default
- Make sure to comply with LinkedIn's terms of service and rate limits

## Troubleshooting

If you encounter issues:
1. Ensure your `.env` file is properly configured
2. Check your internet connection
3. Verify your email credentials
4. Make sure Chrome is installed and up to date
