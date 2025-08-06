# Indian Court Case Information Fetcher

This web application allows users to search for case details from **Delhi District Courts** and stores the results in a local database for future reference.

## Target Court

**Delhi District Courts** (https://delhicourts.nic.in/casestatus)
- Selected for reliable case status search functionality
- Provides comprehensive case information including parties, dates, and orders
- Supports multiple search methods (Case Number, Party Name, FIR, etc.)

## Features

- Search for cases by case type, number, and filing year
- Scrape case details including parties' names, filing & next-hearing dates, and order/judgment PDF links
- Store each query & raw response in SQLite database
- View previous searches with detailed information
- Export search history to CSV
- Download PDF documents related to cases
- Responsive web interface with user-friendly error handling
- Bypass CAPTCHA and view-state tokens programmatically

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd court-data-fetcher
   ```

2. Create a virtual environment:
   ```
   python -m venv myvenv
   source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Install system dependencies for OCR (if using CAPTCHA solving):
   ```
   # Ubuntu/Debian:
   sudo apt-get install tesseract-ocr
   
   # macOS:
   brew install tesseract
   
   # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and go to `http://localhost:5000`

## Usage

1. Enter the case type, case number, and filing year
2. Click "Search Case" to retrieve case details
3. View case details including:
   - Parties' names (petitioner/respondent)
   - Filing date and next hearing date
   - Order/judgment PDF links (most recent downloadable)
4. Download PDF documents directly from the application
5. View search history on the history page
6. Export search history to CSV for offline analysis

## Project Structure

```
court-data-fetcher/
├── app.py              # Main Flask application
├── scraper.py          # Web scraping functionality
├── database.py         # Database models and initialization
├── config.py           # Configuration settings
├── requirements.txt    # Python package dependencies
├── cases.db            # SQLite database (created automatically)
├── static/             # Static files (CSS, PDFs)
│   ├── style.css       # Stylesheet
│   └── pdfs/           # Downloaded PDF files
└── templates/          # HTML templates
    ├── index.html      # Main search page
    ├── results.html    # Case details page
    └── history.html    # Search history page
```

## Configuration

The application can be configured through `config.py`:

- `SECRET_KEY`: Flask secret key for sessions
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `COURT_URL`: Base URL for the court website
- `PDF_DIR`: Directory for storing downloaded PDFs
- `MAX_RETRIES`: Maximum number of retry attempts for failed requests
- `REQUEST_TIMEOUT`: Timeout for web requests in seconds

## Database Schema

The application uses a SQLite database with a single table:

```
case_queries:
- id (Integer, Primary Key)
- case_type (String)
- case_number (String)
- filing_year (Integer)
- query_time (DateTime)
- raw_response (Text)
- status (String)
- parties (JSON)
- dates (JSON)
- pdf_links (JSON)
```

## Web Scraping Approach

The application uses a combination of techniques to bypass common anti-scraping measures:

1. **Session Management**: Maintains session cookies across requests
2. **CAPTCHA Handling**: Uses OCR (Tesseract) to solve simple text CAPTCHAs
3. **ViewState Tokens**: Automatically extracts and includes required form tokens
4. **Request Headers**: Mimics browser requests with appropriate headers
5. **Rate Limiting**: Implements delays between requests to avoid detection

## Error Handling

The application includes robust error handling:

- Network timeouts and retries
- Database connection management
- Graceful handling of missing or malformed data
- User-friendly error messages for:
  - Invalid case numbers
  - Site downtime
  - CAPTCHA solving failures
  - PDF download errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This application is for educational purposes only. Users are responsible for complying with the terms of service of the target websites and applicable laws regarding web scraping.
