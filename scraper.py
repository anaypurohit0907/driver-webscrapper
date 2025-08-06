import time
import re
import os
import requests
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from database import DriverDatabase
from file_processor import FileProcessor
from config import Config

class DriverScraper:
    def __init__(self, config):
        self.config = config
        self.db = DriverDatabase(config.db_path)
        self.processor = FileProcessor()
        self.downloaded_files = set()
        self.session = requests.Session()
        self.driver = None
        
        # Setup selenium driver
        self.setup_selenium()
    
    def setup_selenium(self):
        """Initialize Selenium WebDriver with proper configuration"""
        chrome_options = Options()
        
        # Configure download preferences
        prefs = {
            "download.default_directory": os.path.abspath(self.config.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        if self.config.headless:
            chrome_options.add_argument("--headless")
        
        # Use WebDriver Manager to handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def scrape_website(self, base_url):
        """Main scraping function for a website"""
        print(f"Starting to scrape: {base_url}")
        
        try:
            self.driver.get(base_url)
            time.sleep(2)  # Allow page to load
            
            # Find all download links
            download_links = self.find_driver_links()
            
            print(f"Found {len(download_links)} potential driver links")
            
            for link_info in download_links:
                try:
                    self.process_download_link(link_info, base_url)
                except Exception as e:
                    print(f"Error processing link {link_info.get('url', 'unknown')}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scraping website {base_url}: {e}")
    
    def find_driver_links(self):
        """Find potential driver download links on current page"""
        links = []
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Check if this looks like a driver link
            if self.is_driver_link(href, text):
                link_info = {
                    'url': href,
                    'text': text,
                    'title': link.get('title', ''),
                    'download': link.get('download', '')
                }
                links.append(link_info)
        
        # Also check for JavaScript-triggered downloads
        js_links = self.find_javascript_downloads()
        links.extend(js_links)
        
        return links
    
    def is_driver_link(self, href, text):
        """Determine if a link is likely to be a driver download"""
        # Check file extension in URL
        driver_extensions = [
            '.exe', '.msi', '.zip', '.rar', '.7z', '.cab',
            '.sys', '.inf', '.dll', '.ko', '.deb', '.rpm'
        ]
        
        href_lower = href.lower()
        if any(href_lower.endswith(ext) for ext in driver_extensions):
            return True
        
        # Check for driver-related keywords in URL or text
        driver_keywords = [
            'driver', 'drivers', 'download', 'drv', 'device',
            'hardware', 'adapter', 'controller', 'chipset',
            'firmware', 'bios', 'utility'
        ]
        
        combined_text = (href + ' ' + text).lower()
        if any(keyword in combined_text for keyword in driver_keywords):
            return True
        
        # Check for download-related patterns
        download_patterns = [
            r'download',
            r'get\s+driver',
            r'driver\s+download',
            r'latest\s+driver'
        ]
        
        for pattern in download_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True
        
        return False
    
    def find_javascript_downloads(self):
        """Find JavaScript-triggered downloads using Selenium"""
        js_links = []
        
        try:
            # Find buttons/elements that might trigger downloads
            download_buttons = self.driver.find_elements(
                By.XPATH, 
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'driver')]"
            )
            
            for button in download_buttons:
                try:
                    # Get onclick or other relevant attributes
                    onclick = button.get_attribute('onclick')
                    data_url = button.get_attribute('data-url')
                    
                    if onclick or data_url:
                        js_links.append({
                            'element': button,
                            'text': button.text,
                            'onclick': onclick,
                            'data_url': data_url
                        })
                except:
                    continue
        
        except Exception as e:
            print(f"Error finding JavaScript downloads: {e}")
        
        return js_links
    
    def process_download_link(self, link_info, base_url):
        """Process and download a driver file"""
        if 'element' in link_info:
            # Handle JavaScript download
            self.download_via_javascript(link_info, base_url)
        else:
            # Handle direct download
            self.download_file(link_info, base_url)
    
    def download_via_javascript(self, link_info, base_url):
        """Download file triggered by JavaScript"""
        try:
            # Monitor downloads folder before click
            initial_files = set(os.listdir(self.config.download_dir))
            
            # Click the element
            element = link_info['element']
            self.driver.execute_script("arguments[0].click();", element)
            
            # Wait for download to start
            time.sleep(3)
            
            # Check for new files
            max_wait = 60  # seconds
            waited = 0
            
            while waited < max_wait:
                current_files = set(os.listdir(self.config.download_dir))
                new_files = current_files - initial_files
                
                # Filter out temporary files
                new_files = {f for f in new_files if not f.endswith('.crdownload')}
                
                if new_files:
                    for filename in new_files:
                        file_path = os.path.join(self.config.download_dir, filename)
                        self.process_downloaded_file(file_path, base_url, link_info['text'])
                    break
                
                time.sleep(1)
                waited += 1
        
        except Exception as e:
            print(f"Error with JavaScript download: {e}")
    
    def download_file(self, link_info, base_url):
        """Download file from direct URL"""
        try:
            # Resolve relative URLs
            url = urljoin(base_url, link_info['url'])
            
            # Check if URL is already processed
            if url in self.downloaded_files:
                return
            
            self.downloaded_files.add(url)
            
            # Download with requests
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Determine filename
            filename = self.get_filename_from_response(response, url)
            file_path = os.path.join(self.config.download_dir, filename)
            
            # Ensure unique filename
            file_path = self.ensure_unique_filename(file_path)
            
            # Download file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Downloaded: {filename}")
            self.process_downloaded_file(file_path, base_url, link_info['text'])
        
        except Exception as e:
            print(f"Error downloading {link_info.get('url', 'unknown')}: {e}")
    
    def get_filename_from_response(self, response, url):
        """Extract filename from HTTP response or URL"""
        # Try to get filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"\'')
            return filename
        
        # Fall back to URL parsing
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename or '.' not in filename:
            filename = 'download_file'
        
        return filename
    
    def ensure_unique_filename(self, file_path):
        """Ensure filename is unique by adding number suffix if needed"""
        if not os.path.exists(file_path):
            return file_path
        
        base, ext = os.path.splitext(file_path)
        counter = 1
        
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        
        return f"{base}_{counter}{ext}"
    
    def process_downloaded_file(self, file_path, source_url, link_text):
        """Process a downloaded file for driver detection and database storage"""
        try:
            # Check if file exists and is not empty
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                print(f"File {file_path} doesn't exist or is empty")
                return
            
            # Calculate file hash
            file_hash = self.processor.calculate_hash(file_path)
            if not file_hash:
                print(f"Could not calculate hash for {file_path}")
                return
            
            # Check if this hash already exists
            if self.db.hash_exists(file_hash):
                print(f"Duplicate file detected (hash exists): {os.path.basename(file_path)}")
                os.remove(file_path)  # Remove duplicate
                return
            
            # Check if this is actually a driver file
            filename = os.path.basename(file_path)
            if not self.processor.is_driver_file(file_path, filename):
                print(f"File {filename} doesn't appear to be a driver")
                # Optionally remove non-driver files
                if not self.config.keep_non_drivers:
                    os.remove(file_path)
                return
            
            # Get file type information
            file_type, mime_type = self.processor.get_file_type(file_path)
            file_size = os.path.getsize(file_path)
            
            # Extract driver metadata
            metadata = self.processor.extract_driver_metadata(file_path)
            
            # Prepare database record
            driver_data = (
                file_hash,                          # file_hash
                filename,                           # filename
                file_path,                          # file_path
                file_size,                          # file_size
                file_type,                          # file_type
                mime_type,                          # mime_type
                source_url,                         # download_url
                urlparse(source_url).netloc,       # source_website
                metadata.get('Provider', ''),       # device_vendor
                metadata.get('DeviceDesc', ''),     # device_model
                metadata.get('DriverVer', ''),      # driver_version
                metadata.get('Class', ''),          # os_compatibility
                '',                                 # architecture
                metadata.get('CatalogFile', '')     # digital_signature
            )
            
            # Insert into database
            driver_id = self.db.insert_driver(driver_data)
            
            if driver_id:
                print(f"Successfully processed and stored: {filename} (ID: {driver_id})")
            else:
                print(f"Failed to store driver: {filename}")
        
        except Exception as e:
            print(f"Error processing downloaded file {file_path}: {e}")
    
    def crawl_multiple_sites(self, urls):
        """Crawl multiple websites for drivers"""
        for url in urls:
            try:
                print(f"\n--- Scraping {url} ---")
                self.scrape_website(url)
                time.sleep(self.config.delay_between_sites)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        if self.session:
            self.session.close()

