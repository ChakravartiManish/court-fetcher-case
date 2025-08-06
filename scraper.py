import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin
import json
from PIL import Image
import pytesseract
import io
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DelhiDistrictCourtScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://delhicourts.nic.in"
        self.case_status_url = "https://delhicourts.nic.in/casestatus"
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Chrome options for headless browsing
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')

    def solve_captcha_with_ocr(self, image_data):
        """Solve CAPTCHA using OCR"""
        try:
            # Convert base64 to PIL Image
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess image for better OCR
            image = image.convert('L')  # Convert to grayscale
            image = image.point(lambda x: 0 if x < 128 else 255, '1')  # Threshold
            
            # Use OCR to extract text
            captcha_text = pytesseract.image_to_string(image, config='--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz').strip()
            
            return captcha_text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def search_case_by_number(self, case_type, case_number, filing_year, district="Central District"):
        """Search case by case number using Selenium for better reliability"""
        driver = None
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(self.case_status_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Find the Central District section (or specified district)
            district_section = None
            try:
                district_elements = driver.find_elements(By.XPATH, f"//h3[contains(text(), '{district}')]")
                if district_elements:
                    district_section = district_elements[0].find_element(By.XPATH, "./following-sibling::div[1]")
                else:
                    # Fallback to first available district
                    district_section = driver.find_element(By.XPATH, "//h3[contains(@class, 'district') or contains(text(), 'District')]/following-sibling::div[1]")
            except:
                # If district structure is different, try direct case number search
                pass
            
            # Look for "CASE NUMBER WISE" link
            case_number_link = None
            if district_section:
                try:
                    case_number_link = district_section.find_element(By.XPATH, ".//a[contains(text(), 'CASE NUMBER WISE')]")
                except:
                    pass
            
            if not case_number_link:
                # Try to find any case number search link
                case_number_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'CASE NUMBER WISE')]")
                if case_number_links:
                    case_number_link = case_number_links[0]
            
            if case_number_link:
                case_number_link.click()
                time.sleep(2)
                
                # Fill in the case search form
                try:
                    # Look for case type dropdown
                    case_type_select = driver.find_element(By.NAME, "case_type")
                    select = Select(case_type_select)
                    select.select_by_value(case_type)
                except:
                    try:
                        # Alternative method if dropdown structure is different
                        case_type_input = driver.find_element(By.ID, "case_type")
                        case_type_input.send_keys(case_type)
                    except:
                        pass
                
                # Fill case number
                try:
                    case_number_input = driver.find_element(By.NAME, "case_number")
                    case_number_input.clear()
                    case_number_input.send_keys(case_number)
                except:
                    try:
                        case_number_input = driver.find_element(By.ID, "case_number")
                        case_number_input.clear()
                        case_number_input.send_keys(case_number)
                    except:
                        pass
                
                # Fill year
                try:
                    year_input = driver.find_element(By.NAME, "year")
                    year_input.clear()
                    year_input.send_keys(str(filing_year))
                except:
                    try:
                        year_select = driver.find_element(By.NAME, "year")
                        select = Select(year_select)
                        select.select_by_value(str(filing_year))
                    except:
                        pass
                
                # Handle CAPTCHA if present
                try:
                    captcha_img = driver.find_element(By.XPATH, "//img[contains(@src, 'captcha') or contains(@src, 'Captcha')]")
                    if captcha_img:
                        # Get CAPTCHA image as base64
                        captcha_base64 = driver.execute_script("""
                            var canvas = document.createElement('canvas');
                            var ctx = canvas.getContext('2d');
                            var img = arguments[0];
                            canvas.width = img.width;
                            canvas.height = img.height;
                            ctx.drawImage(img, 0, 0);
                            return canvas.toDataURL('image/png').substring(22);
                        """, captcha_img)
                        
                        captcha_text = self.solve_captcha_with_ocr(captcha_base64)
                        if captcha_text:
                            captcha_input = driver.find_element(By.NAME, "captcha")
                            captcha_input.clear()
                            captcha_input.send_keys(captcha_text)
                except:
                    pass
                
                # Submit the form
                try:
                    submit_button = driver.find_element(By.XPATH, "//input[@type='submit' or @value='Search' or @value='Go']")
                    submit_button.click()
                except:
                    try:
                        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Search') or contains(text(), 'Go')]")
                        submit_button.click()
                    except:
                        pass
                
                # Wait for results
                time.sleep(3)
                
                # Get the page source with results
                html_content = driver.page_source
                
                # Parse the results
                case_details = self.parse_case_details(html_content)
                
                return case_details
            
            return None
            
        except Exception as e:
            print(f"Error in case search: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def parse_case_details(self, html_content):
        """Parse case details from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            case_details = {
                'html': html_content,
                'parties': [],
                'dates': {},
                'pdf_links': [],
                'raw_response': html_content
            }
            
            # Look for case information table
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        header = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        # Extract parties information
                        if 'petitioner' in header or 'plaintiff' in header or 'appellant' in header:
                            case_details['parties'].append({
                                'name': value,
                                'type': 'Petitioner/Plaintiff/Appellant'
                            })
                        elif 'respondent' in header or 'defendant' in header:
                            case_details['parties'].append({
                                'name': value,
                                'type': 'Respondent/Defendant'
                            })
                        
                        # Extract important dates
                        if 'filing' in header or 'registration' in header:
                            case_details['dates']['filing_date'] = value
                        elif 'hearing' in header or 'next' in header:
                            case_details['dates']['next_hearing'] = value
                        elif 'disposal' in header or 'judgment' in header:
                            case_details['dates']['disposal_date'] = value
            
            # Look for PDF links
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
            for link in pdf_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    case_details['pdf_links'].append({
                        'title': link.get_text(strip=True) or 'Court Order/Judgment',
                        'url': full_url
                    })
            
            # Also look for links that might lead to orders/judgments
            order_links = soup.find_all('a', text=re.compile(r'order|judgment|view', re.I))
            for link in order_links:
                href = link.get('href')
                if href and 'pdf' in href.lower():
                    full_url = urljoin(self.base_url, href)
                    case_details['pdf_links'].append({
                        'title': link.get_text(strip=True),
                        'url': full_url
                    })
            
            return case_details
            
        except Exception as e:
            print(f"Error parsing case details: {e}")
            return {
                'html': html_content,
                'parties': [],
                'dates': {},
                'pdf_links': [],
                'raw_response': html_content
            }

    def search_case(self, case_type, case_number, filing_year):
        """Main method to search for case details"""
        return self.search_case_by_number(case_type, case_number, filing_year)

# Keep backward compatibility
DelhiHighCourtOCRScraper = DelhiDistrictCourtScraper
