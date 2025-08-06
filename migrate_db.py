import sqlite3
import json
from datetime import datetime

def migrate_database():
    """Add missing columns to the existing case_queries table"""
    conn = sqlite3.connect('cases.db')
    cursor = conn.cursor()
    
    # Add parties column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE case_queries ADD COLUMN parties JSON")
        print("Added 'parties' column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'parties' column already exists")
        else:
            print(f"Error adding 'parties' column: {e}")
    
    # Add dates column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE case_queries ADD COLUMN dates JSON")
        print("Added 'dates' column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'dates' column already exists")
        else:
            print(f"Error adding 'dates' column: {e}")
    
    # Add pdf_links column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE case_queries ADD COLUMN pdf_links JSON")
        print("Added 'pdf_links' column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'pdf_links' column already exists")
        else:
            print(f"Error adding 'pdf_links' column: {e}")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database migration completed!")

if __name__ == "__main__":
    migrate_database()
    
    
    
    
