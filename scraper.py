from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
import pytesseract
import time
import base64
import os

class DelhiHighCourtOCRScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Use Google Chrome binary
        chrome_options.binary_location = '/usr/bin/google-chrome-stable'
        
        # Try different chromedriver paths
        chromedriver_paths = [
            '/usr/local/bin/chromedriver',
            '/usr/bin/chromedriver',
            'chromedriver'
        ]
        
        service = None
        for path in chromedriver_paths:
            try:
                if os.path.exists(path) or path == 'chromedriver':
                    service = Service(path)
                    break
            except:
                continue
        
        if service is None:
            raise Exception("ChromeDriver not found. Please install ChromeDriver.")
        
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            raise Exception(f"Failed to initialize Chrome WebDriver: {str(e)}")

    def solve_captcha_with_ocr(self, image_path):
        image = Image.open(image_path).convert("L")
        image = image.point(lambda x: 0 if x < 150 else 255, '1')  # basic threshold
        return pytesseract.image_to_string(image, config='--psm 7').strip()

    def search_case(self, case_type, case_no, case_year):
        self.driver.get("https://delhihighcourt.nic.in/app/case-number")
        time.sleep(3)

        # Fill in the case fields
        self.driver.find_element(By.ID, "caseType").send_keys(case_type)
        self.driver.find_element(By.ID, "caseNumber").send_keys(case_no)
        self.driver.find_element(By.ID, "caseYear").send_keys(case_year)

        # Download and solve CAPTCHA
        captcha_img = self.driver.find_element(By.XPATH, '//img[contains(@src, "Captcha")]')
        captcha_base64 = captcha_img.screenshot_as_base64
        with open("captcha.png", "wb") as f:
            f.write(base64.b64decode(captcha_base64))

        captcha_text = self.solve_captcha_with_ocr("captcha.png")
        print(f"[INFO] OCR Solved CAPTCHA: {captcha_text}")

        self.driver.find_element(By.ID, "captcha").send_keys(captcha_text)
        self.driver.find_element(By.XPATH, '//button[contains(text(), "Search")]').click()

        time.sleep(3)
        html = self.driver.page_source
        self.driver.quit()

        return html
