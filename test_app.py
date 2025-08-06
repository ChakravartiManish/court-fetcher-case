#!/usr/bin/env python3
"""
Test script for Delhi District Courts Case Lookup Application
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Test database connectivity and model creation"""
    print("Testing database...")
    try:
        from database import init_db, CaseQuery
        
        SessionLocal = init_db()
        db_session = SessionLocal()
        
        # Test creating a query record
        test_query = CaseQuery(
            case_type='CRL',
            case_number='1234',
            filing_year=2024,
            status='test',
            raw_response='Test HTML content',
            parties='[{"name": "Test Party", "type": "Petitioner"}]',
            dates='{"filing_date": "2024-01-01"}',
            pdf_links='[{"title": "Test Order", "url": "http://example.com/test.pdf"}]'
        )
        
        db_session.add(test_query)
        db_session.commit()
        
        # Query it back
        retrieved = db_session.query(CaseQuery).filter_by(status='test').first()
        if retrieved:
            print(f"✅ Database test passed: {retrieved}")
            # Clean up
            db_session.delete(retrieved)
            db_session.commit()
        else:
            print("❌ Database test failed: Could not retrieve test record")
            
        db_session.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_scraper_init():
    """Test scraper initialization"""
    print("Testing scraper initialization...")
    try:
        from scraper import DelhiDistrictCourtScraper
        
        scraper = DelhiDistrictCourtScraper()
        print("✅ Scraper initialization passed")
        return True
        
    except Exception as e:
        print(f"❌ Scraper initialization failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        from config import Config
        
        required_attrs = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'COURT_URL', 'PDF_DIR']
        for attr in required_attrs:
            if not hasattr(Config, attr):
                print(f"❌ Config test failed: Missing {attr}")
                return False
            print(f"✅ Config has {attr}: {getattr(Config, attr)}")
        
        print("✅ Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app initialization"""
    print("Testing Flask app...")
    try:
        from app import app
        
        # Test that app is configured
        if not app.config['SECRET_KEY']:
            print("❌ Flask app test failed: No secret key")
            return False
            
        # Test that routes are registered
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        expected_routes = ['/', '/history', '/export-history', '/download/<filename>']
        
        for route in expected_routes:
            if route not in rules:
                print(f"❌ Flask app test failed: Missing route {route}")
                return False
        
        print("✅ Flask app test passed")
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_directories():
    """Test that required directories exist or can be created"""
    print("Testing directories...")
    try:
        from config import Config
        
        # Test PDF directory
        pdf_dir = Config.PDF_DIR
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir, exist_ok=True)
            print(f"✅ Created PDF directory: {pdf_dir}")
        else:
            print(f"✅ PDF directory exists: {pdf_dir}")
        
        # Test static directory
        static_dir = 'static'
        if os.path.exists(static_dir):
            print(f"✅ Static directory exists: {static_dir}")
        else:
            print(f"❌ Static directory missing: {static_dir}")
            return False
        
        # Test templates directory
        templates_dir = 'templates'
        if os.path.exists(templates_dir):
            print(f"✅ Templates directory exists: {templates_dir}")
        else:
            print(f"❌ Templates directory missing: {templates_dir}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Directory test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Delhi District Courts Case Lookup - Test Suite")
    print("=" * 50)
    
    tests = [
        test_config,
        test_directories,
        test_database,
        test_scraper_init,
        test_flask_app,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 30)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print("-" * 30)
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nTo run the application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install system dependencies (Tesseract OCR)")
        print("3. Run: python app.py")
        print("4. Open: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())