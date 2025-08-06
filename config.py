import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cases.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    COURT_URL = "https://delhihighcourt.nic.in/"
    PDF_DIR = "static/pdfs"
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 30  # Timeout for Playwright or requests in seconds
                                                                          
                            