from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from scraper import DelhiHighCourtOCRScraper
from database import init_db, CaseQuery
from config import Config
import os
import time
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Ensure PDF directory exists
os.makedirs(app.config['PDF_DIR'], exist_ok=True)

# Initialize database
SessionLocal = init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    case_types = [
        ('CRL', 'Criminal'),
        ('CIVIL', 'Civil'),
        ('WP', 'Writ Petition'),
        ('ARB', 'Arbitration')
    ]
    
    current_year = datetime.now().year
    filing_years = list(range(current_year, current_year - 10, -1))
    
    if request.method == 'POST':
        case_type = request.form.get('case_type')
        case_number = request.form.get('case_number')
        filing_year = request.form.get('filing_year')
        
        if not all([case_type, case_number, filing_year]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('index'))
        
        try:
            # Log the query in database
            db_session = SessionLocal()  # ✅ Use the session factory correctly

            new_query = CaseQuery(
                case_type=case_type,
                case_number=case_number,
                filing_year=int(filing_year),
                status='pending'
            )
            db_session.add(new_query)
            db_session.commit()
            
            # Scrape case details
            scraper = DelhiHighCourtOCRScraper()
            html_content = scraper.search_case(case_type, case_number, filing_year)
            # Parse the HTML content to extract case details
            case_details = {
                'html': html_content,
                'parties': [],
                'dates': {},
                'pdf_links': []
            }
            
            if not case_details:
                new_query.status = 'failed'
                db_session.commit()
                flash('Failed to retrieve case details. Please check the case number or try again later.', 'error')
                return redirect(url_for('index'))
            
            # Store detailed case information in database
            import json
            new_query.parties = json.dumps(case_details.get('parties', []))
            new_query.dates = json.dumps(case_details.get('dates', {}))
            new_query.pdf_links = json.dumps(case_details.get('pdf_links', []))
            
            # Update query status
            new_query.status = 'success'
            db_session.commit()
            
            # Download most recent PDF if available
            pdf_path = None
            if case_details.get('pdf_links'):
                most_recent_pdf = case_details['pdf_links'][0]
                pdf_filename = f"{case_type}_{case_number}_{filing_year}.pdf"
                pdf_path = os.path.join(app.config['PDF_DIR'], pdf_filename)
                
                try:
                    response = requests.get(most_recent_pdf['url'], stream=True, timeout=app.config['REQUEST_TIMEOUT'])
                    with open(pdf_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    case_details['pdf_path'] = pdf_filename
                except Exception as e:
                    app.logger.error(f"Failed to download PDF: {e}")
                    case_details['pdf_path'] = None
            
            return render_template('results.html',
                                 case_type=case_type,
                                 case_number=case_number,
                                 filing_year=filing_year,
                                 details=case_details)
            
        except Exception as e:
            app.logger.error(f"Error processing request: {e}")
            flash('An error occurred while processing your request. Please try again.', 'error')
            return redirect(url_for('index'))
    
    return render_template('index.html',
                         case_types=case_types,
                         filing_years=filing_years)

@app.route('/download/<filename>')
def download_pdf(filename):
    return send_from_directory(app.config['PDF_DIR'], filename, as_attachment=True)

@app.route('/history')
def history():
    SessionLocal = init_db()
    db_session = SessionLocal()
    
    # Get all successful queries, ordered by query time (newest first)
    queries = db_session.query(CaseQuery).filter_by(status='success').order_by(CaseQuery.query_time.desc()).all()
    
    # Parse JSON fields for display
    for query in queries:
        try:
            query.parties = json.loads(query.parties) if query.parties else []
            query.dates = json.loads(query.dates) if query.dates else {}
            query.pdf_links = json.loads(query.pdf_links) if query.pdf_links else []
        except:
            # If JSON parsing fails, keep as is
            pass
    
    db_session.close()
    return render_template('history.html', queries=queries)

@app.route('/export-history')
def export_history():
    SessionLocal = init_db()
    db_session = SessionLocal()
    
    # Get all successful queries, ordered by query time (newest first)
    queries = db_session.query(CaseQuery).filter_by(status='success').order_by(CaseQuery.query_time.desc()).all()
    
    # Create CSV content
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Case Type', 'Case Number', 'Filing Year', 'Search Date', 'Parties', 'Key Dates'])
    
    # Write data rows
    for query in queries:
        try:
            parties = json.loads(query.parties) if query.parties else []
            dates = json.loads(query.dates) if query.dates else {}
            
            # Format parties as string
            parties_str = '; '.join([f"{p.get('name', '')} ({p.get('type', '')})" for p in parties])
            
            # Format dates as string
            dates_str = '; '.join([f"{k}: {v}" for k, v in dates.items()])
            
            writer.writerow([
                query.case_type,
                query.case_number,
                query.filing_year,
                query.query_time.strftime('%Y-%m-%d %H:%M:%S'),
                parties_str,
                dates_str
            ])
        except Exception as e:
            # If parsing fails, write basic info
            writer.writerow([
                query.case_type,
                query.case_number,
                query.filing_year,
                query.query_time.strftime('%Y-%m-%d %H:%M:%S'),
                '',
                ''
            ])
    
    db_session.close()
    
    # Return CSV as attachment
    from flask import Response
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=case_search_history.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True)
