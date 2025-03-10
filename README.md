# Stock Warning System Alert

This project extracts stocks required by the Taiwan Stock Exchange (TWSE) to disclose financial reports following significant press releases on the TWSE website. It scrapes press releases to extract key financial metrics such as revenue and EPS, processes the data, and promptly sends alerts via Telegram to keep investors informed.

## Features
- **Real-Time Monitoring:** Continuously monitors TWSE press releases for noteworthy financial disclosures.
- **Automated Data Extraction:** Employs web scraping to extract financial metrics like revenue and EPS.
- **Robust Error Handling:** Includes retry logic and exception management for reliable data fetching.
- **Instant Alerts:** Notifies investors via Telegram as soon as relevant information is detected.

## Technologies Used
- Python
- Selenium
- BeautifulSoup
- Telebot

## Setup and Installation
1. Clone this repository.
2. Install required dependencies using: `pip install -r requirements.txt`
3. Configure your Telegram bot API key in `main.py`.
4. Run the application with: `python main.py`

## Usage
The system will periodically check for new press releases and trigger alerts when stocks meet disclosure criteria. Ensure that you have a stable internet connection and that your Telegram bot is properly configured.

## Troubleshooting
- If connection issues occur, verify your internet settings.
- Check the console output for error messages to identify issues with data retrieval.

## License
Include license details here if applicable.
