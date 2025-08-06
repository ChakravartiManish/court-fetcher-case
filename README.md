# Delhi High Court Case Data Fetcher

This application allows users to search for case details from the Delhi High Court website and stores the results in a local database for future reference.

## Features

- Search for cases by case type, number, and filing year
- Scrape case details including parties, dates, and PDF links
- Store search history in a SQLite database
- View previous searches with detailed information
- Export search history to CSV
- Download PDF documents related to cases
- Responsive web interface

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

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and go to `http://localhost:5000`

## Usage

1. Enter the case type, case number, and filing year
2. Click "Search Case" to retrieve case details
3. View case details including parties, important dates, and PDF documents
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
│   └── style.css       # Stylesheet
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

## Error Handling

The application includes robust error handling:

- Network timeouts and retries
- Database connection management
- Graceful handling of missing or malformed data
- User-friendly error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.
